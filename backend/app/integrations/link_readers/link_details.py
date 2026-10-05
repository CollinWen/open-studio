"""
Link details: the common shape every link reader returns, whatever site
the link came from. The capture feature turns this into a draft entry.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LinkMedia:
    """One picture or video found at a link.

    type is "image" (shown with <img>), "video" (a video file) or "embed"
    (a player page shown in an iframe, like YouTube). thumbnail_url is a
    still picture used as the cover in the grid.
    """

    type: str
    url: str
    thumbnail_url: str = ""


@dataclass
class LinkDetails:
    url: str
    title: str = ""
    description: str = ""
    kind: str = "link"
    author: str = ""  # who made it: channel, repo owner, site name
    platform: str = ""  # YouTube, GitHub, Google Drive, or the site's name
    published_at: datetime | None = None
    media: list[LinkMedia] = field(default_factory=list)


class LinkReadError(Exception):
    """Raised with a plain-English message when a link can't be read."""
