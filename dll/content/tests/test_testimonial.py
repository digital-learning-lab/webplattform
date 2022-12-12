from constance.test import override_config
from django.core import mail
from django.urls import reverse
from django.test import TestCase, override_settings

from dll.content.models import Testimonial, TestimonialReview, Tool, Subject
from dll.content.tests.test_content_views import BaseTestCase
from dll.user.models import DllUser


@override_settings(SITE_ID=2)
@override_config(TESTIMONIAL_DLT=True)
class TestimonialTests(BaseTestCase):
    fixtures = ["dll/fixtures/sites.json"]

    def setUp(self):
        super().setUp()
        self.tool = Tool.objects.published().first()
        self.subject = Subject.objects.create(name="Test")
        Testimonial.objects.all().delete()
        admin = {
            "username": "super",
            "first_name": "su",
            "last_name": "per",
            "email": "super@blueshoe.de",
            "is_superuser": True,
            "is_active": True,
            "is_staff": True,
        }

        self.admin = DllUser.objects.create(**admin)
        self.admin.set_password("password")
        self.admin.save()

    def _login(self):
        self.client.login(username="test+alice@blueshoe.de", password="password")

    def _login_admin(self):
        self.client.login(username="super@blueshoe.de", password="password")

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
        post_url = reverse("testimonial")
        return self.client.post(post_url, payload, follow=True)

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
        self.assertEqual(Testimonial.objects.all().count(), 1)

    def test_testimonial_submission_once_per_content(self):
        self._login()
        payload = {
            "subject": self.subject.pk,
            "comment": "Tolles Tool!",
            "school_class": 1,
            "content": self.tool.pk,
        }

        response1 = self._submit_testimonial(payload)
        self.assertEqual(response1.status_code, 200)

        response2 = self._submit_testimonial(payload)
        self.assertEqual(response2.status_code, 400)

    def test_testimonial_non_admin_cannot_accept(self):
        Testimonial.objects.all().delete()
        self._login()
        payload = {
            "subject": self.subject.pk,
            "comment": "Tolles Tool!",
            "school_class": 1,
            "content": self.tool.pk,
        }

        response = self._submit_testimonial(payload)
        self.assertEqual(response.status_code, 200)

        testimonial = Testimonial.objects.all().first()
        self.assertFalse(testimonial.is_public)
        self.assertIsNone(testimonial.get_published())

        accept_url = "/api/testimonial-review/{}/accept/"

        accept_response = self.client.post(accept_url.format(testimonial.pk))
        self.assertEqual(accept_response.status_code, 400)

        self.assertFalse(testimonial.is_public)
        self.assertIsNone(testimonial.get_published())

    def test_testimonial_accept(self):
        Testimonial.objects.all().delete()
        self._login()
        payload = {
            "subject": self.subject.pk,
            "comment": "Tolles Tool!",
            "school_class": 1,
            "content": self.tool.pk,
        }

        response = self._submit_testimonial(payload)
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        self._login_admin()

        testimonial = Testimonial.objects.all().first()
        review = testimonial.reviews.first()
        self.assertFalse(testimonial.is_public)
        self.assertIsNone(testimonial.get_published())

        accept_url = "/api/testimonial-review/{}/accept/"

        accept_response = self.client.post(accept_url.format(review.pk), follow=True)
        self.assertEqual(accept_response.status_code, 200)

        testimonial.refresh_from_db()

        self.assertEqual(testimonial.reviews.first().status, TestimonialReview.ACCEPTED)
        self.assertFalse(testimonial.is_public)
        self.assertEqual(Testimonial.objects.all().count(), 2)
        self.assertIsNotNone(testimonial.get_published())

    def test_testimonial_decline(self):

        Testimonial.objects.all().delete()
        self._login()
        payload = {
            "subject": self.subject.pk,
            "comment": "Tolles Tool!",
            "school_class": 1,
            "content": self.tool.pk,
        }

        response = self._submit_testimonial(payload)
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        self._login_admin()

        testimonial = Testimonial.objects.all().first()
        review = testimonial.reviews.first()
        self.assertFalse(testimonial.is_public)
        self.assertIsNone(testimonial.get_published())

        decline_url = "/api/testimonial-review/{}/decline/"

        decline_response = self.client.post(decline_url.format(review.pk), follow=True)
        self.assertEqual(decline_response.status_code, 200)

        testimonial.refresh_from_db()

        self.assertEqual(testimonial.reviews.first().status, TestimonialReview.DECLINED)
        self.assertFalse(testimonial.is_public)
        self.assertEqual(Testimonial.objects.all().count(), 1)
        self.assertIsNone(testimonial.get_published())

    def test_testimonial_request_change(self):
        Testimonial.objects.all().delete()
        self._login()
        payload = {
            "subject": self.subject.pk,
            "comment": "Tolles Tool!",
            "school_class": 1,
            "content": self.tool.pk,
        }

        response = self._submit_testimonial(payload)
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        self._login_admin()

        testimonial = Testimonial.objects.all().first()
        review = testimonial.reviews.first()
        self.assertFalse(testimonial.is_public)
        self.assertIsNone(testimonial.get_published())

        request_url = "/api/testimonial-review/{}/request_changes/"
        comment = "some comment"
        request_response = self.client.post(
            request_url.format(review.pk), {"comment": comment}, follow=True
        )
        self.assertEqual(request_response.status_code, 200)

        testimonial.refresh_from_db()
        review.refresh_from_db()

        self.assertEqual(testimonial.reviews.first().status, TestimonialReview.CHANGES)
        self.assertFalse(testimonial.is_public)
        self.assertEqual(Testimonial.objects.all().count(), 1)
        self.assertEqual(review.comment, comment)
        self.assertIsNone(testimonial.get_published())

    def test_testimonial_mail_sent(self):
        Testimonial.objects.all().delete()
        self._login()
        payload = {
            "subject": self.subject.pk,
            "comment": "Tolles Tool!",
            "school_class": 1,
            "content": self.tool.pk,
        }

        response = self._submit_testimonial(payload)
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        self._login_admin()

        testimonial = Testimonial.objects.all().first()
        review = testimonial.reviews.first()
        self.assertFalse(testimonial.is_public)
        self.assertIsNone(testimonial.get_published())

        decline_url = "/api/testimonial-review/{}/decline/"

        decline_response = self.client.post(decline_url.format(review.pk), follow=True)
        self.assertEqual(decline_response.status_code, 200)

        testimonial.refresh_from_db()

        self.assertEqual(1, len(mail.outbox))
        self.assertIn("einen Erfahrungsbricht für den Inhalt", mail.outbox[0].body)
