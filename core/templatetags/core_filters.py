from django import template
import hashlib
import random

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

@register.filter
def mask_username(value):
    """
    Mask a username for privacy.
    Shows first character and last character with asterisks in between.
    Usage: {{ username|mask_username }}
    Example: "jgarcia28" → "j******8"
    """
    if not value:
        return "Anonymous"
    
    value = str(value)
    length = len(value)
    
    if length <= 2:
        return "*" * length
    elif length <= 4:
        return value[0] + "*" * (length - 1)
    else:
        return value[0] + "*" * (length - 2) + value[-1]

@register.filter
def anonymous_id(obj):
    """
    Generate a unique anonymous ID for a post or comment.
    The ID is based on the object's ID and creation time, making it unique per post/comment.
    Usage: {{ post|anonymous_id }} or {{ comment|anonymous_id }}
    Returns: "Anonymous#1234"
    """
    if not obj:
        return "Anonymous"
    
    try:
        # Create a unique hash based on object ID and created_at timestamp
        obj_id = getattr(obj, 'id', 0)
        created_at = getattr(obj, 'created_at', None)
        
        if created_at:
            unique_string = f"{obj_id}-{created_at.timestamp()}"
        else:
            unique_string = f"{obj_id}-{random.randint(1000, 9999)}"
        
        # Generate a 4-digit number from the hash
        hash_obj = hashlib.md5(unique_string.encode())
        hash_int = int(hash_obj.hexdigest()[:8], 16)
        anon_number = (hash_int % 9000) + 1000  # 4-digit number between 1000-9999
        
        return f"Anonymous#{anon_number}"
    except Exception:
        return f"Anonymous#{random.randint(1000, 9999)}"

@register.simple_tag
def get_anonymous_id(obj):
    """
    Template tag version for more flexibility.
    Usage: {% get_anonymous_id post as anon_id %}
    """
    return anonymous_id(obj)
