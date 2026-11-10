"""
Tests for run tokens: what a token allows can be read back, and a token that
was changed, signed with another secret, expired, or isn't a run token at
all is refused.
"""

import base64
import json
from datetime import datetime, timedelta, timezone

from app.auth.run_tokens import RunClaims, make_run_token, read_run_token


def _claims(hours: float = 1) -> RunClaims:
    return RunClaims(
        run_id="abc123",
        agent="scout",
        scopes=frozenset({"board:research", "web"}),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=hours),
    )


def test_a_token_says_what_it_allows():
    token = make_run_token(_claims())
    claims = read_run_token(token)
    assert claims.run_id == "abc123"
    assert claims.agent == "scout"
    assert claims.scopes == {"board:research", "web"}


def test_its_scopes_are_readable_without_the_secret():
    payload = make_run_token(_claims()).split(".")[1]
    body = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    assert body["scopes"] == ["board:research", "web"]


def test_a_widened_token_is_refused():
    prefix, payload, signature = make_run_token(_claims()).split(".")
    body = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    body["scopes"].append("github")
    widened = base64.urlsafe_b64encode(json.dumps(body).encode()).rstrip(b"=").decode()
    assert read_run_token(f"{prefix}.{widened}.{signature}") is None


def test_an_expired_token_is_refused():
    assert read_run_token(make_run_token(_claims(hours=-1))) is None


def test_other_strings_are_refused():
    for token in ["", "run.", "run.a.b", "test-scout-token", "run.a.b.c"]:
        assert read_run_token(token) is None
