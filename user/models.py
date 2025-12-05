from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UserManager

class Badge(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name 


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, blank=True)  # display only
    name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    points = models.IntegerField(default=0)
    
    ROLE_CHOICES = (
        ("student", "Student"),
        ("admin", "Admin"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
    
    badges = models.ManyToManyField(Badge, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_date = models.DateField(blank=True, null=True) 
    login_streak = models.IntegerField(default=0) 
    objects = UserManager()  # link custom manager

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
