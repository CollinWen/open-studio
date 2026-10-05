"""
Capture service: turns a pasted link into a prefilled entry draft.
The site-specific reading lives in integrations/link_readers/; this file
only maps what was found onto the entry's fields.
"""

from app.features.capture.schemas import CapturedLink
from app.features.entries.schemas import MediaItem
from app.integrations.link_readers.read_link import read_link


def capture_link(url: str) -> CapturedLink:
    details = read_link(url)
    return CapturedLink(
        source_url=details.url,
        title=details.title,
        description=details.description,
        kind=details.kind,
        source_name=_source_name(details.author, details.platform),
        occurred_at=details.published_at,
        media=[
            MediaItem(type=item.type, url=item.url, thumbnail_url=item.thumbnail_url)
            for item in details.media
        ],
    )


def _source_name(author: str, platform: str) -> str:
    """e.g. "Collin Wen, YouTube". Just one of them when they're the same or missing."""
    if author and platform and author.lower() != platform.lower():
        return f"{author}, {platform}"
    return author or platform
