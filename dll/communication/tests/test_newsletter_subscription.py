import re

from django.test import TestCase
from django.core import mail
from django.urls import reverse

from dll.communication.models import CommunicationEventType, NewsletterSubscrption


class NewsletterSubscribeTests(TestCase):
    def setUp(self):
        self.subscribe_url = reverse('communication:newsletter')
        self.data = {
            'email_address': 'test@blueshoe.de',
        }
        self.email_address = 'test@blueshoe.de'
        CommunicationEventType.objects.create(code='NEWSLETTER_CONFIRM', name="Newsletter subscription link")

    def test_newsletter_subscribe(self):
        response = self.client.post(self.subscribe_url, data=self.data)
        # todo: add messages to template
        # self.assertContains(response, 'Bestätigungslink versendet', status_code=302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertFalse(NewsletterSubscrption.objects.get().doi_confirmed)
        link = re.search(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}(\.[a-z]{2,4})?\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
            mail.outbox[0].body)
        confirmation_link = link.group(0)
        self.client.get(confirmation_link)
        self.assertTrue(NewsletterSubscrption.objects.get().doi_confirmed)


class NewsletterUnsubscrbeTests(TestCase):
    def setUp(self):
        self.email = 'test@blueshoe.de'
        sub = NewsletterSubscrption.objects.create(email=self.email)
        sub.activate()
        self.unsubscribe_url = reverse('communication:newsletter-unregister')
        CommunicationEventType.objects.create(code='NEWSLETTER_UNREGISTER_CONFIRM', name="Newsletter subscription link")

    def test_newsletter_unsubscribe(self):
        response = self.client.post(self.unsubscribe_url, data={'email_address': self.email})
        self.assertEqual(len(mail.outbox), 1)
        self.assertFalse(NewsletterSubscrption.objects.exists())
