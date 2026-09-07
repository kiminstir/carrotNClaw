import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from wagtail.models import Page, Site

from apps.music.models import MusicSettings
from apps.navigation.models import FooterSettings, HeaderSettings
from apps.pages.models import FlexPage


@pytest.mark.django_db
def test_bootstrap_is_idempotent(monkeypatch):
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "admin")
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "secret-pass-123")

    call_command("bootstrap_site")
    call_command("bootstrap_site")

    assert FlexPage.objects.count() == 5
    home = FlexPage.objects.get(slug="home")
    assert Site.objects.get(is_default_site=True).root_page_id == home.pk
    assert sorted(p.slug for p in FlexPage.objects.child_of(home)) == [
        "about",
        "gallery",
        "menu",
        "staff",
    ]
    assert not Page.objects.filter(depth=2).exclude(pk=home.pk).exists()  # welcome page removed
    assert all(p.live for p in FlexPage.objects.all())
    assert [b.block_type for b in home.body][0] == "hero"

    assert get_user_model().objects.filter(username="admin", is_superuser=True).count() == 1
    assert len(HeaderSettings.load().menu) == 5
    assert FooterSettings.load().copyright
    assert MusicSettings.load().pk


@pytest.mark.django_db
def test_bootstrap_without_superuser_env_skips_user(monkeypatch):
    monkeypatch.delenv("DJANGO_SUPERUSER_USERNAME", raising=False)
    monkeypatch.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)
    call_command("bootstrap_site")
    assert not get_user_model().objects.exists()
