"""
Web fetch: downloads a page or JSON the way a normal browser would, for the
link readers. Many sites serve less (or nothing) to obvious bots, so this
sends a browser-like User-Agent. Instagram is the opposite: it only describes
a post to link-preview bots, so its reader uses fetch_as_preview_bot.
"""

import ssl

import httpx
import truststore

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


def fetch(url: str, params: dict[str, str] | None = None) -> httpx.Response:
    """GET a URL (with optional query parameters), following redirects. Does not raise on error status codes."""
    with httpx.Client(
        verify=_ssl_context, timeout=20, follow_redirects=True, headers=_BROWSER_HEADERS
    ) as http:
        return http.get(url, params=params)


def fetch_as_preview_bot(url: str) -> httpx.Response:
    """Like fetch, but introduces itself as the link-preview bot chat apps use."""
    with httpx.Client(
        verify=_ssl_context, timeout=20, follow_redirects=True, headers=_PREVIEW_BOT_HEADERS
    ) as http:
        return http.get(url)


def fetch_start(url: str, byte_count: int) -> bytes:
    """Only the first byte_count bytes of a file, e.g. to read a photo's EXIF data without downloading it all."""
    with httpx.Client(
        verify=_ssl_context, timeout=20, follow_redirects=True, headers=_BROWSER_HEADERS
    ) as http:
        response = http.get(url, headers={"Range": f"bytes=0-{byte_count - 1}"})
    return response.content[:byte_count] if response.status_code in (200, 206) else b""
