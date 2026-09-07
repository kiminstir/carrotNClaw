import pytest
from wagtail.blocks import StreamValue
from wagtail.models import Page

from apps.pages.models import FlexPage


def make_page(parent, title, slug, raw_body):
    page = FlexPage(title=title, slug=slug, intro="Intro")
    page.body = StreamValue(FlexPage.body.field.stream_block, raw_body, is_lazy=True)
    parent.add_child(instance=page)
    page.save_revision().publish()
    return page


@pytest.mark.django_db
def test_flexpage_body_api_representation():
    root = Page.get_first_root_node()
    page = make_page(
        root,
        "About",
        "about",
        [
            {"type": "rich_text", "value": "<p>Welcome, traveller.</p>"},
            {
                "type": "collapse",
                "value": {
                    "items": [{"title": "Hours", "content": "<p>Always</p>"}],
                    "allow_multiple_open": False,
                },
            },
        ],
    )
    page.refresh_from_db()
    data = page.body.stream_block.get_api_representation(page.body, context={})
    assert [item["type"] for item in data] == ["rich_text", "collapse"]
    assert data[1]["value"]["items"][0]["title"] == "Hours"
    assert page.api_fields and [f.name for f in page.api_fields] == ["intro", "body"]
