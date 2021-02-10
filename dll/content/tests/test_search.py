import time

from django.core.management import call_command
from django.urls import reverse
from django.core import management

from dll.content.tests.test_content_views import BaseTestCase


class SearchTestCase(BaseTestCase):
    def setUp(self):
        super(SearchTestCase, self).setUp()
        self.search_url = reverse("search")

    def test_search_no_result(self):
        response = self.client.get(
            self.search_url + "?q=somestrangesearchstringwhichhasnoresults"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ihre Suchanfrage ergab keine Treffer.")

    def test_search_with_results(self):
        # Make sure index was updated before running tests.
        time.sleep(15)
        response = self.client.get(self.search_url + "?q=TeachingModule")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TeachingModule Ut a")
