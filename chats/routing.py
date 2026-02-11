from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # This regex captures the Question ID from the URL
    re_path(r'ws/chat/(?P<question_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]