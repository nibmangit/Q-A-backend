from django.db import models
from django.conf import settings

class DiscussionRoom(models.Model):
    question = models.OneToOneField(
        'questions.Question', 
        on_delete=models.CASCADE, 
        related_name='discussion_room'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    participant_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Room: {self.question.title[:30]}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Plain Text'),
        ('code', 'Code Snippet'),
        ('image', 'Image'),
        ('system', 'System Notification'),
    )

    room = models.ForeignKey(DiscussionRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    is_pinned = models.BooleanField(default=False)
    reactions = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user.username if self.user else 'System'}: {self.content[:20]}"