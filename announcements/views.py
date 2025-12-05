from rest_framework import generics, permissions,filters
from .models import Announcement
from .serializers import AnnouncementSerializer
from django.contrib.auth import get_user_model
from notifications.utils import create_notification

User = get_user_model()
class AnnouncementListCreateView(generics.ListCreateAPIView):
    queryset = Announcement.objects.all().order_by('-date')
    serializer_class = AnnouncementSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "body"]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        announcement = serializer.save()
        users = User.objects.filter(is_active = True)
        for user in users:
            create_notification(
                user=user,
                noti_type="announcement",
                message=f"New announcement: {announcement.title}",
                related_object_id=announcement.id,
                related_object_type="Announcement"
            )

class AnnouncementRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]