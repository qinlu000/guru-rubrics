"""Run the two-stage principle-to-rubric extraction prototype."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .client import complete_json
from .io import document_record, load_prompt, quote_span, read_json, read_jsonl, sha256, stable_id, write_json, write_jsonl
from .validation import attribution_flags, partition, principle_errors, rubric_errors, rubric_warnings

CALL_FAILURES: list[dict] = []


def call_model(where: str, **kwargs):
    """One model call; a failed call is recorded and skipped instead of aborting the run."""
    try:
        return complete_json(**kwargs)
    except Exception as error:  # network errors, timeouts, unparseable JSON
        CALL_FAILURES.append({"where": where, "error": f"{type(error).__name__}: {error}"[:500]})
        print(f"call failed ({where}): {type(error).__name__}", flush=True)
        return []


PROMPTS = ["stage1_system.txt", "stage1_user.txt", "stage2_system.txt", "stage2_user.txt"]


def documents(paths: list[str], master: str) -> list[dict]:
    files = []
    for value in paths:
        path = Path(value)
        files.extend(sorted(path.rglob("*.txt")) if path.is_dir() else [path])
    return [document_record(path, master) for path in files]


def as_records(value, key: str) -> list[dict]:
    # Some compatible models return a single record without the requested wrapper.
    if isinstance(value, dict) and key not in value:
        return [value]
    return value[key] if isinstance(value, dict) else value


def principle_prompt(doc: dict) -> str:
    return load_prompt("stage1_user.txt").replace("{{document_text}}", doc["text"])


def rubric_prompt(principle: dict, framework: dict) -> str:
    prompt_principle = {
        key: principle[key]
        for key in ("claim", "principle_type", "polarity", "conditions", "exceptions", "supporting_quotes", "source_support", "confidence")
        if key in principle
    }
    return load_prompt("stage2_user.txt").replace("{{framework_json}}", json.dumps(framework, ensure_ascii=False, indent=2)).replace("{{principle_json}}", json.dumps(prompt_principle, ensure_ascii=False, indent=2))


def extract_principles(docs: list[dict], args) -> list[dict]:
    output = {}
    for doc in docs:
        result = call_model(doc["document_id"], system=load_prompt("stage1_system.txt"), user=principle_prompt(doc), model=args.model, max_tokens=args.max_tokens, provider=args.provider)
        for item in as_records(result, "principles"):
            quote = (item.get("supporting_quotes") or [{}])[0].get("quote", "")
            item["document_id"] = doc["document_id"]
            item["master"] = args.master
            item["principle_id"] = stable_id("principle", doc["document_id"], item.get("claim", ""), quote)
            output.setdefault(item["principle_id"], item)
    return list(output.values())


def extract_rubrics(principles: list[dict], framework: dict, args) -> list[dict]:
    def compile_one(principle: dict):
        return call_model(principle["principle_id"], system=load_prompt("stage2_system.txt"), user=rubric_prompt(principle, framework), model=args.model, max_tokens=args.max_tokens, provider=args.provider)

    # One independent call per principle; results are collected in principle order.
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(compile_one, principles))
    output = {}
    for principle, result in zip(principles, results):
        for item in as_records(result, "rubrics"):
            item["principle_id"] = principle["principle_id"]
            item["framework_id"] = framework["framework_id"]
            item["rubric_id"] = stable_id("rubric", principle["principle_id"], framework["framework_id"], item.get("criterion", ""))
            # Provenance is copied from the validated principle so the model
            # cannot replace an exact quote with a paraphrase.
            item["source"] = {
                "document_id": principle["document_id"],
                "exact_quotes": [q.get("quote", "") for q in principle.get("supporting_quotes", [])],
                "spans": [q["span"] for q in principle.get("supporting_quotes", [])],
            }
            output.setdefault(item["rubric_id"], item)
    return list(output.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--documents", nargs="+", required=True, help="complete .txt documents or a directory")
    parser.add_argument("--framework", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--master", default="Warren Buffett")
    parser.add_argument("--provider", choices=["anthropic", "openai"], default=os.environ.get("LLM_PROVIDER", "anthropic"))
    parser.add_argument("--model", help="defaults to ANTHROPIC_MODEL or OPENAI_MODEL")
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--stage", choices=["all", "principles", "rubrics"], default="all")
    parser.add_argument("--principles", help="validated principles JSONL for --stage rubrics")
    parser.add_argument("--workers", type=int, default=1, help="parallel Stage 2 calls")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    docs = documents(args.documents, args.master)
    framework = read_json(args.framework)
    write_json(out / "run_metadata.json", {
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "master": args.master,
        "documents": args.documents,
        "framework": args.framework,
        "provider": args.provider,
        "model": args.model,
        "stage": args.stage,
        "max_tokens": args.max_tokens,
        "dry_run": args.dry_run,
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=Path(__file__).parent).stdout.strip(),
        "prompt_sha256": {name: sha256(load_prompt(name)) for name in PROMPTS},
    })
    if args.dry_run:
        write_json(out / "documents.json", [{k: v for k, v in doc.items() if k != "text"} for doc in docs])
        print(f"dry-run: found {len(docs)} complete documents")
        return 0

    texts = {doc["document_id"]: doc["text"] for doc in docs}
    if args.stage in {"all", "principles"}:
        raw = extract_principles(docs, args)
        principles, report = partition(raw, "principle_id", lambda p: principle_errors(p, texts))
        for principle in principles:
            for evidence in principle["supporting_quotes"]:
                evidence["span"] = quote_span(evidence["quote"], texts[principle["document_id"]])
        # Quotes that may be someone else's words stay in the library but are listed for human review.
        report["attribution_review"] = [{"principle_id": p["principle_id"], "flags": f} for p in principles if (f := attribution_flags(p, texts))]
        write_jsonl(out / "principles.raw.jsonl", raw)
        write_json(out / "principles.validation.json", report)
        write_jsonl(out / "principles.validated.jsonl", principles)
    else:
        principles = read_jsonl(args.principles or out / "principles.validated.jsonl")

    if args.stage in {"all", "rubrics"}:
        raw = extract_rubrics(principles, framework, args)
        principle_ids = {p["principle_id"] for p in principles}
        rubrics, report = partition(raw, "rubric_id", lambda r: rubric_errors(r, principle_ids, framework, texts))
        report["warnings"] = [{"rubric_id": r["rubric_id"], "warnings": w} for r in rubrics if (w := rubric_warnings(r, framework))]
        write_jsonl(out / "rubrics.raw.jsonl", raw)
        write_json(out / "rubrics.validation.json", report)
        write_jsonl(out / "rubrics.validated.jsonl", rubrics)
    write_json(out / "call_failures.json", CALL_FAILURES)
    print(f"wrote {args.stage} outputs to {out} ({len(CALL_FAILURES)} failed calls)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
