from django import template
from users.models import Notification

register = template.Library()

@register.simple_tag
def unread_count(user):
    if not user.is_authenticated:
        return 0
    return Notification.objects.filter(recipient=user, is_read=False).count()
