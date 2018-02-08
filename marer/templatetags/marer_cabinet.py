from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.assignment_tag
def get_last_comment(issue, user):
    return mark_safe(issue.get_last_comment_for_user(user))


@register.assignment_tag
def get_urgency(issue, user):
    return mark_safe(issue.get_urgency_for_user(user))
