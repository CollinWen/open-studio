"""
Run tokens: the short-lived pass a run's agent works with, and checking one.

A run token is readable on purpose. It is three parts joined by dots:

  run.<what it allows>.<signature>

The middle part is plain JSON in base64 (decode it to see the run, the agent,
its scopes and when it stops working). The signature is an HMAC-SHA256 of the
rest with RUN_TOKEN_SECRET (config.py), so nobody can widen a token without
the studio's secret, and every backend machine can check one without asking
the others. Scopes are short strings: "board:<slug>" (add, link and log on
that board) and the outside tools in features/runs/task_kinds.py ("web",
"code", "github").

Only making and reading the token is here. Which run it belongs to, and
whether that run has been finished, is checked in auth/viewer.py.
"""

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone

from app.config import settings

PREFIX = "run"
VERSION = 1


@dataclass(frozen=True)
class RunClaims:
    run_id: str
    agent: str
    scopes: frozenset[str]
    expires_at: datetime


def make_run_token(claims: RunClaims) -> str:
    body = {
        "v": VERSION,
        "run": claims.run_id,
        "agent": claims.agent,
        "scopes": sorted(claims.scopes),
        "exp": int(claims.expires_at.timestamp()),
    }
    payload = _encode(json.dumps(body, separators=(",", ":")).encode())
    return f"{PREFIX}.{payload}.{_sign(payload)}"


def looks_like_run_token(token: str) -> bool:
    return token.startswith(f"{PREFIX}.")


def read_run_token(token: str) -> RunClaims | None:
    """The claims of a genuine, unexpired run token; None for anything else."""
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != PREFIX or not settings.run_token_secret:
        return None
    payload, signature = parts[1], parts[2]
    if not hmac.compare_digest(signature, _sign(payload)):
        return None
    try:
        body = json.loads(_decode(payload))
        claims = RunClaims(
            run_id=str(body["run"]),
            agent=str(body["agent"]),
            scopes=frozenset(str(scope) for scope in body["scopes"]),
            expires_at=datetime.fromtimestamp(int(body["exp"]), tz=timezone.utc),
        )
    except (ValueError, KeyError, TypeError):
        return None
    if body.get("v") != VERSION or claims.expires_at <= datetime.now(timezone.utc):
        return None
    return claims


def _sign(payload: str) -> str:
    digest = hmac.new(settings.run_token_secret, f"{PREFIX}.{payload}".encode(), hashlib.sha256).digest()
    return _encode(digest)


def _encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
