from django.views.generic import DetailView, CreateView

from dll.survey.models import Survey, SurveyResult


class SurveyDetailView(DetailView):
    model = Survey
    template_name = "survey/survey.html"


class SurveyResultCreateView(CreateView):
    model = SurveyResult
