"""
Picture reader: describes one picture in plain words with a model that can
see (PICTURE_MODEL), so an entry's pictures count toward its tags, Related
and search. For a dish, that's the ingredients, technique and cuisine you can
see; for a made thing, its materials and how it was made.

A picture stored on this machine (local development) is sent as its bytes;
anything with a web address (R2, YouTube or Instagram thumbnails) is sent as
that address, and the model fetches it. The picture itself is never changed.

Used by entries/entry_reading.py.
"""

import base64
import mimetypes

from app.config import settings
from app.integrations import media_storage
from app.integrations.llm_client import ask_llm_about_picture

SYSTEM_PROMPT = """You describe pictures in a personal collection of work and interests,
so they can be found and connected later by what they show. Write plain sentences, no
lists, no more than 120 words. Say what is shown, concretely and with the specific names:
- food: the dish, every ingredient you can see, how it was cut or cooked, the cuisine it suggests
- made things: the object, its materials, the technique or process it shows
- places, people, art: the subject, setting, style and medium
Copy any readable text. Don't guess who people are, and don't praise or judge."""

USER_PROMPT = "Describe this picture."


class PictureNotReadable(Exception):
    """The picture can't be sent to be read (too big, or not a picture we can address)."""


def read_picture(url: str, caption: str = "") -> str:
    """A few plain sentences about what the picture at `url` shows."""
    prompt = f"{USER_PROMPT} Its caption: {caption}" if caption else USER_PROMPT
    reply = ask_llm_about_picture(SYSTEM_PROMPT, prompt, _address_for_model(url), settings.picture_model)
    return " ".join(reply.split())


def _address_for_model(url: str) -> str:
    content = media_storage.read_local_media_file(url)
    if content is None:
        if not url.startswith(("http://", "https://")):
            raise PictureNotReadable(f"Not a picture address: {url}")
        return url
    if len(content) > settings.picture_max_bytes_for_reading:
        raise PictureNotReadable(f"Too big to send to be read: {url}")
    mime = mimetypes.guess_type(url)[0] or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(content).decode()}"
