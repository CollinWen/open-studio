"""
X reader: a post's text, author and date from X's public oEmbed endpoint
(no key needed). Works for twitter.com and x.com links.

oEmbed gives no pictures, so a post with an image has no cover until one is added.
"""

import html
import re
from datetime import datetime

from app.integrations.link_readers.link_details import LinkDetails, LinkReadError
from app.integrations.link_readers.web_fetch import fetch

_POST_PATH = re.compile(r"(?:twitter|x)\.com/([A-Za-z0-9_]+)/status(?:es)?/(\d+)")
_POST_TEXT = re.compile(r"<p[^>]*>(.*?)</p>", re.DOTALL)
_POST_DATE = re.compile(r">([A-Z][a-z]+ \d{1,2}, \d{4})</a>\s*</blockquote>")


def x_post(url: str) -> tuple[str, str] | None:
    """(handle, post id) from an X or Twitter post link, or None."""
    match = _POST_PATH.search(url)
    return (match.group(1), match.group(2)) if match else None


def read_x_post(url: str) -> LinkDetails:
    found = x_post(url)
    if not found:
        raise LinkReadError("That doesn't look like a link to a post on X.")
    handle, post_id = found
    post_url = f"https://x.com/{handle}/status/{post_id}"

    response = fetch("https://publish.twitter.com/oembed", {"url": post_url, "omit_script": "1", "dnt": "true"})
    if response.status_code != 200:
        raise LinkReadError("X didn't return this post. Is it public?")
    info = response.json()

    text, posted_on = read_x_embed(info.get("html", ""))
    return LinkDetails(
        url=post_url,
        title=_first_line(text) or f"Post by @{handle}",
        description=text,
        kind="post",
        author=info.get("author_name", "") or f"@{handle}",
        platform="X",
        published_at=posted_on,
    )


def read_x_embed(embed_html: str) -> tuple[str, datetime | None]:
    """The post's plain text and date from the blockquote X returns."""
    text = ""
    text_match = _POST_TEXT.search(embed_html)
    if text_match:
        with_breaks = re.sub(r"<br\s*/?>", "\n", text_match.group(1))
        text = html.unescape(re.sub(r"<[^>]+>", "", with_breaks)).strip()
    date_match = _POST_DATE.search(embed_html)
    posted_on = datetime.strptime(date_match.group(1), "%B %d, %Y") if date_match else None
    return text, posted_on


def _first_line(text: str, limit: int = 80) -> str:
    line = text.strip().splitlines()[0] if text.strip() else ""
    return line if len(line) <= limit else line[: limit - 1].rstrip() + "…"
