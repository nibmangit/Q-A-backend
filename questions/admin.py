from django.contrib import admin
from .models import Tag, Category, Question, Answer, AnswerComment, AnswerLike, QuestionLike, QuestionBookmark


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ("author", "body", "likes", "dislikes", "created_at")  # include dislikes
    readonly_fields = fields  
    show_change_link = True 

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "short_question_title", "category", "author", "likes_count", "dislikes_count", "answers_count", "created_at"
    )
    list_display_links = ["short_question_title"]
    list_filter = ("category", "author__role", "created_at")  # filter by category, author role, date
    list_per_page = 20 
    search_fields = ("title", "author__name", "author__email")  # search questions by title or author
    readonly_fields = ("likes_count", "dislikes_count", "answers_count", "created_at", "updated_at")  # cannot edit these
    ordering = ("-created_at",)
    inlines = [AnswerInline]

    # Admin actions
    actions = ["reset_likes", "reset_dislikes"]

    def short_question_title(self, obj):
        return obj.title[:35] + "..." if len(obj.title) > 35 else obj.title
    short_question_title.short_description = "Title"

    # Computed fields
    def likes_count(self, obj):
        return obj.likes
    likes_count.short_description = "Likes"

    def dislikes_count(self, obj):
        return obj.dislikes
    dislikes_count.short_description = "Dislikes"

    def answers_count(self, obj):
        return obj.answers_count
    answers_count.short_description = "Answers"

    # Admin actions
    def reset_likes(self, request, queryset):
        updated = queryset.update(likes=0)
        self.message_user(request, f"Reset likes for {updated} question(s).")
    reset_likes.short_description = "Reset likes for selected questions"

    def reset_dislikes(self, request, queryset):
        updated = queryset.update(dislikes=0)
        self.message_user(request, f"Reset dislikes for {updated} question(s).")
    reset_dislikes.short_description = "Reset dislikes for selected questions"

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question_id_display", "author", "short_body", "likes", "dislikes", "created_at")
    list_filter = ("question__category", "author__role", "created_at")
    search_fields = ("body", "author__name", "author__email")
    readonly_fields = ("likes", "dislikes", "created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 20 

    list_display_links =["short_body"]

    def short_body(self, obj):
        return obj.body[:40] + "..." if len(obj.body) > 40 else obj.body
    short_body.short_description = "Body"

    def question_id_display(self, obj):
        return obj.question.id
    question_id_display.short_description = "Question ID"

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    list_display_links =["name"]
    list_per_page = 20 

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "icon", "count")
    search_fields = ("name",)
    list_display_links =["name"]
    list_per_page = 20 

@admin.register(AnswerComment)
class AnswerCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "answer_id_display", "author", "short_body", "created_at")
    list_filter = ("answer", "author__role", "created_at")
    search_fields = ("body", "author__name", "author__email")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 20 

    list_display_links =["short_body"]

    def short_body(self, obj):
        return obj.body[:40] + "..." if len(obj.body) > 40 else obj.body
    short_body.short_description = "Body"

    def answer_id_display(self, obj):
        return obj.answer.id
    answer_id_display.short_description = "Answer ID"

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "short_question_title", "is_like", "created_at")
    list_filter = ("is_like", "question__category", "user__role")
    search_fields = ("user__name", "user__email", "question__title")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 20 

    list_display_links =["short_question_title"]

    def short_question_title(self, obj):
        return obj.question.title[:40] + "..." if len(obj.question.title) > 40 else obj.question.title
    short_question_title.short_description = "Question"

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "answer", "is_like", "created_at")
    list_filter = ("is_like", "answer__question__category", "user__role")
    search_fields = ("user__name", "user__email", "answer__body")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 20 

@admin.register(QuestionBookmark)
class QuestionBookmarkAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "created_at")
    list_filter = ("user__role", "question__category")
    search_fields = ("user__name", "user__email", "question__title")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 20 

    list_display_links = ["question"]