"""
Read link: the front door for all link readers. Looks at a URL, picks the
reader for that site (YouTube, Google Drive, GitHub, Instagram, X), and falls
back to the general webpage reader for everything else.

To support a new site: add a <site>_reader.py next to this file and one line below.
"""

from app.integrations.link_readers.github_reader import github_repo, read_github_repo
from app.integrations.link_readers.google_drive_reader import drive_file_id, read_drive_file
from app.integrations.link_readers.instagram_reader import instagram_post, read_instagram_post
from app.integrations.link_readers.link_details import LinkDetails, LinkReadError
from app.integrations.link_readers.webpage_reader import read_webpage
from app.integrations.link_readers.x_reader import read_x_post, x_post
from app.integrations.link_readers.youtube_reader import read_youtube_video, youtube_video_id


def read_link(url: str) -> LinkDetails:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        raise LinkReadError("Links need to start with http:// or https://")

    if youtube_video_id(url):
        return read_youtube_video(url)
    if drive_file_id(url):
        return read_drive_file(url)
    if "drive.google.com/drive/folders" in url:
        raise LinkReadError("Drive folders aren't supported yet. Paste each photo's own link instead.")
    if github_repo(url):
        return read_github_repo(url)
    if instagram_post(url):
        return read_instagram_post(url)
    if x_post(url):
        return read_x_post(url)
    return read_webpage(url)
