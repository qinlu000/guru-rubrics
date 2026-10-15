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
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def load_prompt(name: str) -> str:
    return (Path(__file__).parent / "prompts" / name).read_text(encoding="utf-8")


def stable_id(prefix: str, *parts: str) -> str:
    normalized = "\n".join(re.sub(r"\s+", " ", part.strip().lower()) for part in parts)
    return f"{prefix}_{hashlib.sha1(normalized.encode('utf-8')).hexdigest()[:12]}"


def normalized_text(text: str) -> str:
    """Normalize extraction-format differences while preserving quote words."""
    text = unicodedata.normalize("NFKC", text)
    # Join hyphenated words, including PDF line-break hyphens ("lead-\nup"),
    # then compare the ordered word stream, ignoring punctuation.
    text = re.sub(r"(?<=\w)-\s*(?=\w)", "", text)
    text = re.sub(r"[^\w]+", " ", text)
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
