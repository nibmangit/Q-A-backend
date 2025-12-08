# from django.contrib import admin
# from .models import Conversation, Message

# class MessageInline(admin.TabularInline):
#     model = Message
#     extra = 0
#     fields = ("sender", "receiver", "short_body", "read", "created_at")
#     readonly_fields = fields  # messages should not be edited here
#     show_change_link = True

#     def short_body(self, obj):
#         return (obj.body[:40] + "...") if len(obj.body) > 40 else obj.body
#     short_body.short_description = "Message"

# @admin.register(Conversation)
# class ConversationAdmin(admin.ModelAdmin):
#     list_display = ("id", "participants_list", "messages_count", "latest_message", "created_at")
#     search_fields = ("participants__name", "participants__email")
#     ordering = ("-created_at",)
#     inlines = [MessageInline]
#     list_filter = ("created_at",)
#     list_per_page = 20 

#     def participants_list(self, obj):
#         return ", ".join([p.name for p in obj.participants.all()])
#     participants_list.short_description = "Participants"

#     def messages_count(self, obj):
#         return obj.messages.count()
#     messages_count.short_description = "Messages"

#     def latest_message(self, obj):
#         last_msg = obj.messages.order_by("-created_at").first()
#         return last_msg.created_at if last_msg else "No messages"
#     latest_message.short_description = "Last Activity"

# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ("id", "conversation", "sender", "receiver",
#                     "short_body", "read", "created_at")
#     list_filter = ("read", "created_at", "sender", "receiver")
#     list_per_page = 20 
#     search_fields = ("body", "sender__name", "receiver__name")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at", "updated_at")
#     actions = ["mark_as_read", "mark_as_unread"]

#     def short_body(self, obj):
#         return (obj.body[:50] + "...") if len(obj.body) > 50 else obj.body
#     short_body.short_description = "Message"

#     def mark_as_read(self, request, queryset):
#         count = queryset.update(read=True)
#         self.message_user(request, f"Marked {count} message(s) as read.")
#     mark_as_read.short_description = "Mark selected as Read"

#     def mark_as_unread(self, request, queryset):
#         count = queryset.update(read=False)
#         self.message_user(request, f"Marked {count} message(s) as unread.")
#     mark_as_unread.short_description = "Mark selected as Unread"
