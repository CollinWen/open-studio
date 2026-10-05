"""
Tests for the offline parts of the link readers: recognizing which site a
link belongs to, and pulling details out of page HTML and photo bytes.
No network calls.
"""

from datetime import datetime

from app.integrations.link_readers.github_reader import github_repo
from app.integrations.link_readers.google_drive_reader import drive_file_id
from app.integrations.link_readers.instagram_reader import instagram_post, split_instagram_title
from app.integrations.link_readers.page_meta import read_page_meta
from app.integrations.link_readers.photo_date import photo_taken_at
from app.integrations.link_readers.x_reader import read_x_embed, x_post
from app.integrations.link_readers.youtube_reader import _full_description, youtube_video_id


def test_youtube_links_in_every_common_form():
    for url in [
        "https://www.youtube.com/watch?v=qTZfw5cSKU8",
        "https://youtu.be/qTZfw5cSKU8?t=10",
        "https://www.youtube.com/shorts/qTZfw5cSKU8",
        "https://m.youtube.com/watch?feature=share&v=qTZfw5cSKU8",
    ]:
        assert youtube_video_id(url) == "qTZfw5cSKU8"
    assert youtube_video_id("https://example.com/watch?v=qTZfw5cSKU8") is None


def test_drive_file_links():
    file_id = "1DF3c1OheEYFane7LwuoApfP5gWO6olpw"
    assert drive_file_id(f"https://drive.google.com/file/d/{file_id}/view?usp=sharing") == file_id
    assert drive_file_id(f"https://drive.google.com/open?id={file_id}") == file_id
    assert drive_file_id("https://drive.google.com/drive/folders/abc") is None


def test_github_repo_links():
    assert github_repo("https://github.com/fastapi/fastapi") == ("fastapi", "fastapi")
    assert github_repo("https://github.com/me/site.git") == ("me", "site")
    assert github_repo("https://gitlab.com/me/site") is None


def test_page_meta_reads_preview_tags_and_title():
    html = """<html><head><title> Fallback </title>
      <meta property="og:title" content="Real title">
      <meta name="description" content="About it">
      <meta itemprop="uploadDate" content="2020-06-04T02:56:51-07:00"></head></html>"""
    meta = read_page_meta(html)
    assert meta["og:title"] == "Real title"
    assert meta["description"] == "About it"
    assert meta["uploaddate"].startswith("2020-06-04")
    assert meta["title"] == "Fallback"


def test_youtube_full_description_is_unescaped():
    page = 'junk "shortDescription":"Line one\\nLine \\"two\\"","isLive":false'
    assert _full_description(page) == 'Line one\nLine "two"'


def test_photo_date_from_exif():
    jpeg_start = b"\xff\xd8\xff\xe1\x00\x10Exif\x00\x00 ... 2022:08:19 19:37:33 ..."
    assert photo_taken_at(jpeg_start) == datetime(2022, 8, 19, 19, 37, 33)
    assert photo_taken_at(b"\xff\xd8 no exif here 2022:08:19 19:37:33") is None


def test_instagram_post_and_reel_links():
    assert instagram_post("https://www.instagram.com/p/BsOGulcndj-/?igsh=abc") == ("p", "BsOGulcndj-")
    assert instagram_post("https://instagram.com/reels/C5ZNdmrr0OH/") == ("reel", "C5ZNdmrr0OH")
    assert instagram_post("https://www.instagram.com/someone/p/BsOGulcndj-/") == ("p", "BsOGulcndj-")
    assert instagram_post("https://www.instagram.com/nasa/") is None


def test_instagram_title_splits_into_author_and_caption():
    assert split_instagram_title('Just An Egg on Instagram: "Let\'s set a "record""') == (
        "Just An Egg",
        'Let\'s set a "record"',
    )
    assert split_instagram_title("NASA (@nasa) • Instagram photos and videos") == ("NASA (@nasa)", "")


def test_x_post_links_on_both_domains():
    assert x_post("https://twitter.com/jack/status/20?s=46") == ("jack", "20")
    assert x_post("https://x.com/jack/status/20") == ("jack", "20")
    assert x_post("https://x.com/jack") is None


def test_x_embed_text_and_date():
    embed = (
        '<blockquote class="twitter-tweet"><p lang="en" dir="ltr">line one<br>a &amp; b '
        '<a href="https://t.co/x">pic.x.com/x</a></p>&mdash; jack (@jack) '
        '<a href="https://x.com/jack/status/20">March 21, 2006</a></blockquote>\n'
    )
    assert read_x_embed(embed) == ("line one\na & b pic.x.com/x", datetime(2006, 3, 21))
