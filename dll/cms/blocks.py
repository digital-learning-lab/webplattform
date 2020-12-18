from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _
from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


class ImageVideoBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)

    alt_text = blocks.CharBlock(
        label=_("Alt Text"),
        required=False,
        help_text=_("Überschreibt den Standard Alt Text des Bildes."),
    )

    video = EmbedBlock(required=False)

    def clean(self, value):
        result = super(ImageVideoBlock, self).clean(value)
        errors = {}
        if value["alt_text"] and not value["image"]:
            errors["alt_text"] = ErrorList(
                ["Es ist kein Bild für den Alt Text hinterlegt."]
            )
        if errors:
            raise ValidationError(
                "ValidationError in SingleElementBlock", params=errors
            )
        return self._to_struct_value(result)


class SingleElementBlock(ImageVideoBlock):
    headline = blocks.CharBlock(label=_("Überschrift"), required=False)
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
        ],
        required=False,
    )

    text_alignment = blocks.ChoiceBlock(
        label=_("Text Ausrichtung"),
        choices=(
            ("left", _("Links")),
            ("center", _("Zentriert")),
            ("right", _("Rechts")),
        ),
        required=False,
        default="center",
    )

    advanced_options = blocks.StructBlock(
        local_blocks=(
            (
                "background_color",
                blocks.CharBlock(
                    label=_("Hintergrund Farbe"),
                    help_text=_("Hex Wert ohne #"),
                    max_length=6,
                    required=False,
                ),
            ),
        ),
        label=_("Erweiterte Einstellungen"),
        form_classname="collapse collapse--custom",
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

    text_alignment = blocks.ChoiceBlock(
        label=_("Text Ausrichtung"),
        choices=(
            ("left", _("Links")),
            ("center", _("Zentriert")),
            ("right", _("Rechts")),
        ),
        required=False,
        default="center",
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


def generate_default_blocks(count):
    return [
        ("dll_element_block", DllElementBlock().to_python({})) for i in range(count)
    ]


class TwoColumnLayout(blocks.StructBlock):
    content = blocks.StreamBlock(
        [
            ("dll_element_block", DllElementBlock()),
        ],
        min_num=2,
        max_num=2,
        default=lazy(lambda: generate_default_blocks(2), list)(),
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
        default=lazy(lambda: generate_default_blocks(3), list)(),
    )

    class Meta:
        template = "blocks/three_column_block.html"
        icon = "wagtail-admin-columns-3"


class IFrameBlock(blocks.StructBlock):
    url = blocks.URLBlock()
    height = blocks.IntegerBlock(required=False)

    class Meta:
        template = "blocks/iframe_block.html"


class MultiElementBlock(blocks.StructBlock):
    headline = blocks.CharBlock(label=_("Überschrift"), required=False)
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
        ],
        required=False,
    )

    text_alignment = blocks.ChoiceBlock(
        label=_("Text Ausrichtung"),
        choices=(
            ("left", _("Links")),
            ("center", _("Zentriert")),
            ("right", _("Rechts")),
        ),
        required=False,
        default="center",
    )

    advanced_options = blocks.StructBlock(
        local_blocks=(
            (
                "background_color",
                blocks.CharBlock(
                    label=_("Hintergrund Farbe"),
                    help_text=_("Hex Wert ohne #"),
                    max_length=6,
                    required=False,
                ),
            ),
        ),
        label=_("Erweiterte Einstellungen"),
        form_classname="collapse collapse--custom",
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
    headline = blocks.CharBlock(label=_("Überschrift"), required=False)
    sub_headline = blocks.CharBlock(label=_("Sub-Überschrift"), required=False)
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

    text_alignment = blocks.ChoiceBlock(
        label=_("Text Ausrichtung"),
        choices=(
            ("left", _("Links")),
            ("center", _("Zentriert")),
            ("right", _("Rechts")),
        ),
        required=False,
        default="left",
    )

    layout = blocks.ChoiceBlock(
        choices=(
            ("image_left", "Bild links, Text rechts"),
            ("image_right", "Bild rechts, Text links"),
        )
    )

    advanced_options = blocks.StructBlock(
        local_blocks=(
            (
                "background_color",
                blocks.CharBlock(
                    label=_("Hintergrund Farbe"),
                    help_text=_("Hex Wert ohne #"),
                    max_length=6,
                    required=False,
                ),
            ),
        ),
        label=_("Erweiterte Einstellungen"),
        form_classname="collapse collapse--custom",
    )

    class Meta:
        template = "blocks/side_by_side.html"
