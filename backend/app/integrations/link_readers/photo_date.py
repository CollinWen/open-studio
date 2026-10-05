"""
Photo date: finds when a photo was taken from the EXIF data cameras (and
drones and phones) write into the start of a JPEG file.
"""

import re
from datetime import datetime

# EXIF dates look like "2022:08:19 19:37:33". The first one in a file is the capture time
# on virtually every camera, so a simple search is enough; no EXIF library needed.
_EXIF_DATE = re.compile(rb"(\d{4}):(\d\d):(\d\d) (\d\d):(\d\d):(\d\d)")


def photo_taken_at(file_start: bytes) -> datetime | None:
    """The capture date in the first bytes of a JPEG, or None if there isn't one."""
    if b"Exif" not in file_start[:64]:
        return None
    match = _EXIF_DATE.search(file_start)
    if not match:
        return None
    try:
        return datetime(*(int(part) for part in match.groups()))
    except ValueError:  # e.g. "0000:00:00 00:00:00" from a camera with no clock set
        return None
