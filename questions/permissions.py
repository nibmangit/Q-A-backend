from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow safe methods to anyone; write methods only to author or staff."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # assume object has .author attribute
        return getattr(obj, "author", None) == request.user or request.user.is_staff