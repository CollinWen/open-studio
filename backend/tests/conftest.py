"""
Test setup: points the app at a throwaway data folder, sets a known owner
token, two agent tokens (scout, archivist) and a board they may add to, and
turns OpenRouter off so tests never make network calls or cost money.
Must run before the app is imported, which is why it sets environment variables at the top.
"""

import os
from collections.abc import Iterator
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="open-studio-test-")
os.environ["OWNER_TOKEN"] = "test-owner-token"
os.environ["OPENROUTER_API_KEY"] = ""
os.environ["AGENT_TOKENS"] = "scout=test-scout-token,archivist=test-archivist-token"
os.environ["AGENT_WRITES_PER_HOUR"] = "5"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.auth.agent_write_limit import forget_agent_writes  # noqa: E402
from app.main import app  # noqa: E402

OWNER_HEADERS = {"Authorization": "Bearer test-owner-token"}
SCOUT_HEADERS = {"Authorization": "Bearer test-scout-token"}
ARCHIVIST_HEADERS = {"Authorization": "Bearer test-archivist-token"}


# A board both test agents are signed on to. Agents can't add to the home board.
AGENT_BOARD = "research"


@pytest.fixture(autouse=True)
def fresh_agent_write_limits():
    forget_agent_writes()


@pytest.fixture(scope="session", autouse=True)
def agent_board():
    board = {"slug": AGENT_BOARD, "name": "Research", "agents": ["scout", "archivist"]}
    TestClient(app).post("/api/boards", json=board, headers=OWNER_HEADERS)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def running_client() -> Iterator[TestClient]:
    """A client with the app's startup run, which the agent server (/mcp) needs.
    The agent server can only start once per process, hence one shared client."""
    with TestClient(app) as started:
        yield started
