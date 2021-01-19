import time

from django.urls import reverse
from django.core import management

from dll.content.tests.test_content_views import BaseTestCase


class SearchTestCase(BaseTestCase):
    def setUp(self):
        super(SearchTestCase, self).setUp()
        self.search_url = reverse("search")
        management.call_command("update_index")

    def test_search_no_result(self):
        # Make sure index was updated before running tests.
        time.sleep(10)
        response = self.client.get(
            self.search_url + "?somestrangesearchstringwhichhasnoresults"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ihre Suchanfrage ergab keine Treffer.")

    def test_search_with_results(self):
        # Make sure index was updated before running tests.
        time.sleep(10)
        response = self.client.get(self.search_url + "?TeachingModule")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TeachingModule Ut a")
