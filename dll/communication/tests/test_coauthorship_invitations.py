import re
from urllib.parse import urlparse

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from dll.communication.models import CommunicationEventType
from dll.content.models import TeachingModule
from dll.user.models import DllUser


class BaseTestCase(TestCase):
    def setUp(self):
        author = {
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Doe",
            "email": "alice@blueshoe.de",
        }

        co_author = {
            "username": "bob",
            "first_name": "Bob",
            "last_name": "Doe",
            "email": "bob@blueshoe.de",
        }

        new_co_author = {
            "username": "carmen",
            "first_name": "Carmen",
            "last_name": "Doe",
            "email": "carmen@blueshoe.de",
        }

        removed_co_author = {
            "username": "daniel",
            "first_name": "Daniel",
            "last_name": "Doe",
            "email": "daniel@blueshoe.de",
        }

        self.author = DllUser.objects.create(**author)
        self.author.set_password("password")
        self.author.save()

        self.co_author = DllUser.objects.create(**co_author)
        self.new_co_author = DllUser.objects.create(**new_co_author)
        self.new_co_author.set_password("password")
        self.new_co_author.save()
        self.removed_co_author = DllUser.objects.create(**removed_co_author)
        self.removed_co_author.set_password("password")
        self.removed_co_author.save()

        self.content = TeachingModule.objects.create(name="Foo", author=self.author,)
        self.content.co_authors.add(self.co_author, self.removed_co_author)
        CommunicationEventType.objects.create(
            code="COAUTHOR_INVITATION", name="Coauthor invitation"
        )


class CoAuthorshipInvitationTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        CommunicationEventType.objects.create(
            code="COAUTHOR_INVITATION_ACCEPTED", name="Coauthor invitation accepted"
        )
        self.login_url = reverse("user:login")

    def TestA(self):
        """
        author invites coauthor, and removes another one. this should have following effects:
        - removed author is directly removed
        - invited author receives mail
        - mail contains valid link
        """
        self.client.login(username="alice@blueshoe.de", password="password")
        update_url = reverse("draft-content-detail", kwargs={"slug": self.content.slug})
        post_data = {
            "co_authors": [{"pk": self.co_author.pk}, {"pk": self.new_co_author.pk}],
            "resourcetype": "TeachingModule",
        }
        self.client.patch(update_url, data=post_data, content_type="application/json")

        # old co author is not removed
        self.assertTrue(self.co_author in self.content.co_authors.all())
        # new co author must first accept the sent invitation
        self.assertFalse(self.new_co_author in self.content.co_authors.all())
        # new co author has received an invitation
        self.assertEqual(len(mail.outbox), 1)
        # author is removed if not present anymore in the coauthor list
        self.assertFalse(self.removed_co_author in self.content.co_authors.all())
        self.client.logout()

    def TestB(self):
        """
        test that login is required to view invitation
        """
        email = mail.outbox[0]
        link = re.search(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}(\.[a-z]{2,4})?\b"
            r"\/einladung\/([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
            email.body,
        )
        self.invitation_link = link.group(0)
        response = self.client.get(self.invitation_link)
        rel_path = urlparse(self.invitation_link).path
        self.assertRedirects(response, self.login_url + "?next=" + rel_path)

    def TestC(self):
        """
        other users cannot accept invitation link
        """
        self.client.login(username="daniel@blueshoe.de", password="password")
        response = self.client.post(self.invitation_link, data={"user_response": "Yes"})
        self.assertFalse(self.new_co_author in self.content.co_authors.all())
        self.client.logout()

    def TestD(self):
        """
        invited user can accept invitation
        """
        self.client.login(username="carmen@blueshoe.de", password="password")
        self.client.post(self.invitation_link, data={"user_response": "Yes"})
        self.assertTrue(self.new_co_author in self.content.co_authors.all())
        self.assertEqual(len(mail.outbox), 2)
        self.client.logout()

    def test_A_then_B_then_C_then_D(self):
        self.TestA()
        self.TestB()
        self.TestC()
        self.TestD()


class InvitationDeclineTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="alice@blueshoe.de", password="password")
        update_url = reverse("draft-content-detail", kwargs={"slug": self.content.slug})
        post_data = {
            "co_authors": [{"pk": self.co_author.pk}, {"pk": self.new_co_author.pk}],
            "resourcetype": "TeachingModule",
        }
        self.client.patch(update_url, data=post_data, content_type="application/json")
        self.client.logout()
        CommunicationEventType.objects.create(
            code="COAUTHOR_INVITATION_DECLINED", name="Coauthor invitation accepted"
        )

    def test_decline_invitation_link(self):
        self.client.login(username="carmen@blueshoe.de", password="password")
        email = mail.outbox[0]
        link = re.search(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}(\.[a-z]{2,4})?\b"
            r"\/einladung\/([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
            email.body,
        )
        invitation_link = link.group(0)
        self.client.post(invitation_link, data={"user_response": "No"})
        self.assertFalse(self.new_co_author in self.content.co_authors.all())
        self.assertEqual(len(mail.outbox), 2)
