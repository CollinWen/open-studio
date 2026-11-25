"""
Test setup: points the app at a throwaway data folder, sets a known owner
token, adds two agents (scout, archivist) on a board they may add to and
issues each a token for all its boards (a run), and turns OpenRouter off so tests never make network calls or cost money, and
reads entries right away instead of in the background.
Must run before the app is imported, which is why it sets environment variables at the top.
"""

import os
from collections.abc import Iterator
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="open-studio-test-")
os.environ["OWNER_TOKEN"] = "test-owner-token"
os.environ["OPENROUTER_API_KEY"] = ""
os.environ["READ_IN_BACKGROUND"] = "false"
os.environ["AGENT_WRITES_PER_HOUR"] = "5"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.auth.agent_write_limit import forget_agent_writes  # noqa: E402
from app.main import app  # noqa: E402

OWNER_HEADERS = {"Authorization": "Bearer test-owner-token"}

# A board both test agents are signed on to. Agents can't add to the home board.
AGENT_BOARD = "research"


def issue_token(agent: str, boards: list[str] | None = None, **fields) -> dict:
    """Headers for a new token (an open run) for this agent, on its boards (all by default)."""
    body = {"agent": agent, "boards": boards or ["*"], **fields}
    response = TestClient(app).post("/api/runs", json=body, headers=OWNER_HEADERS)
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['token']}"}


def _add_test_agents() -> None:
    setup = TestClient(app)
    for name in ("scout", "archivist"):
        setup.post("/api/agents", json={"name": name}, headers=OWNER_HEADERS)
    board = {"slug": AGENT_BOARD, "name": "Research", "agents": ["scout", "archivist"]}
    setup.post("/api/boards", json=board, headers=OWNER_HEADERS)


_add_test_agents()
SCOUT_HEADERS = issue_token("scout")
ARCHIVIST_HEADERS = issue_token("archivist")


@pytest.fixture(autouse=True)
def fresh_agent_write_limits():
    forget_agent_writes()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def running_client() -> Iterator[TestClient]:
    """A client with the app's startup run, which the agent server (/mcp) needs.
    The agent server can only start once per process, hence one shared client."""
    with TestClient(app) as started:
        yield started
