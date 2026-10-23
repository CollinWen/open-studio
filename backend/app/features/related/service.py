"""
Related service: finds the entries closest in meaning to a given entry.

Only entries on the same board count: boards are separate spaces. Within a
board, it ranks by embedding similarity and deliberately ignores kind, so it
can surface connections across topics (a coding project next to a cooking
experiment). Entries without an embedding (e.g. no OpenRouter key
yet) fall back to counting shared tags.
"""

from sqlmodel import Session

from app.auth.viewer import Viewer
from app.features.entries import service as entries_service
from app.features.entries.models import Entry
from app.features.related.similarity import cosine_similarity

DEFAULT_LIMIT = 6


def find_related_entries(
    db: Session, entry: Entry, viewer: Viewer, limit: int = DEFAULT_LIMIT
) -> list[Entry]:
    others = [
        other
        for other in entries_service.list_entries(db, viewer, board=entry.board)
        if other.id != entry.id
    ]
    if entry.embedding:
        ranked = sorted(
            (other for other in others if other.embedding),
            key=lambda other: cosine_similarity(entry.embedding, other.embedding),
            reverse=True,
        )
    else:
        ranked = sorted(
            (other for other in others if _shared_tag_count(entry, other) > 0),
            key=lambda other: _shared_tag_count(entry, other),
            reverse=True,
        )
    return ranked[:limit]


def _shared_tag_count(a: Entry, b: Entry) -> int:
    return len(set(a.tags) & set(b.tags))
