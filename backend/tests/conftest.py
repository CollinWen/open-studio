"""
Test setup: points the app at a throwaway data folder, sets a known owner
token, and turns OpenRouter off so tests never make network calls or cost money.
Must run before the app is imported, which is why it sets environment variables at the top.
"""

import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="open-studio-test-")
os.environ["OWNER_TOKEN"] = "test-owner-token"
os.environ["OPENROUTER_API_KEY"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

OWNER_HEADERS = {"Authorization": "Bearer test-owner-token"}


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
