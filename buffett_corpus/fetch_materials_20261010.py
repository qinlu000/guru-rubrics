"""Fetch public source files listed in material_manifest_20261010.json.

The script writes downloaded files to a user-provided local directory and never
attempts to obtain copyright books or paywalled article bodies.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "material_manifest_20261010.json"
UA = "guru-rubrics-material-fetch/20261010"


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0
        self.in_title = False
        self.title: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg", "template"}:
            self.skip += 1
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg", "template"} and self.skip:
            self.skip -= 1
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.skip:
            return
        value = html.unescape(data).strip()
        if not value:
            return
        if self.in_title:
            self.title.append(value)
        self.parts.append(value)

    def text(self) -> str:
        out: list[str] = []
        for value in self.parts:
            if not out or value != out[-1]:
                out.append(value)
        return "\n\n".join(out)


def fetch(url: str) -> tuple[bytes, str]:
    request = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/pdf,*/*"})
    with urlopen(request, timeout=60) as response:
        return response.read(), response.headers.get("content-type", "")


def safe_name(item: dict) -> str:
    return re.sub(r"[^a-z0-9_.-]+", "_", item["id"].lower()).strip("_")


def write_public(item: dict, out: Path) -> dict:
    body, content_type = fetch(item["url"])
    stem = safe_name(item)
    raw = out / f"{stem}.{'pdf' if item['format'] == 'pdf' else 'html'}"
    raw.write_bytes(body)
    text_path = out / f"{stem}.txt"
    if item["format"] == "pdf":
        subprocess.run(["pdftotext", "-layout", str(raw), str(text_path)], check=True)
    else:
        parser = VisibleText()
        parser.feed(body.decode("utf-8", "ignore"))
        text_path.write_text(parser.text(), encoding="utf-8")
    return {
        **item,
        "local_raw": str(raw),
        "local_text": str(text_path),
        "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "content_type": content_type,
        "raw_bytes": len(body),
        "raw_sha256": hashlib.sha256(body).hexdigest(),
        "text_characters": len(text_path.read_text(errors="ignore")),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="/tmp/guru_reselected_sources_20261010")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text())
    fetched = []
    skipped = []
    for item in manifest["materials"]:
        if item["access"] != "public_open" or item.get("role") == "metadata_only":
            reason = "metadata_only" if item.get("role") == "metadata_only" else item["access"]
            skipped.append({"id": item["id"], "reason": reason})
            continue
        try:
            fetched.append(write_public(item, out))
            print("fetched", item["id"])
        except Exception as exc:
            print("ERROR", item["id"], exc)
    result = {
        "manifest_id": manifest["manifest_id"],
        "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "output_dir": str(out),
        "fetched": fetched,
        "skipped": skipped,
    }
    (out / "retrieval_manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"fetched={len(fetched)} skipped={len(skipped)} out={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
