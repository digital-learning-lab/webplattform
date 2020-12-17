from draftjs_exporter.dom import DOM
from wagtail.core import hooks
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import rich_text, nested_form_data

from dll.cms.models import SimplePage
from dll.cms.wagtail_hooks import extended_link_entity, register_extended_link_feature
from dll.user.models import DllUser


class DllCmsTests(WagtailPageTests):
    def setUp(self) -> None:
        DOM.use("draftjs_exporter.engines.string.DOMString")
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

    def test_link_entity_extension_external(self):
        dom_element = extended_link_entity(
            {"url": "http://www.tuhh.de", "children": "some text"}
        )
        self.assertTrue(hasattr(dom_element, "attr"))
        self.assertIn("linktype", dom_element.attr)
        self.assertEqual(dom_element.attr["linktype"], "external")

    def test_link_entity_extension_wagtail_page(self):
        dom_element = extended_link_entity({"id": 1, "children": "some text"})
        self.assertTrue(hasattr(dom_element, "attr"))
        self.assertIn("linktype", dom_element.attr)
        self.assertEqual(dom_element.attr["linktype"], "page")

    @hooks.register_temporarily(
        "register_rich_text_features", register_extended_link_feature
    )
    # TODO test does not actually cover hook code yet
    def test_extended_link_hook_registration(self):
        self.assertCanCreate(
            self.parent,
            SimplePage,
            nested_form_data(
                {
                    "title": "Some new title",
                    "body": rich_text("<a href='http://google.com'>Some Link</a>"),
                }
            ),
        )
