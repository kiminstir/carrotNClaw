from urllib.parse import urljoin

from django.conf import settings
from wagtail.images.models import SourceImageIOError

from apps.pages.image_operations import focal_crop_rect

# 2560 covers the image lightbox, which shows images at full viewport width on wide and
# high-DPI screens; smaller steps serve the inline layouts (see Picture.svelte `sizes`).
SRCSET_WIDTHS = (480, 960, 1600, 2560)

# Shape (width, height) of the portrait crop; the frontend's Photo card and its pop-up figure
# are 3:4 boxes (app.css `.card-portrait`, CardDialog.svelte).
PORTRAIT_ASPECT = (3, 4)


def absolute_media_url(path: str) -> str:
    return urljoin(settings.WAGTAILAPI_BASE_URL, path)


def serialize_image(
    image, *, alt: str | None = None, widths=SRCSET_WIDTHS, portrait: bool = False
) -> dict | None:
    """Renditions for an <img srcset>; with ``portrait`` also the focal point crop.

    ``portrait`` is the same image cropped to ``PORTRAIT_ASPECT`` around the editor-set
    focal point (see ``focal_crop_rect``): the whole focal rectangle, centred, so layouts
    that fill a portrait box show exactly what the editor marked instead of nudging a
    ``object-fit: cover`` crop with ``object-position``.
    """
    if image is None:
        return None
    try:
        data = _rendition_set(image, [_width_spec(w) for w in _capped(widths, image.width)])
        if portrait:
            data["portrait"] = _portrait_rendition_set(image, widths)
    except SourceImageIOError:
        return None
    return {
        "id": image.pk,
        "alt": alt if alt is not None else image.default_alt_text,
        **data,
    }


def _width_spec(width: int) -> str:
    return f"width-{width}|preserve-svg|format-webp"


def _portrait_rendition_set(image, widths) -> dict:
    aspect = PORTRAIT_ASPECT[0] / PORTRAIT_ASPECT[1]
    crop = focal_crop_rect(image.get_focal_point(), (image.width, image.height), aspect)
    # `preserve-svg` would strip the custom operation, so SVG sources keep their format
    # explicitly instead; everything else is converted like the plain renditions.
    output = "" if image.is_svg() else "|format-webp"
    specs = [
        f"focalfill-{w}x{round(w / aspect)}{output}" for w in _capped(widths, crop.round().width)
    ]
    return _rendition_set(image, specs)


def _capped(widths, limit: int) -> list[int]:
    return sorted({min(w, limit) for w in widths})


def _rendition_set(image, specs: list[str]) -> dict:
    # get_renditions() normalizes each spec's key (e.g. dropping the no-op
    # `preserve-svg` filter for raster sources), but guarantees the returned
    # dict's insertion order matches the order `specs` was passed in.
    ordered = list(image.get_renditions(*specs).values())
    largest = ordered[-1]
    return {
        "src": absolute_media_url(largest.url),
        "width": largest.width,
        "height": largest.height,
        "srcset": [{"url": absolute_media_url(r.url), "width": r.width} for r in ordered],
    }
