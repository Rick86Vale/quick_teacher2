# academico/templatetags/markdown_extras.py

from django import template
import markdown
from django.utils.safestring import mark_safe
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name # Adicione esta importação

register = template.Library()

@register.filter(name='markdown')
def markdown_filter(value):
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'nl2br'], 
                           extension_configs={
                               'codehilite': {
                                   'guess_lang': True, 
                                   'linenums': True  # <-- Ativa a numeração de linhas
                               }
                           })
    return mark_safe(md.convert(value))

@register.simple_tag
def pygments_css():
    # Retornamos vazio para que o Pygments não injete CSS conflituoso
    return ""