import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse, resolve

from dll.user.forms import SignUpForm
from dll.user.views import SignUpView


USER_MODEL = get_user_model()


class SignUpTests(TestCase):
    def setUp(self):
        url = reverse('user:signup')
        self.response = self.client.get(url)

    def test_signup_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/user/signup/')
        self.assertEquals(view.func.view_class, SignUpView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)


class SuccessfulSignupTests(TestCase):
    def setUp(self):
        settings.IGNORE_RECAPTCHA = True
        url = reverse('user:signup')
        data = {
            'username': 'john',
            'gender': 'male',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@blueshoe.de',
            'password1': '@%$hnsd345',
            'password2': '@%$hnsd345',
            'terms_accepted': True
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')
        self.profile_url = reverse('user:profile')

        # confirm registration
        link = re.search(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
                         mail.outbox[0].body)
        activation_link = link.group(0)
        self.client.get(activation_link)

    def test_redirection(self):
        self.assertRedirects(self.response, self.home_url)

    def test_user_creation(self):
        self.assertTrue(USER_MODEL.objects.count() > 0)

    def test_user_authentication(self):
        response = self.client.get(self.profile_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidSignUpTests(TestCase):
    def setUp(self):
        url = reverse('user:signup')
        self.response = self.client.post(url, {})

    def test_signup_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_dont_create_user(self):
        self.assertEqual(USER_MODEL.objects.count(), 0)
