from django import template

from dll.content.models import Favorite

register = template.Library()


@register.inclusion_tag("dll/includes/favorite.html", takes_context=True)
def favored_snippet(context, content):
    request = context.get("request")
    favored = False
    if request and request.user.is_authenticated:
        favored = Favorite.objects.filter(
            user=request.user, content=content.get_draft()
        ).exists()
    return {"favored": favored}
