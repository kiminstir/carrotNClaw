from types import SimpleNamespace
from unittest.mock import patch

import pytest
from wagtail.blocks import StructBlockValidationError
from wagtail.blocks.migrations.utils import apply_changes_to_raw_data
from wagtail.embeds.exceptions import EmbedNotFoundException
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page

from apps.pages.blocks import (
    BodyStreamBlock,
    CardBlock,
    CardGridBlock,
    CollapseBlock,
    ColumnsBlock,
    ColumnStreamBlock,
    ImageSliderBlock,
    LinkBlock,
    SliderImageBlock,
    StyledRichTextBlock,
    VideoEmbedBlock,
)
from apps.pages.models import FlexPage
from apps.pages.stream_migrations import (
    WrapCardDetailImageOperation,
    WrapRichTextOperation,
    WrapSliderImagesOperation,
)


@pytest.mark.django_db
def test_link_block_prefers_page_url():
    welcome = Page.objects.get(depth=2)
    block = LinkBlock()
    value = block.to_python({"label": "Home", "page": welcome.pk, "url": "https://ignored.example"})
    assert block.get_api_representation(value) == {"label": "Home", "href": "/", "external": False}


@pytest.mark.django_db
def test_link_block_external_url():
    block = LinkBlock()
    value = block.to_python({"label": "Wiki", "page": None, "url": "https://wiki.example/tavern"})
    data = block.get_api_representation(value)
    assert data == {"label": "Wiki", "href": "https://wiki.example/tavern", "external": True}


@pytest.mark.django_db
def test_link_block_without_label_is_none():
    block = LinkBlock()
    value = block.to_python({"label": "", "page": None, "url": ""})
    assert block.get_api_representation(value) is None


def test_video_block_expands_embed():
    block = VideoEmbedBlock()
    value = block.to_python("https://www.youtube.com/watch?v=abc123")
    fake = SimpleNamespace(
        html="<iframe></iframe>",
        provider_name="YouTube",
        title="Trailer",
        thumbnail_url="https://i/x.jpg",
    )
    with patch("apps.pages.blocks.get_embed", return_value=fake):
        data = block.get_api_representation(value)
    assert data == {
        "url": "https://www.youtube.com/watch?v=abc123",
        "html": "<iframe></iframe>",
        "provider": "YouTube",
        "title": "Trailer",
        "thumbnail": "https://i/x.jpg",
    }


def test_video_block_unknown_provider_degrades():
    block = VideoEmbedBlock()
    value = block.to_python("https://example.com/not-a-video")
    with patch("apps.pages.blocks.get_embed", side_effect=EmbedNotFoundException):
        data = block.get_api_representation(value)
    assert data["url"] == "https://example.com/not-a-video"
    assert data["html"] is None


@pytest.mark.django_db
def test_collapse_block_structure():
    block = CollapseBlock()
    value = block.to_python(
        {
            "items": [{"title": "Opening hours", "content": "<p>Dusk till dawn</p>"}],
            "allow_multiple_open": True,
        }
    )
    data = block.get_api_representation(value)
    assert data["allow_multiple_open"] is True
    assert data["items"][0]["title"] == "Opening hours"
    assert "Dusk till dawn" in data["items"][0]["content"]


def test_rich_text_block_api_representation():
    block = StyledRichTextBlock()
    value = block.to_python(
        {
            "text": "<p>Hi</p>",
            "color": "accent",
            "size": "lg",
            "line_height": "relaxed",
            "align": "center",
            "vertical_align": "bottom",
        }
    )
    assert block.get_api_representation(value) == {
        "text": "<p>Hi</p>",
        "color": "accent",
        "size": "lg",
        "line_height": "relaxed",
        "align": "center",
        "vertical_align": "bottom",
    }


def test_rich_text_block_defaults_keep_current_look():
    block = StyledRichTextBlock()
    value = block.to_python({"text": "<p>Hi</p>"})
    data = block.get_api_representation(value)
    assert (
        data["color"],
        data["size"],
        data["line_height"],
        data["align"],
        data["vertical_align"],
    ) == ("default", "md", "normal", "left", "top")


def test_rich_text_block_vertical_align_choices():
    choices = dict(StyledRichTextBlock().child_blocks["vertical_align"].field.choices)
    assert set(choices) == {"top", "center", "bottom"}


def test_rich_text_block_is_styled_in_body_and_columns():
    assert isinstance(BodyStreamBlock().child_blocks["rich_text"], StyledRichTextBlock)
    assert isinstance(ColumnStreamBlock().child_blocks["rich_text"], StyledRichTextBlock)


def test_wrap_rich_text_operation_wraps_top_level_and_column_blocks():
    raw = [
        {"type": "rich_text", "value": "<p>Top</p>", "id": "a"},
        {"type": "image", "value": None, "id": "b"},
        {
            "type": "columns",
            "value": {
                "layout": "2",
                "columns": [
                    {
                        "type": "item",
                        "value": [{"type": "rich_text", "value": "<p>Col</p>", "id": "c"}],
                        "id": "d",
                    }
                ],
            },
            "id": "e",
        },
    ]
    op = WrapRichTextOperation()
    out = apply_changes_to_raw_data(raw, "", op, FlexPage.body)
    out = apply_changes_to_raw_data(out, "columns.columns.item", op, FlexPage.body)
    assert out[0] == {"type": "rich_text", "value": {"text": "<p>Top</p>"}, "id": "a"}
    assert out[1] == raw[1]
    assert out[2]["value"]["columns"][0]["value"] == [
        {"type": "rich_text", "value": {"text": "<p>Col</p>"}, "id": "c"}
    ]


def test_wrap_rich_text_operation_leaves_already_wrapped_values_alone():
    raw = [{"type": "rich_text", "value": {"text": "<p>Done</p>", "color": "ink"}, "id": "a"}]
    assert apply_changes_to_raw_data(raw, "", WrapRichTextOperation(), FlexPage.body) == raw


def _columns_value(layout, column_count):
    block = ColumnsBlock()
    return block.to_python(
        {
            "layout": layout,
            "columns": [
                {
                    "type": "item",
                    "id": f"col-{i}",
                    "value": [
                        {"type": "rich_text", "value": {"text": "<p>x</p>"}, "id": f"rt-{i}"}
                    ],
                }
                for i in range(column_count)
            ],
        }
    )


def test_columns_block_rejects_column_count_not_matching_layout():
    block = ColumnsBlock()
    with pytest.raises(StructBlockValidationError) as exc:
        block.clean(_columns_value("3", 2))
    assert "columns" in exc.value.block_errors
    assert "3 columns but 2" in str(exc.value.block_errors["columns"])


def test_columns_block_rejects_single_column():
    # The mistake that puts everything into one column: one list item holding all the content.
    block = ColumnsBlock()
    with pytest.raises(StructBlockValidationError) as exc:
        block.clean(_columns_value("3", 1))
    assert "columns" in exc.value.block_errors


def test_columns_block_accepts_matching_column_count():
    block = ColumnsBlock()
    cleaned = block.clean(_columns_value("3", 3))
    assert len(cleaned["columns"]) == 3


@pytest.mark.django_db
def test_card_block_api_representation_with_details():
    portrait = Image.objects.create(title="Cook", file=get_test_image_file(size=(600, 800)))
    block = CardBlock()
    value = block.to_python(
        {
            "image": {"image": portrait.pk, "decorative": False, "alt_text": "The cook"},
            "title": "Cook",
            "subtitle": "Kitchen",
            "text": "Short blurb",
            "price": "",
            "link": {"label": "", "page": None, "url": ""},
            "description": "<p>Long story</p>",
            "detail_images": [
                {"image": portrait.pk, "decorative": True, "alt_text": ""},
                {"image": portrait.pk, "decorative": False, "alt_text": "At work"},
            ],
        }
    )
    data = block.get_api_representation(value)
    assert data["image"]["alt"] == "The cook"
    assert data["image"]["focal_point"] is None
    assert data["description"] == "<p>Long story</p>"
    assert [(i["id"], i["alt"]) for i in data["detail_images"]] == [
        (portrait.pk, ""),
        (portrait.pk, "At work"),
    ]
    assert data["link"] is None
    assert "detail_image" not in data


@pytest.mark.django_db
def test_card_block_drops_empty_pop_up_photo_slots():
    portrait = Image.objects.create(title="Cook", file=get_test_image_file(size=(600, 800)))
    block = CardBlock()
    value = block.to_python(
        {
            "image": None,
            "title": "Cook",
            "detail_images": [
                {"image": None, "decorative": True, "alt_text": ""},
                {"image": portrait.pk, "decorative": True, "alt_text": ""},
            ],
        }
    )
    data = block.get_api_representation(value)
    assert [i["id"] for i in data["detail_images"]] == [portrait.pk]


@pytest.mark.django_db
def test_card_block_optional_details_default_to_empty():
    block = CardBlock()
    value = block.to_python({"image": None, "title": "Cook"})
    data = block.get_api_representation(value)
    assert data["description"] == ""
    assert data["detail_images"] == []
    assert data["image"] is None


def test_card_block_limits_pop_up_photos():
    assert CardBlock().child_blocks["detail_images"].meta.max_num == 10


def test_card_grid_style_choices_and_default():
    block = CardGridBlock()
    choices = dict(block.child_blocks["style"].field.choices)
    assert set(choices) == {"artwork", "portrait"}
    # Grids saved before the style existed keep the artwork look.
    value = block.to_python({"columns": "3", "cards": []})
    assert block.get_api_representation(value)["style"] == "artwork"


def test_card_description_has_no_inline_images():
    # The pop-up shows the card's own image slot; inline images would duplicate it.
    features = CardBlock().child_blocks["description"].features
    assert "image" not in features
    assert {"bold", "italic", "link", "ul"} <= set(features)


def test_body_stream_block_has_all_block_types():
    assert set(BodyStreamBlock().child_blocks) == {
        "hero",
        "rich_text",
        "image",
        "image_slider",
        "collapse",
        "video",
        "columns",
        "card_grid",
    }


@pytest.mark.django_db
def test_slider_image_block_api_representation_carries_caption():
    photo = Image.objects.create(title="Bar", file=get_test_image_file(size=(800, 600)))
    block = SliderImageBlock()
    value = block.to_python(
        {
            "image": {"image": photo.pk, "decorative": False, "alt_text": "The bar"},
            "caption": "Where the evening starts",
        }
    )
    data = block.get_api_representation(value)
    assert data["image"]["id"] == photo.pk
    assert data["image"]["alt"] == "The bar"
    assert data["caption"] == "Where the evening starts"


@pytest.mark.django_db
def test_slider_image_block_without_image_is_none_and_caption_defaults_empty():
    block = SliderImageBlock()
    assert block.get_api_representation(block.to_python({"image": None, "caption": "x"})) is None
    photo = Image.objects.create(title="Bar", file=get_test_image_file(size=(800, 600)))
    value = block.to_python({"image": {"image": photo.pk, "decorative": True, "alt_text": ""}})
    assert block.get_api_representation(value)["caption"] == ""


@pytest.mark.django_db
def test_image_slider_block_lists_captioned_images():
    photo = Image.objects.create(title="Bar", file=get_test_image_file(size=(800, 600)))
    block = ImageSliderBlock()
    value = block.to_python(
        {
            "images": [
                {
                    "type": "item",
                    "id": "a",
                    "value": {
                        "image": {"image": photo.pk, "decorative": False, "alt_text": "Bar"},
                        "caption": "Cheers",
                    },
                }
            ],
            "autoplay": False,
        }
    )
    data = block.get_api_representation(value)
    assert data["autoplay"] is False
    assert [(i["image"]["alt"], i["caption"]) for i in data["images"]] == [("Bar", "Cheers")]


def test_wrap_slider_images_operation_wraps_old_image_items():
    raw = [
        {
            "type": "image_slider",
            "id": "s",
            "value": {
                "autoplay": True,
                "images": [
                    {
                        "type": "item",
                        "id": "a",
                        "value": {"image": 5, "alt_text": "Bar", "decorative": False},
                    },
                    {"type": "item", "id": "b", "value": 7},
                    {"type": "item", "id": "c", "value": None},
                ],
            },
        },
        {"type": "image", "value": None, "id": "x"},
    ]
    out = apply_changes_to_raw_data(raw, "", WrapSliderImagesOperation(), FlexPage.body)
    assert out[0]["value"]["autoplay"] is True
    assert out[0]["value"]["images"] == [
        {
            "type": "item",
            "id": "a",
            "value": {
                "image": {"image": 5, "alt_text": "Bar", "decorative": False},
                "caption": "",
            },
        },
        {"type": "item", "id": "b", "value": {"image": {"image": 7}, "caption": ""}},
        {"type": "item", "id": "c", "value": {"image": None, "caption": ""}},
    ]
    assert out[1] == raw[1]


def test_wrap_slider_images_operation_leaves_wrapped_items_alone():
    raw = [
        {
            "type": "image_slider",
            "id": "s",
            "value": {
                "autoplay": False,
                "images": [
                    {
                        "type": "item",
                        "id": "a",
                        "value": {"image": {"image": 5, "alt_text": "Bar"}, "caption": "Hi"},
                    }
                ],
            },
        }
    ]
    assert apply_changes_to_raw_data(raw, "", WrapSliderImagesOperation(), FlexPage.body) == raw


def test_wrap_card_detail_image_operation_turns_single_image_into_list():
    raw = [
        {
            "type": "card_grid",
            "id": "g",
            "value": {
                "columns": "3",
                "style": "portrait",
                "cards": [
                    {
                        "type": "item",
                        "id": "a",
                        "value": {
                            "title": "Cook",
                            "detail_image": {"image": 5, "alt_text": "", "decorative": True},
                        },
                    },
                    {"type": "item", "id": "b", "value": {"title": "Bard", "detail_image": None}},
                    # Bootstrap seeds cards without the ListBlock item wrapper.
                    {"title": "Maid", "detail_image": 7},
                ],
            },
        },
        {"type": "image", "value": None, "id": "x"},
    ]
    out = apply_changes_to_raw_data(raw, "", WrapCardDetailImageOperation(), FlexPage.body)
    cards = out[0]["value"]["cards"]
    assert out[0]["value"]["style"] == "portrait"
    assert cards[0]["id"] == "a"
    assert "detail_image" not in cards[0]["value"]
    (photo,) = cards[0]["value"]["detail_images"]
    assert photo["type"] == "item"
    assert photo["id"]
    assert photo["value"] == {"image": 5, "alt_text": "", "decorative": True}
    assert cards[1]["value"] == {"title": "Bard", "detail_images": []}
    assert cards[2]["title"] == "Maid"
    assert [p["value"] for p in cards[2]["detail_images"]] == [{"image": 7}]
    assert out[1] == raw[1]


def test_wrap_card_detail_image_operation_leaves_migrated_cards_alone():
    raw = [
        {
            "type": "card_grid",
            "id": "g",
            "value": {
                "columns": "2",
                "style": "artwork",
                "cards": [
                    {"type": "item", "id": "a", "value": {"title": "Stew", "detail_images": []}}
                ],
            },
        }
    ]
    assert apply_changes_to_raw_data(raw, "", WrapCardDetailImageOperation(), FlexPage.body) == raw
