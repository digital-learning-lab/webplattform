from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from dll.communication.models import CommunicationEventType


@override_settings(VALIDATE_RECAPTCHA=False)
class ContactTests(TestCase):
    def setUp(self):
        self.contact_url = reverse('communication:contact')
        self.test_data = {
            'from_email': "test@blueshoe.de",
            'message': "Very Important Message Content"
        }
        CommunicationEventType.objects.create(code='CONTACT_BSB', name="Contact BSB")
        CommunicationEventType.objects.create(code='CONTACT_DLL', name="Contact DLL")
        CommunicationEventType.objects.create(code='USER_CONTACT_SUCCESSFUL', name="Contact user")

    def test_send_contact_request_to_bsb(self):
        self.test_data.update({'subject': '0'})
        self.client.post(self.contact_url, data=self.test_data)
        # user and BSB must receive a message
        self.assertEqual(2, len(mail.outbox))
        found = False
        for email in mail.outbox:
            if settings.CONTACT_EMAIL_BSB in email.to:
                found = True
                self.assertIn(self.test_data['message'], str(email.body))
        self.assertTrue(found)

    def test_send_contact_request_to_tuhh(self):
        self.test_data.update({'subject': '1'})
        self.client.post(self.contact_url, data=self.test_data)
        self.assertEqual(2, len(mail.outbox))
        found = False
        for email in mail.outbox:
            if settings.CONTACT_EMAIL_DLL in email.to:
                found = True
                self.assertIn(self.test_data['message'], str(email.body))
        self.assertTrue(found)
