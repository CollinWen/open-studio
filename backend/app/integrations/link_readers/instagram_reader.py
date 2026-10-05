"""
Instagram reader: a post or reel's picture, caption and author from its
link-preview tags. Instagram only shows these to link-preview bots, so this
fetches the page as one.

The picture URL is Instagram's own and stops working after a few weeks.
"""

import html
import re

from app.integrations.link_readers.link_details import LinkDetails, LinkMedia, LinkReadError
from app.integrations.link_readers.page_meta import read_page_meta
from app.integrations.link_readers.web_fetch import fetch_as_preview_bot

_POST_PATH = re.compile(r"instagram\.com/(?:[A-Za-z0-9_.]+/)?(p|reels?|tv)/([A-Za-z0-9_-]+)")
# og:title looks like: Name on Instagram: "the caption"
_TITLE_FORM = re.compile(r'^(.*?) on Instagram: "(.*)"$', re.DOTALL)


def instagram_post(url: str) -> tuple[str, str] | None:
    """(post type, code) from an Instagram post or reel link, or None. Type is "p", "reel" or "tv"."""
    match = _POST_PATH.search(url)
    if not match:
        return None
    post_type = "reel" if match.group(1) == "reels" else match.group(1)
    return post_type, match.group(2)


def read_instagram_post(url: str) -> LinkDetails:
    found = instagram_post(url)
    if not found:
        raise LinkReadError("That doesn't look like an Instagram post link.")
    post_type, code = found
    post_url = f"https://www.instagram.com/{post_type}/{code}/"

    response = fetch_as_preview_bot(post_url)
    meta = read_page_meta(response.text) if response.status_code == 200 else {}
    if not meta.get("og:title"):
        raise LinkReadError("Instagram didn't describe this post. It may be private.")

    author, caption = split_instagram_title(html.unescape(meta["og:title"]))
    image = meta.get("og:image", "")
    return LinkDetails(
        url=post_url,
        title=_first_line(caption) or f"Post by {author}",
        description=caption,
        kind="video" if post_type in ("reel", "tv") else "post",
        author=author,
        platform="Instagram",
        media=[LinkMedia(type="image", url=image, thumbnail_url=image)] if image else [],
    )


def split_instagram_title(og_title: str) -> tuple[str, str]:
    """(author, caption) from an og:title like 'Name on Instagram: "caption"'."""
    match = _TITLE_FORM.match(og_title.strip())
    if not match:
        return og_title.split(" • ")[0].strip(), ""
    return match.group(1).strip(), match.group(2).strip()


def _first_line(text: str, limit: int = 80) -> str:
    line = text.strip().splitlines()[0] if text.strip() else ""
    return line if len(line) <= limit else line[: limit - 1].rstrip() + "…"
