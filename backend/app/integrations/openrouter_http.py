"""
OpenRouter HTTP: the one function that sends a request to OpenRouter.

Shared by llm_client.py and embedding_client.py so the key, base URL and
certificate handling live in one place. Mirrors how macro-research calls
OpenRouter (an OpenAI-compatible API over plain HTTP).
"""

import ssl
from typing import Any

import httpx
import truststore

from app.config import settings

# Use the operating system's certificate store, so requests work behind
# networks that inspect TLS (the same fix macro-research uses).
_ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


def is_configured() -> bool:
    return bool(settings.openrouter_api_key)


def post_to_openrouter(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST a JSON payload to an OpenRouter endpoint (e.g. "/embeddings") and return the JSON reply."""
    with httpx.Client(verify=_ssl_context, timeout=60) as http:
        response = http.post(
            f"{settings.openrouter_base_url}{path}",
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
            json=payload,
        )
    response.raise_for_status()
    return response.json()
