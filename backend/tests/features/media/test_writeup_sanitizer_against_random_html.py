"""
Tests media/writeup_sanitizer.py against made-up hostile HTML: a fixed-seed
generator strings together tags, attributes and values known to sneak code
or outside requests past sanitizers (event handlers, javascript: links,
style escapes, unclosed and stray tags, SVG animation) and checks every
result. Nothing that can run or reach outside may survive, and sanitizing
a result again changes nothing.

The hand-picked cases live in test_writeup_sanitizer.py; this one is the
safety net for when the allow lists or the parser change.
"""

import random
import re
from html.parser import HTMLParser

from app.features.media.writeup_sanitizer import sanitize_writeup

CASES = 1500
SEED = 7

TAGS = ["p", "a", "img", "svg", "math", "style", "script", "table", "td", "tr", "div", "span", "noscript",
        "template", "textarea", "title", "iframe", "object", "foreignObject", "use", "animate", "set", "mtext",
        "mglyph", "select", "xmp", "noembed", "plaintext", "figure", "pre", "!--", "![CDATA[", "/p", "/svg",
        "/style", "/math", "/a", "/textarea", "/noscript"]
ATTRIBUTES = ["href", "src", "style", "onerror", "onload", "onclick", "title", "class", "id", "xlink:href", "srcdoc",
              "formaction", "data", "width", "viewBox", "d", "target", "srcset", "attributeName", "values", "to"]
VALUES = ["javascript:alert(1)", "jav&#x61;script:alert(1)", "java\tscript:alert(1)", "  JAVASCRIPT:alert(1)",
          "data:text/html,<script>alert(1)</script>", "https://evil.example/x", "x", "alert(1)",
          '"><script>alert(1)</script>', "'><img src=x onerror=alert(1)>", "background:url(https://evil.example/t)",
          "width:expression(alert(1))", "</style><script>alert(1)</script>", "--><script>alert(1)</script>",
          "data:image/png;base64,AAAA", "#x"]
TEXTS = ["hello", "<", "&", ">", '"', "'", "</", "<!--", "-->", "]]>", "<script>alert(1)</script>"]

URL_ATTRIBUTES = {"href", "src", "xlink:href", "action", "formaction", "data", "poster", "background", "srcdoc", "srcset"}
LOADING_ATTRIBUTES = {"src", "srcset", "poster", "background", "data"}
RUNS_CODE = re.compile(r"^(javascript|vbscript|data:(?!image/))", re.IGNORECASE)
REACHES_OUT_IN_CSS = re.compile(r"url\(|@import|expression|\\", re.IGNORECASE)
NEVER_KEPT_TAGS = {"script", "iframe", "object", "embed", "form", "base", "meta", "link", "frame", "template",
                   "foreignobject", "animate", "set", "textarea", "select", "input", "button"}


def test_random_hostile_html_never_keeps_anything_that_runs_or_reaches_out():
    generator = random.Random(SEED)
    for _ in range(CASES):
        source = _hostile_fragment(generator)
        result = sanitize_writeup(source).html
        problems = _problems_in(result)
        assert not problems, f"{problems} kept from {source!r} as {result!r}"
        assert sanitize_writeup(result).html == result, f"not stable: {source!r}"


def _hostile_fragment(generator: random.Random, depth: int = 0) -> str:
    parts = []
    for _ in range(generator.randint(1, 5)):
        if generator.random() < 0.55 and depth < 4:
            tag = generator.choice(TAGS)
            attributes = "".join(
                f" {generator.choice(ATTRIBUTES)}{generator.choice(['=', '= ', ''])}"
                f"{generator.choice(['\"', '\'', ''])}{generator.choice(VALUES)}{generator.choice(['\"', '\'', ''])}"
                for _ in range(generator.randint(0, 3))
            )
            parts.append(f"<{tag}{attributes}{generator.choice(['>', '/>', ' >', ''])}{_hostile_fragment(generator, depth + 1)}")
            if generator.random() < 0.6 and not tag.startswith(("/", "!")):
                parts.append(f"</{tag}>")
        else:
            parts.append(generator.choice(TEXTS))
    return "".join(parts)


def _problems_in(html: str) -> list[str]:
    reader = _TagReader()
    reader.feed(html)
    reader.close()
    return reader.problems


class _TagReader(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.problems: list[str] = []
        self._in_style = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in NEVER_KEPT_TAGS:
            self.problems.append(f"<{tag}>")
        self._in_style = tag == "style"
        for name, value in attrs:
            plain = re.sub(r"[\x00-\x20]", "", value or "")
            if name.startswith("on"):
                self.problems.append(f"{name}=")
            if name in URL_ATTRIBUTES and RUNS_CODE.match(plain):
                self.problems.append(f"{name}={value!r}")
            if name in LOADING_ATTRIBUTES and not plain.lower().startswith("data:image/"):
                self.problems.append(f"outside {name}={value!r}")
            if name == "style" and REACHES_OUT_IN_CSS.search(value or ""):
                self.problems.append(f"style={value!r}")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self._in_style = False

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False

    def handle_data(self, data: str) -> None:
        if self._in_style and REACHES_OUT_IN_CSS.search(data):
            self.problems.append(f"<style> {data[:40]!r}")
