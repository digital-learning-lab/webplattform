from django.urls import reverse

from dll.content.utils import is_favored
from dll.content.models import Content
from dll.content.tests.test_content_views import BaseTestCase


class FavorTestCase(BaseTestCase):
    def test_unauthenticated_user_favor(self):
        published_content = Content.objects.published().first()
        response = self.client.post(
            published_content.get_favor_url(), data={"slug": published_content.slug}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(published_content.favorite_set.count(), 0)

    def test_unauthenticated_user_unfavor(self):
        published_content = Content.objects.published().first()
        response = self.client.post(
            published_content.get_unfavor_url(), data={"slug": published_content.slug}
        )
        self.assertEqual(response.status_code, 403)

    def _favor_content(self, content):
        return self.client.post(content.get_favor_url(), data={"slug": content.slug})

    def test_authenticated_user_favor(self):
        self.client.login(email="test+alice@blueshoe.de", password="password")
        published_content = Content.objects.published().first()
        response = self._favor_content(published_content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(published_content.get_draft().favorite_set.count(), 1)
        self.assertTrue(is_favored(self.author, published_content))

    def test_authenticated_user_unfavor(self):
        self.client.login(email="test+alice@blueshoe.de", password="password")
        published_content = Content.objects.published().first()
        response = self._favor_content(published_content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(published_content.get_draft().favorite_set.count(), 1)
        self.assertTrue(is_favored(self.author, published_content))

        response = self.client.post(
            published_content.get_unfavor_url(), data={"slug": published_content.slug}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(published_content.get_draft().favorite_set.count(), 0)
        self.assertFalse(is_favored(self.author, published_content))
        # Test content cannot be unfavored twice
        response = self.client.post(
            published_content.get_unfavor_url(), data={"slug": published_content.slug}
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json())

    def test_authenticated_preview_favor_button_hidden(self):
        self.client.login(email="test+alice@blueshoe.de", password="password")
        draft_content = Content.objects.drafts().first()
        response = self.client.get(
            draft_content.get_preview_url(),
        )
        self.assertTemplateUsed(response, "dll/content/detail.html")
        self.assertNotContains(response, "content-info__favor")

    def test_authenticated_favor_button_shown(self):
        self.client.login(email="test+alice@blueshoe.de", password="password")
        draft_content = Content.objects.drafts().first()
        response = self.client.get(
            draft_content.get_absolute_url(),
        )
        self.assertTemplateUsed(response, "dll/content/detail.html")
        self.assertContains(response, "Zum Merkzettel hinzufügen")

    def test_authenticated_unfavor_button_shown(self):
        self.client.login(email="test+alice@blueshoe.de", password="password")
        draft_content = Content.objects.drafts().first()
        response = self.client.get(
            draft_content.get_absolute_url(),
        )
        self.assertTemplateUsed(response, "dll/content/detail.html")
        self.assertContains(response, "Vom Merkzettel entfernen")

    def test_favor_list_view(self):
        self.client.login(email="test+alice@blueshoe.de", password="password")
        draft_content = Content.objects.drafts().first()
        self._favor_content(draft_content)
        response = self.client.get(
            reverse("user-favorites-overview"),
        )
        self.assertTemplateUsed(response, "dll/user/content/favorites.html")
        self.assertContains(response, draft_content.name)

    def test_content_teaser_favor_indication(self):

        self.client.login(email="test+alice@blueshoe.de", password="password")
        draft_content = Content.objects.drafts().first()
        self._favor_content(draft_content)
        response = self.client.get(
            reverse("user-favorites-overview"),
        )
        self.assertTemplateUsed(response, "dll/includes/content_teaser.html")
        self.assertContains(response, "Auf dem Merkzettel")

    def test_double_favor(self):
        self.client.login(email="test+alice@blueshoe.de", password="password")
        draft_content = Content.objects.drafts().first()
        self._favor_content(draft_content)
        response = self._favor_content(draft_content)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json())
