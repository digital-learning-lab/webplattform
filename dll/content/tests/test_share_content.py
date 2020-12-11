from django.urls import reverse

from dll.content.utils import is_favored
from dll.content.models import Content
from dll.content.tests.test_content_creation import BaseTestCase


class ShareContentTestCase(BaseTestCase):
    def test_share_button_shown(self):
        self.client.login(email="test+alice@blueshoe.de", password="password")
        draft_content = Content.objects.drafts().first()
        response = self.client.get(
            draft_content.get_absolute_url(),
        )
        self.assertTemplateUsed(response, "dll/content/detail.html")
        self.assertContains(response, "Mit anderen teilen")

    def test_no_share_button_in_preview(self):
        self.client.login(email="test+alice@blueshoe.de", password="password")
        draft_content = Content.objects.drafts().first()
        response = self.client.get(
            draft_content.get_preview_url(),
        )
        self.assertTemplateUsed(response, "dll/content/detail.html")
        self.assertNotContains(response, "Mit anderen teilen")
