"""
Tests that capturing a link to a site that can't be reached answers with a
plain message (422) the form can show, not a server error. No network calls.
"""

import httpx

from conftest import OWNER_HEADERS


def test_capturing_an_unreachable_link_says_so(client, monkeypatch):
    def get(self, url, **kwargs):
        raise httpx.ConnectError("no such host")

    monkeypatch.setattr(httpx.Client, "get", get)
    for url in ["https://unreachable.example/recipe", "https://www.youtube.com/watch?v=abc123", "https://github.com/a/b"]:
        response = client.post("/api/capture/link", json={"url": url}, headers=OWNER_HEADERS)
        assert response.status_code == 422, (url, response.text)
        assert "couldn't be reached" in response.json()["detail"]
