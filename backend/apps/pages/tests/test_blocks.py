from types import SimpleNamespace
from unittest.mock import patch

import pytest
from wagtail.embeds.exceptions import EmbedNotFoundException
from wagtail.models import Page

from apps.pages.blocks import (
    BodyStreamBlock,
    CollapseBlock,
    LinkBlock,
    VideoEmbedBlock,
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
