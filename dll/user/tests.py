from django.test import TestCase
from django.urls import reverse, resolve


class SignUpTests(TestCase):
    def test_signup_status_code(self):
        url = reverse('user:signup')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/user/signup/')
        from dll.user.views import SignUpView
        self.assertEquals(view.func, SignUpView.as_view())
