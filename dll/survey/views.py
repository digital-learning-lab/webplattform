from django.views.generic import DetailView

from dll.survey.models import Survey


class SurveyDetailView(DetailView):
    model = Survey
    template_name = "survey/survey.html"
