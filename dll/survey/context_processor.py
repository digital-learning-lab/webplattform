from dll.survey.models import Trigger


def survey_triggers(request):
    return {"survey_triggers": Trigger.objects.filter(active=True)}
