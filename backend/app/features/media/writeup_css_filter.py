"""
Write-up CSS filter: keeps a write-up's arrangement and removes its appearance.

The line: the writer decides how things are laid out (columns, grids,
widths, alignment, gaps, order); the studio decides how they look
(typeface, sizes, colors, backgrounds, borders, shadows, the space between
blocks), from frontend/src/styles/writeup.css. So only the layout
properties below survive, in `style` attributes and `<style>` blocks, and
nothing that could load a file (url(), @import, @font-face) ever does.

Used by writeup_sanitizer.py. The list of properties is repeated for
agents in skills/studio-writeup/SKILL.md; keep the two in step.
"""

import re

LAYOUT_PROPERTIES = {
    "display", "flex", "flex-direction", "flex-wrap", "flex-flow", "flex-grow", "flex-shrink",
    "flex-basis", "justify-content", "justify-items", "justify-self", "align-items",
    "align-content", "align-self", "place-items", "place-content", "place-self", "order",
    "gap", "row-gap", "column-gap", "grid-template", "grid-template-columns",
    "grid-template-rows", "grid-template-areas", "grid-area", "grid-column", "grid-row",
    "grid-column-start", "grid-column-end", "grid-row-start", "grid-row-end", "grid-auto-flow",
    "grid-auto-columns", "grid-auto-rows", "width", "min-width", "max-width", "height",
    "min-height", "max-height", "aspect-ratio", "text-align", "vertical-align", "columns",
    "column-count", "column-width", "break-inside", "break-before", "break-after",
    "table-layout", "white-space", "object-fit", "object-position", "list-style-type",
    "overflow-x",
}
# Letters, numbers, units, quotes (grid areas), var(--line) and calc(). Nothing else.
SAFE_VALUE = re.compile(r"^[A-Za-z0-9\s.,%()'\"+*/_-]*$")
UNSAFE_WORDS = ("url", "expression", "image", "element", "src")
COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
SAFE_MEDIA_QUERY = re.compile(r"^@media[\sA-Za-z0-9():,.-]*$")


def filter_declarations(css: str) -> tuple[str, list[str]]:
    """Keep only the layout declarations of a `style` attribute (or one rule's body).
    Returns what's kept and the names of the properties removed."""
    kept, removed = [], []
    for declaration in COMMENT.sub("", css).split(";"):
        if not declaration.strip():
            continue
        name, _, value = declaration.partition(":")
        name = name.strip().lower()
        value = value.replace("!important", "").strip()
        if name in LAYOUT_PROPERTIES and value and _is_safe_value(value):
            kept.append(f"{name}: {value}")
        else:
            removed.append(name or "unreadable style")
    return "; ".join(kept), removed


def filter_stylesheet(css: str) -> tuple[str, list[str]]:
    """Keep the layout rules of a `<style>` block. @media blocks are kept (filtered
    the same way); every other @ rule (@import, @font-face, @keyframes...) is removed."""
    kept, removed = [], []
    for selector, body in _rules(COMMENT.sub("", css)):
        if selector.startswith("@"):
            if SAFE_MEDIA_QUERY.match(selector):
                inner, inner_removed = filter_stylesheet(body)
                removed += inner_removed
                if inner:
                    kept.append(f"{selector} {{ {inner} }}")
            else:
                removed.append(selector.split()[0].lower())
            continue
        if "<" in selector or "\\" in selector:
            removed.append("unreadable style")
            continue
        declarations, rule_removed = filter_declarations(body)
        removed += rule_removed
        if declarations:
            kept.append(f"{selector} {{ {declarations} }}")
    return "\n".join(kept), removed


def _rules(css: str) -> list[tuple[str, str]]:
    """Split a stylesheet into (selector, body) pairs, keeping nested blocks whole."""
    rules, depth, start, selector = [], 0, 0, ""
    for index, char in enumerate(css):
        if char == "{":
            if depth == 0:
                selector, start = css[start:index].strip(), index + 1
            depth += 1
        elif char == "}" and depth:
            depth -= 1
            if depth == 0:
                rules.append((selector, css[start:index]))
                start = index + 1
        elif char == ";" and depth == 0:
            # A rule with no block, like @import "x.css"; never kept.
            statement = css[start:index].strip()
            if statement:
                rules.append((statement, ""))
            start = index + 1
    return rules


def _is_safe_value(value: str) -> bool:
    lowered = value.lower()
    return bool(SAFE_VALUE.match(value)) and not any(word in lowered for word in UNSAFE_WORDS)
