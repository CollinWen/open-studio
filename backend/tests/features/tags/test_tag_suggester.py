"""
Tests for tags/tag_suggester.py: messy LLM output is cleaned into short,
lowercase, unique tags.
"""

from app.features.tags.tag_suggester import MAX_TAGS, _clean_tags


def test_cleans_case_spacing_and_duplicates():
    assert _clean_tags(["Bread", "  bread ", "Machine   Learning"]) == ["bread", "machine learning"]


def test_drops_non_strings_and_long_phrases():
    assert _clean_tags(["art", 3, "a very long sentence about things"]) == ["art"]


def test_caps_number_of_tags():
    assert len(_clean_tags([f"tag{i}" for i in range(10)])) == MAX_TAGS


def test_non_list_reply_gives_no_tags():
    assert _clean_tags({"tags": ["art"]}) == []
