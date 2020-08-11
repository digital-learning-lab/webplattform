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
from django.contrib.flatpages import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from dll.content.views import (
    HomePageView,
    ImprintView,
    DataPrivacyView,
    StructureView,
    UsageView,
    DevelopmentView,
    ToolDetailView,
    TrendDetailView,
    TeachingModuleDetailView,
    CompetenceFilterView,
    TeachingModuleFilterView,
    TeachingModuleDataFilterView,
    ToolDataFilterView,
    TrendFilterView,
    ToolFilterView,
    TrendDataFilterView,
    PublishedContentViewSet,
    DraftsContentViewSet,
    AuthorSearchView,
    SchoolTypesSearchView,
    StateSearchView,
    CompetencesSearchView,
    SubCompetencesSearchView,
    SubjectSearchView,
    FileUploadView,
    ToolApplicationSearchView,
    OperatingSystemSearchView,
    ReviewViewSet,
    ToolDetailPreviewView,
    TeachingModuleDetailPreviewView,
    TrendDetailPreviewView,
    SubmitContentView,
    ApproveContentView,
    DeclineContentView,
    search_view,
    HelpTextFieldChoices,
    ImageUploadView,
    DeleteContentFileView,
    AssignReviewerView,
    UnassignReviewerView,
    ReviewerSearchView,
    TeachingModulesFeed,
    ToolsFeed,
    TrendsFeed,
)
from dll.user.views import (
    MyContentView,
    CreateEditTeachingModuleView,
    CreateEditToolView,
    CreateEditTrendView,
    UserContentView,
    MyReviewsView,
    ReviewTeachingModuleView,
    ReviewToolView,
    ReviewTrendView,
    PendingReviewContentView,
    UserInvitationView,
)

router = DefaultRouter()
router.register(r"inhalte", PublishedContentViewSet, basename="public-content")
router.register(r"inhalt-bearbeiten", DraftsContentViewSet, basename="draft-content")
router.register(r"review", ReviewViewSet, basename="review")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomePageView.as_view(), name="home"),
    path("impressum", ImprintView.as_view(), name="imprint"),
    path("datenschutz", DataPrivacyView.as_view(), name="data-privacy"),
    path("struktur", StructureView.as_view(), name="structure"),
    path("nutzung", UsageView.as_view(), name="usage"),
    path("entwicklung", DevelopmentView.as_view(), name="development"),
    path("faq", views.flatpage, {"url": "/faq/"}, name="faq"),
    path("terms", views.flatpage, {"url": "/terms/"}, name="terms"),
    path("tools/rss", ToolsFeed(), name="tools-feed"),
    path(
        "unterrichtsbausteine/rss", TeachingModulesFeed(), name="teaching-modules-feed"
    ),
    path("trends/rss", TrendsFeed(), name="trends-feed"),
    path("tools/<slug:slug>", ToolDetailView.as_view(), name="tool-detail"),
    path(
        "tools/<slug:slug>/vorschau",
        ToolDetailPreviewView.as_view(),
        name="tool-detail-preview",
    ),
    path("trends/<slug:slug>", TrendDetailView.as_view(), name="trend-detail"),
    path(
        "trends/<slug:slug>/vorschau",
        TrendDetailPreviewView.as_view(),
        name="trend-detail-preview",
    ),
    path(
        "unterrichtsbausteine/<slug:slug>",
        TeachingModuleDetailView.as_view(),
        name="teaching-module-detail",
    ),
    path(
        "unterrichtsbausteine/<slug:slug>/vorschau",
        TeachingModuleDetailPreviewView.as_view(),
        name="teaching-module-detail-preview",
    ),
    path(
        "kompetenz/<slug:slug>",
        CompetenceFilterView.as_view(),
        name="competence-filter",
    ),
    path(
        "unterrichtsbausteine",
        TeachingModuleFilterView.as_view(),
        name="teaching-modules-filter",
    ),
    path("tools", ToolFilterView.as_view(), name="tools-filter"),
    path("trends", TrendFilterView.as_view(), name="trends-filter"),
    path("meine-inhalte", MyContentView.as_view(), name="user-content-overview"),
    path("review-inhalte", MyReviewsView.as_view(), name="user-content-review"),
    path(
        "meine-inhalte/unterrichtsbausteine/",
        CreateEditTeachingModuleView.as_view(),
        name="add-teaching-module",
    ),
    path(
        "meine-inhalte/unterrichtsbausteine/<slug:slug>",
        CreateEditTeachingModuleView.as_view(),
        name="edit-teaching-module",
    ),
    path(
        "review-inhalte/unterrichtsbausteine/<slug:slug>/review",
        ReviewTeachingModuleView.as_view(),
        name="review-teaching-module",
    ),
    path(
        "review-inhalte/tools/<slug:slug>/review",
        ReviewToolView.as_view(),
        name="review-tool",
    ),
    path(
        "review-inhalte/trends/<slug:slug>/review",
        ReviewTrendView.as_view(),
        name="review-trend",
    ),
    path("meine-inhalte/tools/", CreateEditToolView.as_view(), name="add-tool"),
    path(
        "meine-inhalte/tools/<slug:slug>",
        CreateEditToolView.as_view(),
        name="edit-tool",
    ),
    path("meine-inhalte/trends/", CreateEditTrendView.as_view(), name="add-trend"),
    path(
        "meine-inhalte/trends/<slug:slug>",
        CreateEditTrendView.as_view(),
        name="edit-trend",
    ),
    path("", include("dll.user.urls", namespace="user")),
    path("", include("dll.communication.urls", namespace="communication")),
    # path('', include('django.contrib.flatpages.urls')),
    path("api/", include(router.urls)),
    path(
        "api/unterrichtsbausteine",
        TeachingModuleDataFilterView.as_view(),
        name="teaching-modules-data-filter",
    ),
    path("api/tools", ToolDataFilterView.as_view(), name="tools-data-filter"),
    path("api/trends", TrendDataFilterView.as_view(), name="trends-data-filter"),
    path("api/authors", AuthorSearchView.as_view(), name="author-search"),
    path("api/reviewers", ReviewerSearchView.as_view(), name="reviewer-search"),
    path("api/schoolTypes", SchoolTypesSearchView.as_view(), name="school-type-search"),
    path("api/states", StateSearchView.as_view(), name="state-search"),
    path("api/subjects", SubjectSearchView.as_view(), name="subject-search"),
    path("api/competences", CompetencesSearchView.as_view(), name="competence-search"),
    path(
        "api/sub-competences",
        SubCompetencesSearchView.as_view(),
        name="sub-competence-search",
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
    path("api/meine-inhalte", UserContentView.as_view(), name="user-contents"),
    path(
        "api/meine-einladungen", UserInvitationView.as_view(), name="user-invitations"
    ),
    path(
        "api/review-inhalte", PendingReviewContentView.as_view(), name="content-pending"
    ),
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
        "select2/admin_help_fields",
        HelpTextFieldChoices.as_view(),
        name="admin-help-text-choices",
    ),
    path("suche", search_view, name="search"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
