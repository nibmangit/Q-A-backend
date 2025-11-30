from django.db import models
from user.models import User
# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name
class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, blank=True) 
    count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
class Question(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    answers = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title