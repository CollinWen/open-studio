"""
Tests for media/writeup_css_filter.py: layout declarations survive, appearance
and anything that could load a file never do, in style attributes and blocks.
"""

from app.features.media.writeup_css_filter import filter_declarations, filter_stylesheet


def test_layout_is_kept_and_looks_are_removed():
    kept, removed = filter_declarations("display:flex; gap: calc(2 * var(--line)); color: red; margin: 40px")
    assert kept == "display: flex; gap: calc(2 * var(--line))"
    assert removed == ["color", "margin"]


def test_a_layout_property_that_tries_to_load_something_is_removed():
    kept, removed = filter_declarations("width: url(https://x.com/a); height: 10px")
    assert kept == "height: 10px"
    assert removed == ["width"]


def test_important_is_dropped_so_the_studio_stays_in_charge():
    assert filter_declarations("width: 50% !important")[0] == "width: 50%"


def test_only_media_blocks_survive_among_the_at_rules():
    kept, removed = filter_stylesheet(
        "@import 'x.css'; @keyframes spin { to { width: 1px } } "
        "@media (max-width: 600px) { .a { display: block } }"
    )
    assert kept == "@media (max-width: 600px) { .a { display: block } }"
    assert removed == ["@import", "@keyframes"]


def test_a_selector_that_could_end_the_style_block_is_removed():
    kept, _ = filter_stylesheet("</style><script>x</script> { width: 1px } p { width: 2px }")
    assert kept == "p { width: 2px }"
