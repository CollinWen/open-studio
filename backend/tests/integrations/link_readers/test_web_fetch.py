"""
Tests for link_readers/web_fetch.py: a site that can't be reached at all
(no such domain, refused, timed out, blocked) becomes a LinkReadError with a
plain message, the same as a site that answers with an error, instead of an
uncaught network error. No network calls: the request is made to fail.
"""

import httpx
import pytest

from app.integrations.link_readers import web_fetch
from app.integrations.link_readers.link_details import LinkReadError

FAILURES = [
    httpx.ConnectError("no such host"),
    httpx.ConnectTimeout("too slow"),
    httpx.ReadTimeout("too slow"),
    httpx.ProxyError("403 Forbidden"),
]


@pytest.fixture
def failing_network(monkeypatch):
    def fail_with(error):
        def get(self, url, **kwargs):
            raise error

        monkeypatch.setattr(httpx.Client, "get", get)

    return fail_with


@pytest.mark.parametrize("error", FAILURES, ids=lambda error: type(error).__name__)
def test_an_unreachable_site_is_a_plain_link_read_error(failing_network, error):
    failing_network(error)
    for read in (web_fetch.fetch, web_fetch.fetch_as_preview_bot):
        with pytest.raises(LinkReadError, match="couldn't be reached"):
            read("https://unreachable.example/page")


def test_reading_the_start_of_an_unreachable_file_gives_nothing(failing_network):
    failing_network(httpx.ConnectError("no such host"))
    assert web_fetch.fetch_start("https://unreachable.example/photo.jpg", 64) == b""
