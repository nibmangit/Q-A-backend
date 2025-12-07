from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from user.models import User
from notifications.utils import create_notification
from questions.pagination import StandardResultsSetPagination
from rest_framework.throttling import ScopedRateThrottle

class ConversationListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request): 
        conversations = Conversation.objects.filter(participants=request.user).order_by('-created_at').distinct()
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(conversations, request)
        serializer = ConversationSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        # Create or return existing conversation
        other_user_id = request.data.get("userId")
        if not other_user_id:
            return Response({"error": "userId is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if conversation already exists
        conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
        if conversation:
            serializer = ConversationSerializer(conversation, context={"request": request})
            return Response(serializer.data)

        # Create new conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
        serializer = ConversationSerializer(conversation, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class MessageListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)

        
        if request.user not in conversation.participants.all():
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        messages = conversation.messages.order_by("-created_at")
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(messages, request)
        serializer = MessageSerializer(page, many=True)
        
        conversation.messages.filter(read=False).exclude(sender=request.user).update(read=True)
        
        return paginator.get_paginated_response(serializer.data)

class MessageCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_classes = 'send_message'

    def post(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user not in conversation.participants.all():
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        body = request.data.get("body")
        if not body:
            return Response({"error": "Message body is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Determine receiver (for 1-to-1 chat)
        receiver = conversation.participants.exclude(id=request.user.id).first()

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            receiver=receiver,
            body=body
        )

        serializer = MessageSerializer(message)
        if receiver:
            create_notification(
                user=receiver,
                noti_type="message",
                message=f"{request.user.name} sent you a message",
                related_object_id=message.id,
                related_object_type="Message"
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)