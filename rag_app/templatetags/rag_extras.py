from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter and return a list"""
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter) if item.strip()]

@register.filter
def strip(value):
    """Strip whitespace from a string"""
    if value:
        return value.strip()
    return value

@register.filter  
def percentage(value, total):
    """Calculate percentage"""
    if not total or total == 0:
        return 0
    return round((value / total) * 100, 1)
