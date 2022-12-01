from constance.test import override_config
from django.urls import reverse
from django.test import TestCase, override_settings

from dll.content.models import Testimonial, Tool, Subject
from dll.content.tests.test_content_views import BaseTestCase


@override_settings(SITE_ID=2)
@override_config(TESTIMONIAL_DLT=True)
class TestimonialTests(BaseTestCase):
    fixtures = ["dll/fixtures/sites.json"]

    def setUp(self):
        super().setUp()
        self.tool = Tool.objects.published().first()
        self.subject = Subject.objects.create(name="Test")
        Testimonial.objects.all().delete()

    def _login(self):
        self.client.login(username="test+alice@blueshoe.de", password="password")

    def test_testimonial_form_not_visible_for_anonymous(self):
        detail_view = reverse("tool-detail", kwargs={"slug": self.tool.slug})
        response = self.client.get(detail_view)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "js-testimonialSection")

    def test_testimonial_form_visible_for_logged_in(self):
        self._login()
        detail_view = reverse("tool-detail", kwargs={"slug": self.tool.slug})
        response = self.client.get(detail_view)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "js-testimonialSection")

    def _submit_testimonial(self, payload):
        self._login()
        post_url = reverse("testimonial")
        return self.client.post(post_url, payload)

    def test_testimonial_submission_error(self):
        self._login()
        payload = {
            "subject": self.subject.pk,
            "comment": "Tolles Tool!",
            "school_class": 1,
            "content": "123213",
        }
        response = self._submit_testimonial(payload)
        self.assertEqual(response.status_code, 404)

    def test_testimonial_submission(self):
        self._login()
        payload = {
            "subject": self.subject.pk,
            "comment": "Tolles Tool!",
            "school_class": 1,
            "content": self.tool.pk,
        }
        response = self._submit_testimonial(payload)
        self.assertEqual(response.status_code, 200)

    def test_testimonial_submission_once_per_content(self):
        self._login()
        payload = {
            "subject": self.subject.pk,
            "comment": "Tolles Tool!",
            "school_class": 1,
            "content": self.tool.pk,
        }

        response1 = self._submit_testimonial(payload)
        print(response1.content)
        self.assertEqual(response1.status_code, 200)

        print(Testimonial.objects.all())

        response2 = self._submit_testimonial(payload)
        print(response2.content)
        self.assertEqual(response2.status_code, 400)

    def test_testimonial_accept(self):
        pass

    def test_testimonial_decline(self):
        pass

    def test_testimonial_request_change(self):
        pass
