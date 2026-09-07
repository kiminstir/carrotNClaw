import pytest
from django.core.files.base import ContentFile
from wagtail.blocks import StreamValue
from wagtail.documents.models import Document

from apps.music.models import MusicSettings, TrackBlock


@pytest.mark.django_db
def test_track_block_api_representation_has_absolute_src():
    doc = Document.objects.create(
        title="Lute song", file=ContentFile(b"\x00" * 16, name="lute.mp3")
    )
    block = TrackBlock()
    value = block.to_python({"title": "Lute song (live)", "file": doc.pk})
    data = block.get_api_representation(value)
    assert data["id"] == doc.pk
    assert data["title"] == "Lute song (live)"
    assert data["src"].startswith("http://testserver/media/")
    assert data["src"].endswith("lute.mp3")


@pytest.mark.django_db
def test_music_settings_defaults_and_stream():
    music = MusicSettings.load()
    assert music.enabled is True
    assert music.volume == 40
    music.tracks = StreamValue(MusicSettings.tracks.field.stream_block, [], is_lazy=True)
    music.save()
    assert len(MusicSettings.load().tracks) == 0
