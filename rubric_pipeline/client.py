"""Minimal clients for Anthropic and OpenAI-compatible chat APIs."""
from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen


def _post(url: str, headers: dict, body: dict) -> dict:
    request = Request(url, data=json.dumps(body).encode("utf-8"), headers={"content-type": "application/json", **headers}, method="POST")
    with urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def _parse_json(text: str):
    # Skip any prose or code fence before the first JSON value.
    starts = [i for i in (text.find("{"), text.find("[")) if i >= 0]
    if not starts:
        raise ValueError("model response did not contain JSON")
    return json.JSONDecoder().raw_decode(text[min(starts):])[0]


def _complete_anthropic(system: str, user: str, model: str | None, max_tokens: int) -> str:
    payload = _post(
        os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/") + "/v1/messages",
        {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"},
        {
            "model": model or os.environ["ANTHROPIC_MODEL"],
            "max_tokens": max_tokens,
            "temperature": 0,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
    )
    return "".join(block["text"] for block in payload["content"] if block["type"] == "text")


def _complete_openai(system: str, user: str, model: str | None, max_tokens: int) -> str:
    payload = _post(
        os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/") + "/chat/completions",
        {"authorization": "Bearer " + os.environ["OPENAI_API_KEY"]},
        {
            "model": model or os.environ["OPENAI_MODEL"],
            "max_tokens": max_tokens,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        },
    )
    return payload["choices"][0]["message"]["content"]


PROVIDERS = {"anthropic": _complete_anthropic, "openai": _complete_openai}


def complete_json(*, system: str, user: str, model: str | None = None, max_tokens: int = 8192, provider: str = "anthropic"):
    return _parse_json(PROVIDERS[provider](system, user, model, max_tokens))
