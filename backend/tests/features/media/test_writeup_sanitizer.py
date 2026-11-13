"""
Tests for media/writeup_sanitizer.py: a write-up keeps its words, structure,
embedded pictures and simple drawings, and loses everything that could run,
restyle the page or reach outside it, with a note of what was removed.
The skill's example write-up must come through untouched.
"""

from pathlib import Path

from app.features.media.writeup_sanitizer import sanitize_writeup


def _kept(html: str) -> str:
    return sanitize_writeup(html).html


def _removed(html: str) -> list[str]:
    return sanitize_writeup(html).removed


def test_plain_writing_is_kept_as_it_is():
    html = '<h1>Crumb</h1><p class="lead">Open <em>and</em> even.</p><table><tr><th scope="col">a</th></tr></table>'
    assert _kept(html) == html


def test_scripts_styles_and_handlers_are_removed_and_noted():
    result = sanitize_writeup(
        '<script>alert(1)</script>'
        '<link rel="stylesheet" href="https://x.com/a.css">'
        '<p onclick="steal()">words</p>'
    )
    assert result.html == "<p>words</p>"
    assert {"<script>: 1", "linked stylesheets and files: 1", "event handlers (on…): 1"} <= set(result.removed)


def test_a_whole_page_is_reduced_to_its_body():
    page = "<!DOCTYPE html><html><head><title>T</title><meta charset=utf-8></head><body><p>hi</p></body></html>"
    result = sanitize_writeup(page)
    assert result.html == "<p>hi</p>"
    assert result.removed == []


def test_only_embedded_pictures_are_kept():
    embedded = '<img src="data:image/png;base64,iVBORw0KGgo=" alt="crumb">'
    result = sanitize_writeup(embedded + '<img src="https://tracker.example.com/pixel.gif">')
    assert result.html == embedded
    assert "pictures not written into the file: 1" in result.removed


def test_links_point_out_but_never_run_code():
    out = '<a href="https://example.com" target="_blank" rel="noopener noreferrer">a</a>'
    assert _kept('<a href="https://example.com" target="_top">a</a>') == out
    assert _kept('<a href="#notes">a</a>') == '<a href="#notes">a</a>'
    assert _kept('<a href=" java\tscript:alert(1)">a</a>') == "<a>a</a>"
    assert _kept('<a href="data:text/html,<script>">a</a>') == "<a>a</a>"


def test_frames_forms_and_media_players_are_removed_with_their_contents():
    html = '<iframe src="https://x.com">x</iframe><form><input name="a"><p>in</p></form><p>after</p>'
    assert _kept(html) == "<p>after</p>"


def test_unknown_tags_are_dropped_but_their_text_stays():
    assert _kept("<custom-box><p>kept</p></custom-box>") == "<p>kept</p>"


def test_layout_styles_stay_and_appearance_goes():
    result = sanitize_writeup(
        '<div style="display: grid; grid-template-columns: 2fr 1fr; gap: var(--gutter); '
        'color: hotpink; font-family: Papyrus">two columns</div>'
    )
    assert result.html == (
        '<div style="display: grid; grid-template-columns: 2fr 1fr; gap: var(--gutter)">two columns</div>'
    )
    assert {"color (the studio sets how things look): 1",
            "font-family (the studio sets how things look): 1"} <= set(result.removed)


def test_style_blocks_keep_only_layout_rules():
    result = sanitize_writeup(
        "<style>@import url(https://x.com/a.css); @font-face { font-family: X; src: url(x.woff) }"
        ".pair { display: flex; gap: 22px; background: url(https://x.com/track.png); color: red }"
        "@media (max-width: 600px) { .pair { flex-direction: column; font-size: 40px } }"
        "h1 { font-size: 90px }</style><p>x</p>"
    )
    assert result.html == (
        "<style>.pair { display: flex; gap: 22px }\n"
        "@media (max-width: 600px) { .pair { flex-direction: column } }</style><p>x</p>"
    )
    assert {"@import rules: 1", "@font-face rules: 1"} <= set(result.removed)


def test_a_style_block_can_never_close_itself_early():
    html = _kept("<style>p { width: 1px } </style><script>alert(1)</script><style>a{width:2px}</style>")
    assert "<script>" not in html


def test_diagrams_keep_arrowheads_hatching_and_reused_shapes():
    html = (
        '<svg viewBox="0 0 10 10"><defs>'
        '<marker id="arrow" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M0 0L6 3L0 6" fill="currentColor"></path></marker>'
        '<pattern id="hatch" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0 4L4 0"></path></pattern>'
        '</defs><line x1="0" y1="0" x2="9" y2="9" marker-end="url(#arrow)"></line>'
        '<rect width="4" height="4" fill="url(#hatch)"></rect><use href="#arrow"></use></svg>'
    )
    assert _kept(html) == html
    assert _kept('<svg><use href="https://x.com/s.svg#a"></use></svg>') == "<svg><use></use></svg>"
    assert _kept('<svg><rect fill="url(https://x.com/a.png)"></rect></svg>') == "<svg><rect></rect></svg>"


def test_the_text_a_reader_sees_is_read_out_for_tags_and_search():
    result = sanitize_writeup("<style>p { width: 1px }</style><h1>Crumb</h1><p>Open <em>and</em> even.</p><script>no</script>")
    assert result.text == "Crumb Open and even."


def test_drawings_keep_their_shape_but_take_the_studio_ink():
    kept = _kept(
        '<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M0 0L10 10" stroke="red" fill="currentColor"/>'
        '<rect width="2" height="2" fill="#c00" class="soft"/></svg>'
    )
    assert kept == (
        '<svg viewBox="0 0 10 10"><path d="M0 0L10 10" fill="currentColor"></path>'
        '<rect width="2" height="2" class="soft"></rect></svg>'
    )


def test_class_names_stay_so_layout_rules_can_use_them():
    assert _kept('<p class="lead pair">a</p>') == '<p class="lead pair">a</p>'
    assert _kept('<p class="x&quot;onclick">a</p>') == "<p>a</p>"


def test_text_is_never_turned_back_into_tags():
    assert _kept("<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>") == "<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>"


def test_unclosed_tags_are_closed():
    assert _kept("<ul><li>one<li>two") == "<ul><li>one</li><li>two</li></ul>"


def test_the_skills_example_write_up_keeps_everything():
    """skills/studio-writeup/example.html shows agents what survives; it must survive whole."""
    example = Path(__file__).resolve().parents[4] / "skills" / "studio-writeup" / "example.html"
    assert sanitize_writeup(example.read_text()).removed == []
