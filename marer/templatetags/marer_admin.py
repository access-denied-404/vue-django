from django import template
from django.conf import settings

register = template.Library()


def alter_add_url(inline_adm, parent_obj):
    return inline_adm.get_alter_add_url(parent_obj)


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, '')


register.filter('alter_add_url', alter_add_url)
