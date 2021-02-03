from django.test import TestCase
from django.urls import reverse

from dll.survey.models import Trigger, Survey


class SurveyTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SurveyTests, cls).setUpClass()
        cls.survey = Survey.objects.create(
            title="Test Survey", description="Test Description"
        )
        cls.trigger = Trigger.objects.create(
            event="click",
            delay=1000,
            url="",
            target="body",
            survey=cls.survey,
            active=True,
        )
        cls.trigger2 = Trigger.objects.create(
            event="click", delay=1000, target="body", survey=cls.survey, active=False
        )

    def test_trigger_api_view(self):
        url = reverse("trigger-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["event"], "click")
        self.assertEqual(data["results"][0]["delay"], 1000)
        self.assertEqual(data["results"][0]["target"], "body")
        self.assertEqual(data["results"][0]["survey"], self.survey.pk)
        self.assertEqual(data["results"][0]["url"], "")
