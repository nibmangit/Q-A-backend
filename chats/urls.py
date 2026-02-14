from django.urls import path
from .views import (
    BannedUsersListView,
    ChatHistoryView, 
    RequestWriteAccessView, 
    HandleWriteRequestView, 
    MessageControlView
)

urlpatterns = [
    path('history/<int:question_id>/', ChatHistoryView.as_view(), name='chat-history'),
    path('request-write/<int:question_id>/', RequestWriteAccessView.as_view(), name='request-write'),
    path('requests/<int:question_id>/', HandleWriteRequestView.as_view()),
    path('handle-request/<int:request_id>/', HandleWriteRequestView.as_view(), name='handle-request'),
    path('message/<int:message_id>/', MessageControlView.as_view(), name='message-control'),
    path('banned-users/<int:question_id>/', BannedUsersListView.as_view(), name='banned-users-list'),
]