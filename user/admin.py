from django.contrib import admin
from .models import User, Badge 

@admin.register(User)
class UserAdmin(admin.ModelAdmin): 
    list_display = ("id", "name", "email", "role", "points", "questions_count", "answers_count", "badge_list", "date_joined")
    list_filter = (("role"), "is_active")
    search_fields = ("name", "email")
    readonly_fields = ("date_joined", "updated_at")
    list_per_page = 20 
    actions = ["reset_points"] 
 
    def questions_count(self, obj):
        return obj.questions.count() if hasattr(obj, "questions") else 0
    questions_count.short_description = "Questions"
 
    def answers_count(self, obj):
        return obj.answers.count() if hasattr(obj, "answers") else 0
    answers_count.short_description = "Answers"
 
    def badge_list(self, obj):
        return ", ".join([b.name for b in obj.badges.all()])
    badge_list.short_description = "Badges"
 
    def reset_points(self, request, queryset):
        updated = queryset.update(points=0)
        self.message_user(request, f"Reset points for {updated} user(s).")
    reset_points.short_description = "Reset points to 0 for selected users"
 
# @admin.register(Badge)
# class BadgeAdmin(admin.ModelAdmin):
#     list_display = ("name", "icon", "description")
#     search_fields = ("name", "description") 
#     list_per_page = 20 

admin.site.site_header = "Q&A Platform Admin"
admin.site.site_title = "Q&A Admin Portal"
admin.site.index_title = "Welcome to Q&A Admin"
admin.site.site_url = "http://q-a-s-p.netlify.app/"