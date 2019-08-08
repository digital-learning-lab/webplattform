import random

from django.views.generic import TemplateView

from dll.content.models import Content, TeachingModule, Trend, Tool


class HomePageView(TemplateView):
    template_name = 'dll/home.html'

    def get_context_data(self, **kwargs):
        ctx = super(HomePageView, self).get_context_data(**kwargs)
        content_pks = []
        content_pks += random.choices(TeachingModule.objects.values_list('pk', flat=True), k=2)
        content_pks += random.choices(Trend.objects.values_list('pk', flat=True), k=2)
        content_pks += random.choices(Tool.objects.values_list('pk', flat=True), k=2)
        ctx['contents'] = Content.objects.filter(pk__in=content_pks)
        return ctx
