from django.db import models
from user.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('answer', 'Answer'),
        ('comment', 'Comment'),
        ('message', 'Message'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    noti_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_object_id = models.IntegerField(null=True, blank=True)  # optional FK reference
    related_object_type = models.CharField(max_length=50, blank=True)  # e.g., "Question", "Answer"

    def __str__(self):
        return f"Notification for {self.user.name}: {self.message}"