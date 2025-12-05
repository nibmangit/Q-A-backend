from rest_framework import serializers
from .models import Announcement

class AnnouncementSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'body', 'author', 'tags', 'image', 'date']