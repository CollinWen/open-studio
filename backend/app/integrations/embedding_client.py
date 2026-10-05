"""
Embedding client: turns a piece of text into a list of numbers (a vector)
using an embedding model on OpenRouter.

Texts with similar meaning get vectors that point in similar directions.
That's how "Related" entries are found.
"""

from app.config import settings
from app.integrations.openrouter_http import post_to_openrouter


def embed_text(text: str) -> list[float]:
    """Return the embedding vector for one piece of text."""
    reply = post_to_openrouter(
        "/embeddings",
        {"model": settings.embedding_model, "input": text},
    )
    return reply["data"][0]["embedding"]
