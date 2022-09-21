"""dll URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from dll.content.views import (
    ToolDetailView,
    ToolDataFilterView,
    ToolFilterView,
    ToolApplicationSearchView,
    ToolDetailPreviewView,
    ToolsFeed,
)
from dll.survey.views import SurveyDetailView, TriggerListApiView
from dll.user.views import (
    MyContentView,
    CreateEditToolView,
    UserContentView,
    MyReviewsView,
    PendingReviewContentView,
    UserInvitationView,
    UserFavoriteView,
)

router = DefaultRouter()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tools/rss", ToolsFeed(), name="tools-feed"),
    path("tools/<slug:slug>", ToolDetailView.as_view(), name="tool-detail"),
    path(
        "tools/<slug:slug>/vorschau",
        ToolDetailPreviewView.as_view(),
        name="tool-detail-preview",
    ),
    path("tools", ToolFilterView.as_view(), name="tools-filter"),
    path("api/", include(router.urls)),
    path("api/tools", ToolDataFilterView.as_view(), name="tools-data-filter"),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("", include(wagtail_urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
