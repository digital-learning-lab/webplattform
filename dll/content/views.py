import json
import random

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, Http404, HttpResponse
from django.urls import reverse_lazy, resolve
from django.views.generic import TemplateView, DetailView
from django.views.generic.base import ContextMixin
from django_filters.rest_framework import DjangoFilterBackend
from filer.models import Image, Folder, File
from psycopg2._range import NumericRange
from rest_framework import viewsets, filters, mixins, status
from rest_framework.generics import ListAPIView, GenericAPIView, DestroyAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from dll.content.models import Content, TeachingModule, Trend, Tool, Competence, Subject, SubCompetence, SchoolType, \
    Review, OperatingSystem, ToolApplication, HelpText, ContentFile
from dll.content.serializers import AuthorSerializer, CompetenceSerializer, SubCompetenceSerializer, \
    SchoolTypeSerializer, ReviewSerializer, SubjectSerializer, ImageFileSerializer, FileSerializer
from dll.general.utils import GERMAN_STATES
from dll.user.models import DllUser
from .serializers import ContentListSerializer, ContentPolymorphicSerializer


class BreadcrumbMixin(ContextMixin):
    breadcrumb_title = ''
    breadcrumb_url = ''

    def get_context_data(self, **kwargs):
        ctx = super(BreadcrumbMixin, self).get_context_data(**kwargs)
        ctx['breadcrumbs'] = self.get_breadcrumbs()
        return ctx

    def get_breadcrumbs(self):
        return [
            {'title': 'Home', 'url': '/'},
            {'title': self.breadcrumb_title, 'url': self.breadcrumb_url}
        ]


class HomePageView(TemplateView):
    template_name = 'dll/home.html'

    def get_context_data(self, **kwargs):
        ctx = super(HomePageView, self).get_context_data(**kwargs)
        content_pks = []
        try:
            content_pks += random.choices(TeachingModule.objects.published().values_list('pk', flat=True), k=2)
            content_pks += random.choices(Trend.objects.published().values_list('pk', flat=True), k=2)
            content_pks += random.choices(Tool.objects.published().values_list('pk', flat=True), k=2)
        except IndexError:
            pass  # no content yet
        ctx['contents'] = Content.objects.filter(pk__in=content_pks)
        try:
            ctx['training_trend'] = Trend.objects.published().get(slug='fortbildung-digitallearninglab')
        except Trend.DoesNotExist:
            pass
        return ctx


class ImprintView(TemplateView, BreadcrumbMixin):
    template_name = 'dll/imprint.html'
    breadcrumb_title = 'Impressum'
    breadcrumb_url = reverse_lazy('imprint')


class DataPrivacyView(TemplateView, BreadcrumbMixin):
    template_name = 'dll/data_privacy.html'
    breadcrumb_title = 'Datenschutz'
    breadcrumb_url = reverse_lazy('data-privacy')


class StructureView(TemplateView, BreadcrumbMixin):
    template_name = 'dll/structure.html'
    breadcrumb_title = 'Struktur'
    breadcrumb_url = reverse_lazy('structure')


class UsageView(TemplateView, BreadcrumbMixin):
    template_name = 'dll/usage.html'
    breadcrumb_title = 'Nutzung'
    breadcrumb_url = reverse_lazy('usage')


class DevelopmentView(TemplateView, BreadcrumbMixin):
    template_name = 'dll/development.html'
    breadcrumb_title = 'Entwicklung'
    breadcrumb_url = reverse_lazy('development')


class ContentDetailBase(DetailView):
    def get_context_data(self, **kwargs):
        ctx = super(ContentDetailBase, self).get_context_data(**kwargs)
        ctx['competences'] = Competence.objects.all()
        return ctx


class ContentDetailView(ContentDetailBase):
    def get_queryset(self):
        qs = super(ContentDetailView, self).get_queryset()
        return qs.published()


class ContentPreviewView(ContentDetailBase):
    def get_context_data(self, **kwargs):
        ctx = super(ContentPreviewView, self).get_context_data(**kwargs)
        ctx['preview'] = True
        return ctx

    def get_object(self, queryset=None):
        obj = super(ContentPreviewView, self).get_object(queryset=queryset)
        user = self.request.user
        if not user.has_perm('content.view_content', obj):
            raise Http404
        return obj

    def get_queryset(self):
        qs = super(ContentPreviewView, self).get_queryset()
        return qs.drafts()


class ToolDetailView(ContentDetailView):
    model = Tool
    template_name = 'dll/content/tool_detail.html'


class TrendDetailView(ContentDetailView):
    model = Trend
    template_name = 'dll/content/trend_detail.html'


class TeachingModuleDetailView(ContentDetailView):
    model = TeachingModule
    template_name = 'dll/content/teaching_module_detail.html'


class ToolDetailPreviewView(ContentPreviewView):
    model = Tool
    template_name = 'dll/content/tool_detail.html'


class TrendDetailPreviewView(ContentPreviewView):
    model = Trend
    template_name = 'dll/content/trend_detail.html'


class TeachingModuleDetailPreviewView(ContentPreviewView):
    model = TeachingModule
    template_name = 'dll/content/teaching_module_detail.html'


class PublishedContentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContentPolymorphicSerializer
    queryset = Content.objects.published()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['name', 'teaser']
    permission_classes = []
    authentication_classes = []

    def get_queryset(self):
        competence = self.request.GET.get('competence', '')
        sorting = self.request.GET.get('sorting', 'az')
        teaching_modules = self.request.GET.get('teachingModules', 'true')
        trends = self.request.GET.get('trends', 'true')
        tools = self.request.GET.get('tools', 'true')

        qs = super(PublishedContentViewSet, self).get_queryset()

        if competence:
            qs = qs.filter(competences__slug=competence)
        if teaching_modules != 'true':
            qs = qs.not_instance_of(TeachingModule)
        if trends != 'true':
            qs = qs.not_instance_of(Trend)
        if tools != 'true':
            qs = qs.not_instance_of(Tool)

        if sorting == 'az':
            return qs.order_by('name')
        else:
            return qs.order_by('-name')

    def get_serializer_class(self):
        name = resolve(self.request.path_info).url_name
        if name == 'public-content-list' and self.request.method == 'GET':
            return ContentListSerializer
        else:
            return super(PublishedContentViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class DraftsContentViewSet(AutoPermissionViewSetMixin,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """Authors can create, update and retrieve content, reviewers can only retrieve"""
    serializer_class = ContentPolymorphicSerializer
    queryset = Content.objects.drafts()
    lookup_field = 'slug'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SubmitContentView(GenericAPIView):
    queryset = Content.objects.drafts()
    lookup_field = 'slug'

    def post(self, *args, **kwargs):
        obj = self.get_object()
        user = self.request.user
        if user.has_perm('content.change_content', obj):
            obj.submit_for_review(user)
            return HttpResponse(status=200)
        return HttpResponse(status=403)


class ReviewViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    """Authors have only view permission, reviewers have view and edit permission"""
    serializer_class = ReviewSerializer
    queryset = Review.objects.filter(content__publisher_is_draft=True, is_active=True)
    permission_classes = [DjangoObjectPermissions]
    lookup_field = 'content__slug'
    lookup_url_kwarg = 'slug'

    def perform_update(self, serializer):
        serializer.save()


class BaseActionReviewView(GenericAPIView):
    queryset = Review.objects.filter(content__publisher_is_draft=True, is_active=True)
    lookup_field = 'content__slug'
    lookup_url_kwarg = 'slug'
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


class CompetenceFilterView(DetailView):
    model = Competence
    template_name = 'dll/filter/competence.html'


class ContentDataFilterView(ListAPIView):
    queryset = Content
    serializer_class = ContentListSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['name', 'teaser']
    model = None
    permission_classes = []
    authentication_classes = []

    def get_queryset(self):
        qs = super(ContentDataFilterView, self).get_queryset().objects.instance_of(self.model)
        qs = qs.published()

        sorting = self.request.GET.get('sorting', 'az')
        competences = self.request.GET.getlist('competences[]', [])
        print(competences)
        if competences:
            qs = qs.filter(competences__pk__in=competences)

        if sorting == 'az':
            return qs.order_by('name')
        elif sorting == 'latest':
            return qs.order_by('modified')
        elif sorting == '-latest':
            return qs.order_by('-modified')
        else:
            return qs.order_by('-name')


class TeachingModuleFilterView(TemplateView):
    template_name = 'dll/filter/teaching_modules.html'

    def get_context_data(self, **kwargs):
        ctx = super(TeachingModuleFilterView, self).get_context_data(**kwargs)
        subject_filter = [
            {'value': subject.pk, 'name': subject.name} for subject in Subject.objects.all()
        ]
        states_filter = [
            {'value': state[0], 'name': state[1]} for state in GERMAN_STATES
        ]
        states_filter.insert(0, {'value': '', 'name': '------'})
        ctx['subject_filter'] = json.dumps(subject_filter)
        ctx['states_filter'] = json.dumps(states_filter)
        return ctx


class TeachingModuleDataFilterView(ContentDataFilterView):
    model = TeachingModule

    def get_queryset(self):
        qs = super(TeachingModuleDataFilterView, self).get_queryset()

        subjects = self.request.GET.getlist('subjects[]', [])
        state = self.request.GET.get('state', [])
        class_from = self.request.GET.get('schoolClassFrom', [])
        class_to = self.request.GET.get('schoolClassTo', [])

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


        if subjects:
            qs = qs.filter(TeachingModule___subjects__pk__in=subjects)

        if state:
            qs = qs.filter(TeachingModule___state=state)

        if class_from:
            qs = qs.filter(TeachingModule___school_class__overlap=NumericRange(int(class_from), None))

        if class_to:
            qs = qs.filter(TeachingModule___school_class__overlap=NumericRange(None, int(class_to)))
        return qs


class ToolFilterView(TemplateView):
    template_name = 'dll/filter/tools.html'


class ToolDataFilterView(ContentDataFilterView):
    model = Tool

    def get_queryset(self):
        qs = super(ToolDataFilterView, self).get_queryset()

        status = self.request.GET.get('status', None)
        applications = self.request.GET.getlist('applications[]', [])
        operating_systems = self.request.GET.getlist('operatingSystems[]', [])

        if status:
            qs = qs.filter(Tool___status=status)

        if applications:
            qs = qs.filter(Tool___applications__name__in=applications)

        if operating_systems:
            qs = qs.filter(Tool___operating_systems__pk__in=operating_systems)
        return qs

class TrendFilterView(TemplateView):
    template_name = 'dll/filter/trends.html'


class TrendDataFilterView(ContentDataFilterView):
    model = Trend

    def get_queryset(self):
        qs = super(TrendDataFilterView, self).get_queryset()

        language = self.request.GET.get('language', None)
        trend_types = self.request.GET.getlist('trendTypes[]', [])

        if language:
            qs = qs.filter(Trend___language=language)

        if trend_types:
            qs = qs.filter(Trend___category__in=trend_types)

        return qs


class AuthorSearchView(ListAPIView):
    queryset = DllUser.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['username']



class CompetencesSearchView(ListAPIView):
    queryset = Competence.objects.all()
    serializer_class = CompetenceSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['name']


class SubCompetencesSearchView(ListAPIView):
    queryset = SubCompetence.objects.all()
    serializer_class = SubCompetenceSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['name']

    def get_queryset(self):
        qs = super(SubCompetencesSearchView, self).get_queryset()
        competences = self.request.GET.getlist('competences[]', [])


        if competences:
            competences_ids = [json.loads(competence)['pk'] for competence in competences]
            return qs.filter(competence__pk__in=competences_ids)
        return qs.none()


class SchoolTypesSearchView(ListAPIView):
    queryset = SchoolType.objects.all()
    serializer_class = SchoolTypeSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['name']


class SubjectSearchView(ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['name']


class OperatingSystemSearchView(ListAPIView):
    queryset = OperatingSystem.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['name']


class ToolApplicationSearchView(ListAPIView):
    queryset = ToolApplication.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['name']


class StateSearchView(APIView):

    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'results': [{'name': state[1], 'value': state[0]} for state in GERMAN_STATES]
        })


class FileUploadBaseView(APIView):
    parser_class = (FileUploadParser,)

    def put(self, request, *args, **kwargs):
        slug = kwargs.get('slug', None)
        if not slug:
            raise Http404

        obj = Content.objects.drafts().get(slug=slug)
        file_serializer = FileSerializer(data=request.data)

        return obj, file_serializer


class ImageUploadView(FileUploadBaseView):

    def put(self, request, *args, **kwargs):
        obj, file_serializer = super(ImageUploadView, self).put(*args, **kwargs)
        if file_serializer.is_valid():
            image = file_serializer.validated_data['file']
            filer_folder = Folder.objects.get(name=obj.__class__.__name__)
            filer_image = Image.objects.create(
                original_filename=image.name,
                file=image,
                folder=filer_folder,
                owner=self.request.user
            )

            obj.image = filer_image
            obj.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def admin_help_text_choices(request):
    ct = request.GET.get('content_type', None)
    ht = HelpText.objects.get(content_type_id=ct)
    choices = ht.get_help_text_fields_for_content_type()
    results = [{'text': i[1], 'id': i[0]} for i in choices]
    return JsonResponse({'results': results, 'more': False})


class FileUploadView(FileUploadBaseView):

    def put(self, request, *args, **kwargs):
        obj, file_serializer = super(FileUploadView, self).put(request, *args, **kwargs)
        if file_serializer.is_valid():
            file = file_serializer.validated_data['file']
            filer_folder = Folder.objects.get(name=obj.__class__.__name__)
            filer_file = File.objects.create(
                original_filename=file.name,
                file=file,
                folder=filer_folder,
                owner=self.request.user
            )

            cf = ContentFile.objects.create(
                content=obj,
                title=file.name,
                file = filer_file
            )
            result = {
                'title': cf.title,
                'url': cf.file.url,
                'id': cf.id
            }
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteContentFileView(DestroyAPIView):
    queryset = Content.objects.drafts()

    def get_object(self):
        slug = self.kwargs.get('slug', None)
        id = self.kwargs.get('pk', None)
        user = self.request.user
        if not slug or not id:
            raise Http404
        try:
            content = Content.objects.drafts().get(slug=slug)
            if not user.has_perm('content.delete_content', content):
                return HttpResponse(status=status.HTTP_403_FORBIDDEN)
            content_file = content.content_files.get(id=id)
        except ObjectDoesNotExist:
            raise Http404

        return content_file
