from django import template

from content.utils import is_favored

register = template.Library()


@register.inclusion_tag("dll/includes/favorite.html", takes_context=True)
def favored_snippet(context, content):
    request = context.get("request")
    favored = False
    if request:
        favored = is_favored(request.user, content)
    return {"favored": favored}
