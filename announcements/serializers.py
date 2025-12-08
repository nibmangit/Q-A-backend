from rest_framework import serializers
from .models import Announcement

class AnnouncementSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'body', 'author', 'tags', 'image', 'date']

        def validate_image(self, value): 
            if value: 
                valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
                if value.content_type not in valid_mime_types:
                    raise serializers.ValidationError("Unsupported file type. Allowed: jpg, png, gif.")
 
                max_size = 5 * 1024 * 1024
                if value.size > max_size:
                    raise serializers.ValidationError("Image file too large. Max size is 5MB.")