"""
Tests for the picture reader: a picture on this machine is sent as its bytes,
one with a web address is sent as that address, and anything else (or a file
too big to send) is refused. Never calls OpenRouter.
"""

from dataclasses import replace

import pytest

from app.features.media import picture_reader
from app.integrations import media_storage


@pytest.fixture
def sent(monkeypatch) -> list[str]:
    addresses: list[str] = []

    def fake_ask(system, user, picture_url, model):
        addresses.append(picture_url)
        return "  A halibut fillet\\n on leeks.  "

    monkeypatch.setattr(picture_reader, "ask_llm_about_picture", fake_ask)
    return addresses


def test_a_picture_with_a_web_address_is_sent_as_that_address(sent):
    assert picture_reader.read_picture("https://media.example.com/a.jpg") == "A halibut fillet\\n on leeks."
    assert sent == ["https://media.example.com/a.jpg"]


def test_a_picture_stored_here_is_sent_as_its_bytes(sent, monkeypatch):
    monkeypatch.setattr(media_storage, "settings", replace(media_storage.settings, r2_account_id=""))
    url = media_storage.save_media_file("dish.png", b"\x89PNG")
    picture_reader.read_picture(url)
    assert sent == ["data:image/png;base64,iVBORw=="]


def test_a_picture_too_big_to_send_is_refused(sent, monkeypatch):
    monkeypatch.setattr(media_storage, "settings", replace(media_storage.settings, r2_account_id=""))
    url = media_storage.save_media_file("big.png", b"x" * 20)
    monkeypatch.setattr(picture_reader, "settings", replace(picture_reader.settings, picture_max_bytes_for_reading=10))
    with pytest.raises(picture_reader.PictureNotReadable):
        picture_reader.read_picture(url)
    assert sent == []


def test_an_address_that_isnt_a_picture_is_refused(sent):
    with pytest.raises(picture_reader.PictureNotReadable):
        picture_reader.read_picture("javascript:alert(1)")
