from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import views as auth_views, get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core import mail
from django.urls import resolve, reverse
from django.test import TestCase


USER_MODEL = get_user_model()


class PasswordResetTests(TestCase):
    def setUp(self):
        url = reverse("user:password_reset")
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve("/reset/")
        self.assertEqual(view.func.view_class, auth_views.PasswordResetView)

    def test_csrf(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, PasswordResetForm)

    def test_form_inputs(self):
        """
        The view must contain two inputs: csrf and email
        """
        self.assertContains(self.response, "<input", 4)
        self.assertContains(self.response, 'type="email"', 1)


class SuccessfulPasswordResetTests(TestCase):
    def setUp(self):
        email = "john@doe.com"
        USER_MODEL.objects.create_user(
            username="john", email=email, password="123abcdef"
        )
        url = reverse("user:password_reset")
        self.response = self.client.post(url, {"email": email})

    def test_redirection(self):
        """
        A valid form submission should redirect the user to `password_reset_done` view
        """
        url = reverse("user:password_reset_done")
        self.assertRedirects(self.response, url)

    def test_send_password_reset_email(self):
        self.assertEqual(1, len(mail.outbox))


class InvalidPasswordResetTests(TestCase):
    def setUp(self):
        url = reverse("user:password_reset")
        self.response = self.client.post(url, {"email": "donotexist@email.com"})

    def test_redirection(self):
        """
        Even invalid emails in the database should
        redirect the user to `password_reset_done` view
        """
        url = reverse("user:password_reset_done")
        self.assertRedirects(self.response, url)

    def test_no_reset_email_sent(self):
        self.assertEqual(0, len(mail.outbox))


class PasswordResetDoneTests(TestCase):
    def setUp(self):
        url = reverse("user:password_reset_done")
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve("/reset/done/")
        self.assertEqual(view.func.view_class, auth_views.PasswordResetDoneView)


class PasswordResetConfirmTests(TestCase):
    def setUp(self):
        user = USER_MODEL.objects.create_user(
            username="john", email="john@doe.com", password="123abcdef"
        )

        """
        create a valid password reset token
        based on how django creates the token internally:
        https://github.com/django/django/blob/1.11.5/django/contrib/auth/forms.py#L280
        """
        self.uid = urlsafe_base64_encode(force_bytes(user.pk))
        self.token = default_token_generator.make_token(user)

        url = reverse(
            "user:password_reset_confirm",
            kwargs={"uidb64": self.uid, "token": self.token},
        )
        self.response = self.client.get(url, follow=True)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve(
            "/reset/{uidb64}/{token}/".format(uidb64=self.uid, token=self.token)
        )
        self.assertEqual(view.func.view_class, auth_views.PasswordResetConfirmView)

    def test_csrf(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, SetPasswordForm)

    def test_form_inputs(self):
        """
        The view must contain two inputs: csrf and two password fields
        """
        self.assertContains(self.response, "<input", 5)
        self.assertContains(self.response, 'type="password"', 2)


class InvalidPasswordResetConfirmTests(TestCase):
    def setUp(self):
        user = USER_MODEL.objects.create_user(
            username="john", email="john@doe.com", password="123abcdef"
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        """
        invalidate the token by changing the password
        """
        user.set_password("abcdef123")
        user.save()

        url = reverse(
            "user:password_reset_confirm", kwargs={"uidb64": uid, "token": token}
        )
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_html(self):
        self.assertContains(self.response, "Ungültiger Link")


class PasswordResetCompleteTests(TestCase):
    def setUp(self):
        url = reverse("user:password_reset_complete")
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve("/reset/complete/")
        self.assertEqual(view.func.view_class, auth_views.PasswordResetCompleteView)
