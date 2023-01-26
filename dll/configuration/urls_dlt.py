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
    HelpTextFieldChoices,
    SubjectSearchView,
    TestimonialReviewViewSet,
    TestimonialReviewsOverview,
    TestimonialUpdateView,
    TestimonialOverview,
    ToolDetailView,
    ToolDataFilterView,
    ToolFilterView,
    ToolDetailPreviewView,
    ToolsFeed,
    search_view,
    TrendDetailView,
    TeachingModuleDetailView,
    TestimonialView,
    FileUploadView,
    DeleteContentFileView,
    SubmitContentView,
    ImageUploadView,
    ApproveContentView,
    DeclineContentView,
    AssignReviewerView,
    UnassignReviewerView,
    PublishedContentViewSet,
    DraftsContentViewSet,
    ReviewViewSet,
    ToolFunctionSearchView,
    ToolPotentialSearchView,
    ToolApplicationSearchView,
    OperatingSystemSearchView,
)
from dll.user.views import (
    MyContentView,
    CreateEditToolView,
    UserContentView,
    UserToolBoxView,
)

router = DefaultRouter()
router.register(r"inhalte", PublishedContentViewSet, basename="public-content")
router.register(r"inhalt-bearbeiten", DraftsContentViewSet, basename="draft-content")
router.register(r"review", ReviewViewSet, basename="review"),
router.register(
    r"testimonial-review", TestimonialReviewViewSet, basename="testimonial-review"
),

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
    path(
        "review-erfahrungsberichte",
        TestimonialReviewsOverview.as_view(),
        name="content-testimonial-review",
    ),
    path(
        "api/testimonial/<int:pk>/",
        TestimonialUpdateView.as_view(),
        name="testimonial-update",
    ),
    path(
        "meine-erfahrungsberichte",
        TestimonialOverview.as_view(),
        name="my-content-testimonials",
    ),
    path("meine-inhalte", MyContentView.as_view(), name="user-content-overview"),
    path("meine-toolbox", UserToolBoxView.as_view(), name="user-toolbox-overview"),
    path("meine-inhalte/tools/", CreateEditToolView.as_view(), name="add-tool"),
    path(
        "meine-inhalte/tools/<slug:slug>",
        CreateEditToolView.as_view(),
        name="edit-tool",
    ),
    path("tools", ToolFilterView.as_view(), name="tools-filter"),
    path(
        "api/inhalt-bearbeiten/<slug:slug>/vorschau-bild",
        ImageUploadView.as_view(),
        name="add-preview-image",
    ),
    path(
        "api/inhalt-bearbeiten/<slug:slug>/file-upload",
        FileUploadView.as_view(),
        name="add-content-file",
    ),
    path(
        "api/inhalt-bearbeiten/<slug:slug>/file-remove/<int:pk>",
        DeleteContentFileView.as_view(),
        name="remove-content-file",
    ),
    path(
        "api/inhalt-einreichen/<slug:slug>",
        SubmitContentView.as_view(),
        name="submit-content",
    ),
    path(
        "api/review/<slug:slug>/approve",
        ApproveContentView.as_view(),
        name="approve-content",
    ),
    path(
        "api/review/<slug:slug>/decline",
        DeclineContentView.as_view(),
        name="decline-content",
    ),
    path(
        "api/review/<slug:slug>/assign",
        AssignReviewerView.as_view(),
        name="assign-reviewer",
    ),
    path(
        "api/review/<slug:slug>/unassign",
        UnassignReviewerView.as_view(),
        name="unassign-reviewer",
    ),
    path(
        "api/toolFunctions",
        ToolFunctionSearchView.as_view(),
        name="tool-function-search",
    ),
    path(
        "api/potentials",
        ToolPotentialSearchView.as_view(),
        name="tool-potential-search",
    ),
    path(
        "api/applications",
        ToolApplicationSearchView.as_view(),
        name="application-search",
    ),
    path(
        "api/operatingSystems",
        OperatingSystemSearchView.as_view(),
        name="operating-system-search",
    ),
    path("api/subjects", SubjectSearchView.as_view(), name="subject-search"),
    path("api/meine-inhalte", UserContentView.as_view(), name="user-contents"),
    path("api/", include(router.urls)),
    path("api/tools", ToolDataFilterView.as_view(), name="tools-data-filter"),
    path("suche", search_view, name="search"),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("shared-session/", shared_session.urls),
    path("testimonial", TestimonialView.as_view(), name="testimonial"),
    path(
        "select2/admin_help_fields",
        HelpTextFieldChoices.as_view(),
        name="admin-help-text-choices",
    ),
    path("", include("dll.communication.urls", namespace="communication")),
    path("", include("dll.user.urls", namespace="user")),
    path("", include(wagtail_urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
