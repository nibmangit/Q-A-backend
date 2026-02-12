from django.db import models
from django.conf import settings

class DiscussionRoom(models.Model):
    question = models.OneToOneField('questions.Question', on_delete=models.CASCADE, related_name='discussion_room')
    authorized_writers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='allowed_discussion_rooms', blank=True)
    # Users who are blocked from the room entirely
    banned_users = models.ManyToManyField( settings.AUTH_USER_MODEL, related_name='banned_discussion_rooms', blank=True )
    
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
    
    

class WriteRequest(models.Model):
    """Users apply here to get permission to send messages."""
    room = models.ForeignKey(DiscussionRoom, on_delete=models.CASCADE, related_name='write_requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, 
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], 
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('room', 'user')