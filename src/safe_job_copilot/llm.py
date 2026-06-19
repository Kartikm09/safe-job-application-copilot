"""Optional OpenAI-compatible LLM client for richer application packs."""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "https://zenmux.ai/api/v1"
DEFAULT_MODEL = "moonshotai/kimi-k2.7-code-free"


class LLMConfigurationError(RuntimeError):
    """Raised when optional LLM settings are missing."""


class LLMRequestError(RuntimeError):
    """Raised when the optional LLM provider cannot return a completion."""


def generate_text(
    prompt: str,
    *,
    system: str = "You are a concise AI analyst.",
    max_tokens: int = 6000,
) -> str:
    """Generate a text completion through a ZenMux/OpenAI-compatible endpoint."""
    api_key = os.environ.get("ZENMUX_API_KEY")
    if not api_key:
        raise LLMConfigurationError("Set ZENMUX_API_KEY to enable optional Kimi/ZenMux output.")

    base_url = os.environ.get("ZENMUX_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    model = os.environ.get("ZENMUX_MODEL", DEFAULT_MODEL)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90, context=_ssl_context()) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise LLMRequestError(f"LLM API error {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise LLMRequestError(f"LLM connection error: {exc.reason}") from exc

    try:
        choice = data["choices"][0]
        text = choice["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMRequestError(f"Unexpected LLM response shape: {data}") from exc
    if choice.get("finish_reason") == "length":
        raise LLMRequestError("LLM output reached max_tokens before finishing; increase max_tokens.")
    if not text:
        raise LLMRequestError("LLM returned an empty message; increase max_tokens or try another model.")
    return text


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()
