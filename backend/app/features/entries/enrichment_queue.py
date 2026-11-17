"""
Enrichment queue: runs an entry's enrichment (reading, tags, embedding;
enrichment.py) after it's saved, one entry at a time in the background, so
saving never waits on a model. The entry's tags and Related fill in a few
seconds later.

The work is done on a copy of the entry. Before saving the result it checks
the entry hasn't changed meaning in the meantime (meaning_fingerprint); if it
has, the result is dropped, because that edit queued a newer reading of its own.

The queue lives in memory: a reading still waiting when the backend restarts
is lost, and the entry keeps its old tags and embedding until it's read again
(the owner's "read again" on the entry page, or POST /api/entries/read-all-again).
With READ_IN_BACKGROUND=false (tests), the reading happens right away instead.

Used by entries/service.py.
"""

import logging
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from sqlmodel import Session, select

from app.config import settings
from app.database import engine
from app.features.entries.enrichment import enrich_entry, meaning_fingerprint
from app.features.entries.models import Entry

log = logging.getLogger(__name__)

# One at a time: SQLite takes one writer, and it keeps model calls to a steady trickle.
_worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="enrichment")
# How many readings are queued or under way for each entry (an entry edited twice quickly has two).
_waiting: Counter[str] = Counter()
_waiting_lock = threading.Lock()


def queue_enrichment(entry_id: str, read_again: bool = False) -> None:
    """Read, tag and embed this entry after the current save. `read_again` reads every part afresh."""
    if not settings.read_in_background:
        enrich_and_save(entry_id, read_again)
        return
    with _waiting_lock:
        _waiting[entry_id] += 1
    _worker.submit(_run_queued, entry_id, read_again)


def is_waiting(entry_id: str) -> bool:
    """True while this entry's reading is queued or under way."""
    with _waiting_lock:
        return _waiting[entry_id] > 0


def enrich_and_save(entry_id: str, read_again: bool = False) -> None:
    """Enrich one entry now and save what was found, unless the entry changed meanwhile."""
    with Session(engine) as db:
        stored = db.get(Entry, entry_id)
        if stored is None:
            return
        entry = Entry.model_validate(stored.model_dump())
        before = meaning_fingerprint(stored)
        existing_tags = _tags_in_use(db)

    result = enrich_entry(entry, existing_tags, read_again)
    if result is None:
        return

    with Session(engine) as db:
        stored = db.get(Entry, entry_id)
        if stored is None or meaning_fingerprint(stored) != before:
            return
        stored.readings = result.readings
        if result.tags is not None and not stored.tags:
            stored.tags = result.tags
        if result.embedding is not None:
            stored.embedding = result.embedding
            stored.embedding_model = settings.embedding_model
        db.add(stored)
        db.commit()


def _run_queued(entry_id: str, read_again: bool) -> None:
    try:
        enrich_and_save(entry_id, read_again)
    except Exception:
        log.exception("Enrichment failed for entry %s", entry_id)
    finally:
        with _waiting_lock:
            _waiting[entry_id] -= 1
            if _waiting[entry_id] <= 0:
                del _waiting[entry_id]


def _tags_in_use(db: Session) -> list[str]:
    """Every tag already in use, so new suggestions reuse them instead of inventing near-duplicates."""
    return sorted({tag for tags in db.exec(select(Entry.tags)) for tag in tags or []})
