import pytest
from django.core.management import call_command

from apps.pages.models import FlexPage


@pytest.fixture
def site(db):
    call_command("bootstrap_site")
    return {p.slug: p for p in FlexPage.objects.all()}


def test_find_redirects_to_detail(client, site):
    response = client.get("/api/v2/pages/find/", {"html_path": "/about/"})
    assert response.status_code == 302
    # Wagtail 8.0's PagesAPIViewSet.find_view always appends "?" + the
    # remaining (possibly empty) querystring; strip it before comparing.
    assert response["Location"].split("?")[0].endswith(f"/api/v2/pages/{site['about'].pk}/")


def test_find_unknown_path_404(client, site):
    assert client.get("/api/v2/pages/find/", {"html_path": "/nope/"}).status_code == 404


def test_page_detail_has_structured_body_and_expanded_rich_text(client, site):
    data = client.get(f"/api/v2/pages/{site['home'].pk}/").json()
    assert data["title"] == "Carrot&Claw"
    assert data["intro"]
    assert data["body"][0]["type"] == "hero"
    assert data["body"][0]["value"]["cta"] == {
        "label": "See the menu",
        "href": "/menu/",
        "external": False,
    }
    assert data["body"][1]["type"] == "rich_text"
    assert data["body"][1]["value"].startswith("<p>")


def test_site_settings_endpoint(client, site):
    response = client.get("/api/v2/site-settings/")
    assert response.status_code == 200
    data = response.json()
    assert data["header"]["site_title"] == "Carrot&Claw"
    assert [link["label"] for link in data["header"]["menu"]] == [
        "Home",
        "About",
        "Menu",
        "Gallery",
        "Staff",
    ]
    assert data["header"]["menu"][1]["href"] == "/about/"
    assert data["footer"]["copyright"] == "© Carrot&Claw"
    assert data["footer"]["text"].startswith("<p>")
    assert data["music"] == {"enabled": True, "volume": 40, "tracks": []}


def test_preview_endpoint_serves_draft(client, site):
    page = site["about"]
    page.intro = "Draft intro, not yet published"
    page.save_revision()
    preview = page.create_page_preview()
    response = client.get(
        "/api/v2/page_preview/1/", {"content_type": "pages.flexpage", "token": preview.token}
    )
    assert response.status_code == 200
    assert response.json()["intro"] == "Draft intro, not yet published"
    assert FlexPage.objects.get(pk=page.pk).intro == ""


def test_preview_endpoint_bad_token_is_404(client, site):
    response = client.get(
        "/api/v2/page_preview/1/", {"content_type": "pages.flexpage", "token": "bogus"}
    )
    assert response.status_code == 404


def test_preview_endpoint_unknown_content_type_is_404(client, site):
    response = client.get("/api/v2/page_preview/1/", {"content_type": "bogus", "token": "bogus"})
    assert response.status_code == 404
