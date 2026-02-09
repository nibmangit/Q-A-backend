from django.db import models
from cloudinary.models import CloudinaryField

class Announcement(models.Model): 
    title = models.CharField(max_length=255)
    body = models.TextField()
    author = models.CharField(max_length=300)
    tags = models.JSONField(default=list, blank=True)  # list of strings
    image = CloudinaryField('image', blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.author}"