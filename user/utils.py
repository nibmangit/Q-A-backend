from datetime import date, timedelta
from .models import Badge
from notifications.utils import create_notification

def award_badge(user, badge_name):
    """
    Add a badge to a user if they don't already have it.
    Also send a notification.
    """
    try:
        badge = Badge.objects.get(name=badge_name)
    except Badge.DoesNotExist:
        return 
 
    if user.badges.filter(id=badge.id).exists():
        return
 
    user.badges.add(badge)
 
    create_notification(
        user=user,
        noti_type="badge",
        message=f"Congratulations! You earned the '{badge_name}' badge.",
        related_object_id=badge.id,
        related_object_type="badge"
    )


def check_active_user_badge(user):
    today = date.today()
 
    if not user.last_login_date:
        user.last_login_date = today
        user.login_streak = 1
        user.save()
        return

    if user.last_login_date == today: 
        return
    elif user.last_login_date == today - timedelta(days=1): 
        user.login_streak += 1
    else: 
        user.login_streak = 1

    user.last_login_date = today
    user.save()

    # Check for Active User badge
    if user.login_streak >= 7:
        award_badge(user, "Active User")
