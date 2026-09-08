from wagtail.rich_text import expand_db_html

from apps.pages.images import serialize_image


def stream_to_api(value, context):
    return value.stream_block.get_api_representation(value, context)


def flatten(stream_repr):
    """Drop the StreamField wrapper and skip blocks that serialized to None."""
    return [item["value"] for item in stream_repr if item["value"] is not None]


def serialize_header(header, context):
    return {
        "site_title": header.site_title,
        "logo": serialize_image(header.logo, alt=header.site_title),
        "menu": flatten(stream_to_api(header.menu, context)),
    }


def serialize_footer(footer, context):
    return {
        "text": expand_db_html(footer.text) if footer.text else "",
        "links": flatten(stream_to_api(footer.links, context)),
        "copyright": footer.copyright,
        "social": footer.social_links(),
    }


def serialize_hours(hours, context):
    return {
        "enabled": hours.enabled,
        "slots": flatten(stream_to_api(hours.slots, context)),
    }


def serialize_music(music, context):
    return {
        "enabled": music.enabled,
        "volume": music.volume,
        "tracks": flatten(stream_to_api(music.tracks, context)),
    }
