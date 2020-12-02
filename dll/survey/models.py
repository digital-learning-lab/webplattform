from ckeditor.fields import RichTextField
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class Survey(models.Model):
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = RichTextField(
        verbose_name=_("Description"),
    )

    def __str__(self):
        return self.title


class SurveyQuestion(models.Model):
    question_type = models.SmallIntegerField(
        verbose_name=_("Type"),
        choices=(
            (0, _("Radio")),
            (1, _("Dropdown")),
            (2, _("Checkbox")),
            (3, _("Text")),
        ),
    )

    survey = models.ForeignKey(
        "survey.Survey", on_delete=models.CASCADE, related_name="survey_questions"
    )

    position = models.PositiveIntegerField(verbose_name=_("Position"), default=0)

    title = models.CharField(verbose_name=_("Title"), max_length=255)

    required = models.BooleanField(verbose_name=_("Required"), default=False)

    def __str__(self):
        return self.title


class SurveyQuestionChoice(models.Model):
    label = models.CharField(verbose_name=_("Label"), max_length=64)

    position = models.PositiveIntegerField(verbose_name=_("Position"), default=0)

    question = models.ForeignKey(
        "survey.SurveyQuestion", on_delete=models.CASCADE, related_name="choices"
    )

    def __str__(self):
        return self.label

    class Meta:
        ordering = ["position"]


class SurveyResult(models.Model):
    survey = models.ForeignKey("survey.Survey", on_delete=models.CASCADE)

    def __str__(self):
        return self.survey.title


class SurveyResultAnswer(models.Model):
    question = models.ForeignKey(
        "survey.SurveyQuestion", on_delete=models.SET_NULL, null=True, blank=False
    )

    value = models.TextField(
        verbose_name=_("Value"),
    )

    def __str__(self):
        return self.question.title


class Trigger(models.Model):

    event = models.CharField(
        verbose_name=_("Trigger Type"), choices=settings.TRIGGER_EVENTS, max_length=64
    )

    delay = models.PositiveIntegerField(
        verbose_name=_("Delay"), default=1000, blank=False
    )

    url = models.URLField(verbose_name=_("Page Url"), null=True, blank=True)

    survey = models.ForeignKey("survey.Survey", on_delete=models.CASCADE)

    active = models.BooleanField(verbose_name=_("Active"), default=True)

    def __str__(self):
        return "{} - {}".format(self.survey.title, self.get_event_display())
