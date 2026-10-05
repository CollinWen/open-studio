"""
Page meta: pulls the <meta> tags out of an HTML page, e.g. og:title,
og:image, article:published_time. Most sites describe themselves this way
(the "OpenGraph" tags used for link previews).
"""

from html.parser import HTMLParser


class _MetaCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "title":
            self._in_title = True
        if tag != "meta":
            return
        values = dict(attrs)
        key = values.get("property") or values.get("name") or values.get("itemprop")
        content = values.get("content")
        if key and content and key.lower() not in self.meta:
            self.meta[key.lower()] = content

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def read_page_meta(html: str) -> dict[str, str]:
    """All meta tags as {name: content}, lowercase names. The <title> is under "title"."""
    collector = _MetaCollector()
    collector.feed(html)
    meta = dict(collector.meta)
    if collector.title.strip():
        meta.setdefault("title", collector.title.strip())
    return meta
