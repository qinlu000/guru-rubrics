"""Minimal Anthropic Messages API client used by the extraction prototype."""
from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen


def _parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = "\n".join(text.splitlines()[1:-1]).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        for start, char in enumerate(text):
            if char in "[{":
                try:
                    return decoder.raw_decode(text[start:])[0]
                except json.JSONDecodeError:
                    continue
    raise ValueError("model response did not contain valid JSON")


def complete_json(*, system: str, user: str, model: str | None = None, max_tokens: int = 8192):
    api_key = os.environ["ANTHROPIC_API_KEY"]
    model = model or os.environ["ANTHROPIC_MODEL"]
    request = Request(
        os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/") + "/v1/messages",
        data=json.dumps({
            "model": model,
            "max_tokens": max_tokens,
            "temperature": 0,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urlopen(request, timeout=180) as response:
        payload = json.loads(response.read().decode("utf-8"))
    text = "\n".join(block["text"] for block in payload["content"] if block.get("type") == "text")
    return _parse_json(text)
