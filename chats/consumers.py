import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import DiscussionRoom, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.question_id = self.scope['url_route']['kwargs']['question_id']
        self.room_group_name = f'chat_{self.question_id}'
        user = self.scope['user']

        # 1. Reject if not logged in or if banned
        if not user.is_authenticated or await self.is_user_banned(user):
            await self.close(code=4003) # 4003 is a custom 'Forbidden' code
            return

        # 2. Join the Room Group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

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
           
            # --- HANDLE NEW MESSAGE ---
            # Check if user has write permission (Author or Authorized)
            if not await self.can_user_write(user):
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Permission denied: You need write access.'
                }))
                return

            message_text = data.get('message')
            saved_msg = await self.save_message(user, message_text)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'content': saved_msg.content,
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

    async def chat_message(self, event):
        """Sends a new message to the browser"""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'content': event['content'],
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
    def save_message(self, user, content):
        room, created = DiscussionRoom.objects.get_or_create(question_id=self.question_id)
        return ChatMessage.objects.create(
            room=room,
            user=user,
            content=content,
            message_type='text'
        )