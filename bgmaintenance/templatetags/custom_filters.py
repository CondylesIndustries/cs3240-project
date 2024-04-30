# In your app's templatetags folder, create a new Python file, e.g., custom_filters.py

from django import template

register = template.Library()

@register.filter
def decode_bytes(content):
    # Ensure content is bytes before decoding
    if isinstance(content, bytes):
        return content.decode('utf-8')
    return content
