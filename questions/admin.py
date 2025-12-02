from django.contrib import admin
from .models import Tag, Category, Question, Answer,AnswerComment,AnswerLike,QuestionLike
# Register your models here.

admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(AnswerLike)
admin.site.register(AnswerComment)
admin.site.register(QuestionLike)