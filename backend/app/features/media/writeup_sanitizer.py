"""
Write-up sanitizer: turns whatever HTML an agent (or the owner) sends into a
self-contained write-up the studio can show safely, and reads out its text.

The line it draws: the writer decides what's on the page and how it's
arranged (structure, tables, layout, drawings); the studio decides how it
looks (typeface, sizes, colors), from frontend/src/styles/writeup.css; and
nothing can run or load from elsewhere. Scripts, forms, frames, event
handlers and outside files are removed; styles keep only their layout
(writeup_css_filter.py); pictures must be written into the file (data:
URLs); links may point out, but only open, in a new tab, when clicked.
Unknown tags are dropped but their text is kept. What may stay is listed in
writeup_allow_lists.py.

Used by media/service.py. The text it reads out is what tags, Related and
search use for the write-up.
"""

from collections import Counter
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser

from app.features.media import writeup_allow_lists as allowed
from app.features.media.writeup_css_filter import filter_stylesheet


@dataclass
class SanitizedWriteup:
    html: str
    # The words a reader sees, in one plain line.
    text: str
    # What was removed, in plain words with a count each; empty if nothing was.
    removed: list[str]


def sanitize_writeup(html: str) -> SanitizedWriteup:
    parser = _WriteupParser()
    parser.feed(html)
    parser.close()
    return SanitizedWriteup(
        html=parser.finish(),
        text=" ".join("".join(parser.text).split()),
        removed=sorted(f"{what}: {count}" for what, count in parser.removed.items()),
    )


class _WriteupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.text: list[str] = []
        self.open_tags: list[str] = []
        self.dropping: list[str] = []
        self.style: list[str] | None = None  # The text of a <style> block being read.
        self.removed: Counter[str] = Counter()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.text.append(" ")
        if self.dropping:
            # Only the dropped tag's own name matters for finding where it ends.
            if tag == self.dropping[-1]:
                self.dropping.append(tag)
            return
        if tag == "style":
            self.style = []
            return
        if tag in allowed.DROPPED_WITH_CONTENT:
            self._note_removed_tag(tag)
            if tag not in allowed.DROPPED_VOID:
                self.dropping.append(tag)
            return
        if tag not in allowed.TEXT_TAGS and tag not in allowed.DRAWING_TAGS:
            if tag not in allowed.DROPPED_QUIETLY:
                self.removed[f"<{tag}> (its text kept)"] += 1
            return
        kept = "".join(self._attribute(tag, name, value or "") for name, value in attrs)
        if tag == "a" and ' href="' in kept and ' href="#' not in kept:
            kept += ' target="_blank" rel="noopener noreferrer"'  # Links out open beside the studio.
        if tag == "img" and ' src="' not in kept:
            self.removed["pictures not written into the file"] += 1
            return
        if self.open_tags and self.open_tags[-1] in allowed.CLOSED_BY_SIBLING.get(tag, set()):
            self.out.append(f"</{self.open_tags.pop()}>")
        self.out.append(f"<{tag}{kept}>")
        if tag not in allowed.VOID_TAGS:
            self.open_tags.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag in allowed.DRAWING_TAGS and self.open_tags and self.open_tags[-1] == tag:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        self.text.append(" ")
        if self.dropping:
            if tag == self.dropping[-1]:
                self.dropping.pop()
            return
        if tag == "style" and self.style is not None:
            self._keep_style_block("".join(self.style))
            self.style = None
            return
        if tag not in self.open_tags:
            return
        while self.open_tags:
            closing = self.open_tags.pop()
            self.out.append(f"</{closing}>")
            if closing == tag:
                break

    def handle_data(self, data: str) -> None:
        if self.style is not None:
            self.style.append(data)
        elif not self.dropping:
            self.out.append(escape(data, quote=False))
            self.text.append(data)

    def handle_comment(self, data: str) -> None:
        pass  # Comments are dropped quietly: they never show.

    def finish(self) -> str:
        if self.style is not None:  # A <style> block never closed.
            self._keep_style_block("".join(self.style))
            self.style = None
        self.out.extend(f"</{tag}>" for tag in reversed(self.open_tags))
        self.open_tags = []
        return "".join(self.out).strip()

    def _keep_style_block(self, css: str) -> None:
        kept, removed = filter_stylesheet(css)
        self._note_removed_styles(removed)
        if kept:
            self.out.append(f"<style>{kept}</style>")

    def _attribute(self, tag: str, name: str, value: str) -> str:
        if name.startswith("xmlns"):
            return ""  # Not needed inside an HTML page.
        if not allowed.is_allowed_attribute(tag, name):
            self.removed[_removed_attribute_label(name)] += 1
            return ""
        kept, removed_styles = allowed.check_value(tag, name, value.strip())
        self._note_removed_styles(removed_styles)
        if kept is None:
            if name not in {"src", "style"}:
                self.removed[f"{name} values the studio can't keep"] += 1
            return ""
        name = allowed.DRAWING_SPELLING.get(name, name)
        return f' {name}="{escape(kept, quote=True)}"'

    def _note_removed_tag(self, tag: str) -> None:
        if tag == "link":
            self.removed["linked stylesheets and files"] += 1
        elif tag not in allowed.DROPPED_QUIETLY:
            self.removed[f"<{tag}>"] += 1

    def _note_removed_styles(self, properties: list[str]) -> None:
        for name in properties:
            self.removed[f"{name} (the studio sets how things look)" if not name.startswith("@")
                         else f"{name} rules"] += 1


def _removed_attribute_label(name: str) -> str:
    if name.startswith("on"):
        return "event handlers (on…)"
    return f"{name} attributes"
