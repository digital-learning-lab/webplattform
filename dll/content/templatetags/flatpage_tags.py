# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def flatpage_breadcrumbs(context):
    flatpage_title = ''
    try:
        flatpage_title = context['flatpage'].title
    except KeyError:
        pass
    return [
        {
            'title': 'Home',
            'url': '/'
        },
        {
            'title': flatpage_title
        }
    ]
