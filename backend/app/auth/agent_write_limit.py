"""
Agent write limits: how many entries each agent may add or edit per hour
(AGENT_WRITES_PER_HOUR), so a runaway agent can't flood the studio or the
OpenRouter bill, and how many lines it may write to the agent log per hour
(AGENT_LOG_LINES_PER_HOUR), which cost nothing but could still drown the page.

Counts are kept in memory, which is right while the backend runs on one
machine; with several machines this would move to a shared store.
Used by auth/viewer.py and agent_log/service.py.
"""

import time
from collections import defaultdict, deque
from threading import Lock

from app.config import settings

WINDOW_SECONDS = 3600

_recent: dict[tuple[str, str], deque[float]] = defaultdict(deque)
_lock = Lock()


def record_agent_write(agent_name: str) -> bool:
    """Count one entry write for this agent. False (and nothing counted) when it is over its limit."""
    return _record(("entry", agent_name), settings.agent_writes_per_hour)


def record_agent_log_line(agent_name: str) -> bool:
    """Count one agent log line for this agent. False (and nothing counted) when it is over its limit."""
    return _record(("log", agent_name), settings.agent_log_lines_per_hour)


def forget_agent_writes() -> None:
    """Start every agent's counts from zero (used by tests)."""
    with _lock:
        _recent.clear()


def _record(key: tuple[str, str], limit: int) -> bool:
    now = time.monotonic()
    with _lock:
        recent = _recent[key]
        while recent and recent[0] <= now - WINDOW_SECONDS:
            recent.popleft()
        if len(recent) >= limit:
            return False
        recent.append(now)
        return True
