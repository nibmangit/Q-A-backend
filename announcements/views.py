from rest_framework import generics, permissions
from .models import Announcement
from .serializers import AnnouncementSerializer

class AnnouncementListCreateView(generics.ListCreateAPIView):
    queryset = Announcement.objects.all().order_by('-date')
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

class AnnouncementRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]