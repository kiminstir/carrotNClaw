from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.embeds.embeds import get_embed
from wagtail.embeds.exceptions import EmbedException
from wagtail.images.blocks import ImageBlock

from apps.pages.images import serialize_image

RICH_TEXT_FEATURES = [
    "h2",
    "h3",
    "bold",
    "italic",
    "link",
    "document-link",
    "ol",
    "ul",
    "hr",
    "blockquote",
    "image",
]


class ApiImageBlock(ImageBlock):
    """Image + alt text whose API output is ready for an <img srcset>."""

    def get_api_representation(self, value, context=None):
        if value is None:
            return None
        if getattr(value, "decorative", False):
            alt = ""
        else:
            alt = getattr(value, "contextual_alt_text", None) or value.default_alt_text
        return serialize_image(value, alt=alt)


class LinkBlock(blocks.StructBlock):
    label = blocks.CharBlock(required=False, max_length=60)
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(required=False, label="External URL")

    class Meta:
        icon = "link"
        label = "Link"

    def get_api_representation(self, value, context=None):
        if value is None or not value.get("label"):
            return None
        page = value.get("page")
        if page is not None:
            return {"label": value["label"], "href": page.url or "/", "external": False}
        return {"label": value["label"], "href": value.get("url") or "#", "external": True}


class VideoEmbedBlock(EmbedBlock):
    class Meta:
        icon = "media"
        label = "Video (YouTube / Vimeo URL)"

    def get_api_representation(self, value, context=None):
        if not value:
            return None
        data = {"url": value.url, "html": None, "provider": None, "title": None, "thumbnail": None}
        try:
            embed = get_embed(value.url)
        except EmbedException:
            return data
        data.update(
            html=embed.html,
            provider=embed.provider_name,
            title=embed.title,
            thumbnail=embed.thumbnail_url,
        )
        return data


class CollapseItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=120)
    content = blocks.RichTextBlock(features=RICH_TEXT_FEATURES)


class CollapseBlock(blocks.StructBlock):
    items = blocks.ListBlock(CollapseItemBlock())
    allow_multiple_open = blocks.BooleanBlock(required=False, default=False)

    class Meta:
        icon = "list-ul"
        label = "Collapse / accordion"


class ImageSliderBlock(blocks.StructBlock):
    images = blocks.ListBlock(ApiImageBlock())
    autoplay = blocks.BooleanBlock(required=False, default=True)

    class Meta:
        icon = "image"
        label = "Image slider"


class HeroBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=120)
    subheading = blocks.CharBlock(required=False, max_length=240)
    background = ApiImageBlock(required=False)
    cta = LinkBlock(required=False, label="Call to action")

    class Meta:
        icon = "pick"
        label = "Hero"


class CardBlock(blocks.StructBlock):
    image = ApiImageBlock(required=False)
    title = blocks.CharBlock(max_length=120)
    subtitle = blocks.CharBlock(required=False, max_length=120)
    text = blocks.TextBlock(required=False)
    price = blocks.CharBlock(required=False, max_length=40)
    link = LinkBlock(required=False)


class CardGridBlock(blocks.StructBlock):
    columns = blocks.ChoiceBlock(choices=[("2", "2"), ("3", "3"), ("4", "4")], default="3")
    cards = blocks.ListBlock(CardBlock())

    class Meta:
        icon = "table"
        label = "Card grid (menu items, staff, …)"


class ColumnStreamBlock(blocks.StreamBlock):
    rich_text = blocks.RichTextBlock(features=RICH_TEXT_FEATURES)
    image = ApiImageBlock()
    collapse = CollapseBlock()
    video = VideoEmbedBlock()


class ColumnsBlock(blocks.StructBlock):
    layout = blocks.ChoiceBlock(choices=[("2", "Two columns"), ("3", "Three columns")], default="2")
    columns = blocks.ListBlock(ColumnStreamBlock())

    class Meta:
        icon = "grip"
        label = "Columns"


class BodyStreamBlock(blocks.StreamBlock):
    hero = HeroBlock()
    rich_text = blocks.RichTextBlock(features=RICH_TEXT_FEATURES)
    image = ApiImageBlock()
    image_slider = ImageSliderBlock()
    collapse = CollapseBlock()
    video = VideoEmbedBlock()
    columns = ColumnsBlock()
    card_grid = CardGridBlock()
