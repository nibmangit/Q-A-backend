from datetime import datetime
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import DiscussionRoom, ChatMessage,RoomSeen, WriteRequest
from django.core.cache import cache
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.question_id = self.scope['url_route']['kwargs']['question_id']
        self.room_group_name = f'chat_{self.question_id}'
        user = self.scope['user']
        
        self.room_id = await self.get_room_id_from_question(self.question_id)
        if not self.room_id:
            await self.close(code=4004) # Room not found
            return

        # 1. Reject if not logged in or if banned
        if not user.is_authenticated or await self.is_user_banned(user):
            await self.close(code=4003) # 4003 is a custom 'Forbidden' code
            return

        # 2. Join the Room Group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.update_last_seen(user, self.room_id)
        await self.accept()
        
        # BROADCAST that a user joined
        
        cache_key = f"online_users_{self.question_id}"
        online_data = cache.get(cache_key, {}) # {user_id: username}
        online_data[str(user.id)] = user.username
        cache.set(cache_key, online_data, 3600) # Expire in 1 hour if idle
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'presence_update_full',
                'online_users': online_data
            }
        )

    async def disconnect(self, close_code):
        # await self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )
        user = self.scope['user']
        cache_key = f"online_users_{self.question_id}"
        online_data = cache.get(cache_key, {})
        
        user_id_str = str(user.id)
        if user_id_str in online_data:
            del online_data[user_id_str]
        cache.set(cache_key, online_data, 3600)
        # BROADCAST that a user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'presence_update_full',
                'online_users': online_data
            }
        )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):  
        try:
            data = json.loads(text_data)
            action_type = data.get('type', 'message') 
            user = self.scope['user']
 
            if not user.is_authenticated:
                return

            # --- HANDLE MESSAGE DELETION ---
            if action_type == 'delete_message':
                message_id = data.get('message_id')
                if await self.can_delete_message(user, message_id):
                    await self.delete_message_from_db(message_id)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'message_deleted',
                            'message_id': message_id
                        }
                    )
                return
            
            # --- HANDLE MESSAGE EDITING ---
            if action_type == 'edit_message':
                message_id = data.get('message_id')
                new_content = data.get('message')
                
                # Verify ownership and update DB before broadcasting
                if await self.is_message_owner(user, message_id):
                    await self.update_message_in_db(message_id, new_content)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'message_edited',
                            'message_id': message_id,
                            'new_content': new_content
                        }
                    )
                return
           
            #Request handler
            if action_type == 'request_access':
                # This signal comes from the user asking to join
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'access_requested',
                        'user_id': user.id,
                        'username': user.username
                    }
                )
                return
                
            #Approval and rejection broadcast
            if action_type == 'update_request_status':
                target_user_id = data.get('user_id')
                new_status = data.get('status') # 'approved' or 'rejected'
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'request_status_changed',
                        'target_user_id': target_user_id,
                        'status': new_status
                    }
                )
                return
                
            #Typing indicator
            if action_type == 'typing':
                is_typing = data.get('is_typing', False)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_typing',
                        'user_id': user.id,
                        'username': user.username,
                        'is_typing': is_typing
                    }
                )
                return
                
            #reaction  functionality
            if action_type == 'toggle_reaction':
                message_id = data.get('message_id')
                emoji = data.get('emoji')
                
                # Update DB and get the new state of reactions
                updated_reactions = await self.toggle_msg_reaction(user, message_id, emoji)
                
                if updated_reactions is not None:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'reaction_update',
                            'message_id': message_id,
                            'reactions': updated_reactions
                        }
                    )
                return
            
            if action_type == 'mark_read':
                # Update the timestamp for the current user
                await self.update_last_seen(user, self.room_id)
                
                # Broadcast that this user has read the messages
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_read_messages',
                        'user_id': user.id,
                        'timestamp': timezone.now().isoformat(),
                        'sender_channel_name': self.channel_name
                    }
                )
                return
            
            # --- HANDLE BANNING ---
            if action_type == 'ban_user':
                target_user_id = data.get('user_id')
                # Only the Question Author (Room Owner) can ban
                if await self.is_room_author(user):
                    await self.ban_user_in_db(target_user_id)
                    # Broadcast to everyone in the room
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'user_banned_broadcast',
                            'target_user_id': target_user_id
                        }
                    )
                return

            # --- HANDLE UNBANNING ---
            if action_type == 'unban_user':
                target_user_id = data.get('user_id')
                if await self.is_room_author(user):
                    await self.unban_user_in_db(target_user_id)
                    # Broadcast to everyone
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'user_unbanned_broadcast',
                            'target_user_id': target_user_id
                        }
                    )
                return
            
            # --- HANDLE NEW MESSAGE ---
            # Check if user has write permission (Author or Authorized)
            if action_type == 'chat_message':
                if not await self.can_user_write(user):
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Permission denied: You need write access.'
                    }))
                    return

                message_text = data.get('message')
                image_url = data.get('image_url')
                msg_type = 'image' if image_url else 'text'
                saved_msg = await self.save_message(user, message_text, image_url, msg_type)
                
                await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_handler',
                    'content': saved_msg.content,
                    'image': image_url,
                    'message_type': msg_type,
                    'username': user.username,
                    'timestamp': str(saved_msg.timestamp),
                    'user_id': user.id,
                    'message_id': saved_msg.id
                }
            )
        except Exception as e:
            # This will catch and log the error if something goes wrong
            print(f"CRASH IN RECEIVE: {str(e)}")

    # --- BROADCAST HANDLERS (Methods called by group_send) ---

    async def chat_message_handler(self, event):
        """Sends a new message (text or image) to the browser"""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'content': event['content'],
            'image': event.get('image'),
            'message_type': event.get('message_type'),
            'username': event['username'],
            'timestamp': event['timestamp'],
            'user_id': event['user_id'],
            'message_id': event['message_id']
        }))

    async def message_deleted(self, event):
        """Tells the browser to remove a message from UI"""
        await self.send(text_data=json.dumps({
            'type': 'delete_confirmation',
            'message_id': event['message_id']
        }))
    
    async def message_edited(self, event):
        """Tells the browser to update a specific message's text"""
        await self.send(text_data=json.dumps({
            'type': 'edit_confirmation',
            'message_id': event['message_id'],
            'new_content': event['new_content']
        }))
    
    async def access_requested(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_access_request',
            'user_id': event['user_id'],
            'username': event['username']
        }))
        
    async def request_status_changed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'access_status_update',
            'target_user_id': event['target_user_id'],
            'status': event['status']
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing_indicator',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))
        
    async def presence_update_full(self, event):
        await self.send(text_data=json.dumps({
            'type': 'presence_update',
            'users': event['online_users']
        }))
    
    async def reaction_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction_broadcast',
            'message_id': event['message_id'],
            'reactions': event['reactions']
        }))
    
    async def user_read_messages(self, event):
        """Tells others that a user has caught up with the messages"""
        if self.channel_name != event.get('sender_channel_name'):
            await self.send(text_data=json.dumps({
                'type': 'user_read_broadcast',
                'user_id': event['user_id'],
                'timestamp': event['timestamp']
            }))
    
    #for banning
    async def user_banned_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_banned_signal',
            'target_user_id': event['target_user_id']
        }))

    async def user_unbanned_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_unbanned_signal',
            'target_user_id': event['target_user_id']
        }))
    # --- DATABASE OPERATIONS (Must be database_sync_to_async) ---
    @database_sync_to_async
    def is_user_banned(self, user):
        return DiscussionRoom.objects.filter(question_id=self.question_id, banned_users=user).exists()

    @database_sync_to_async
    def can_user_write(self, user):
        try:
            room = DiscussionRoom.objects.get(question_id=self.question_id) 
            return room.question.author == user or room.authorized_writers.filter(id=user.id).exists()
        except DiscussionRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def is_message_owner(self, user, message_id):
        return ChatMessage.objects.filter(id=message_id, user=user).exists()

    @database_sync_to_async
    def can_delete_message(self, user, message_id):
        try:
            msg = ChatMessage.objects.get(id=message_id) 
            return msg.user == user or msg.room.question.author == user
        except ChatMessage.DoesNotExist:
            return False

    @database_sync_to_async
    def update_message_in_db(self, message_id, new_content):
        """Persists edits so they stay after page refresh"""
        ChatMessage.objects.filter(id=message_id).update(content=new_content)

    @database_sync_to_async
    def delete_message_from_db(self, message_id):
        ChatMessage.objects.filter(id=message_id).delete()
    
    @database_sync_to_async
    def toggle_msg_reaction(self, user, message_id, emoji):
        try:
            msg = ChatMessage.objects.get(id=message_id)
            reactions = msg.reactions or {} # Ensure it's a dict
            user_id_str = str(user.id)
            
            existing_emoji = None
            for emj, user_list in reactions.items():
                if user_id_str in user_list:
                    existing_emoji = emj
                    break 
            if existing_emoji:
                reactions[existing_emoji].remove(user_id_str)
                if not reactions[existing_emoji]:
                    del reactions[existing_emoji]
            
            if existing_emoji != emoji:
                if emoji not in reactions:
                    reactions[emoji] = []
                reactions[emoji].append(user_id_str) 
                
            msg.reactions = reactions
            msg.save()
            return reactions
        except ChatMessage.DoesNotExist:
            return None

    #last seen login in Room Seen model
    @database_sync_to_async
    def get_room_id_from_question(self, question_id):
        try:
            room = DiscussionRoom.objects.get(question_id=question_id)
            return room.id
        except DiscussionRoom.DoesNotExist:
            return None
    @database_sync_to_async
    def update_last_seen(self, user, room_id):
        if user.is_authenticated:
            # get_or_create finds the record or makes a new one
            # .save() or update() will trigger auto_now=True
            RoomSeen.objects.update_or_create(
                user=user,
                room_id=room_id,
                defaults={} # Just triggering the auto_now timestamp
            )
    
    #for banning a user
    @database_sync_to_async
    def is_room_author(self, user):
        return DiscussionRoom.objects.filter(question_id=self.question_id, question__author=user).exists()

    @database_sync_to_async
    def ban_user_in_db(self, target_user_id):
        room = DiscussionRoom.objects.get(question_id=self.question_id)
        # 1. Add to banned list
        room.banned_users.add(target_user_id)
        # 2. Remove from authorized writers (optional but recommended)
        room.authorized_writers.remove(target_user_id)
        # 3. Clean up any pending write requests
        WriteRequest.objects.filter(room=room, user_id=target_user_id).delete()

    @database_sync_to_async
    def unban_user_in_db(self, target_user_id):
        room = DiscussionRoom.objects.get(question_id=self.question_id)
        room.banned_users.remove(target_user_id)
    
    @database_sync_to_async
    def save_message(self, user, content, image_url=None, message_type='text'):
        room = DiscussionRoom.objects.get(question_id=self.question_id)
        return ChatMessage.objects.create(
            room=room,
            user=user,
            content=content,
            image=image_url, # CloudinaryField accepts the URL string directly
            message_type=message_type
        )