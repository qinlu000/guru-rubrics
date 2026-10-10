"""File and prompt helpers used by the CLI."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} is not a JSON object")
        rows.append(value)
    return rows


def load_prompt(name: str) -> str:
    return (Path(__file__).parent / "prompts" / name).read_text(encoding="utf-8")


def stable_id(prefix: str, *parts: str) -> str:
    normalized = "\n".join(re.sub(r"\s+", " ", part.strip().lower()) for part in parts)
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:12]
    clean_prefix = re.sub(r"[^a-z0-9_]+", "_", prefix.lower()).strip("_")
    return f"{clean_prefix}_{digest}"


def normalized_text(text: str) -> str:
    """Normalize extraction-format differences while preserving quote words."""
    text = unicodedata.normalize("NFKC", text)
    # PDF layout extraction may split one word at a line ending (or leave a
    # space after the split hyphen). Rejoin those fragments before comparing
    # the ordered word stream.
    text = re.sub(r"(?<=\w)-[ \t\r\n]+(?=\w)", "", text)
    # Treat ordinary hyphenated compounds consistently with PDF line-break
    # extraction (for example, ``lead-up`` versus ``lead-\\nup``).
    text = re.sub(r"(?<=\w)-(?=\w)", "", text)
    # PDF and HTML extraction disagree on quotation marks, dashes,
    # hyphenation, and other punctuation. Compare the ordered word stream.
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip().casefold()


def quote_in_document(quote: str, document: str) -> bool:
    return bool(quote.strip()) and normalized_text(quote) in normalized_text(document)


def document_record(path: str | Path, master: str) -> dict[str, Any]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    return {
        "document_id": stable_id("doc", master, source.name),
        "master": master,
        "title": source.stem,
        "local_file": str(source),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "character_count": len(text),
        "word_count": len(text.split()),
        "text": text,
    }
