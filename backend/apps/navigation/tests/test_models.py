import datetime

import pytest
from wagtail.blocks import StreamBlockValidationError, StreamValue

from apps.navigation.models import FooterSettings, HeaderSettings, OpeningHoursSettings


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


def slots_value(*slots):
    return StreamValue(
        OpeningHoursSettings.slots.field.stream_block,
        [
            {"type": "slot", "value": {"day": day, "opens": opens, "closes": closes}}
            for day, opens, closes in slots
        ],
        is_lazy=True,
    )


@pytest.mark.django_db
def test_opening_hours_defaults_to_enabled_with_no_slots():
    hours = OpeningHoursSettings.load()
    assert hours.enabled is True
    assert len(hours.slots) == 0


@pytest.mark.django_db
def test_opening_hours_slot_roundtrips_with_overnight_closing():
    hours = OpeningHoursSettings.load()
    hours.slots = slots_value(("4", "20:00", "02:00"))
    hours.save()
    hours = OpeningHoursSettings.load()
    slot = hours.slots[0].value
    assert slot["day"] == "4"
    assert slot["opens"] == datetime.time(20, 0)
    assert slot["closes"] == datetime.time(2, 0)


@pytest.mark.django_db
def test_opening_hours_slot_rejects_identical_open_and_close():
    hours = OpeningHoursSettings.load()
    hours.slots = slots_value(("0", "20:00", "20:00"))
    with pytest.raises(StreamBlockValidationError):
        hours.slots.stream_block.clean(hours.slots)
