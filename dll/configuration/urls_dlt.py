from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from dll import shared_session
from dll.content.views import (
    ToolDetailView,
    ToolDataFilterView,
    ToolFilterView,
    ToolDetailPreviewView,
    ToolsFeed,
    search_view,
    TrendDetailView,
    TeachingModuleDetailView,
)

router = DefaultRouter()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tools/rss", ToolsFeed(), name="tools-feed"),
    path("trends/<slug:slug>", TrendDetailView.as_view(), name="trend-detail"),
    path(
        "unterrichtsbausteine/<slug:slug>",
        TeachingModuleDetailView.as_view(),
        name="teaching-module-detail",
    ),
    path("tools/<slug:slug>", ToolDetailView.as_view(), name="tool-detail"),
    path(
        "tools/<slug:slug>/vorschau",
        ToolDetailPreviewView.as_view(),
        name="tool-detail-preview",
    ),
    path("tools", ToolFilterView.as_view(), name="tools-filter"),
    path("api/", include(router.urls)),
    path("api/tools", ToolDataFilterView.as_view(), name="tools-data-filter"),
    path("suche", search_view, name="search"),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("shared-session/", shared_session.urls),
    path("", include("dll.communication.urls", namespace="communication")),
    path("", include("dll.user.urls", namespace="user")),
    path("", include(wagtail_urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
