from django.urls import path
from .views import NotificationDeleteAllView, NotificationDeleteView,MarkAllReadView, NotificationListView, NotificationMarkReadView

urlpatterns = [
    path('list/', NotificationListView.as_view(), name='notifications-list'),
    path('read/<int:pk>/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('read-all/', MarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('delete/<int:pk>/', NotificationDeleteView.as_view(), name='notification-delete'),
    path('delete-all/', NotificationDeleteAllView.as_view(), name='notification-delete-all'),

]