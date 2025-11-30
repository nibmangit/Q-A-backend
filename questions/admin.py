from django.contrib import admin
from .models import Tag, Category, Question
# Register your models here.

admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Question)