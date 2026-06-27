# academico/templatetags/markdown_extras.py
from django import template
import markdown
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='markdown')
def markdown_filter(value):
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'nl2br'])
    return mark_safe(md.convert(value))