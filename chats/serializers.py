from rest_framework import serializers
from django.conf import settings
from .models import Conversation, Message
from user.models import User

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'avatar']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserShortSerializer(read_only = True)
    receiver = UserShortSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "sender","receiver", "body", "created_at","updated_at", "read"]


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserShortSerializer(many=True, read_only=True)

    lastMessage = serializers.SerializerMethodField()
    lastMessageDate = serializers.SerializerMethodField()
    unreadCount = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "participants", "lastMessage", "lastMessageDate", "unreadCount",]

    def get_lastMessage(self, obj):
        last_msg = obj.messages.order_by("-created_at").first()
        if last_msg:
            return last_msg.body
        return None

    def get_lastMessageDate(self, obj):
        last_msg = obj.messages.order_by("-created_at").first()
        if last_msg:
            return last_msg.created_at
        return None

    def get_unreadCount(self, obj):
        user = self.context.get("request").user
        return obj.messages.filter(read=False).exclude(sender=user).count()