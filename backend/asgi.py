import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from backend.middleware import TokenAuthMiddleware  # keep as-is
from chats.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# initialize Django
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": TokenAuthMiddleware(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    }
)