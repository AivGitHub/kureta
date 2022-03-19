from django import template

import settings


register = template.Library()


@register.simple_tag
def get_setting_value(name):
    if 'password' in name.lower() or 'secret' in name.lower():
        raise PermissionError(f'Attribute `{name}` can\'t be loaded through tag.')

    return getattr(settings, name)
