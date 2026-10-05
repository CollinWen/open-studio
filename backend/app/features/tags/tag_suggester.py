"""
Tag suggester: asks an LLM for a few short, plain tags that describe an entry.

Tags should be self-explanatory to a visitor: one or two everyday words,
lowercase ("bread", "machine learning", "portraits"). The LLM is shown the
tags already in use and told to reuse them, so the vocabulary stays small.
"""

from app.integrations.llm_client import ask_llm, extract_json

MAX_TAGS = 4

SYSTEM_PROMPT = f"""You label items in a personal collection of work and interests.
Return 2 to {MAX_TAGS} tags as a JSON array of strings, and nothing else.

Rules for tags:
- lowercase, one or two plain words each (e.g. "bread", "machine learning", "portraits")
- a stranger should understand each tag without explanation
- describe the topic or medium, not opinions ("good", "interesting" are not tags)
- strongly prefer reusing a tag from the existing list when one fits
- only invent a new tag when nothing existing fits"""


def suggest_tags(
    title: str,
    description: str,
    kind: str,
    source_name: str,
    existing_tags: list[str],
) -> list[str]:
    """Return a short list of clean tags for one entry."""
    user_prompt = "\n".join(
        [
            f"Existing tags: {', '.join(existing_tags) or '(none yet)'}",
            "",
            f"Title: {title}",
            f"Kind: {kind}",
            f"Source: {source_name or '(my own work)'}",
            f"Description: {description or '(none)'}",
        ]
    )
    reply = extract_json(ask_llm(SYSTEM_PROMPT, user_prompt))
    return _clean_tags(reply)


def _clean_tags(raw: object) -> list[str]:
    """Lowercase, trim, drop duplicates and anything that isn't a short string."""
    if not isinstance(raw, list):
        return []
    tags: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            continue
        tag = " ".join(item.lower().split())
        if tag and len(tag.split()) <= 3 and tag not in tags:
            tags.append(tag)
    return tags[:MAX_TAGS]
