from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import DiscussionRoom, WriteRequest, ChatMessage, RoomSeen
from .serializers import ChatMessageSerializer, WriteRequestSerializer, BannedUserSerializer

class ChatHistoryPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ChatHistoryView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    pagination_class = ChatHistoryPagination

    def get_queryset(self):
        question_id = self.kwargs['question_id']
        return ChatMessage.objects.filter(room__question_id=question_id).order_by('-timestamp')

    def list(self, request, *args, **kwargs): 
        response = super().list(request, *args, **kwargs) 
        question_id = self.kwargs['question_id']
        room = get_object_or_404(DiscussionRoom, question_id=question_id)
        user = request.user 
        # 1. Permission checks
        is_owner = (room.question.author == user)
        is_authorized = room.authorized_writers.filter(id=user.id).exists()
        is_banned = room.banned_users.filter(id=user.id).exists() 
        
        my_seen = RoomSeen.objects.filter(user=user, room=room).first()
        others_seen = RoomSeen.objects.filter(room=room).exclude(user=user).order_by('-last_seen_timestamp').first()
        my_timestamp = my_seen.last_seen_timestamp.isoformat() if my_seen else None
        others_timestamp = others_seen.last_seen_timestamp.isoformat() if others_seen else None
        
        response.data.update({
            'user_can_write': is_owner or is_authorized,
            'is_owner': is_owner,
            'is_banned': is_banned,
            'last_seen_timestamp': my_timestamp,
            'others_last_seen_timestamp': others_timestamp,
        })
        
        return response

class RequestWriteAccessView(generics.CreateAPIView):
    serializer_class = WriteRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        room = get_object_or_404(DiscussionRoom, question_id=self.kwargs['question_id'])
        serializer.save(user=self.request.user, room=room)

class HandleWriteRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, question_id):
        room = get_object_or_404(DiscussionRoom, question_id=question_id)
        
        # Security: Compare logged-in user to the Question author object
        if room.question.author != request.user:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
            
        pending_requests = WriteRequest.objects.filter(room=room, status='pending')
        serializer = WriteRequestSerializer(pending_requests, many=True)
        return Response(serializer.data)
    
    def patch(self, request, request_id):
        write_req = get_object_or_404(WriteRequest, id=request_id)
        
        if write_req.room.question.author != request.user:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get('status') 
        if new_status not in ['accepted', 'rejected']:
            return Response({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        write_req.status = new_status
        write_req.save()

        if new_status == 'accepted':
            write_req.room.authorized_writers.add(write_req.user)
            
        return Response({"status": f"Request {new_status}"})

class MessageControlView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, message_id):
        message = get_object_or_404(ChatMessage, id=message_id)
        
        # Permission: Sender OR Question Author
        if message.user == request.user or message.room.question.author == request.user:
            message.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    def patch(self, request, message_id):
        message = get_object_or_404(ChatMessage, id=message_id)

        if message.user != request.user:
            return Response({"detail": "You can only edit your own messages."}, status=status.HTTP_403_FORBIDDEN)

        new_content = request.data.get('content')
        if not new_content:
            return Response({"detail": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)

        message.content = new_content
        message.save()

        serializer = ChatMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class BannedUsersListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, question_id):
        room = get_object_or_404(DiscussionRoom, question_id=question_id)
        
        # Security: Only the room author can see the banned list
        if room.question.author != request.user:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
            
        banned_users = room.banned_users.all()
        serializer = BannedUserSerializer(banned_users, many=True)
        return Response(serializer.data)