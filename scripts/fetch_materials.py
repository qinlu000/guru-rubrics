"""Download guru-rubrics public source materials on your own computer.

Run:  python3 scripts/fetch_materials.py --out materials_local
Uses curl (built into macOS). Raw files land in <out>/<master>/ and the URL,
SHA-256 and retrieval time of each file go to <out>/retrieval_manifest.json.
The input is the material selection: every `access: "public"` item with a URL,
plus the Wesco letters (Munger) discovered from the Wesco home page. Text
conversion is a separate step. Books (`purchase`) are never fetched.
Pershing Square (Ackman, `public_browser`) blocks non-browser requests, so
those PDFs are listed for manual download in a real browser.
"""
import argparse, datetime as dt, hashlib, json, re, subprocess, sys
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SELECTION = ROOT / "materials" / "material_selection_v3_20261015.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36"

def get(url: str) -> bytes:
    r = subprocess.run(["curl", "-fsSL", "--max-time", "120", "-A", UA, url], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl exit {r.returncode}: {r.stderr.decode(errors='ignore').strip()[:200]}")
    return r.stdout

def links(page_url: str, body: bytes) -> list[str]:
    hrefs = re.findall(rb'href=["\']([^"\']+)["\']', body, flags=re.I)
    return [urljoin(page_url, h.decode(errors="ignore")) for h in hrefs]

def discover() -> list[dict]:
    found = []
    # Munger: Wesco Financial letters 1997-2009 linked from the Wesco home page.
    try:
        home = "https://www.berkshirehathaway.com/wesco/WescoHome.html"
        for u in sorted(set(links(home, get(home)))):
            name = u.rsplit("/", 1)[-1].lower()
            if "/wesco/" in u.lower() and re.search(r"(19|20)?\d\d", name) and name.endswith((".pdf", ".html")) and "wescohome" not in name:
                found.append({"id": "munger.wesco_" + re.sub(r"\W+", "_", name.rsplit(".", 1)[0]), "master": "munger", "url": u,
                              "format": "pdf" if name.endswith(".pdf") else "html", "role": "core", "discovered_from": home})
    except Exception as e:
        print("DISCOVER-FAIL wesco", e)
    return found

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--out", type=Path, default=ROOT / "materials_local")
    args = parser.parse_args()
    OUT = args.out.resolve()
    materials = json.loads(args.selection.read_text())["materials"]
    items = [{**m, "format": "pdf" if m["url"].lower().split("?")[0].endswith(".pdf") else "html"}
             for m in materials if m.get("access") == "public" and m.get("url")]
    if any(m["id"].startswith("munger.wesco") for m in materials):
        items += discover()
    for m in materials:
        if m.get("access") == "public_browser":
            print("BROWSER", m["id"], m.get("url", "(URL to be located)"))
    OUT.mkdir(parents=True, exist_ok=True)
    fetched, failed, done_urls = [], [], set()
    while items:
        it = items.pop(0)
        if it["url"] in done_urls:
            continue
        done_urls.add(it["url"])
        stem = re.sub(r"[^a-z0-9_.-]+", "_", it["id"].lower()).strip("_")
        d = OUT / it["master"]; d.mkdir(exist_ok=True)
        raw = d / f"{stem}.{it['format']}"
        try:
            body = get(it["url"])
            raw.write_bytes(body)
            fetched.append({**it, "local_raw": str(raw.relative_to(OUT)), "raw_bytes": len(body),
                            "raw_sha256": hashlib.sha256(body).hexdigest(),
                            "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat()})
            print("ok  ", it["id"], len(body))
            if it.get("follow_pdf_links"):
                for n, u in enumerate(sorted({u for u in links(it["url"], body) if u.lower().split("?")[0].endswith(".pdf")}), 1):
                    items.append({"id": f"{it['id']}_pdf{n}", "master": it["master"], "url": u, "format": "pdf", "role": it["role"], "discovered_from": it["url"]})
        except Exception as e:
            failed.append({**it, "error": str(e)}); print("FAIL", it["id"], e)
    (OUT / "retrieval_manifest.json").write_text(json.dumps({"fetched": fetched, "failed": failed}, ensure_ascii=False, indent=2) + "\n")
    print(f"\nfetched={len(fetched)} failed={len(failed)} -> {OUT}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
