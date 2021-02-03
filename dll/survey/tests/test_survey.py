from django.test import TestCase
from django.urls import reverse

from dll.survey.models import (
    Survey,
    SurveyQuestion,
    SurveyQuestionChoice,
    SurveyResult,
    SurveyResultAnswer,
)


class SurveyTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SurveyTests, cls).setUpClass()
        cls.survey = Survey.objects.create(
            title="Test Survey", description="Test Description"
        )

        cls.questions = [
            {
                "question_type": 0,
                "title": "Rate something from 1 to 5.",
                "required": True,
                "choices": [1, 2, 3, 4, 5],
            },
            {
                "question_type": 1,
                "title": "Choose a fruit..",
                "required": False,
                "choices": ["Apple", "Banana", "Peach"],
            },
            {
                "question_type": 2,
                "title": "Check all items you like..",
                "required": True,
                "choices": ["Cars", "Bikes", "Airplanes", "Trains"],
            },
            {"question_type": 3, "title": "Tell us about your day.", "required": False},
        ]

        for question in cls.questions:
            choices = question.pop("choices") if "choices" in question else []
            question = SurveyQuestion.objects.create(survey=cls.survey, **question)
            for choice in choices:
                SurveyQuestionChoice.objects.create(question=question, label=choice)

    def test_detail_view_get(self):
        url = reverse("survey-detail", kwargs={"pk": self.survey.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.survey.title)
        self.assertContains(response, self.survey.description)
        self.assertContains(response, "Peach")
        self.assertContains(response, "Train")
        self.assertContains(response, "radio")
        self.assertContains(response, "checkbox")
        self.assertContains(response, "select")

    def test_detail_view_post(self):
        url = reverse("survey-detail", kwargs={"pk": self.survey.pk})
        data = {}
        text_answer = "Test Text"
        for question in self.survey.survey_questions.all():
            if question.question_type != 3:
                value = question.choices.all().first().pk
            else:
                value = text_answer
            data[f"question_{question.pk}"] = value
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        for question in self.survey.survey_questions.all():
            answer = SurveyResultAnswer.objects.get(question=question)
            if question.question_type != 3:
                self.assertEqual(answer.value, question.choices.all().first().label)
            else:
                self.assertEqual(answer.value, text_answer)

    def test_submit_fail(self):
        url = reverse("survey-detail", kwargs={"pk": self.survey.pk})
        data = {}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertContains(response, "Peach")
        self.assertContains(response, "Train")
        self.assertContains(response, "radio")
        self.assertContains(response, "checkbox")
        self.assertContains(response, "select")
