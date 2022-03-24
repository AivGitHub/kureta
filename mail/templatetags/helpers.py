from django import template
from django.utils.safestring import mark_safe

import settings


register = template.Library()


@register.simple_tag
def get_setting_value(name):
    if 'password' in name.lower() or 'secret' in name.lower():
        raise PermissionError(f'Attribute `{name}` can\'t be loaded through tag.')

    return getattr(settings, name)


@register.filter(name='split')
def split(tags, arg):
    return tags.split(arg)
