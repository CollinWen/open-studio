"""
LLM client: sends a prompt to a chat model on OpenRouter and returns its text reply.

Knows nothing about entries or tags. The prompts themselves live with the
feature that uses them (e.g. features/tags/tag_suggester.py).
"""

import json
from typing import Any

from app.config import settings
from app.integrations.openrouter_http import post_to_openrouter


def ask_llm(system: str, user: str, model: str | None = None) -> str:
    """Send one system + user message and return the model's reply text."""
    reply = post_to_openrouter(
        "/chat/completions",
        {
            "model": model or settings.tag_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.0,
            # Generous because some models think before answering.
            "max_tokens": 4096,
        },
    )
    return reply["choices"][0]["message"]["content"] or ""


def extract_json(text: str) -> Any:
    """Pull the JSON value out of a reply that may be wrapped in ``` fences or extra words."""
    starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not starts:
        raise ValueError(f"No JSON found in model reply: {text[:200]}")
    end = max(text.rfind("}"), text.rfind("]"))
    return json.loads(text[min(starts) : end + 1])
