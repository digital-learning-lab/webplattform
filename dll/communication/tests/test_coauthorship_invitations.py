import re

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from dll.communication.models import CommunicationEventType
from dll.content.models import TeachingModule
from dll.user.models import DllUser


class BaseTestCase(TestCase):
    def setUp(self):
        author = {
            'username': 'alice',
            'gender': 'female',
            'first_name': 'Alice',
            'last_name': 'Doe',
            'email': 'alice@blueshoe.de',
        }

        co_author = {
            'username': 'bob',
            'gender': 'male',
            'first_name': 'Bob',
            'last_name': 'Doe',
            'email': 'bob@blueshoe.de',
        }

        new_co_author = {
            'username': 'carmen',
            'gender': 'female',
            'first_name': 'Carmen',
            'last_name': 'Doe',
            'email': 'carmen@blueshoe.de',
        }

        removed_co_author = {
            'username': 'daniel',
            'gender': 'male',
            'first_name': 'Daniel',
            'last_name': 'Doe',
            'email': 'daniel@blueshoe.de',
        }

        self.author = DllUser.objects.create(**author)
        self.author.set_password('password')
        self.author.save()

        self.co_author = DllUser.objects.create(**co_author)
        self.new_co_author = DllUser.objects.create(**new_co_author)
        self.new_co_author.set_password('password')
        self.new_co_author.save()
        self.removed_co_author = DllUser.objects.create(**removed_co_author)

        self.content = TeachingModule.objects.create(
            name='Foo',
            author=self.author,
        )
        self.content.co_authors.add(self.co_author, self.removed_co_author)
        CommunicationEventType.objects.create(code='COAUTHOR_INVITATION', name="Coauthor invitation")


class CoAuthorshipInvitationTests(BaseTestCase):
    def test_author_invites_coauthor(self):
        self.client.login(username='alice@blueshoe.de', password='password')
        update_url = reverse('draft-content-detail', kwargs={'pk': self.content.pk})
        post_data = {
            "co_authors": [self.co_author.pk, self.new_co_author.pk],
            "resourcetype": "TeachingModule"
        }
        self.client.patch(update_url, data=post_data, content_type='application/json')

        # old co author is not removed
        self.assertTrue(self.co_author in self.content.co_authors.all())
        # new co author must first accept the sent invitation
        self.assertFalse(self.new_co_author in self.content.co_authors.all())
        # new co author has received an invitation
        self.assertEqual(len(mail.outbox), 1)
        # author is removed if not present anymore in the coauthor list
        self.assertFalse(self.removed_co_author in self.content.co_authors.all())


class InvitationAcceptTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='alice@blueshoe.de', password='password')
        update_url = reverse('draft-content-detail', kwargs={'pk': self.content.pk})
        post_data = {
            "co_authors": [self.co_author.pk, self.new_co_author.pk],
            "resourcetype": "TeachingModule"
        }
        self.client.patch(update_url, data=post_data, content_type='application/json')
        self.client.logout()
        CommunicationEventType.objects.create(code='COAUTHOR_INVITATION_ACCEPTED', name="Coauthor invitation accepted")

    def test_accept_invitation_link(self):
        self.client.login(username='carmen@blueshoe.de', password='password')
        email = mail.outbox[0]
        link = re.search(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}(\.[a-z]{2,4})?\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
            email.body)
        invitation_link = link.group(0)
        self.client.post(invitation_link, data={'user_response': "Yes"})
        self.assertTrue(self.new_co_author in self.content.co_authors.all())
        self.assertEqual(len(mail.outbox), 2)


class InvitationDeclineTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='alice@blueshoe.de', password='password')
        update_url = reverse('draft-content-detail', kwargs={'pk': self.content.pk})
        post_data = {
            "co_authors": [self.co_author.pk, self.new_co_author.pk],
            "resourcetype": "TeachingModule"
        }
        self.client.patch(update_url, data=post_data, content_type='application/json')
        self.client.logout()
        CommunicationEventType.objects.create(code='COAUTHOR_INVITATION_DECLINED', name="Coauthor invitation accepted")

    def test_accept_invitation_link(self):
        self.client.login(username='carmen@blueshoe.de', password='password')
        email = mail.outbox[0]
        link = re.search(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}(\.[a-z]{2,4})?\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
            email.body)
        invitation_link = link.group(0)
        self.client.post(invitation_link, data={'user_response': "No"})
        self.assertFalse(self.new_co_author in self.content.co_authors.all())
        self.assertEqual(len(mail.outbox), 2)
