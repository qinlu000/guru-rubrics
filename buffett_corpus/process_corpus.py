"""Normalize downloaded Berkshire Hathaway HTML/PDF sources.

The script does not download files. Put official copies in ``raw/`` and run this
script to create reproducible UTF-8 text plus a hash manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "head"}:
            self.skip += 1
        if tag in {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "hr"} and self.skip == 0:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "head"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if self.skip == 0:
            self.parts.append(data)


def html_text(path: Path) -> str:
    raw = path.read_bytes()
    decoded = ""
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            decoded = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    parser = VisibleText()
    parser.feed(decoded)
    lines = []
    for line in "".join(parser.parts).replace("\xa0", " ").splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def pdf_text(path: Path) -> str:
    pages: list[str] = []
    for number, page in enumerate(PdfReader(str(path)).pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            text = f"[EXTRACTION_ERROR {exc}]"
        pages.append(f"\n[PAGE {number}]\n{text}")
    return "\n".join(pages)


def selected_files(raw: Path) -> list[Path]:
    candidates = []
    for path in raw.iterdir():
        if path.name == "letters.html" or path.stat().st_size < 5000:
            continue
        if (
            path.name.startswith("linked_")
            or re.fullmatch(r"(19\d\d|200[0-3])\.html", path.name)
            or re.fullmatch(r"20(?:0[4-9]|1\d|2[0-4])ltr\.pdf", path.name)
            or path.name in {"owners.html", "ownman.pdf"}
        ):
            candidates.append(path)
    for year in range(1998, 2004):
        if any(path.name.startswith(f"linked_{year}") for path in candidates):
            candidates = [path for path in candidates if path.name != f"{year}.html"]
    return sorted(candidates, key=lambda path: path.name)


def source_url(name: str) -> str:
    if name in {"owners.html", "ownman.pdf"}:
        return f"https://www.berkshirehathaway.com/{name}"
    return f"https://www.berkshirehathaway.com/letters/{name}"


def process(raw_dir: Path, out_dir: Path, manifest_path: Path) -> list[dict[str, object]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    for path in selected_files(raw_dir):
        text = pdf_text(path) if path.suffix.lower() == ".pdf" else html_text(path)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        output_name = f"{path.stem}.txt"
        (out_dir / output_name).write_text(text, encoding="utf-8")
        match = re.search(r"(19\d\d|20\d\d)", path.name)
        year = int(match.group(1)) if match else None
        if path.name in {"owners.html", "ownman.pdf"}:
            year = 1999
        manifest.append({
            "file": path.name,
            "processed_file": output_name,
            "year": year,
            "format": path.suffix[1:].lower(),
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "characters": len(text),
            "words": len(text.split()),
            "url": source_url(path.name),
            "retrieved_via": "official_berkshirehathaway",
        })
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", default="buffett_corpus/raw")
    parser.add_argument("--out-dir", default="buffett_corpus/processed")
    parser.add_argument("--manifest", default="buffett_corpus/manifest.json")
    args = parser.parse_args()
    records = process(Path(args.raw_dir), Path(args.out_dir), Path(args.manifest))
    print(f"processed {len(records)} source files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
