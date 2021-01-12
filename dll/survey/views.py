from crispy_forms.utils import render_crispy_form
from django.http import JsonResponse
from django.views.generic import DetailView

from dll.survey.forms import SurveyResultForm
from dll.survey.models import Survey


class SurveyDetailView(DetailView):
    model = Survey
    template_name = "survey/survey.html"

    def get_context_data(self, **kwargs):
        ctx = super(SurveyDetailView, self).get_context_data(**kwargs)
        ctx["form"] = SurveyResultForm(survey=self.get_object())
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = SurveyResultForm(data=request.POST, survey=self.object)
        if not form.is_valid():
            return JsonResponse(
                {
                    "success": False,
                    "form": render_crispy_form(form, context=self.get_context_data()),
                }
            )
        form.save()
        return JsonResponse({"success": True})
