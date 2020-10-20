import logging
from urllib.parse import urlparse

from django.templatetags.static import static
from django.utils.html import format_html

from wagtail.core.rich_text import LinkHandler
from draftjs_exporter.dom import DOM
from wagtail.core import hooks
import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    ExternalLinkElementHandler,
    PageLinkElementHandler,
)
from dll.content.models import Content

logger = logging.getLogger("dll.cms")


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">', static("css/wagtail_admin.css")
    )


def extended_link_entity(props):
    """
    Parse external links. When it is a link to a Content instance, adapt db representation.
    :param props:
    :return:
    """
    id_ = props.get("id")
    link_props = {}

    if id_ is not None:
        link_props["linktype"] = "page"
        link_props["id"] = id_
    else:
        # This is is most likely an external url.
        url = props.get("url")
        link_props["linktype"] = "external"
        # We need to find out if it links to an internal page (Content instance).
        if "digitallearninglab.de" in url:
            link_props["linktype"] = "content"
            url_obj = urlparse(url)
            slug = url_obj.path.split("/")[-1]
            try:
                id_ = Content.objects.published().get(slug=slug).get_draft().id
                link_props["data-content"] = id_
            except Content.DoesNotExist:
                # If there is no public Content instance with this slug - just link to the url.
                link_props["linktype"] = "external"
                link_props["href"] = props.get("url")
        else:
            link_props["href"] = props.get("url")

    return DOM.create_element("a", link_props, props["children"])


class ContentLinkHandler(LinkHandler):
    """Converts content link types into corresponding url."""

    identifier = "content"

    @staticmethod
    def get_model():
        return Content

    @classmethod
    def get_instance(cls, attrs) -> "Content":
        model = cls.get_model()
        return model.objects.filter(id=attrs["data-content"]).get().get_published()

    @classmethod
    def expand_db_attributes(cls, attrs):
        if attrs.get("data-content"):
            content = cls.get_instance(attrs).get_real_instance()
            return f"<a href='{content.get_absolute_url()}'>"
        return f"<a href='{attrs.get('href')}'>"


@hooks.register("register_rich_text_features")
def register_content_links(features):
    features.register_link_type(ContentLinkHandler)


@hooks.register("register_rich_text_features")
def register_extended_link_feature(features):
    features.default_features.append("extended_link")
    feature_name = "extended_link"
    type_ = "LINK"

    control = {
        "type": type_,
        "icon": "link",
        "description": "Extended link",
        # We want to enforce constraints on which links can be pasted into rich text.
        # Keep only the attributes Wagtail needs.
        "attributes": ["url", "id"],
        "whitelist": {
            # Keep pasted links with http/https protocol, and not-pasted links (href = undefined).
            "href": "^(http:|https:|undefined$)",
        },
    }

    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.EntityFeature(control)
    )

    features.register_converter_rule(
        "contentstate",
        feature_name,
        {
            "from_database_format": {
                "a[href]": ExternalLinkElementHandler("LINK"),
                'a[linktype="page"]': PageLinkElementHandler("LINK"),
            },
            "to_database_format": {"entity_decorators": {type_: extended_link_entity}},
        },
    )
