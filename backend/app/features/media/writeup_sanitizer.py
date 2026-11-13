"""
Write-up sanitizer: turns whatever HTML an agent (or the owner) sends into a
plain, self-contained write-up the studio can show safely.

Everything not on the allow lists below is removed: scripts, styles (style
tags, style attributes, linked stylesheets), fonts, forms, frames, event
handlers, and anything that would load from elsewhere. Pictures must be
written into the file (data: URLs); links may point out, but only open, in
a new tab, when clicked. Unknown tags are dropped but their text is kept. The look always
comes from the studio's own stylesheet (frontend/src/styles/writeup.css),
never from the write-up.

Used by media/service.py. The skill that tells agents what survives is
skills/studio-writeup/SKILL.md; keep the two in step.
"""

import re
from collections import Counter
from html import escape
from html.parser import HTMLParser

TEXT_TAGS = {
    "h1", "h2", "h3", "h4", "p", "br", "hr", "ul", "ol", "li", "dl", "dt", "dd",
    "blockquote", "figure", "figcaption", "table", "caption", "thead", "tbody", "tfoot",
    "tr", "th", "td", "pre", "code", "em", "strong", "b", "i", "small", "sub", "sup",
    "mark", "a", "img", "abbr", "cite", "q", "kbd", "span", "div", "section", "article",
    "header", "footer", "aside", "details", "summary",
}
DRAWING_TAGS = {
    "svg", "g", "path", "line", "polyline", "polygon", "rect", "circle", "ellipse", "text", "tspan",
}
VOID_TAGS = {"br", "hr", "img"}
# Tags a browser closes by itself when a sibling starts ("<li>one<li>two").
CLOSED_BY_SIBLING = {"li": {"li"}, "p": {"p"}, "dt": {"dt", "dd"}, "dd": {"dt", "dd"},
                     "tr": {"tr"}, "td": {"td", "th"}, "th": {"td", "th"}}
# Removed together with everything inside them.
DROPPED_WITH_CONTENT = {
    "script", "style", "noscript", "template", "iframe", "object", "embed", "frame", "frameset",
    "form", "input", "button", "select", "textarea", "option", "video", "audio", "source",
    "track", "canvas", "math", "foreignobject", "title", "link", "meta", "base",
}
# Of those, the ones with no closing tag.
DROPPED_VOID = {"meta", "base", "link", "source", "track", "input", "embed", "frame"}
# Removed without a note: they're page furniture, not part of the write-up.
DROPPED_QUIETLY = {"html", "head", "body", "meta", "base", "title"}

# The class names writeup.css gives meaning to. Others are removed.
CLASS_NAMES = {"lead", "soft", "faint", "wide"}

COMMON_ATTRIBUTES = {"id", "class", "title", "role", "aria-label", "aria-hidden"}
TEXT_ATTRIBUTES = {
    "a": {"href"},
    "img": {"src", "alt", "width", "height"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan", "scope"},
    "ol": {"start"},
    "abbr": {"title"},
}
DRAWING_ATTRIBUTES = {
    "viewbox", "width", "height", "preserveaspectratio", "x", "y", "x1", "y1", "x2", "y2",
    "cx", "cy", "r", "rx", "ry", "d", "points", "transform", "text-anchor", "dominant-baseline",
    "stroke-width", "stroke-dasharray", "stroke-linecap", "stroke-linejoin", "fill", "stroke",
}
# The parser lowercases names; SVG wants these spelled its own way.
DRAWING_SPELLING = {"viewbox": "viewBox", "preserveaspectratio": "preserveAspectRatio"}

SAFE_ID = re.compile(r"^[A-Za-z][\w-]{0,63}$")
SAFE_SIZE = re.compile(r"^\d+(\.\d+)?(%|px)?$")
SAFE_NUMBER = re.compile(r"^\d{1,4}$")
SAFE_GEOMETRY = re.compile(r"^[0-9A-Za-z.,\s+\-()]*$")
SAFE_WORD = re.compile(r"^[A-Za-z-]+$")
DRAWING_COLORS = {"none", "currentcolor"}
EMBEDDED_PICTURE = re.compile(r"^data:image/(png|jpeg|gif|webp);base64,[A-Za-z0-9+/=\s]+$")
LINK_SCHEMES = ("http://", "https://", "mailto:")
INVISIBLE = re.compile(r"[\x00-\x20\x7f]+")


def sanitize_writeup(html: str) -> tuple[str, list[str]]:
    """The safe write-up, and a plain list of what was removed (empty if nothing was)."""
    parser = _WriteupParser()
    parser.feed(html)
    parser.close()
    return parser.finish(), sorted(f"{what}: {count}" for what, count in parser.removed.items())


class _WriteupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.open_tags: list[str] = []
        self.dropping: list[str] = []
        self.removed: Counter[str] = Counter()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.dropping:
            # Only the dropped tag's own name matters for finding where it ends.
            if tag == self.dropping[-1]:
                self.dropping.append(tag)
            return
        if tag in DROPPED_WITH_CONTENT:
            self._note_removed_tag(tag)
            if tag not in DROPPED_VOID:
                self.dropping.append(tag)
            return
        if tag not in TEXT_TAGS and tag not in DRAWING_TAGS:
            if tag not in DROPPED_QUIETLY:
                self.removed[f"<{tag}> (its text kept)"] += 1
            return
        kept = "".join(self._attribute(tag, name, value or "") for name, value in attrs)
        if tag == "a" and ' href="' in kept and ' href="#' not in kept:
            kept += ' target="_blank" rel="noopener noreferrer"'  # Links out open beside the studio.
        if tag == "img" and ' src="' not in kept:
            self.removed["pictures not written into the file"] += 1
            return
        if self.open_tags and self.open_tags[-1] in CLOSED_BY_SIBLING.get(tag, set()):
            self.out.append(f"</{self.open_tags.pop()}>")
        self.out.append(f"<{tag}{kept}>")
        if tag not in VOID_TAGS:
            self.open_tags.append(tag)

    def _note_removed_tag(self, tag: str) -> None:
        if tag == "link":
            self.removed["linked stylesheets and files"] += 1
        elif tag not in DROPPED_QUIETLY:
            self.removed[f"<{tag}>"] += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag in DRAWING_TAGS and self.open_tags and self.open_tags[-1] == tag:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if self.dropping:
            if tag == self.dropping[-1]:
                self.dropping.pop()
            return
        if tag not in self.open_tags:
            return
        while self.open_tags:
            closing = self.open_tags.pop()
            self.out.append(f"</{closing}>")
            if closing == tag:
                break

    def handle_data(self, data: str) -> None:
        if not self.dropping:
            self.out.append(escape(data, quote=False))

    def handle_comment(self, data: str) -> None:
        pass  # Comments are dropped quietly: they never show.

    def finish(self) -> str:
        self.out.extend(f"</{tag}>" for tag in reversed(self.open_tags))
        self.open_tags = []
        return "".join(self.out).strip()

    def _attribute(self, tag: str, name: str, value: str) -> str:
        kept = self._kept_value(tag, name, value.strip())
        if kept is None:
            return ""
        name = DRAWING_SPELLING.get(name, name)
        return f' {name}="{escape(kept, quote=True)}"'

    def _kept_value(self, tag: str, name: str, value: str) -> str | None:
        """The value to keep, or None to remove the attribute (noting why)."""
        if tag in DRAWING_TAGS:
            allowed = name in COMMON_ATTRIBUTES or name in DRAWING_ATTRIBUTES or name == "xmlns"
        else:
            allowed = name in COMMON_ATTRIBUTES or name in TEXT_ATTRIBUTES.get(tag, set())
        if not allowed:
            self.removed[_removed_attribute_label(name)] += 1
            return None
        if name == "xmlns":
            return None  # Not needed inside an HTML page.
        check = _VALUE_CHECKS.get(name, _check_plain)
        kept = check(tag, value)
        if kept is None and name != "src":
            self.removed[f"{name} values the studio can't keep"] += 1
        return kept


def _removed_attribute_label(name: str) -> str:
    if name.startswith("on"):
        return "event handlers (on…)"
    if name == "style":
        return "style attributes"
    return f"{name} attributes"


def _check_plain(tag: str, value: str) -> str | None:
    return value if "url(" not in value.lower() and "javascript:" not in value.lower() else None


def _check_class(tag: str, value: str) -> str | None:
    kept = [name for name in value.split() if name in CLASS_NAMES]
    return " ".join(kept) or None


def _check_href(tag: str, value: str) -> str | None:
    bare = INVISIBLE.sub("", value).lower()
    return value if value.startswith("#") or bare.startswith(LINK_SCHEMES) else None


def _check_src(tag: str, value: str) -> str | None:
    return value if EMBEDDED_PICTURE.match(value) else None


def _check_size(tag: str, value: str) -> str | None:
    return value if SAFE_SIZE.match(value) else None


def _check_number(tag: str, value: str) -> str | None:
    return value if SAFE_NUMBER.match(value) else None


def _check_id(tag: str, value: str) -> str | None:
    return value if SAFE_ID.match(value) else None


def _check_geometry(tag: str, value: str) -> str | None:
    return value if SAFE_GEOMETRY.match(value) and "url" not in value.lower() else None


def _check_word(tag: str, value: str) -> str | None:
    return value if SAFE_WORD.match(value) else None


def _check_drawing_color(tag: str, value: str) -> str | None:
    return value if value.lower() in DRAWING_COLORS else None


_VALUE_CHECKS = {
    "class": _check_class,
    "id": _check_id,
    "href": _check_href,
    "src": _check_src,
    "colspan": _check_number,
    "rowspan": _check_number,
    "start": _check_number,
    "scope": _check_word,
    "role": _check_word,
    "width": _check_size,
    "height": _check_size,
    "fill": _check_drawing_color,
    "stroke": _check_drawing_color,
    "text-anchor": _check_word,
    "dominant-baseline": _check_word,
    "stroke-linecap": _check_word,
    "stroke-linejoin": _check_word,
    **{name: _check_geometry for name in (
        "viewbox", "preserveaspectratio", "x", "y", "x1", "y1", "x2", "y2", "cx", "cy",
        "r", "rx", "ry", "d", "points", "transform", "stroke-width", "stroke-dasharray",
    )},
}
