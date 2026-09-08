from urllib.parse import urljoin

from django.conf import settings
from wagtail.images.models import SourceImageIOError

SRCSET_WIDTHS = (480, 960, 1600)


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
    }
