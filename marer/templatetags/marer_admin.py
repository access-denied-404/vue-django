from django import template

register = template.Library()


def alter_add_url(inline_adm, parent_obj):
    return inline_adm.get_alter_add_url(parent_obj)


register.filter('alter_add_url', alter_add_url)
