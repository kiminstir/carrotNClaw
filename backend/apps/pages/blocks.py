from wagtail.images.blocks import ImageBlock

from apps.pages.images import serialize_image


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
