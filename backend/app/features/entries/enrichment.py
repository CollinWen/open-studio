"""
Enrichment: the automatic work done after an entry is saved or edited, in
three stages that end in one place:

  1. Read each part into words (entry_reading.py): the source link, every
     picture, the write-ups. Each kind of part is read its own way.
  2. Suggest tags with an LLM (only if the entry has none), from all of it.
  3. Embed: one embedding for the whole entry, from one text that puts the
     owner's words first (title, description), then tags, then what was read
     from its parts (build_embedding_text).

It only works things out (enrich_entry returns an Enrichment); saving it is
enrichment_queue.py's job, which runs this after the save, in the background.
If OpenRouter isn't configured or a call fails, the entry keeps what it had;
the owner can have it read again from the entry page.
"""

import hashlib
import json
import logging
from dataclasses import dataclass

from app.config import settings
from app.features.entries.entry_reading import picture_address, picture_key, read_entry_parts
from app.features.entries.models import Entry
from app.features.tags.tag_suggester import suggest_tags
from app.integrations import openrouter_http
from app.integrations.embedding_client import embed_text

log = logging.getLogger(__name__)

# Edits to these fields change an entry's meaning, so it's read and embedded again.
MEANING_FIELDS = ("title", "description", "kind", "source_name", "source_url", "media", "tags", "writeup_text")


@dataclass
class Enrichment:
    readings: dict[str, str]
    # None: leave the entry's tags as they are.
    tags: list[str] | None
    # None: the embedding couldn't be made; keep the old one.
    embedding: list[float] | None


def enrich_entry(entry: Entry, existing_tags: list[str], read_again: bool = False) -> Enrichment | None:
    """Read, tag and embed one entry. None when OpenRouter isn't set up. `read_again` ignores earlier readings."""
    if not openrouter_http.is_configured():
        log.warning("OPENROUTER_API_KEY not set; skipping reading, tags and embedding.")
        return None

    readings = read_entry_parts(entry, earlier={} if read_again else dict(entry.readings or {}))
    tags = None
    if not entry.tags:
        try:
            tags = suggest_tags(
                title=entry.title,
                description=entry.description,
                kind=entry.kind,
                source_name=entry.source_name,
                existing_tags=existing_tags,
                writeup_text=_parts_text(entry, readings),
            )
        except Exception:
            log.exception("Tag suggestion failed for entry %s", entry.id)

    embedding = None
    try:
        embedding = embed_text(build_embedding_text(entry, readings, tags))
    except Exception:
        log.exception("Embedding failed for entry %s", entry.id)
    return Enrichment(readings=readings, tags=tags, embedding=embedding)


def build_embedding_text(entry: Entry, readings: dict[str, str] | None = None, tags: list[str] | None = None) -> str:
    """The text that represents an entry's meaning. Changing this changes what counts as "Related"."""
    readings = entry.readings if readings is None else readings
    tags = tags or entry.tags
    parts = [
        entry.title,
        entry.description,
        f"Kind: {entry.kind}",
        f"Source: {entry.source_name}" if entry.source_name else "",
        f"Tags: {', '.join(tags)}" if tags else "",
        _parts_text(entry, readings or {}),
    ]
    return "\n".join(part for part in parts if part)


def meaning_fingerprint(entry: Entry) -> str:
    """Changes whenever a meaning field does: a reading worked out for an older version isn't saved."""
    values = {field: getattr(entry, field) for field in MEANING_FIELDS}
    return hashlib.sha256(json.dumps(values, sort_keys=True, default=str).encode()).hexdigest()


def _parts_text(entry: Entry, readings: dict[str, str]) -> str:
    """Everything read from the entry's parts: the source, each picture with its caption, the write-up."""
    lines = []
    for key, text in readings.items():
        if key.startswith("source "):
            lines.append(f"From the source: {text}")
    for item in entry.media:
        caption = item.get("caption", "")
        picture = picture_address(item)
        seen = readings.get(picture_key(picture), "") if picture else ""
        if seen:
            lines.append(f"Picture{f' ({caption})' if caption else ''}: {seen}")
        elif caption:
            lines.append(f"Caption: {caption}")
    if entry.writeup_text:
        lines.append(f"Write-up: {entry.writeup_text[: settings.writeup_text_for_meaning]}")
    return "\n".join(lines)
