"""
Media storage: saves uploaded files and returns the URL they're served from.

Right now files go to backend/data/media on disk. When the site moves to
Firebase or AWS, only this file should need to change.
"""

import uuid
from pathlib import Path

from app.config import settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm"}


def save_media_file(original_name: str, content: bytes) -> str:
    """Store the file under a random name and return its public URL path."""
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}")

    settings.media_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{extension}"
    (settings.media_dir / stored_name).write_bytes(content)
    return f"/media/{stored_name}"
