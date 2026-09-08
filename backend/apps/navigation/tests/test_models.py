import pytest
from wagtail.blocks import StreamValue

from apps.navigation.models import FooterSettings, HeaderSettings


@pytest.mark.django_db
def test_header_settings_menu_streamfield_roundtrip():
    header = HeaderSettings.load()
    header.menu = StreamValue(
        HeaderSettings.menu.field.stream_block,
        [
            {
                "type": "link",
                "value": {"label": "Menu", "page": None, "url": "https://x.example/menu"},
            }
        ],
        is_lazy=True,
    )
    header.save()
    header = HeaderSettings.load()
    data = header.menu.stream_block.get_api_representation(header.menu, context={})
    assert data[0]["value"] == {"label": "Menu", "href": "https://x.example/menu", "external": True}


@pytest.mark.django_db
def test_footer_settings_defaults():
    footer = FooterSettings.load()
    assert footer.text == ""
    assert len(footer.links) == 0
    assert (footer.discord_url, footer.youtube_url, footer.twitch_url) == ("", "", "")
