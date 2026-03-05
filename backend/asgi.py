import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Initialize Django
django_asgi_app = get_asgi_application()

# Lazy import inside the application setup
def get_application():
    from backend.middleware import TokenAuthMiddleware
    from chats.routing import websocket_urlpatterns

    return ProtocolTypeRouter(
        {
            "http": django_asgi_app,
            "websocket": TokenAuthMiddleware(
                URLRouter(websocket_urlpatterns)
            ),
        }
    )

application = get_application()