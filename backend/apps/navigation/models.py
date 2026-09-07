from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.fields import RichTextField, StreamField

from apps.pages.blocks import LinkBlock


@register_setting(icon="site")
class HeaderSettings(BaseGenericSetting):
    logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    site_title = models.CharField(max_length=80, default="Carrot&Claw")
    menu = StreamField([("link", LinkBlock())], blank=True)

    panels = [FieldPanel("logo"), FieldPanel("site_title"), FieldPanel("menu")]

    class Meta:
        verbose_name = "Header"


@register_setting(icon="link")
class FooterSettings(BaseGenericSetting):
    text = RichTextField(blank=True, features=["bold", "italic", "link"])
    links = StreamField([("link", LinkBlock())], blank=True)
    copyright = models.CharField(max_length=160, blank=True)

    panels = [FieldPanel("text"), FieldPanel("links"), FieldPanel("copyright")]

    class Meta:
        verbose_name = "Footer"
