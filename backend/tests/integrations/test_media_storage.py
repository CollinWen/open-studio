"""
Tests for integrations/media_storage.py: uploads go to disk without R2 settings
and to the R2 bucket (with a public URL back) when they're filled in.
"""

from dataclasses import replace
from unittest.mock import MagicMock

import pytest

from app.config import settings
from app.integrations import media_storage


def test_saves_to_disk_without_r2(tmp_path, monkeypatch):
    monkeypatch.setattr(media_storage, "settings", replace(settings, data_dir=tmp_path, r2_account_id=""))

    url = media_storage.save_media_file("photo.JPG", b"pixels")

    assert url.startswith("/media/") and url.endswith(".jpg")
    assert (tmp_path / "media" / url.removeprefix("/media/")).read_bytes() == b"pixels"


def test_saves_to_r2_when_configured(monkeypatch):
    r2_settings = replace(
        settings,
        r2_account_id="account",
        r2_bucket="studio-media",
        media_public_url="https://media.example.com/",
    )
    monkeypatch.setattr(media_storage, "settings", r2_settings)
    client = MagicMock()
    monkeypatch.setattr(media_storage, "_r2_client", lambda: client)

    url = media_storage.save_media_file("clip.mp4", b"frames")

    stored = client.put_object.call_args.kwargs
    assert stored["Bucket"] == "studio-media"
    assert stored["Body"] == b"frames"
    assert stored["ContentType"] == "video/mp4"
    assert url == f"https://media.example.com/{stored['Key']}"


def test_rejects_unknown_file_types():
    with pytest.raises(ValueError):
        media_storage.save_media_file("notes.exe", b"")
