"""
Tests for GET /api/auth/owner: the owner's password passes, and anything
else (no sign-in, a wrong password, an agent's token) is turned away.
"""

from conftest import OWNER_HEADERS, SCOUT_HEADERS


def test_only_the_owners_password_passes(client):
    assert client.get("/api/auth/owner", headers=OWNER_HEADERS).status_code == 204
    assert client.get("/api/auth/owner").status_code == 401
    assert client.get("/api/auth/owner", headers={"Authorization": "Bearer not-the-password"}).status_code == 401
    assert client.get("/api/auth/owner", headers=SCOUT_HEADERS).status_code == 401
