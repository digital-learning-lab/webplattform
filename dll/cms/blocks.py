from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


class ImageVideoBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    video = EmbedBlock(required=False)

    def clean(self, value):
        result = super(ImageVideoBlock, self).clean(value)
        errors = {}
        if value["image"] and value["video"]:
            errors["image"] = ErrorList(["Nur Bild oder Video erlaubt, nicht beides."])
        if not value["image"] and not value["video"]:
            errors["image"] = ErrorList(
                ["Bitte geben Sie ein Bild oder eine Video-Url an."]
            )
        if errors:
            raise ValidationError(
                "ValidationError in SingleElementBlock", params=errors
            )
        return result


class SingleElementBlock(ImageVideoBlock):

    headline = blocks.CharBlock()
    text = blocks.RichTextBlock(
        features=[
            "bold",
            "italic",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ol",
            "ul",
            "hr",
            "extended_link",
            "document-link",
            "image",
            "embed",
        ]
    )
    background_color = blocks.ChoiceBlock(
        choices=(
            ("blue", "Blau"),
            ("white", "Weiß"),
        )
    )

    class Meta:
        template = "blocks/single_element_block.html"


class DllElementBlock(ImageVideoBlock):
    subline = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(
        required=False,
        features=[
            "bold",
            "italic",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ol",
            "ul",
            "hr",
            "extended_link",
            "document-link",
            "image",
            "embed",
        ],
    )
    link_text = blocks.CharBlock(required=False)
    url = blocks.URLBlock(required=False)

    def clean(self, value):
        result = super(DllElementBlock, self).clean(value)
        if bool(value["link_text"]) != bool(value["url"]):
            raise ValidationError(
                "ValidationError in DllElementBlock",
                params={
                    "link_text": ErrorList(["Link Text muss mit URL verwendet werden."])
                },
            )
        return result

    class Meta:
        template = "blocks/dll_element_block.html"
        icon = "wagtail-admin-layout"


class TwoColumnLayout(blocks.StructBlock):
    content = blocks.StreamBlock(
        [
            ("dll_element_block", DllElementBlock()),
        ],
        min_num=2,
        max_num=2,
    )

    class Meta:
        template = "blocks/two_column_block.html"
        icon = "wagtail-admin-columns-2"


class ThreeColumnLayout(blocks.StructBlock):
    content = blocks.StreamBlock(
        [
            ("dll_element_block", DllElementBlock()),
        ],
        min_num=3,
        max_num=3,
    )

    class Meta:
        template = "blocks/three_column_block.html"
        icon = "wagtail-admin-columns-3"


class IFrameBlock(blocks.StructBlock):
    url = blocks.URLBlock()
    height = blocks.IntegerBlock()

    class Meta:
        template = "blocks/iframe_block.html"


class MultiElementBlock(blocks.StructBlock):

    headline = blocks.CharBlock()
    text = blocks.RichTextBlock(
        features=[
            "bold",
            "italic",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ol",
            "ul",
            "hr",
            "extended_link",
            "document-link",
            "image",
            "embed",
        ]
    )
    background_color = blocks.ChoiceBlock(
        choices=(
            ("blue", "Blau"),
            ("white", "Weiß"),
        )
    )

    elements = blocks.StreamBlock(
        [
            ("two_column_block", TwoColumnLayout()),
            ("three_column_block", ThreeColumnLayout()),
            ("iframe_block", IFrameBlock()),
        ],
    )

    class Meta:
        template = "blocks/multi_element_block.html"


class SideBySideBlock(ImageVideoBlock):
    headline = blocks.CharBlock()
    sub_headline = blocks.CharBlock()
    text = blocks.RichTextBlock(
        features=[
            "bold",
            "italic",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ol",
            "ul",
            "hr",
            "extended_link",
            "document-link",
            "image",
            "embed",
        ]
    )
    layout = blocks.ChoiceBlock(
        choices=(
            ("image_left", "Bild links, Text rechts"),
            ("image_right", "Bild rechts, Text links"),
        )
    )
    background_color = blocks.ChoiceBlock(
        choices=(
            ("blue", "Blau"),
            ("white", "Weiß"),
        )
    )

    class Meta:
        template = "blocks/side_by_side.html"
