from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "display_tags", "date")
    list_filter = ("author", "date")
    search_fields = ("title", "body", "author")
    ordering = ("-date",)
    list_per_page = 20 
    list_display_links = ["title"]

    def display_tags(self, obj):
        if not obj.tags:
            return "-"
        return ", ".join(obj.tags)
    display_tags.short_description = "Tags"
