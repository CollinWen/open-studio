"""
Google Drive reader: turns a Drive file's share link into something the
site can show at full resolution, without copying the file.

  - images are shown straight from Google's image server: the original,
    full-resolution file on the entry page, Google's 1600px copy in the grid
  - videos are shown in Drive's own player
  - a photo's date is read from its EXIF data (when it was taken)

The file must be shared as "Anyone with the link can view". Otherwise
Google asks visitors to sign in, and this reader says so.
"""

import re
from pathlib import Path

from app.integrations.link_readers.link_details import LinkDetails, LinkMedia, LinkReadError
from app.integrations.link_readers.page_meta import read_page_meta
from app.integrations.link_readers.photo_date import photo_taken_at
from app.integrations.link_readers.web_fetch import fetch, fetch_start

_FILE_ID = re.compile(r"(?:/file/d/|[?&]id=)([A-Za-z0-9_-]{20,})")

NOT_PUBLIC_MESSAGE = (
    "This Drive file isn't public. In Drive, choose Share → General access → "
    "'Anyone with the link' (Viewer), then try again."
)


def drive_file_id(url: str) -> str | None:
    """The file id in a Google Drive file link, or None."""
    if "drive.google.com" not in url and "docs.google.com" not in url:
        return None
    match = _FILE_ID.search(url)
    return match.group(1) if match else None


def read_drive_file(url: str) -> LinkDetails:
    file_id = drive_file_id(url)
    if not file_id:
        raise LinkReadError("That doesn't look like a Google Drive file link.")

    page = fetch(f"https://drive.google.com/file/d/{file_id}/view")
    if page.status_code in (401, 403) or "accounts.google.com" in str(page.url):
        raise LinkReadError(NOT_PUBLIC_MESSAGE)

    file_name = read_page_meta(page.text).get("og:title", "")
    image_url = f"https://lh3.googleusercontent.com/d/{file_id}"
    original_url = f"{image_url}=s0"  # "=s0" asks for the original size

    taken_at = None
    if _is_video(file_name):
        media = LinkMedia(
            type="embed",
            url=f"https://drive.google.com/file/d/{file_id}/preview",
            thumbnail_url=f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000",
        )
    else:
        media = LinkMedia(type="image", url=original_url, thumbnail_url=image_url)
        taken_at = photo_taken_at(fetch_start(original_url, 64 * 1024))

    return LinkDetails(
        url=f"https://drive.google.com/file/d/{file_id}/view",
        title=Path(file_name).stem if file_name else "",
        kind="video" if media.type == "embed" else "photo",
        # No platform or author: Drive is just where my own files live, not a source to credit.
        published_at=taken_at,
        media=[media],
    )


def _is_video(file_name: str) -> bool:
    return Path(file_name).suffix.lower() in {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}
