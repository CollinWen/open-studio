"""
Live runs: whether a run's token should still work, checked on every request
that carries one (by auth/viewer.py).

A run token stops working when it expires (checked in auth/run_tokens.py) or
when its run is finished, by the agent or the owner (checked here). Kept apart
from service.py so auth can use it without pulling in the rest of the studio.
"""

from sqlmodel import Session

from app.features.runs.models import Run


def find_live_run(db: Session, run_id: str) -> Run | None:
    run = db.get(Run, run_id)
    if run is None or run.finished_at is not None:
        return None
    return run
