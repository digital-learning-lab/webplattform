from crispy_forms.bootstrap import InlineRadios, InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.shortcuts import get_object_or_404

from dll.survey.models import (
    SurveyResult,
    SurveyResultAnswer,
    SurveyQuestion,
    SurveyQuestionChoice,
)


class SurveyResultForm(forms.ModelForm):

    FIELD_MAP = {
        0: forms.ChoiceField,
        1: forms.MultipleChoiceField,
        2: forms.ChoiceField,
        3: forms.CharField,
    }

    WIDGET_MAP = {
        0: forms.RadioSelect,
        1: forms.Select,
        2: forms.CheckboxSelectMultiple,
        3: forms.TextInput,
    }

    CRISPY_MAP = {
        0: InlineRadios,
        2: InlineCheckboxes,
    }

    def __init__(self, *args, **kwargs):
        self.survey = kwargs.pop("survey")
        super(SurveyResultForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.error_text_inline = True
        self.helper.layout = Layout()
        self._generate_fields()
        self.helper.layout.append(Submit("submit", "Absenden"))

    def _generate_fields(self):
        self.fields = {}
        for question in self.survey.survey_questions.all():
            field_name = "question_{}".format(question.id)
            kwargs = {
                "widget": self._get_widget(question.question_type),
                "label": question.title,
                "required": question.required,
            }
            if question.question_type in self.CRISPY_MAP.keys():
                self.helper.layout.fields.append(
                    self.CRISPY_MAP[question.question_type](field_name)
                )
            else:
                self.helper.layout.fields.append(field_name)
            if question.question_type in [0, 1, 2]:
                kwargs["choices"] = question.choices.all().values_list("pk", "label")
            self.fields[field_name] = self.FIELD_MAP[question.question_type](**kwargs)

    def save(self, commit=True):
        self.instance.survey = self.survey
        instance = super(SurveyResultForm, self).save(commit=commit)
        for key, value in self.cleaned_data.items():
            if key.startswith("question"):
                try:
                    question_id = key.split("_")[1]
                except IndexError:
                    continue
                question = get_object_or_404(SurveyQuestion, id=question_id)
                if question.question_type in [0, 1, 2]:
                    result = [
                        get_object_or_404(SurveyQuestionChoice, id=id).label
                        for id in value
                    ]
                    result = ",".join(result)
                else:
                    result = value
                SurveyResultAnswer.objects.create(
                    question=question, result=instance, value=result
                )
        return instance

    def _get_widget(self, question_type):
        return self.WIDGET_MAP[question_type]

    class Meta:
        model = SurveyResult
        fields = ()
