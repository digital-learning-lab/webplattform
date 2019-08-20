import json
import random

from django.urls import reverse_lazy, resolve
from django.views.generic import TemplateView, DetailView
from django.views.generic.base import ContextMixin
from django_filters.rest_framework import DjangoFilterBackend
from psycopg2._range import NumericRange
from rest_framework import viewsets, filters
from rest_framework.generics import ListAPIView

from dll.content.models import Content, TeachingModule, Trend, Tool, Competence, Subject
from dll.general.utils import GERMAN_STATES
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
            content_pks += random.choices(TeachingModule.objects.drafts().values_list('pk', flat=True), k=2)
            content_pks += random.choices(Trend.objects.drafts().values_list('pk', flat=True), k=2)
            content_pks += random.choices(Tool.objects.drafts().values_list('pk', flat=True), k=2)
        except IndexError:
            pass  # no content yet
        ctx['contents'] = Content.objects.filter(pk__in=content_pks)
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


class NewsletterRegisterView(TemplateView, BreadcrumbMixin):
    template_name = 'dll/newsletter/register.html'
    breadcrumb_title = 'Newsletteranmeldung'
    breadcrumb_url = reverse_lazy('newsletter')


class NewsletterUnregisterView(TemplateView, BreadcrumbMixin):
    template_name = 'dll/newsletter/unregister.html'
    breadcrumb_title = 'Newsletterabmeldung'
    breadcrumb_url = reverse_lazy('newsletter-unregister')


class ContactView(TemplateView, BreadcrumbMixin):
    template_name = 'dll/contact.html'
    breadcrumb_title = 'Kontakt'
    breadcrumb_url = reverse_lazy('contact')


class ContentDetailView(DetailView):
    def get_context_data(self, **kwargs):
        ctx = super(ContentDetailView, self).get_context_data(**kwargs)
        ctx['competences'] = Competence.objects.all()
        return ctx


class ToolDetailView(ContentDetailView):
    model = Tool
    template_name = 'dll/content/tool_detail.html'


class TrendDetailView(ContentDetailView):
    model = Trend
    template_name = 'dll/content/trend_detail.html'


class TeachingModuleDetailView(ContentDetailView):
    model = TeachingModule
    template_name = 'dll/content/teaching_module_detail.html'


class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentPolymorphicSerializer
    queryset = Content.objects.published()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['name', 'teaser']
    permission_classes = []

    def get_queryset(self):
        competence = self.request.GET.get('competence', '')
        sorting = self.request.GET.get('sorting', 'az')
        teaching_modules = self.request.GET.get('teachingModules', 'true')
        trends = self.request.GET.get('trends', 'true')
        tools = self.request.GET.get('tools', 'true')
        qs = super(ContentViewSet, self).get_queryset()

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
        if name == 'content-list' and self.request.method == 'GET':
            return ContentListSerializer
        else:
            return super(ContentViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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
