from django.urls import path
from .views import AnnouncementListCreateView, AnnouncementRetrieveUpdateDestroyView

urlpatterns = [
    path('', AnnouncementListCreateView.as_view(), name='announcements-list-create'),
    path('<int:pk>/', AnnouncementRetrieveUpdateDestroyView.as_view(), name='announcement-detail'),
]