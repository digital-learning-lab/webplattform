from django.urls import path
from dll.cms import chooser


urlpatterns = [
    path(
        "choose-content-link/", chooser.content_link, name="wagtailadmin_choose_content"
    ),
]
