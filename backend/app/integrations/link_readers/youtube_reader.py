"""
YouTube reader: everything about a video from just its link, no API key.

  - title, channel and thumbnail come from YouTube's public oEmbed endpoint
  - upload date and full description come from the video's own web page

The video itself is never downloaded; the site embeds YouTube's player.
"""

import json
import re
from datetime import datetime

from app.integrations.link_readers.link_details import LinkDetails, LinkMedia, LinkReadError
from app.integrations.link_readers.page_meta import read_page_meta
from app.integrations.link_readers.web_fetch import fetch

_VIDEO_ID = re.compile(r"(?:v=|youtu\.be/|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})")


def youtube_video_id(url: str) -> str | None:
    """The 11-character video id in any common YouTube link, or None."""
    if "youtube.com" not in url and "youtu.be" not in url:
        return None
    match = _VIDEO_ID.search(url)
    return match.group(1) if match else None


def read_youtube_video(url: str) -> LinkDetails:
    video_id = youtube_video_id(url)
    if not video_id:
        raise LinkReadError("That doesn't look like a YouTube video link.")
    watch_url = f"https://www.youtube.com/watch?v={video_id}"

    oembed = fetch("https://www.youtube.com/oembed", {"url": watch_url, "format": "json"})
    if oembed.status_code != 200:
        raise LinkReadError("YouTube didn't return this video. Is it public or unlisted?")
    info = oembed.json()

    page = fetch(watch_url).text
    meta = read_page_meta(page)

    return LinkDetails(
        url=watch_url,
        title=info.get("title", ""),
        description=_full_description(page) or meta.get("description", ""),
        kind="video",
        author=info.get("author_name", ""),
        platform="YouTube",
        published_at=_parse_date(meta.get("uploaddate") or meta.get("datepublished")),
        media=[
            LinkMedia(
                type="embed",
                url=f"https://www.youtube-nocookie.com/embed/{video_id}",
                thumbnail_url=f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            )
        ],
    )


def _full_description(page_html: str) -> str:
    """The untruncated description, stored in the page's data as "shortDescription"."""
    marker = '"shortDescription":'
    start = page_html.find(marker)
    if start == -1:
        return ""
    try:
        value, _ = json.JSONDecoder().raw_decode(page_html[start + len(marker) :])
    except ValueError:
        return ""
    return value if isinstance(value, str) else ""


def _parse_date(text: str | None) -> datetime | None:
    try:
        return datetime.fromisoformat(text) if text else None
    except ValueError:
        return None
