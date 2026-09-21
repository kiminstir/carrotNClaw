"""Image filter operations of our own, registered in ``wagtail_hooks.py``.

Wagtail's ``fill-WxH-cN`` positions the focal point proportionally (a point at 10 % of the
image lands at 10 % of the crop) and limits how far it zooms in by the requested output size,
so every srcset width frames a different region. ``focalfill`` crops to the focal point
rectangle itself, centred, the same way at every size.
"""

from wagtail.images.image_operations import FillOperation, TransformOperation
from wagtail.images.rect import Rect


def focal_crop_rect(focal_point: Rect | None, size: tuple[int, int], aspect: float) -> Rect:
    """Region of an image to keep when cropping it to ``aspect`` (width / height).

    The crop is the smallest box of that shape holding the whole focal point rectangle,
    centred on it, shifted only as far as needed to stay inside the image. Without a focal
    point it is the largest such box, centred on the image.
    """
    image_width, image_height = size
    max_width = min(image_width, image_height * aspect)
    if focal_point is None:
        width = max_width
        centre = (image_width / 2, image_height / 2)
    else:
        width = min(max(focal_point.width, focal_point.height * aspect), max_width)
        centre = focal_point.centroid
    # A degenerate focal point (zero size) must still give a croppable rect.
    width = max(width, 1.0, aspect)
    rect = Rect.from_point(centre[0], centre[1], width, width / aspect)
    return rect.move_to_clamp(Rect(0, 0, image_width, image_height))


class FocalFillOperation(TransformOperation):
    """``focalfill-WxH``: crop per ``focal_crop_rect`` and scale down to at most W×H.

    Never upscales: a small focal point yields a small rendition, and the serializer caps
    the widths it asks for at the crop's own width.
    """

    vary_fields = FillOperation.vary_fields

    def construct(self, size):
        width, height = size.split("x")
        self.width = int(width)
        self.height = int(height)

    def run(self, transform, image):
        rect = focal_crop_rect(image.get_focal_point(), transform.size, self.width / self.height)
        transform = transform.crop(rect.round())
        if transform.size[0] > self.width:
            transform = transform.resize((self.width, self.height))
        return transform
