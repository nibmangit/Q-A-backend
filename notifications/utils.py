from .models import Notification

def create_notification(user, noti_type, message, related_object_id=None, related_object_type=None):
    """
    Creates a notification for a user.
    """
    Notification.objects.create(
        user=user,
        noti_type=noti_type,
        message=message,
        related_object_id=related_object_id,
        related_object_type=related_object_type
    )