"""
Write-up allow lists: every tag, attribute, class name and attribute value a
write-up may keep, and how each value is checked. Anything not here is removed.

Used by writeup_sanitizer.py; the layout styles a write-up may keep are in
writeup_css_filter.py. Agents read the same rules in
skills/studio-writeup/SKILL.md, and frontend/src/styles/writeup.css styles
what's kept; change all three together.
"""

import re

from app.features.media.writeup_css_filter import filter_declarations

TEXT_TAGS = {
    "h1", "h2", "h3", "h4", "p", "br", "hr", "ul", "ol", "li", "dl", "dt", "dd",
    "blockquote", "figure", "figcaption", "table", "caption", "thead", "tbody", "tfoot",
    "tr", "th", "td", "pre", "code", "em", "strong", "b", "i", "small", "sub", "sup",
    "mark", "a", "img", "abbr", "cite", "q", "kbd", "span", "div", "section", "article",
    "header", "footer", "aside", "details", "summary",
}
# Drawings: shapes and text, plus arrowheads (marker), hatching (pattern) and reusable shapes (defs, symbol, use).
DRAWING_TAGS = {
    "svg", "g", "path", "line", "polyline", "polygon", "rect", "circle", "ellipse", "text", "tspan",
    "defs", "marker", "pattern", "symbol", "use",
}
VOID_TAGS = {"br", "hr", "img"}
# Tags a browser closes by itself when a sibling starts ("<li>one<li>two").
CLOSED_BY_SIBLING = {"li": {"li"}, "p": {"p"}, "dt": {"dt", "dd"}, "dd": {"dt", "dd"},
                     "tr": {"tr"}, "td": {"td", "th"}, "th": {"td", "th"}}
# Removed together with everything inside them.
DROPPED_WITH_CONTENT = {
    "script", "noscript", "template", "iframe", "object", "embed", "frame", "frameset",
    "form", "input", "button", "select", "textarea", "option", "video", "audio", "source",
    "track", "canvas", "math", "foreignobject", "title", "link", "meta", "base",
}
# Of those, the ones with no closing tag.
DROPPED_VOID = {"meta", "base", "link", "source", "track", "input", "embed", "frame"}
# Removed without a note: they're page furniture, not part of the write-up.
DROPPED_QUIETLY = {"html", "head", "body", "meta", "base", "title"}

# The class names writeup.css gives a look to (lead, soft, faint, wide). A write-up may
# use other names too, to hang its own layout rules on; those can only arrange, not style.
SAFE_CLASS_NAME = re.compile(r"^[A-Za-z][\w-]{0,39}$")

COMMON_ATTRIBUTES = {"id", "class", "title", "role", "aria-label", "aria-hidden", "style"}
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
    "cx", "cy", "r", "rx", "ry", "dx", "dy", "d", "points", "transform", "text-anchor",
    "dominant-baseline", "stroke-width", "stroke-dasharray", "stroke-linecap", "stroke-linejoin",
    "fill", "stroke", "marker-start", "marker-mid", "marker-end", "markerwidth", "markerheight",
    "refx", "refy", "orient", "markerunits", "patternunits", "patterntransform", "href",
}
# The parser lowercases names; SVG wants these spelled its own way.
DRAWING_SPELLING = {
    "viewbox": "viewBox", "preserveaspectratio": "preserveAspectRatio",
    "markerwidth": "markerWidth", "markerheight": "markerHeight", "refx": "refX", "refy": "refY",
    "markerunits": "markerUnits", "patternunits": "patternUnits",
    "patterntransform": "patternTransform",
}

SAFE_ID = re.compile(r"^[A-Za-z][\w-]{0,63}$")
SAFE_SIZE = re.compile(r"^\d+(\.\d+)?(%|px)?$")
SAFE_NUMBER = re.compile(r"^\d{1,4}$")
SAFE_GEOMETRY = re.compile(r"^[0-9A-Za-z.,\s+\-()]*$")
SAFE_WORD = re.compile(r"^[A-Za-z-]+$")
# A reference to something drawn in the same write-up, like an arrowhead: url(#arrow).
INNER_REFERENCE = re.compile(r"^url\(#[A-Za-z][\w-]{0,63}\)$")
DRAWING_COLORS = {"none", "currentcolor"}
EMBEDDED_PICTURE = re.compile(r"^data:image/(png|jpeg|gif|webp);base64,[A-Za-z0-9+/=\s]+$")
LINK_SCHEMES = ("http://", "https://", "mailto:")
# A link to another entry in the studio, by its id: /entry/<id> (skills/linking-entries/).
ENTRY_LINK = re.compile(r"^/entry/[A-Za-z0-9_-]{1,64}$")
INVISIBLE = re.compile(r"[\x00-\x20\x7f]+")


def is_allowed_attribute(tag: str, name: str) -> bool:
    if tag in DRAWING_TAGS:
        return name in COMMON_ATTRIBUTES or name in DRAWING_ATTRIBUTES
    return name in COMMON_ATTRIBUTES or name in TEXT_ATTRIBUTES.get(tag, set())


def check_value(tag: str, name: str, value: str) -> tuple[str | None, list[str]]:
    """The value to keep (None: remove the attribute), and any style properties removed from it."""
    if name == "style":
        kept, removed = filter_declarations(value)
        return kept or None, removed
    return _VALUE_CHECKS.get(name, _check_plain)(tag, value), []


def _check_plain(tag: str, value: str) -> str | None:
    return value if "url(" not in value.lower() and "javascript:" not in value.lower() else None


def _check_class(tag: str, value: str) -> str | None:
    kept = [name for name in value.split() if SAFE_CLASS_NAME.match(name)]
    return " ".join(kept) or None


def _check_href(tag: str, value: str) -> str | None:
    if tag == "use":
        return value if SAFE_ID.match(value.removeprefix("#")) and value.startswith("#") else None
    bare = INVISIBLE.sub("", value).lower()
    if value.startswith("#") or ENTRY_LINK.match(value) or bare.startswith(LINK_SCHEMES):
        return value
    return None


def _check_src(tag: str, value: str) -> str | None:
    return value if EMBEDDED_PICTURE.match(value) else None


def _matches(pattern: re.Pattern):
    return lambda tag, value: value if pattern.match(value) else None


def _check_geometry(tag: str, value: str) -> str | None:
    return value if SAFE_GEOMETRY.match(value) and "url" not in value.lower() else None


def _check_drawing_color(tag: str, value: str) -> str | None:
    return value if value.lower() in DRAWING_COLORS or INNER_REFERENCE.match(value) else None


_VALUE_CHECKS = {
    "class": _check_class,
    "id": _matches(SAFE_ID),
    "href": _check_href,
    "src": _check_src,
    "colspan": _matches(SAFE_NUMBER),
    "rowspan": _matches(SAFE_NUMBER),
    "start": _matches(SAFE_NUMBER),
    "width": _matches(SAFE_SIZE),
    "height": _matches(SAFE_SIZE),
    "fill": _check_drawing_color,
    "stroke": _check_drawing_color,
    **{name: _matches(INNER_REFERENCE) for name in ("marker-start", "marker-mid", "marker-end")},
    **{name: _matches(SAFE_WORD) for name in (
        "scope", "role", "text-anchor", "dominant-baseline", "stroke-linecap", "stroke-linejoin",
        "markerunits", "patternunits",
    )},
    **{name: _check_geometry for name in (
        "viewbox", "preserveaspectratio", "x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx",
        "ry", "dx", "dy", "d", "points", "transform", "stroke-width", "stroke-dasharray",
        "markerwidth", "markerheight", "refx", "refy", "orient", "patterntransform",
    )},
}
