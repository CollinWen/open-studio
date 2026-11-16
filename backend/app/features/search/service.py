"""
Search service: finds entries for a typed query, by meaning as well as words.

  - semantic: the query is turned into an embedding and compared with every
    entry's embedding, so "bread" can find a sourdough entry that never says "bread"
  - text: entries whose title, description, tags, kind, source, write-up or readings
    (what was read from their pictures and source link) contain the query come first

Every entry that contains the query is returned, however many there are, so
a search never quietly hides one; only the entries found by meaning alone
are capped (RESULT_LIMIT in all), since that list grows looser as it goes.
Only embeddings from the current model are compared.

Without an OpenRouter key (or before entries have embeddings), only the text
match is used.
"""

import logging

from sqlmodel import Session

from app.auth.viewer import Viewer
from app.config import settings
from app.features.entries import service as entries_service
from app.features.entries.models import Entry
from app.features.related.similarity import cosine_similarity
from app.integrations import openrouter_http
from app.integrations.embedding_client import embed_text

log = logging.getLogger(__name__)

# The most results, counting entries that contain the query; meaning-only ones fill up to it.
RESULT_LIMIT = 24
# How alike (0..1) an entry must be to the query to count as a match by meaning.
# Raise it for fewer, closer results; lower it for more, looser ones.
MIN_SIMILARITY = 0.25


def search_entries(db: Session, query: str, viewer: Viewer, board: str | None = None) -> list[Entry]:
    """`board` searches one board (every board when None)."""
    query = query.strip()
    if not query:
        return []
    entries = entries_service.list_entries(db, viewer, board=board)
    query_vector = _embed_query(query) if any(entry.embedding for entry in entries) else None

    with_words: list[tuple[float, Entry]] = []
    by_meaning_only: list[tuple[float, Entry]] = []
    for entry in entries:
        similarity = (
            cosine_similarity(query_vector, entry.embedding)
            if query_vector and entry.embedding and entry.embedding_model == settings.embedding_model
            else 0.0
        )
        if _contains(entry, query):
            with_words.append((similarity, entry))
        elif similarity >= MIN_SIMILARITY:
            by_meaning_only.append((similarity, entry))

    with_words.sort(key=lambda pair: pair[0], reverse=True)
    by_meaning_only.sort(key=lambda pair: pair[0], reverse=True)
    room_left = max(0, RESULT_LIMIT - len(with_words))
    return [entry for _, entry in with_words + by_meaning_only[:room_left]]


def _embed_query(query: str) -> list[float] | None:
    if not openrouter_http.is_configured():
        return None
    try:
        return embed_text(query)
    except Exception:
        log.exception("Embedding the search query failed; falling back to text search.")
        return None


def _contains(entry: Entry, query: str) -> bool:
    haystack = " ".join(
        [entry.title, entry.description, entry.kind, entry.source_name, entry.writeup_text, *entry.tags,
         *(entry.readings or {}).values()]
    )
    return query.lower() in haystack.lower()
