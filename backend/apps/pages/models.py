from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail_headless_preview.models import HeadlessMixin

from apps.pages.blocks import BodyStreamBlock


class FlexPage(HeadlessMixin, Page):
    """The single page type: any layout is built from blocks in `body`."""

    intro = models.CharField(
        max_length=255, blank=True, help_text="Short lead text under the title."
    )
    body = StreamField(BodyStreamBlock(), blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro"), FieldPanel("body")]
    api_fields = [APIField("intro"), APIField("body")]

    class Meta:
        verbose_name = "Page"
