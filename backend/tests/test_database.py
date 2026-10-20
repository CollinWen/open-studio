"""
Tests for the database connection settings: it runs in WAL mode, and many
writes and reads at once (as from many agents) all succeed.
"""

from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import text

from app.database import engine
from conftest import OWNER_HEADERS

PARALLEL_REQUESTS = 24


def test_database_uses_wal():
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA journal_mode")).scalar_one() == "wal"


def test_parallel_writes_and_reads_all_succeed(client):
    def write(number: int) -> int:
        body = {"title": f"parallel {number}", "tags": ["test"], "visibility": "public"}
        return client.post("/api/entries", json=body, headers=OWNER_HEADERS).status_code

    def read(_: int) -> int:
        return client.get("/api/entries").status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        writes = pool.map(write, range(PARALLEL_REQUESTS))
        reads = pool.map(read, range(PARALLEL_REQUESTS))
        statuses = list(writes) + list(reads)
    assert set(statuses) == {200}
