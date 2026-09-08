from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
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
    discord_url = models.URLField("Discord", blank=True)
    youtube_url = models.URLField("YouTube", blank=True)
    twitch_url = models.URLField("Twitch", blank=True)

    # Rendered as icons in the footer, in this order, for whichever URLs are set.
    SOCIAL_NETWORKS = (
        ("discord", "discord_url"),
        ("youtube", "youtube_url"),
        ("twitch", "twitch_url"),
    )

    panels = [
        FieldPanel("text"),
        FieldPanel("links"),
        FieldPanel("copyright"),
        MultiFieldPanel(
            [FieldPanel(field) for _, field in SOCIAL_NETWORKS],
            heading="Social links",
            help_text="Icons appear in the footer for each link that is filled in.",
        ),
    ]

    def social_links(self):
        return [
            {"network": network, "url": getattr(self, field)}
            for network, field in self.SOCIAL_NETWORKS
            if getattr(self, field)
        ]

    class Meta:
        verbose_name = "Footer"
