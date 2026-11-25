"""
Agent write limits: how many entries each agent may add or edit per hour
(AGENT_WRITES_PER_HOUR), so a runaway agent can't flood the studio or the
OpenRouter bill, how many lines it may write to the agent log per hour
(AGENT_LOG_LINES_PER_HOUR), which cost nothing but could still drown the page,
and how many toolkit tools it may call per hour (AGENT_TOOLKIT_CALLS_PER_HOUR),
each of which may cost a paid call on one of the owner's accounts.

Counts are kept in memory, which is right while the backend runs on one
machine; with several machines this would move to a shared store.
Used by auth/viewer.py, agent_log/service.py and toolkits/service.py.
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


def record_agent_toolkit_call(agent_name: str) -> bool:
    """Count one toolkit call for this agent. False (and nothing counted) when it is over its limit."""
    return _record(("toolkit", agent_name), settings.agent_toolkit_calls_per_hour)


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
