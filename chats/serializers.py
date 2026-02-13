from rest_framework import serializers
from .models import ChatMessage,WriteRequest, DiscussionRoom

class ChatMessageSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source = 'user.id')
    message_id = serializers.IntegerField(source='id', read_only=True)
    image = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    class_name = "ChatMessageSerializer"

    class Meta:
        model = ChatMessage
        fields = ['message_id', 'username','user_id', 'image','content', 'timestamp', 'message_type', 'reactions', 'status']
        
    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
    def get_status(self, obj):
        return 'sent'
        
        
class WriteRequestSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = WriteRequest
        fields = ['id', 'username', 'user', 'reason', 'status', 'created_at']
        read_only_fields = ['user', 'status','room']

class RoomModerationSerializer(serializers.ModelSerializer):
    """Used by the Author to see the room settings and banned list"""
    authorized_writers_count = serializers.IntegerField(source='authorized_writers.count', read_only=True)
    
    class Meta:
        model = DiscussionRoom
        fields = ['is_active', 'authorized_writers_count']