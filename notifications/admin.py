from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin): 
    list_display = ("id", "user", "noti_type", "short_message", "read_status", "created_at", )
    list_display_links = ("id", "short_message")
    list_filter = ("noti_type", "read", "created_at") 
    search_fields = ("message", "user__name", "user__email") 
    ordering = ("-created_at",) 
    readonly_fields = ("created_at", "related_object_id", "related_object_type")
    list_per_page = 20
 
    actions = ["mark_as_read", "mark_as_unread"] 

    def short_message(self, obj): 
        return obj.message[:40] + "..." if len(obj.message) > 40 else obj.message
    short_message.short_description = "Message"

    def read_status(self, obj):
        color = "green" if obj.read else "red"
        text = "Read" if obj.read else "Unread"
        return mark_safe(f"<span style='color:{color}; font-weight:bold'>{text}</span>")
    read_status.short_description = "Status"

    def mark_as_read(self, request, queryset):
        updated = queryset.update(read=True)
        self.message_user(request, f"{updated} notification(s) marked as read.")
    mark_as_read.short_description = "Mark selected notifications as READ"

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(read=False)
        self.message_user(request, f"{updated} notification(s) marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as UNREAD"