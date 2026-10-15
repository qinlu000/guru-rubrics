"""File and prompt helpers used by the CLI."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from functools import lru_cache
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


@lru_cache(maxsize=None)
def _word_stream(text: str) -> tuple[str, tuple[int, ...]]:
    """Return the casefolded word stream of ``text`` and each character's offset in ``text``.

    Punctuation, quotation marks and whitespace are ignored, and words split by a
    hyphen (including PDF line-break hyphens, "lead-\\nup") are joined.
    Offsets refer to the NFKC-normalized text, which equals the original for
    the plain-text corpus.
    """
    text = unicodedata.normalize("NFKC", text)
    chars, offsets, end = [], [], None
    for match in re.finditer(r"\w+", text):
        if end is not None and not re.fullmatch(r"-\s*", text[end:match.start()]):
            chars.append(" ")
            offsets.append(end)
        for i, char in enumerate(match.group(), start=match.start()):
            folded = char.casefold()
            chars.extend(folded)
            offsets.extend([i] * len(folded))
        end = match.end()
    return "".join(chars), tuple(offsets)


def normalized_text(text: str) -> str:
    return _word_stream(text)[0]


def quote_span(quote: str, document: str) -> list[int] | None:
    """Character span ``[start, end)`` of ``quote`` in ``document``, or None if absent."""
    needle = normalized_text(quote)
    stream, offsets = _word_stream(document)
    start = stream.find(needle) if needle else -1
    if start < 0:
        return None
    return [offsets[start], offsets[start + len(needle) - 1] + 1]


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def document_record(path: str | Path, master: str) -> dict[str, Any]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    return {
        "document_id": stable_id("doc", master, source.name),
        "master": master,
        "title": source.stem,
        "local_file": str(source),
        "sha256": sha256(text),
        "character_count": len(text),
        "word_count": len(text.split()),
        "text": text,
    }
