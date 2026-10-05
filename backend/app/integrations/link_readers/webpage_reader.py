"""
Webpage reader: the fallback for any link without its own reader. Uses the
page's link-preview tags (title, description, image, site name, date).
Works well for articles and blogs. Sites that hide content from logged-out
visitors give little back; Instagram and X have their own readers for that.
"""

from datetime import datetime
from urllib.parse import urljoin, urlparse

from app.integrations.link_readers.link_details import LinkDetails, LinkMedia, LinkReadError
from app.integrations.link_readers.page_meta import read_page_meta
from app.integrations.link_readers.web_fetch import fetch


def read_webpage(url: str) -> LinkDetails:
    response = fetch(url)
    if response.status_code >= 400:
        raise LinkReadError(f"That page didn't load (status {response.status_code}).")
    meta = read_page_meta(response.text)

    final_url = str(response.url)
    site_name = meta.get("og:site_name") or urlparse(final_url).netloc.removeprefix("www.")
    image = meta.get("og:image") or meta.get("twitter:image")
    media = []
    if image:
        image_url = urljoin(final_url, image)  # some sites give a relative path
        media.append(LinkMedia(type="image", url=image_url, thumbnail_url=image_url))

    return LinkDetails(
        url=final_url,
        title=meta.get("og:title") or meta.get("twitter:title") or meta.get("title", ""),
        description=meta.get("og:description") or meta.get("description", ""),
        kind="link",
        author=meta.get("author") or site_name,
        platform=site_name,
        published_at=_parse_date(meta.get("article:published_time") or meta.get("datepublished")),
        media=media,
    )


def _parse_date(text: str | None) -> datetime | None:
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")) if text else None
    except ValueError:
        return None
