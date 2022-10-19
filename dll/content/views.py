import json
import random

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse_lazy, resolve
from django.views.generic import TemplateView, DetailView
from django.views.generic.base import ContextMixin
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from django_select2.views import AutoResponseView
from filer.models import Image, File
from haystack.backends import SQ
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from psycopg2._range import NumericRange
from rest_framework import viewsets, filters, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, GenericAPIView, DestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import (
    DjangoObjectPermissions,
    BasePermission,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rules.contrib.rest_framework import AutoPermissionViewSetMixin
from django.contrib.sites import models

from dll.content.filters import SolrTagFilter, SortingFilter
from dll.content.models import (
    Content,
    TeachingModule,
    Trend,
    Tool,
    Competence,
    Subject,
    SubCompetence,
    SchoolType,
    Review,
    OperatingSystem,
    ToolApplication,
    HelpText,
    ContentFile,
    Potential,
)
from dll.content.serializers import (
    AuthorSerializer,
    CompetenceSerializer,
    ToolFunctionSerializer,
    SubCompetenceSerializer,
    SchoolTypeSerializer,
    ReviewSerializer,
    SubjectSerializer,
    FileSerializer,
    ImageFileSerializer,
    ContentPolymorphicSubmissionSerializer,
)
from dll.general.utils import GERMAN_STATES
from dll.user.models import DllUser
from .filters import (
    ToolStatusFilter,
    ToolApplicationFilter,
    ToolOperationSystemFilter,
    ToolDataPrivacyFilter,
    TeachingModuleSubjectFilter,
    TeachingModuleStateFilter,
    TeachingModuleSchoolTypeFilter,
    ToolFunctionFilter,
)
from .models import ToolFunction, Favorite
from .more_like_this import more_like_this
from .serializers import (
    ContentListSerializer,
    ContentPolymorphicSerializer,
    FavoriteSerializer,
)
from .utils import get_random_content


class ReviewerPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_superuser or user.is_reviewer


class ReviewerMixin(GenericAPIView):
    def get_permissions(self):
        permission = super(ReviewerMixin, self).get_permissions()
        permission.append(ReviewerPermission())
        return permission


class BreadcrumbMixin(ContextMixin):
    breadcrumb_title = ""
    breadcrumb_url = ""

    def get_context_data(self, **kwargs):
        ctx = super(BreadcrumbMixin, self).get_context_data(**kwargs)
        ctx["breadcrumbs"] = self.get_breadcrumbs()
        return ctx

    def get_breadcrumbs(self):
        return [
            {"title": "Home", "url": "/"},
            {"title": self.breadcrumb_title, "url": self.breadcrumb_url},
        ]


class ContentDetailBase(DetailView):
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            # The length of the slug field has been adapted from 50 to 200.
            # To make sure old slugs, which have been truncated in the past, are still available
            # this redirect logic had to be implemented.
            queryset = self.get_queryset()
            pk = self.kwargs.get(self.pk_url_kwarg)
            slug = self.kwargs.get(self.slug_url_kwarg)
            # Only check for slugs with the length of 50 (which are likely to be old truncated slugs).
            if (
                slug is not None
                and (pk is None or self.query_pk_and_slug)
                and len(slug) in [49, 50]
            ):
                slug_field = self.get_slug_field()
                queryset = queryset.filter(**{slug_field + "__startswith": slug})
                try:
                    obj = queryset.get()
                except MultipleObjectsReturned:
                    # This is very unlikely to happen. However, in case there are multiple
                    # Content objects which start with the same 50 letters we return the first found.
                    obj = queryset.first()
                except ObjectDoesNotExist:
                    raise Http404
                return redirect(obj.get_absolute_url())
            raise Http404
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        ctx = super(ContentDetailBase, self).get_context_data(**kwargs)
        ctx["competences"] = Competence.objects.all()
        ctx["functions"] = ToolFunction.objects.all()
        ctx["potentials"] = Potential.objects.all()
        ctx["recommended_content"] = more_like_this(self.object)
        if self.request.user.is_authenticated:
            ctx["favored"] = Favorite.objects.filter(
                user=self.request.user, content=self.get_object().get_draft()
            ).exists()
        return ctx


class ContentDetailView(ContentDetailBase):
    def get_queryset(self):
        qs = super(ContentDetailView, self).get_queryset()
        return qs.published()

    def get_context_data(self, **kwargs):
        ctx = super(ContentDetailView, self).get_context_data(**kwargs)
        ctx["meta"] = self.get_object().as_meta(self.request)
        return ctx


class ContentPreviewView(ContentDetailBase):
    def get_context_data(self, **kwargs):
        ctx = super(ContentPreviewView, self).get_context_data(**kwargs)
        ctx["preview"] = True
        return ctx

    def get_object(self, queryset=None):
        obj = super(ContentPreviewView, self).get_object(queryset=queryset)
        user = self.request.user
        if not user.has_perm("content.view_content", obj):
            raise Http404
        return obj

    def get_queryset(self):
        qs = super(ContentPreviewView, self).get_queryset()
        return qs.drafts()


class ToolDetailView(ContentDetailView):
    model = Tool
    template_name = "dll/content/tool_detail.html"

    def get(self, *args, **kwargs):
        if settings.SITE_ID == 2:
            return super().get(self.request)
        else:
            site = models.Site.objects.get(pk=2)
            domain = site.domain
            return redirect(f"//{domain}{self.request.path}")


class TrendDetailView(ContentDetailView):
    model = Trend
    template_name = "dll/content/trend_detail.html"


class TeachingModuleDetailView(ContentDetailView):
    model = TeachingModule
    template_name = "dll/content/teaching_module_detail.html"


class ToolDetailPreviewView(ContentPreviewView):
    model = Tool
    template_name = "dll/content/tool_detail.html"


class TrendDetailPreviewView(ContentPreviewView):
    model = Trend
    template_name = "dll/content/trend_detail.html"


class TeachingModuleDetailPreviewView(ContentPreviewView):
    model = TeachingModule
    template_name = "dll/content/teaching_module_detail.html"


class PublishedContentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContentPolymorphicSerializer
    queryset = Content.objects.published()
    filter_backends = [DjangoFilterBackend, SolrTagFilter, SortingFilter]
    permission_classes = []

    def get_queryset(self):
        competence = self.request.GET.get("competence", "")
        teaching_modules = self.request.GET.get("teachingModules", "true")
        trends = self.request.GET.get("trends", "true")
        tools = self.request.GET.get("tools", "true")

        qs = super(PublishedContentViewSet, self).get_queryset()

        if competence:
            qs = qs.filter(competences__slug=competence)
        if teaching_modules != "true":
            qs = qs.not_instance_of(TeachingModule)
        if trends != "true":
            qs = qs.not_instance_of(Trend)
        if tools != "true":
            qs = qs.not_instance_of(Tool)

        return qs

    def get_serializer_class(self):
        name = resolve(self.request.path_info).url_name
        if name == "public-content-list" and self.request.method == "GET":
            return ContentListSerializer
        else:
            return super(PublishedContentViewSet, self).get_serializer_class()


class DraftsContentViewSet(
    AutoPermissionViewSetMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Authors can create, update and retrieve content, reviewers can only retrieve"""

    serializer_class = ContentPolymorphicSerializer
    queryset = Content.objects.drafts()
    lookup_field = "slug"
    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "favor": None,
        "unfavor": None,
    }

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def favor(self, request, slug):
        user = self.request.user
        content = self.get_object()
        result = content.favor(user)
        if result:
            return HttpResponse()
        return JsonResponse(
            status=400, data={"error": _("Inhalt bereits favorisiert.")}
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unfavor(self, request, slug):
        user = self.request.user
        content = self.get_object()
        result = content.unfavor(user)
        if result:
            return HttpResponse()
        return JsonResponse(
            status=400, data={"error": _("Favorit konnte nicht gefunden werden.")}
        )


class SubmitContentView(GenericAPIView):
    queryset = Content.objects.drafts()
    lookup_field = "slug"

    def post(self, *args, **kwargs):
        obj = self.get_object()
        user = self.request.user
        if not self.is_valid(obj):
            return JsonResponse(
                status=400,
                data={
                    "message": "Einreichung nicht erfolgreich. Bitte prüfen Sie Ihre Angaben."
                },
            )
        if user.has_perm("content.change_content", obj):
            obj.submit_for_review(user)
            return HttpResponse(status=200)
        return HttpResponse(status=403)

    def is_valid(self, obj: Content):
        """Validate with the 'SubmissionSerializer'.

        From the models perspective there is not much validation - just a name is required.
        As soon as the content is submitted we need to validate whether all required fields are actually
        filled out. If they continue, if not raise an error.
        """
        instance = obj.get_real_instance()
        instance.validate_required = True
        serializer = ContentPolymorphicSerializer(instance)
        data_serializer = ContentPolymorphicSubmissionSerializer(data=serializer.data)
        return data_serializer.is_valid()


class ReviewViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """Authors have only view permission, reviewers have view and edit permission"""

    serializer_class = ReviewSerializer
    queryset = Review.objects.filter(content__publisher_is_draft=True, is_active=True)
    permission_classes = [DjangoObjectPermissions]
    lookup_field = "content__slug"
    lookup_url_kwarg = "slug"

    def perform_update(self, serializer):
        serializer.save()


class BaseActionReviewView(GenericAPIView):
    queryset = Review.objects.filter(content__publisher_is_draft=True, is_active=True)
    lookup_field = "content__slug"
    lookup_url_kwarg = "slug"
    serializer_class = ReviewSerializer


class ApproveContentView(BaseActionReviewView):
    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.accept(self.request.user)
        return JsonResponse(self.get_serializer(instance=obj).data)


class DeclineContentView(BaseActionReviewView):
    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.decline(self.request.user)
        return JsonResponse(self.get_serializer(instance=obj).data)


class AssignReviewerView(ReviewerMixin, GenericAPIView):
    queryset = Content.objects.drafts()
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    serializer_class = ContentListSerializer

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        to_be_assigned_user_id = request.data.get("user")
        if to_be_assigned_user_id:
            to_be_assigned_user = get_object_or_404(DllUser, pk=to_be_assigned_user_id)
            obj.assign_reviewer(
                by_user=request.user, to_be_assigned_user=to_be_assigned_user
            )
        else:
            obj.assign_reviewer(by_user=request.user, to_be_assigned_user=request.user)
        return JsonResponse({}, status=200)


class UnassignReviewerView(ReviewerMixin, GenericAPIView):
    queryset = Content.objects.drafts()
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    serializer_class = ContentListSerializer

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        to_be_unassigned_user = self.request.POST.get("user")
        if to_be_unassigned_user:
            obj.unassign_reviewer(
                by_user=request.user, to_be_unassigned_user=to_be_unassigned_user
            )
        else:
            obj.unassign_reviewer(
                by_user=request.user, to_be_unassigned_user=request.user
            )
        return JsonResponse({}, status=200)


class CompetenceFilterView(DetailView):
    model = Competence
    template_name = "dll/filter/competence.html"
    query_pk_and_slug = True


class ContentDataFilterView(ListAPIView):
    queryset = Content
    serializer_class = ContentListSerializer
    filter_backends = [DjangoFilterBackend, SolrTagFilter, SortingFilter]
    model = None
    permission_classes = []

    def get_queryset(self):
        qs = (
            super(ContentDataFilterView, self)
            .get_queryset()
            .objects.instance_of(self.model)
        )
        qs = qs.published()

        competences = self.request.GET.getlist("competences[]", [])
        if competences:
            qs = qs.filter(competences__pk__in=competences)

        return qs


class BaseFilterView(TemplateView):
    rss_feed_url = None

    def get_context_data(self, **kwargs):
        ctx = super(BaseFilterView, self).get_context_data(**kwargs)
        if self.rss_feed_url:
            site = get_current_site(self.request)
            ctx[
                "rss_feed_url"
            ] = f"{self.request.scheme}://{site.domain}{self.rss_feed_url}"
        return ctx


class TeachingModuleFilterView(BaseFilterView):
    template_name = "dll/filter/teaching_modules.html"
    rss_feed_url = reverse_lazy("teaching-modules-feed")

    def get_context_data(self, **kwargs):
        ctx = super(TeachingModuleFilterView, self).get_context_data(**kwargs)
        subject_filter = [
            {"value": subject.pk, "name": subject.name}
            for subject in Subject.objects.all()
        ]
        school_types_filter = [
            {"value": school_type.pk, "name": school_type.name}
            for school_type in SchoolType.objects.all()
        ]
        school_types_filter.insert(0, {"value": "", "name": "------"})
        ctx["subject_filter"] = json.dumps(subject_filter)
        ctx["school_types_filter"] = json.dumps(school_types_filter)
        return ctx


class TeachingModuleDataFilterView(ContentDataFilterView):
    model = TeachingModule
    filter_backends = [
        TeachingModuleSubjectFilter,
        TeachingModuleSchoolTypeFilter,
        TeachingModuleStateFilter,
    ] + ContentDataFilterView.filter_backends

    def get_queryset(self):
        qs = super(TeachingModuleDataFilterView, self).get_queryset()

        class_from = self.request.GET.get("schoolClassFrom", [])
        class_to = self.request.GET.get("schoolClassTo", [])
        hybrid = self.request.GET.get("hybrid") == "true"

        try:
            if class_from:
                class_from = int(class_from)
        except ValueError:
            class_from = None
        try:
            if class_to:
                class_to = int(class_to)
        except ValueError:
            class_to = None

        if class_from:
            qs = qs.filter(
                TeachingModule___school_class__overlap=NumericRange(
                    int(class_from), None
                )
            )

        if class_to:
            qs = qs.filter(
                TeachingModule___school_class__overlap=NumericRange(None, int(class_to))
            )

        if hybrid:
            qs = qs.filter(TeachingModule___hybrid=hybrid)

        return qs.distinct()


class ToolFilterView(BaseFilterView):
    template_name = "dll/filter/tools.html"
    rss_feed_url = reverse_lazy("tools-feed")

    def get_context_data(self, **kwargs):
        ctx = super(ToolFilterView, self).get_context_data(**kwargs)
        ctx["functions_filter"] = [
            {"id": function.id, "title": function.title}
            for function in ToolFunction.objects.all()
        ]
        return ctx


class ToolDataFilterView(ContentDataFilterView):
    model = Tool
    filter_backends = [
        ToolStatusFilter,
        ToolApplicationFilter,
        ToolDataPrivacyFilter,
        ToolOperationSystemFilter,
        ToolFunctionFilter,
    ] + ContentDataFilterView.filter_backends


class TrendFilterView(BaseFilterView):
    template_name = "dll/filter/trends.html"
    rss_feed_url = reverse_lazy("trends-feed")


class TrendDataFilterView(ContentDataFilterView):
    model = Trend

    def get_queryset(self):
        qs = super(TrendDataFilterView, self).get_queryset()

        language = self.request.GET.get("language", None)
        trend_types = self.request.GET.getlist("trendTypes[]", [])

        if language:
            qs = qs.filter(Trend___language=language)

        if trend_types:
            qs = qs.filter(Trend___category__in=trend_types)

        return qs.distinct()


class DropdownSmallPagination(PageNumberPagination):
    page_size = 50


class DropdownLargePagination(PageNumberPagination):
    page_size = 1000


class AuthorSearchView(ListAPIView):
    queryset = DllUser.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["username", "first_name", "last_name"]
    pagination_class = DropdownSmallPagination

    def get_queryset(self):
        qs = super(AuthorSearchView, self).get_queryset()
        return qs.exclude(pk=self.request.user.pk)


class ReviewerSearchView(ReviewerMixin, ListAPIView):
    queryset = DllUser.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["username", "first_name", "last_name"]

    def get_queryset(self):
        qs = super(ReviewerSearchView, self).get_queryset()
        return qs.filter(
            Q(is_superuser=True) | Q(groups__name__in=["BSB-Reviewer", "TUHH-Reviewer"])
        )


class CompetencesSearchView(ListAPIView):
    queryset = Competence.objects.all()
    serializer_class = CompetenceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]


class ToolFunctionSearchView(ListAPIView):
    queryset = ToolFunction.objects.all()
    serializer_class = ToolFunctionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title"]


class SubCompetencesSearchView(ListAPIView):
    queryset = SubCompetence.objects.all()
    serializer_class = SubCompetenceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = DropdownLargePagination

    def get_queryset(self):
        qs = super(SubCompetencesSearchView, self).get_queryset()
        competences = self.request.GET.getlist("competences[]", [])

        if competences:
            competences_ids = [
                json.loads(competence)["pk"] for competence in competences
            ]
            return qs.filter(competence__pk__in=competences_ids).order_by("ordering")
        return qs.none()


class SchoolTypesSearchView(ListAPIView):
    queryset = SchoolType.objects.all()
    serializer_class = SchoolTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = DropdownLargePagination


class SubjectSearchView(ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = DropdownLargePagination


class OperatingSystemSearchView(ListAPIView):
    queryset = OperatingSystem.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = DropdownLargePagination


class ToolApplicationSearchView(ListAPIView):
    queryset = ToolApplication.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = DropdownLargePagination


class StateSearchView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {
                "results": [
                    {"name": state[1], "value": state[0]} for state in GERMAN_STATES
                ]
            }
        )


class FileUploadBaseView(APIView):
    parser_class = (FileUploadParser,)
    serializer_klaas = FileSerializer

    def put(self, request, *args, **kwargs):
        slug = kwargs.get("slug", None)
        if not slug:
            raise Http404

        obj = Content.objects.drafts().get(slug=slug)
        file_serializer = self.serializer_klaas(data=request.data)

        return obj, file_serializer


class ImageUploadView(FileUploadBaseView):
    serializer_klaas = ImageFileSerializer

    def put(self, request, *args, **kwargs):
        obj, file_serializer = super(ImageUploadView, self).put(
            request, *args, **kwargs
        )
        if file_serializer.is_valid():
            image = file_serializer.validated_data["image"]
            filer_folder = obj.get_folder()
            filer_image = Image.objects.create(
                original_filename=image.name,
                file=image,
                folder=filer_folder,
                owner=self.request.user,
            )

            obj.image = filer_image
            obj.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HelpTextFieldChoices(AutoResponseView):
    def get(self, request, *args, **kwargs):
        ct = request.GET.get("content_type", None)
        ht = HelpText.objects.get(content_type_id=ct)
        term = request.GET.get("term", None)
        choices = ht.get_help_text_fields_for_content_type()
        if term:
            results = [
                {"text": i[1], "id": i[0]} for i in choices if term in str.lower(i[1])
            ]
        else:
            results = [{"text": i[1], "id": i[0]} for i in choices]
        return JsonResponse({"results": results, "more": False})


class FileUploadView(FileUploadBaseView):
    def put(self, request, *args, **kwargs):
        obj, file_serializer = super(FileUploadView, self).put(request, *args, **kwargs)
        if file_serializer.is_valid():
            file = file_serializer.validated_data["file"]
            folder = obj.get_folder()

            filer_file = File.objects.create(
                original_filename=file.name,
                file=file,
                folder=folder,
                owner=self.request.user,
            )
            cf = ContentFile.objects.create(
                content=obj,
                title=file.name,
                file=filer_file,
            )
            result = {"title": cf.title, "url": cf.file.url, "id": cf.id}
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteContentFileView(DestroyAPIView):
    queryset = Content.objects.drafts()

    def get_object(self):
        slug = self.kwargs.get("slug", None)
        id = self.kwargs.get("pk", None)
        user = self.request.user
        if not slug or not id:
            raise Http404
        try:
            content = Content.objects.drafts().get(slug=slug)
            if not user.has_perm("content.delete_content", content):
                return HttpResponse(status=status.HTTP_403_FORBIDDEN)
            content_file = content.content_files.get(id=id)
        except ObjectDoesNotExist:
            raise Http404

        return content_file


class ContentFeed(Feed):
    model = None

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.teaser

    def item_author_name(self, item):
        return str(item.author.full_name)

    def item_pubdate(self, item):
        return item.created

    def item_updateddate(self, item):
        return item.modified

    def items(self):
        if not self.model:
            raise NotImplementedError
        return self.model.objects.published().order_by("-created")[:50]


class TrendsFeed(ContentFeed):
    model = Trend
    title = "Trends Feed"
    link = reverse_lazy("tools-feed")
    description = "DLL Trend Updates"


class ToolsFeed(ContentFeed):
    model = Tool
    title = "Tools Feed"
    link = reverse_lazy("trends-feed")
    description = "DLL Tool Updates"


class TeachingModulesFeed(ContentFeed):
    model = TeachingModule
    title = "Unterrichtsbausteine Feed"
    link = reverse_lazy("teaching-modules-feed")
    description = "DLL TeachingModule Updates"


def search_view(request):
    q = AutoQuery(request.GET.get("q", ""))
    sqs = SearchQuerySet().filter(
        SQ(name=q)
        | SQ(teaser=q)
        | SQ(additional_info=q)
        | SQ(authors=q)
        | SQ(subjects=q)
        | SQ(school_types=q)
    )
    sqs.query.boost_fields = {
        "name": 2,
        "teaser": 1.5,
        "additional_info": 1,
        "authors": 1,
    }
    if request.is_ajax():
        results = [{"title": result.name, "url": result.url} for result in sqs[:10]]
        return JsonResponse(results, safe=False)

    # If there are no results - display random Content objects.
    suggestions = []
    if sqs.count() == 0:
        suggestions = get_random_content(2, 2, 2)

    ctx = {
        "results": Content.objects.filter(pk__in=sqs.values_list("pk", flat=True)),
        "mlt": suggestions,
    }
    return render(request, "dll/search.html", ctx)


class FavoriteListApiView(ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Favorite.objects.filter(user=user)
