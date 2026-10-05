"""
Enrichment: the automatic work done after an entry is saved or edited.

  1. Suggest tags with an LLM (only if the entry has none).
  2. Compute an embedding from the entry's text.

If OpenRouter isn't configured or a call fails, the entry is still saved;
it just goes without tags or an embedding until the next edit.
"""

import logging

from app.config import settings
from app.features.entries.models import Entry
from app.features.tags.tag_suggester import suggest_tags
from app.integrations import openrouter_http
from app.integrations.embedding_client import embed_text

log = logging.getLogger(__name__)


def enrich_entry(entry: Entry, existing_tags: list[str]) -> None:
    """Fill in missing tags and refresh the embedding, in place."""
    if not openrouter_http.is_configured():
        log.warning("OPENROUTER_API_KEY not set; skipping tags and embedding.")
        return

    if not entry.tags:
        try:
            entry.tags = suggest_tags(
                title=entry.title,
                description=entry.description,
                kind=entry.kind,
                source_name=entry.source_name,
                existing_tags=existing_tags,
            )
        except Exception:
            log.exception("Tag suggestion failed for entry %s", entry.id)

    try:
        entry.embedding = embed_text(build_embedding_text(entry))
        entry.embedding_model = settings.embedding_model
    except Exception:
        log.exception("Embedding failed for entry %s", entry.id)


def build_embedding_text(entry: Entry) -> str:
    """The text that represents an entry's meaning. Changing this changes what counts as "Related"."""
    parts = [
        entry.title,
        entry.description,
        f"Kind: {entry.kind}",
        f"Source: {entry.source_name}" if entry.source_name else "",
        f"Tags: {', '.join(entry.tags)}" if entry.tags else "",
    ]
    return "\n".join(part for part in parts if part)
