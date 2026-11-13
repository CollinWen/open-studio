"""
Media storage: saves uploaded files and returns the URL they're served from.

When the R2 settings are filled in (production), files go to the Cloudflare R2
bucket and the URL points at its public address. Otherwise (local development)
they go to backend/data/media and are served by main.py under /media.
Files are stored exactly as uploaded, under a random name. Write-ups (.html)
are stored only through save_writeup_file, which callers use for HTML they
have already made safe (features/media/writeup_sanitizer.py); a raw .html
upload through save_media_file is refused.
"""

import mimetypes
import uuid
from pathlib import Path

import boto3

from app.config import settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm"}
WRITEUP_EXTENSION = ".html"


def save_media_file(original_name: str, content: bytes) -> str:
    """Store the file under a random name and return its public URL."""
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}")

    return _save(f"{uuid.uuid4().hex}{extension}", content)


def save_writeup_file(safe_html: str) -> str:
    """Store an already-sanitized write-up and return its public URL."""
    return _save(f"{uuid.uuid4().hex}{WRITEUP_EXTENSION}", safe_html.encode("utf-8"))


def is_stored_writeup_url(url: str) -> bool:
    """True for a write-up this studio stored (so it was sanitized on the way in)."""
    name = url.rsplit("/", 1)[-1]
    stored_here = url == f"/media/{name}" or (
        bool(settings.media_public_url) and url == f"{settings.media_public_url.rstrip('/')}/{name}"
    )
    return stored_here and name.endswith(WRITEUP_EXTENSION) and name[: -len(WRITEUP_EXTENSION)].isalnum()


def _save(stored_name: str, content: bytes) -> str:
    if settings.r2_enabled:
        return _save_to_r2(stored_name, content)
    return _save_to_disk(stored_name, content)


def _save_to_r2(stored_name: str, content: bytes) -> str:
    # Content type lets browsers show the file inline instead of downloading it.
    content_type = mimetypes.guess_type(stored_name)[0] or "application/octet-stream"
    if content_type.startswith("text/"):
        content_type += "; charset=utf-8"
    _r2_client().put_object(
        Bucket=settings.r2_bucket,
        Key=stored_name,
        Body=content,
        ContentType=content_type,
    )
    return f"{settings.media_public_url.rstrip('/')}/{stored_name}"


def _save_to_disk(stored_name: str, content: bytes) -> str:
    settings.media_dir.mkdir(parents=True, exist_ok=True)
    (settings.media_dir / stored_name).write_bytes(content)
    return f"/media/{stored_name}"


def _r2_client():
    # R2 speaks the same protocol as Amazon S3, so the standard S3 client works.
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )
