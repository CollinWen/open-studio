"""
Agent write limit: how many entries each agent may add or edit per hour
(AGENT_WRITES_PER_HOUR), so a runaway agent can't flood the studio or the
OpenRouter bill.

Counts are kept in memory, which is right while the backend runs on one
machine; with several machines this would move to a shared store.
Used by auth/viewer.py.
"""

import time
from collections import defaultdict, deque
from threading import Lock

from app.config import settings

WINDOW_SECONDS = 3600

_recent_writes: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def record_agent_write(agent_name: str) -> bool:
    """Count one write for this agent. False (and nothing counted) when it is over its limit."""
    now = time.monotonic()
    with _lock:
        writes = _recent_writes[agent_name]
        while writes and writes[0] <= now - WINDOW_SECONDS:
            writes.popleft()
        if len(writes) >= settings.agent_writes_per_hour:
            return False
        writes.append(now)
        return True


def forget_agent_writes() -> None:
    """Start every agent's count from zero (used by tests)."""
    with _lock:
        _recent_writes.clear()
