from django.contrib import admin
from .models import ChatMessage, DiscussionRoom,WriteRequest
# Register your models here.

admin.site.register(ChatMessage)
admin.site.register(DiscussionRoom)
admin.site.register(WriteRequest)