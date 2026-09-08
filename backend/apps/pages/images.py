from urllib.parse import urljoin

from django.conf import settings
from wagtail.images.models import SourceImageIOError

# 2560 covers the image lightbox, which shows images at full viewport width on wide and
# high-DPI screens; smaller steps serve the inline layouts (see Picture.svelte `sizes`).
SRCSET_WIDTHS = (480, 960, 1600, 2560)


def absolute_media_url(path: str) -> str:
    return urljoin(settings.WAGTAILAPI_BASE_URL, path)


def serialize_image(image, *, alt: str | None = None, widths=SRCSET_WIDTHS) -> dict | None:
    if image is None:
        return None
    capped_widths = sorted({min(w, image.width) for w in widths})
    specs = [f"width-{w}|preserve-svg|format-webp" for w in capped_widths]
    try:
        renditions = image.get_renditions(*specs)
    except SourceImageIOError:
        return None
    # get_renditions() normalizes each spec's key (e.g. dropping the no-op
    # `preserve-svg` filter for raster sources), but guarantees the returned
    # dict's insertion order matches the order `specs` was passed in.
    ordered = list(renditions.values())
    largest = ordered[-1]
    return {
        "id": image.pk,
        "alt": alt if alt is not None else image.default_alt_text,
        "src": absolute_media_url(largest.url),
        "width": largest.width,
        "height": largest.height,
        "srcset": [{"url": absolute_media_url(r.url), "width": r.width} for r in ordered],
        "focal_point": focal_point_percentages(image),
    }


def focal_point_percentages(image) -> dict | None:
    """Centre of the editor-set focal point as percentages of the source image.

    Layouts that crop with ``object-fit: cover`` feed this straight into
    ``object-position`` so the crop keeps the chosen area in view. ``None``
    when no focal point is set, so the frontend falls back to the centre.
    """
    rect = image.get_focal_point()
    if rect is None or not image.width or not image.height:
        return None
    x, y = rect.centroid
    return {
        "x": round(100 * x / image.width, 1),
        "y": round(100 * y / image.height, 1),
    }
