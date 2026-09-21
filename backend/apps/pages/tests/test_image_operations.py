import pytest
from wagtail.images.models import Filter, Image
from wagtail.images.rect import Rect
from wagtail.images.tests.utils import get_test_image_file

from apps.pages.image_operations import focal_crop_rect

PORTRAIT = 3 / 4
SIZE = (1200, 800)


def crop(focal_point: Rect | None) -> tuple:
    # Rect.__eq__ would take over a comparison with approx(), so compare plain tuples.
    return tuple(focal_crop_rect(focal_point, SIZE, PORTRAIT))


def rect(*bounds: float):
    return pytest.approx(bounds)


def test_no_focal_point_keeps_the_largest_centred_box():
    assert crop(None) == rect(300, 0, 900, 800)


def test_focal_point_is_fully_contained_and_centred():
    # A 200x600 focal rect widens to 3:4 (450x600) around its own centre.
    assert crop(Rect(500, 100, 700, 700)) == rect(375, 100, 825, 700)


def test_wide_focal_point_expands_downwards_around_its_centre():
    # 400x100 focal rect at the top: crop 400x533 centred on it, then pushed inside the image.
    assert crop(Rect(400, 0, 800, 100)) == rect(400, 0, 800, 533.3333)


def test_focal_point_near_an_edge_is_shifted_inside_not_shrunk():
    # 50x100 at the right edge: the 3:4 box (75x100) cannot be centred, so it slides left.
    assert crop(Rect(1150, 300, 1200, 400)) == rect(1125, 300, 1200, 400)


def test_focal_point_larger_than_the_image_allows_falls_back_to_the_largest_box():
    assert crop(Rect(0, 0, 1200, 800)) == rect(300, 0, 900, 800)


def test_degenerate_focal_point_still_yields_a_croppable_rect():
    r = focal_crop_rect(Rect(600, 400, 600, 400), SIZE, PORTRAIT)
    assert r.width >= 1 and r.height >= 1


@pytest.fixture
def image(db):
    return Image.objects.create(title="Tavern hall", file=get_test_image_file(size=SIZE))


def test_focalfill_transform_crops_then_scales_down(image):
    transform = Filter("focalfill-480x640").get_transform(image)
    assert transform.get_rect().as_tuple() == pytest.approx((300, 0, 900, 800))
    assert transform.size == (480, 640)


def test_focalfill_never_upscales_a_small_focal_point(image):
    image.set_focal_point(Rect(0, 0, 240, 160))
    image.save()
    transform = Filter("focalfill-480x640").get_transform(image)
    assert transform.get_rect().as_tuple() == (0, 0, 240, 320)
    assert transform.size == (240, 320)


def test_focalfill_frames_the_same_region_at_every_size(image):
    image.set_focal_point(Rect(500, 100, 700, 700))
    image.save()
    rects = {
        Filter(f"focalfill-{w}x{round(w * 4 / 3)}").get_transform(image).get_rect().as_tuple()
        for w in (240, 480, 960)
    }
    assert rects == {(375, 100, 825, 700)}


def test_focalfill_rendition_has_the_requested_size(image):
    rendition = image.get_rendition("focalfill-480x640|format-webp")
    assert (rendition.width, rendition.height) == (480, 640)
    assert rendition.url.endswith(".webp")


def test_focalfill_renditions_vary_with_the_focal_point(image):
    before = Filter("focalfill-480x640").get_cache_key(image)
    image.set_focal_point(Rect(0, 0, 240, 160))
    image.save()
    assert Filter("focalfill-480x640").get_cache_key(image) != before
