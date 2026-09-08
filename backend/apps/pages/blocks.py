from django.core.exceptions import ValidationError
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


# Keys are consumed by frontend/src/lib/blocks/richTextStyles.ts; keep both in sync.
TEXT_COLOR_CHOICES = [
    ("default", "Default"),
    ("ink", "Light"),
    ("accent", "Gold"),
    ("sage", "Sage"),
]
TEXT_SIZE_CHOICES = [("sm", "Small"), ("md", "Normal"), ("lg", "Large")]
LINE_HEIGHT_CHOICES = [("tight", "Tight"), ("normal", "Normal"), ("relaxed", "Relaxed")]
TEXT_ALIGN_CHOICES = [("left", "Left"), ("center", "Center"), ("right", "Right")]
VERTICAL_ALIGN_CHOICES = [("top", "Top"), ("center", "Center"), ("bottom", "Bottom")]


class StyledRichTextBlock(blocks.StructBlock):
    """Rich text plus block-wide typography settings.

    Defaults reproduce the look a plain RichTextBlock had before these
    settings existed, so content migrated from that shape renders unchanged.
    """

    text = blocks.RichTextBlock(features=RICH_TEXT_FEATURES)
    color = blocks.ChoiceBlock(choices=TEXT_COLOR_CHOICES, default="default", label="Text color")
    size = blocks.ChoiceBlock(choices=TEXT_SIZE_CHOICES, default="md", label="Font size")
    line_height = blocks.ChoiceBlock(
        choices=LINE_HEIGHT_CHOICES, default="normal", label="Line spacing"
    )
    align = blocks.ChoiceBlock(choices=TEXT_ALIGN_CHOICES, default="left", label="Alignment")
    vertical_align = blocks.ChoiceBlock(
        choices=VERTICAL_ALIGN_CHOICES,
        default="top",
        label="Vertical alignment",
        help_text="How the text lines up with an image aligned left or right.",
    )

    class Meta:
        icon = "pilcrow"
        label = "Rich text"


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


# The pop-up shows the card's own image slot; inline images would duplicate it.
CARD_DESCRIPTION_FEATURES = [f for f in RICH_TEXT_FEATURES if f != "image"]


class CardBlock(blocks.StructBlock):
    image = ApiImageBlock(
        required=False,
        help_text="In the Photo style the image is cropped to the card; set a focal point on "
        "the image to choose which part stays in view.",
    )
    title = blocks.CharBlock(max_length=120)
    subtitle = blocks.CharBlock(required=False, max_length=120)
    text = blocks.TextBlock(required=False)
    price = blocks.CharBlock(required=False, max_length=40)
    link = LinkBlock(required=False)
    description = blocks.RichTextBlock(
        required=False,
        features=CARD_DESCRIPTION_FEATURES,
        help_text="When filled in, the card opens a pop-up with this text and the image.",
    )
    detail_image = ApiImageBlock(
        required=False,
        label="Pop-up image",
        help_text="Shown in the pop-up instead of the card image. Only visible when a "
        "description is set.",
    )


# Keys are consumed by frontend/src/lib/blocks/CardGrid.svelte; keep both in sync.
CARD_STYLE_CHOICES = [
    ("artwork", "Artwork above text (menu items)"),
    ("portrait", "Photo filling the card, text over the bottom (staff)"),
]


class CardGridBlock(blocks.StructBlock):
    columns = blocks.ChoiceBlock(choices=[("2", "2"), ("3", "3"), ("4", "4")], default="3")
    style = blocks.ChoiceBlock(
        choices=CARD_STYLE_CHOICES,
        default="artwork",
        help_text="Artwork shows cut-out images whole; Photo crops the image to a portrait "
        "card around its focal point.",
    )
    cards = blocks.ListBlock(CardBlock())

    class Meta:
        icon = "table"
        label = "Card grid (menu items, staff, …)"


class ColumnStreamBlock(blocks.StreamBlock):
    rich_text = StyledRichTextBlock()
    image = ApiImageBlock()
    collapse = CollapseBlock()
    video = VideoEmbedBlock()


class ColumnsBlock(blocks.StructBlock):
    layout = blocks.ChoiceBlock(choices=[("2", "Two columns"), ("3", "Three columns")], default="2")
    columns = blocks.ListBlock(
        ColumnStreamBlock(),
        min_num=2,
        max_num=3,
        help_text="Add one list item per column; put the column's content inside that item.",
    )

    class Meta:
        icon = "grip"
        label = "Columns"

    def clean(self, value):
        cleaned = super().clean(value)
        layout, count = cleaned["layout"], len(cleaned["columns"])
        if str(count) != layout:
            raise blocks.StructBlockValidationError(
                block_errors={
                    "columns": ValidationError(
                        f"Layout is set to {layout} columns but {count} column(s) were added. "
                        "Each column is a separate list item."
                    )
                }
            )
        return cleaned


class BodyStreamBlock(blocks.StreamBlock):
    hero = HeroBlock()
    rich_text = StyledRichTextBlock()
    image = ApiImageBlock()
    image_slider = ImageSliderBlock()
    collapse = CollapseBlock()
    video = VideoEmbedBlock()
    columns = ColumnsBlock()
    card_grid = CardGridBlock()
