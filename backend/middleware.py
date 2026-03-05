from channels.db import database_sync_to_async
from django.conf import settings

# Lazy imports only when needed
@database_sync_to_async
def get_user(user_id):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import AnonymousUser

    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Lazy imports here to avoid AppRegistryNotReady at startup
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from jwt import decode as jwt_decode

        # Default to anonymous user
        scope["user"] = AnonymousUser()

        # Look for token in query string (?token=...)
        query_string = scope.get("query_string", b"").decode()
        query_params = dict(x.split("=") for x in query_string.split("&") if "=" in x)
        token_key = query_params.get("token")

        if token_key:
            try:
                # Validate token
                UntypedToken(token_key)
                decoded_data = jwt_decode(token_key, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded_data.get("user_id")
                scope["user"] = await get_user(user_id)
            except (InvalidToken, TokenError, Exception) as e:
                print(f"Token Auth Error: {e}")
                # Keep anonymous if token invalid

        return await self.inner(scope, receive, send)