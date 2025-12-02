from django.urls import path
from .views import ( ConversationListCreateView, MessageListView, 
                    MessageCreateView,
                    )

urlpatterns = [
    path("conversations/", ConversationListCreateView.as_view(), name="conversations-list-create"),
    path("conversations/<int:conversation_id>/messages/", MessageListView.as_view(), name="messages-list"),
    path("conversations/<int:conversation_id>/messages/send/", MessageCreateView.as_view(), name="messages-create"),
]