"""
Pinned arguments: the check that a toolkit call keeps to the values the
owner allowed, e.g. GitHub's "repo" only "open-studio" or "proto-*". An
allowed value ending in "*" allows any value starting with the rest; any
other must match exactly. A list argument must keep to them in every item.
A pinned argument the tool takes must be given, so a tool's own default
(say, every repository) can't slip past the pin.

Pins only fence the arguments they name, so grant tools whose reach those
arguments decide (GitHub's owner and repo), not tools that search widely.
Used by toolkits/service.py.
"""

from typing import Any


class PinnedArgumentError(Exception):
    """A call goes outside a pinned argument's allowed values."""


def check_pinned_arguments(pins: dict[str, list[str]], arguments: dict[str, Any], input_schema: dict | None) -> None:
    takes = set((input_schema or {}).get("properties", {}))
    for name, allowed in pins.items():
        if name not in arguments:
            if name in takes:
                raise PinnedArgumentError(f"{name} must be given, as one of: {', '.join(allowed)}")
            continue
        value = arguments[name]
        values = value if isinstance(value, list) else [value]
        if not values or not all(_allowed(item, allowed) for item in values):
            raise PinnedArgumentError(f"{name} may only be: {', '.join(allowed)} (not {value!r})")


def _allowed(value: Any, allowed: list[str]) -> bool:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        return False
    text = str(value)
    return any(text.startswith(pin[:-1]) if pin.endswith("*") else text == pin for pin in allowed)
