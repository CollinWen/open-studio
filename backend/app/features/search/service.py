"""
Search service: finds entries for a typed query, by meaning as well as words.

  - semantic: the query is turned into an embedding and compared with every
    entry's embedding, so "bread" can find a sourdough entry that never says "bread"
  - text: entries whose title, description, tags, kind or source contain the
    query get a boost, so exact matches come first

Without an OpenRouter key (or before entries have embeddings), only the text
match is used.
"""

import logging

from sqlmodel import Session

from app.features.entries import service as entries_service
from app.features.entries.models import Entry
from app.features.related.similarity import cosine_similarity
from app.integrations import openrouter_http
from app.integrations.embedding_client import embed_text

log = logging.getLogger(__name__)

RESULT_LIMIT = 24
# How alike (0..1) an entry must be to the query to count as a match by meaning.
# Raise it for fewer, closer results; lower it for more, looser ones.
MIN_SIMILARITY = 0.25
TEXT_MATCH_BOOST = 1.0


def search_entries(db: Session, query: str, include_private: bool = False) -> list[Entry]:
    query = query.strip()
    if not query:
        return []
    entries = entries_service.list_entries(db, include_private=include_private)
    query_vector = _embed_query(query) if any(entry.embedding for entry in entries) else None

    scored: list[tuple[float, Entry]] = []
    for entry in entries:
        similarity = (
            cosine_similarity(query_vector, entry.embedding) if query_vector and entry.embedding else 0.0
        )
        text_match = _contains(entry, query)
        if text_match or similarity >= MIN_SIMILARITY:
            scored.append((similarity + (TEXT_MATCH_BOOST if text_match else 0.0), entry))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [entry for _, entry in scored[:RESULT_LIMIT]]


def _embed_query(query: str) -> list[float] | None:
    if not openrouter_http.is_configured():
        return None
    try:
        return embed_text(query)
    except Exception:
        log.exception("Embedding the search query failed; falling back to text search.")
        return None


def _contains(entry: Entry, query: str) -> bool:
    haystack = " ".join([entry.title, entry.description, entry.kind, entry.source_name, *entry.tags])
    return query.lower() in haystack.lower()
