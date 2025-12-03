from django.urls import path
from .views import NotificationListView, NotificationMarkReadView

urlpatterns = [
    path('list/', NotificationListView.as_view(), name='notifications-list'),
    path('read/<int:pk>/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
]