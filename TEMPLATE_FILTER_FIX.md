# Template Filter Fix - Organization Dashboard

## Issue Fixed
**TemplateSyntaxError**: Invalid filter 'replace' in organization dashboard template.

## Root Cause
The template was using a non-existent `replace` filter in Django templates:
```django
{{ case.severity_level|title|replace:"_":" " }}
```

Django doesn't have a built-in `replace` template filter, which caused the TemplateSyntaxError.

## Solutions Implemented

### 1. **Primary Fix - Use Model's Display Method**
Replaced the problematic filter with the model's built-in display method:
```django
# Before (Error)
{{ case.severity_level|title|replace:"_":" " }}

# After (Fixed)
{{ case.get_severity_level_display }}
```

This uses Django's automatic `get_FIELD_display()` method for choice fields, which is the proper way to display human-readable choice values.

### 2. **Custom Template Filter Created**
Created custom template filters in `core/templatetags/core_filters.py`:

```python
@register.filter
def replace(value, args):
    """Replace all occurrences of a substring in a string."""
    if not args or ',' not in args:
        return value
    try:
        old, new = args.split(',', 1)
        return str(value).replace(old, new)
    except (ValueError, AttributeError):
        return value

@register.filter
def underscore_to_space(value):
    """Replace underscores with spaces and title case the result."""
    if not value:
        return value
    return str(value).replace('_', ' ').title()
```

Usage:
```django
{% load core_filters %}
{{ value|replace:"_"," " }}
{{ value|underscore_to_space }}
```

### 3. **Additional Template Fixes**
- **Fixed Score Display**: Changed `{{ case.total_score }}` to `{{ case.user_assessment.total_score|default:"N/A" }}` to properly access the score from the related UserAssessment model
- **Added Score Range**: Added display of score range when available
- **Fixed Analytics Template**: Applied the custom filter to organization analytics template

## Files Modified

### Templates Fixed:
1. `templates/core/organization_dashboard.html`
   - Fixed severity level display
   - Fixed score access from correct model
   - Added score range display

2. `templates/core/organization_analytics.html`
   - Added custom filter loading
   - Fixed severity level display

### New Files Created:
1. `core/templatetags/__init__.py` - Package initialization
2. `core/templatetags/core_filters.py` - Custom template filters

## Technical Details

### Model Relationships:
- `AssessmentResult` has `severity_level` with `SEVERITY_LEVELS` choices
- `AssessmentResult.user_assessment` → `UserAssessment` has `total_score`
- Using `get_severity_level_display()` provides proper display names

### Choice Field Values:
```python
SEVERITY_LEVELS = [
    ('minimal', 'Minimal'),
    ('mild', 'Mild'),
    ('moderate', 'Moderate'),
    ('moderately_severe', 'Moderately Severe'),
    ('severe', 'Severe')
]
```

The `get_severity_level_display()` method automatically returns the human-readable label (e.g., "Moderately Severe" instead of "moderately_severe").

## Benefits of the Fix

1. **Proper Django Convention**: Uses built-in model methods instead of custom filters
2. **Better Performance**: No string manipulation needed in templates
3. **Maintainability**: Changes to choice labels automatically reflect in templates
4. **Error Prevention**: Eliminates template syntax errors
5. **Future-Proof**: Custom filters available for other use cases

## Testing
- ✅ Django configuration check passes
- ✅ No template syntax errors
- ✅ Organization dashboard loads properly
- ✅ Severity levels display correctly
- ✅ Score information shows properly

## Usage Notes
- The custom `replace` filter is available for future use if needed
- The `underscore_to_space` filter provides a convenient way to format underscored values
- Always prefer Django's built-in model methods when available (like `get_FIELD_display()`)

This fix ensures the organization dashboard works properly while providing reusable custom filters for future template needs.
