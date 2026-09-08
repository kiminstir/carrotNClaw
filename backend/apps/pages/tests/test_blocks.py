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
    LinkBlock,
    StyledRichTextBlock,
    VideoEmbedBlock,
)
from apps.pages.models import FlexPage
from apps.pages.stream_migrations import WrapRichTextOperation


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
            "detail_image": {"image": portrait.pk, "decorative": True, "alt_text": ""},
        }
    )
    data = block.get_api_representation(value)
    assert data["image"]["alt"] == "The cook"
    assert data["image"]["focal_point"] is None
    assert data["description"] == "<p>Long story</p>"
    assert data["detail_image"]["id"] == portrait.pk
    assert data["detail_image"]["alt"] == ""
    assert data["link"] is None


@pytest.mark.django_db
def test_card_block_optional_details_default_to_empty():
    block = CardBlock()
    value = block.to_python({"image": None, "title": "Cook"})
    data = block.get_api_representation(value)
    assert data["description"] == ""
    assert data["detail_image"] is None
    assert data["image"] is None


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
