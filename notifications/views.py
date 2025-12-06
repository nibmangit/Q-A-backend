from rest_framework import generics, permissions
from .models import Notification
from .serializers import NotificationSerializer
from questions.pagination import StandardResultsSetPagination

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.request.user.notifications.all().order_by('-created_at')

class NotificationMarkReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return self.request.user.notifications.all()

    def perform_update(self, serializer):
        serializer.save(read=True)