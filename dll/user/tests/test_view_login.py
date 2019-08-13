import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

USER_MODEL = get_user_model()


class SuccessfulLoginTests(TestCase):
    def setUp(self):
        settings.IGNORE_RECAPTCHA = True
        signup_url = reverse('user:signup')
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
        self.response = self.client.post(signup_url, data)

        # confirm registration
        link = re.search(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
                         mail.outbox[0].body)
        activation_link = link.group(0)
        self.client.get(activation_link)

        self.login_url = reverse('user:login')
        self.profile_url = reverse('user:profile')

    def test_log_in(self):
        data = {
            'username': 'john',
            'password': '@%$hnsd345'
        }

        response = self.client.post(self.login_url, data)
        self.assertRedirects(response, self.profile_url)

        redirected_response = self.client.get(response.url)
        user = redirected_response.context.get('user')
        self.assertTrue(user.is_authenticated)
