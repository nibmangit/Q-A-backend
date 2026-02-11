import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import DiscussionRoom, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 1. Get the Question ID from the URL (e.g., /ws/chat/15/)
        self.question_id = self.scope['url_route']['kwargs']['question_id']
        self.room_group_name = f'chat_{self.question_id}'

        # 2. Join the Room Group (The "Pipes")
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 3. Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # This handles receiving a message FROM the frontend
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message')
        user = self.scope['user']

        if not user.is_authenticated:
            return # Basic security check

        # 4. Save to Database (We use a helper function for this)
        saved_msg = await self.save_message(user, message_text)

        # 5. Broadcast to the Group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': saved_msg.content,
                'username': user.username,
                'timestamp': str(saved_msg.timestamp),
                'user_id': user.id
            }
        )

    # This handles sending the broadcasted message TO the browser
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
            'user_id': event['user_id']
        }))

    @database_sync_to_async
    def save_message(self, user, content):
        # Ensure the room exists
        room, created = DiscussionRoom.objects.get_or_create(question_id=self.question_id)
        # Create the message
        return ChatMessage.objects.create(
            room=room,
            user=user,
            content=content,
            message_type='text'
        )