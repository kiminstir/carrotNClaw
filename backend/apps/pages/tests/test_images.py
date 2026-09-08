from unittest.mock import patch

import pytest
from wagtail.images.models import Image, SourceImageIOError
from wagtail.images.tests.utils import get_test_image_file

from apps.pages.blocks import ApiImageBlock
from apps.pages.images import absolute_media_url, serialize_image


@pytest.fixture
def image(db):
    return Image.objects.create(title="Tavern hall", file=get_test_image_file(size=(1200, 800)))


def test_absolute_media_url_uses_api_base():
    assert absolute_media_url("/media/x.webp") == "http://testserver/media/x.webp"


def test_serialize_image_returns_srcset_and_dimensions(image):
    data = serialize_image(image, alt="A cozy hall")
    assert data["id"] == image.pk
    assert data["alt"] == "A cozy hall"
    assert data["src"].startswith("http://testserver/media/")
    assert data["src"].endswith(".webp")
    assert [s["width"] for s in data["srcset"]] == [480, 960, 1200]
    assert data["width"] == 1200 and data["height"] == 800


def test_serialize_image_none():
    assert serialize_image(None) is None


def test_serialize_image_missing_source_file_returns_none(image):
    with patch.object(Image, "get_renditions", side_effect=SourceImageIOError("missing")):
        assert serialize_image(image, alt="A cozy hall") is None


def test_serialize_image_narrow_source_has_no_duplicate_widths(db):
    narrow = Image.objects.create(title="Narrow", file=get_test_image_file(size=(700, 500)))
    data = serialize_image(narrow, alt="narrow")
    assert [s["width"] for s in data["srcset"]] == [480, 700]
    assert data["width"] == 700 and data["height"] == 500


def test_api_image_block_uses_contextual_alt(image):
    block = ApiImageBlock()
    value = block.to_python({"image": image.pk, "decorative": False, "alt_text": "Roaring fire"})
    data = block.get_api_representation(value)
    assert data["alt"] == "Roaring fire"
    assert len(data["srcset"]) == 3


def test_api_image_block_decorative_has_empty_alt(image):
    block = ApiImageBlock()
    value = block.to_python({"image": image.pk, "decorative": True, "alt_text": ""})
    assert block.get_api_representation(value)["alt"] == ""


def test_api_image_block_none():
    assert ApiImageBlock(required=False).get_api_representation(None) is None
