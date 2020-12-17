from django.urls import reverse
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import nested_form_data, rich_text, streamfield

from dll.cms.models import SimplePage, BlockPage
from dll.user.models import DllUser


class DllCmsTests(WagtailPageTests):
    def setUp(self):
        self.parent = Page.objects.first()
        user = {
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Doe",
            "email": "alice@blueshoe.de",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
        }
        self.admin = DllUser.objects.create(**user)
        self.admin.set_password("password")
        self.admin.save()
        self.client.login(username="alice@blueshoe.de", password="password")

    def test_can_create_simple_page(self):
        self.assertCanCreate(
            self.parent,
            SimplePage,
            nested_form_data(
                {
                    "title": "Some new title",
                    "body": rich_text("<p>Some sub page</p>"),
                    "extra_source": "<style>body {background-color: red;}</style>",
                }
            ),
        )

    def test_can_create_block_page(self):
        self.assertCanCreate(
            self.parent,
            BlockPage,
            nested_form_data(
                {
                    "title": "Some new title",
                    "extra_source": "<style>body {background-color: red;}</style>",
                    "body": streamfield([]),
                }
            ),
        )

    def test_can_create_frontpage(self):
        pass

    def test_single_element_block(self):
        # Correct data test
        self.assertCanCreate(
            self.parent,
            BlockPage,
            nested_form_data(
                {
                    "title": "Some new title1",
                    "extra_source": "<style>body {background-color: red;}</style>",
                    "body": streamfield(
                        [
                            (
                                "single_element_block",
                                {
                                    "headline": "Some headline",
                                    "text": rich_text("<p>Test</p>"),
                                    "text_alignment": "left",
                                    "advanced_options": {"background_color": "000000"},
                                },
                            )
                        ]
                    ),
                }
            ),
        )

    def test_too_long_hex_value(self):
        response = self._post_page_creation_data(
            self.parent,
            BlockPage,
            nested_form_data(
                {
                    "title": "Some new title2",
                    "extra_source": "<style>body {background-color: red;}</style>",
                    "body": streamfield(
                        [
                            (
                                "single_element_block",
                                {
                                    "headline": "Some headline",
                                    "text": rich_text("<p>Test</p>"),
                                    "text_alignment": "left",
                                    "advanced_options": {"background_color": "0000000"},
                                },
                            )
                        ]
                    ),
                }
            ),
        )

        form = response.context["form"]
        self.assertIn("body", form.errors)

    def test_alt_text_without_image(self):
        response = self._post_page_creation_data(
            self.parent,
            BlockPage,
            nested_form_data(
                {
                    "title": "Some new title2",
                    "extra_source": "<style>body {background-color: red;}</style>",
                    "body": streamfield(
                        [
                            (
                                "single_element_block",
                                {
                                    "headline": "Some headline",
                                    "text": rich_text("<p>Test</p>"),
                                    "text_alignment": "left",
                                    "alt_text": "Something",
                                },
                            )
                        ]
                    ),
                }
            ),
        )
        self.assertIn("den Alt Text hinterlegt", str(response.content))

    def test_link_text_without_link(self):
        response = self._post_page_creation_data(
            self.parent,
            BlockPage,
            nested_form_data(
                {
                    "title": "Some new title2",
                    "extra_source": "<style>body {background-color: red;}</style>",
                    "body": streamfield(
                        [
                            (
                                "multi_element_block",
                                {
                                    "headline": "Some headline",
                                    "text": rich_text("<p>Test</p>"),
                                    "text_alignment": "left",
                                    "alt_text": "Something",
                                    "elements": streamfield(
                                        [
                                            (
                                                "two_column_block",
                                                {
                                                    "content": streamfield(
                                                        [
                                                            (
                                                                "dll_element_block",
                                                                {
                                                                    "link_text": "something"
                                                                },
                                                            ),
                                                            ("dll_element_block", {}),
                                                        ]
                                                    )
                                                },
                                            )
                                        ]
                                    ),
                                },
                            )
                        ]
                    ),
                }
            ),
        )

        self.assertIn("Link Text muss mit URL verwendet werden.", str(response.content))

    def _post_page_creation_data(self, parent, child_model, data):
        add_url = reverse(
            "wagtailadmin_pages:add",
            args=[child_model._meta.app_label, child_model._meta.model_name, parent.pk],
        )
        return self.client.post(add_url, data, follow=True)
