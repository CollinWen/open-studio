"""
Tests for pinned arguments: an exact value or a prefix ("proto-*") is
allowed, anything else is refused; lists must keep to the pins in every
item; a pinned argument the tool takes must be given; one it doesn't take
is no business of the pin; objects and booleans never pass a pin.
"""

import pytest

from app.features.toolkits.pinned_arguments import PinnedArgumentError, check_pinned_arguments

PINS = {"owner": ["CollinWen"], "repo": ["open-studio", "proto-*"]}
SCHEMA = {"properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "title": {"type": "string"}}}


def test_exact_values_and_prefixes_are_allowed():
    check_pinned_arguments(PINS, {"owner": "CollinWen", "repo": "open-studio", "title": "x"}, SCHEMA)
    check_pinned_arguments(PINS, {"owner": "CollinWen", "repo": "proto-folding"}, SCHEMA)


@pytest.mark.parametrize(
    "arguments",
    [
        {"owner": "someone-else", "repo": "open-studio"},
        {"owner": "CollinWen", "repo": "open-studio-fork"},
        {"owner": "CollinWen", "repo": "private-notes"},
        {"owner": "CollinWen", "repo": ["open-studio", "private-notes"]},
        {"owner": "CollinWen", "repo": []},
        {"owner": "CollinWen", "repo": {"name": "open-studio"}},
        {"owner": True, "repo": "open-studio"},
    ],
)
def test_anything_else_is_refused(arguments):
    with pytest.raises(PinnedArgumentError):
        check_pinned_arguments(PINS, arguments, SCHEMA)


def test_a_pinned_argument_the_tool_takes_must_be_given():
    with pytest.raises(PinnedArgumentError, match="repo must be given"):
        check_pinned_arguments(PINS, {"owner": "CollinWen"}, SCHEMA)


def test_a_pin_on_an_argument_the_tool_doesnt_take_doesnt_apply():
    check_pinned_arguments(PINS, {"query": "folding"}, {"properties": {"query": {"type": "string"}}})
    # Without a schema (Composio unreachable), only arguments that are given are checked.
    check_pinned_arguments(PINS, {"query": "folding"}, None)
    with pytest.raises(PinnedArgumentError):
        check_pinned_arguments(PINS, {"repo": "elsewhere"}, None)
