import random

from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView
from django.views.generic.base import ContextMixin

from dll.content.models import Content, TeachingModule, Trend, Tool, Competence


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


class CompetenceFilterView(TemplateView):
    template_name = 'dll/filter/competence.html'
