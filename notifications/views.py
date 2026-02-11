from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from questions.pagination import StandardResultsSetPagination

# 1. LIST & 2. MARK ONE AS READ (Your existing code)
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        return self.request.user.notifications.all().order_by('read','-created_at')

class NotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            notification = request.user.notifications.get(pk=pk)
            notification.read = True
            notification.save()
            return Response({"message": "Marked as read", "read": True}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)

# 3. MARK ALL AS READ
class MarkAllReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        request.user.notifications.filter(read=False).update(read=True)
        return Response({"message": "All marked as read"}, status=status.HTTP_200_OK)

# 4. DELETE ONE
class NotificationDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return self.request.user.notifications.all()

# 5. DELETE ALL
class NotificationDeleteAllView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request):
        request.user.notifications.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)