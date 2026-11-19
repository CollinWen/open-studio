"""
Web fetch: downloads a page or JSON the way a normal browser would, for the
link readers. Many sites serve less (or nothing) to obvious bots, so this
sends a browser-like User-Agent. Instagram is the opposite: it only describes
a post to link-preview bots, so its reader uses fetch_as_preview_bot.

A site that can't be reached at all (no such domain, refused, timed out)
raises LinkReadError with a plain message, the same kind of error as a site
that answers badly, so the owner sees why instead of a server error.
"""

import ssl

import httpx
import truststore

from app.integrations.link_readers.link_details import LinkReadError

_BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
_PREVIEW_BOT_HEADERS = {
    "User-Agent": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
    "Accept-Language": "en-US,en;q=0.9",
}
_ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
UNREACHABLE_MESSAGE = "That site couldn't be reached. Check the link, or try again later."


def fetch(url: str, params: dict[str, str] | None = None) -> httpx.Response:
    """GET a URL (with optional query parameters), following redirects. Does not raise on error status codes."""
    return _get(url, _BROWSER_HEADERS, params=params)


def fetch_as_preview_bot(url: str) -> httpx.Response:
    """Like fetch, but introduces itself as the link-preview bot chat apps use."""
    return _get(url, _PREVIEW_BOT_HEADERS)


def fetch_start(url: str, byte_count: int) -> bytes:
    """Only the first byte_count bytes of a file, e.g. to read a photo's EXIF data without downloading it all.
    Nothing (b"") when the file can't be had: what it's for is optional."""
    try:
        response = _get(url, _BROWSER_HEADERS, headers={"Range": f"bytes=0-{byte_count - 1}"})
    except LinkReadError:
        return b""
    return response.content[:byte_count] if response.status_code in (200, 206) else b""


def _get(url: str, client_headers: dict[str, str], **request) -> httpx.Response:
    try:
        with httpx.Client(verify=_ssl_context, timeout=20, follow_redirects=True, headers=client_headers) as http:
            return http.get(url, **request)
    except httpx.TransportError as error:
        raise LinkReadError(UNREACHABLE_MESSAGE) from error
