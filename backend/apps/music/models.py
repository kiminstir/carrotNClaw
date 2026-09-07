from django.core.validators import MaxValueValidator
from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.fields import StreamField

from apps.pages.images import absolute_media_url


class TrackBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        required=False, max_length=120, help_text="Defaults to the file title."
    )
    file = DocumentChooserBlock(label="Audio file (mp3/ogg/m4a)")

    class Meta:
        icon = "media"
        label = "Track"

    def get_api_representation(self, value, context=None):
        doc = value.get("file") if value else None
        if doc is None:
            return None
        return {
            "id": doc.pk,
            "title": value.get("title") or doc.title,
            "src": absolute_media_url(doc.url),
        }


@register_setting(icon="media")
class MusicSettings(BaseGenericSetting):
    enabled = models.BooleanField(default=True, help_text="Show the music player on the site.")
    volume = models.PositiveSmallIntegerField(default=40, validators=[MaxValueValidator(100)])
    tracks = StreamField([("track", TrackBlock())], blank=True)

    panels = [FieldPanel("enabled"), FieldPanel("volume"), FieldPanel("tracks")]

    class Meta:
        verbose_name = "Music"
