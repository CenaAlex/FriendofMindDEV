from django import template

register = template.Library()

@register.filter
def replace(value, args):
    """
    Replace all occurrences of a substring in a string.
    Usage: {{ value|replace:"old,new" }}
    """
    if not args or ',' not in args:
        return value
    
    try:
        old, new = args.split(',', 1)
        return str(value).replace(old, new)
    except (ValueError, AttributeError):
        return value

@register.filter
def underscore_to_space(value):
    """
    Replace underscores with spaces and title case the result.
    Usage: {{ value|underscore_to_space }}
    """
    if not value:
        return value
    return str(value).replace('_', ' ').title()
