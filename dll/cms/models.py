import random

from django.db.models import TextField
from django.utils.functional import cached_property
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.blocks import RichTextBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page

from dll.cms.blocks import (
    SingleElementBlock,
    MultiElementBlock,
    SideBySideBlock,
    IFrameBlock,
)
from dll.content.models import TeachingModule, Trend, Tool, Content


class DllPageMixin:
    @cached_property
    def breadcrumbs(self):
        """Returns ancestors - leaving out the root node."""
        return self.get_ancestors(inclusive=True)[1:]

    def get_context(self, request, *args, **kwargs):
        ctx = super(DllPageMixin, self).get_context(request, *args, **kwargs)
        ctx["breadcrumbs"] = self.breadcrumbs
        return ctx


class SimplePage(DllPageMixin, Page):
    body = RichTextField(
        blank=False,
        null=True,
        features=[
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "bold",
            "italic",
            "ol",
            "ul",
            "link",
            "document-link",
            "image",
            "embed",
        ],
    )

    extra_source = TextField(blank=True, null=True)

    settings_panels = Page.settings_panels + [
        FieldPanel(
            "extra_source",
        )
    ]

    content_panels = Page.content_panels + [
        FieldPanel("body", classname="full"),
    ]

    class Meta:
        verbose_name = "Simple Page"
        verbose_name_plural = "Simple Pages"


class BlockPage(DllPageMixin, Page):

    body = StreamField(
        [
            ("single_element_block", SingleElementBlock()),
            ("side_by_side_block", SideBySideBlock()),
            ("multi_element_block", MultiElementBlock()),
            ("richtext", RichTextBlock(template="blocks/richtext.html")),
        ],
        blank=True,
    )

    extra_source = TextField(blank=True)

    settings_panels = Page.settings_panels + [
        FieldPanel(
            "extra_source",
        )
    ]

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Block Page"
        verbose_name_plural = "Block Pages"


class Frontpage(DllPageMixin, Page):

    body = StreamField(
        [
            ("single_element_block", SingleElementBlock()),
            ("side_by_side_block", SideBySideBlock()),
            ("multi_element_block", MultiElementBlock()),
            ("richtext", RichTextBlock(template="blocks/richtext.html")),
        ],
        null=True,
    )

    extra_source = TextField(blank=True, null=True)

    settings_panels = Page.settings_panels + [
        FieldPanel(
            "extra_source",
        )
    ]

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
    ]

    def get_context(self, request, *args, **kwargs):
        ctx = super(Frontpage, self).get_context(request, *args, **kwargs)
        content_pks = []
        try:
            content_pks += random.choices(
                TeachingModule.objects.published().values_list("pk", flat=True), k=2
            )
            content_pks += random.choices(
                Trend.objects.published().values_list("pk", flat=True), k=2
            )
            content_pks += random.choices(
                Tool.objects.published().values_list("pk", flat=True), k=2
            )
        except IndexError:
            pass  # no content yet
        ctx["contents"] = Content.objects.filter(pk__in=content_pks)
        try:
            ctx["training_trend"] = Trend.objects.published().get(
                slug="fortbildung-digitallearninglab"
            )
        except Trend.DoesNotExist:
            pass
        return ctx

    class Meta:
        verbose_name = "Frontpage"
        verbose_name_plural = "Frontpage"
