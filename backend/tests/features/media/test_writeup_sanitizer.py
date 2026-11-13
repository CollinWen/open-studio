"""
Tests for media/writeup_sanitizer.py: a write-up keeps its words, structure,
embedded pictures and simple drawings, and loses everything that could run,
restyle the page or reach outside it, with a note of what was removed.
The skill's example write-up must come through untouched.
"""

from pathlib import Path

from app.features.media.writeup_sanitizer import sanitize_writeup


def _kept(html: str) -> str:
    return sanitize_writeup(html)[0]


def test_plain_writing_is_kept_as_it_is():
    html = '<h1>Crumb</h1><p class="lead">Open <em>and</em> even.</p><table><tr><th scope="col">a</th></tr></table>'
    assert _kept(html) == html


def test_scripts_styles_and_handlers_are_removed_and_noted():
    kept, removed = sanitize_writeup(
        '<style>p{color:red}</style><script>alert(1)</script>'
        '<link rel="stylesheet" href="https://x.com/a.css">'
        '<p style="color:red" onclick="steal()">words</p>'
    )
    assert kept == "<p>words</p>"
    assert {"<style>: 1", "<script>: 1", "linked stylesheets and files: 1",
            "style attributes: 1", "event handlers (on…): 1"} <= set(removed)


def test_a_whole_page_is_reduced_to_its_body():
    page = "<!DOCTYPE html><html><head><title>T</title><meta charset=utf-8></head><body><p>hi</p></body></html>"
    kept, removed = sanitize_writeup(page)
    assert kept == "<p>hi</p>"
    assert removed == []


def test_only_embedded_pictures_are_kept():
    embedded = '<img src="data:image/png;base64,iVBORw0KGgo=" alt="crumb">'
    kept, removed = sanitize_writeup(embedded + '<img src="https://tracker.example.com/pixel.gif">')
    assert kept == embedded
    assert "pictures not written into the file: 1" in removed


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


def test_drawings_keep_their_shape_but_take_the_studio_ink():
    kept = _kept(
        '<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M0 0L10 10" stroke="red" fill="currentColor"/>'
        '<rect width="2" height="2" fill="url(#pattern)" class="soft"/></svg>'
    )
    assert kept == (
        '<svg viewBox="0 0 10 10"><path d="M0 0L10 10" fill="currentColor"></path>'
        '<rect width="2" height="2" class="soft"></rect></svg>'
    )


def test_only_the_studio_class_names_survive():
    assert _kept('<p class="lead hero-banner text-xl">a</p>') == '<p class="lead">a</p>'
    assert _kept('<p class="hero">a</p>') == "<p>a</p>"


def test_text_is_never_turned_back_into_tags():
    assert _kept("<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>") == "<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>"


def test_unclosed_tags_are_closed():
    assert _kept("<ul><li>one<li>two") == "<ul><li>one</li><li>two</li></ul>"


def test_the_skills_example_write_up_keeps_everything():
    """skills/studio-writeup/example.html shows agents what survives; it must survive whole."""
    example = Path(__file__).resolve().parents[4] / "skills" / "studio-writeup" / "example.html"
    assert sanitize_writeup(example.read_text())[1] == []
