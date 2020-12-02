import re
from urllib.parse import urlparse

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from dll.communication.models import CommunicationEventType, CommunicationEvent
from dll.user.models import DllUser
from dll.user.views import ProfileViewEmails


class BaseTestCase(TestCase):
    def setUp(self):
        author = {
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Doe",
            "email": "alice@blueshoe.de",
        }

        self.author = DllUser.objects.create(**author)
        self.author.set_password("password")
        self.author.save()

    def test_user_email_change(self):
        self.client.login(username="alice@blueshoe.de", password="password")
        post_data = {"email": "alice+1@blueshoe.de"}
        response = self.client.post(reverse("user:email"), post_data, follow=True)

        self.assertContains(response, ProfileViewEmails.INFO_TEXT)
        email = mail.outbox[0]
        link = re.search(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}(\.[a-z]{2,4})?\b"
            r"\/profil/email-bestaetigen\/([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
            email.body,
        )
        self.confirm_link = link.group(0)
        response = self.client.get(self.confirm_link, follow=True)
        self.assertContains(response, "Ihre E-Mail wurde erfolgreich geändert.")
        self.assertTrue(DllUser.objects.filter(email="alice+1@blueshoe.de").exists())
        communication_event = CommunicationEvent.objects.latest("pk")
        self.assertEqual(
            communication_event.event_type_id,
            CommunicationEventType.objects.get(code="USER_EMAIL_CHANGE").id,
        )
        self.assertEqual(communication_event.to[0], "alice+1@blueshoe.de")
