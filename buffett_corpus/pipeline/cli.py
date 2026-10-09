"""Run the two-stage principle-to-rubric extraction prototype."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from .client import complete_json
from .io import document_record, load_prompt, read_json, read_jsonl, stable_id, write_json, write_jsonl
from .validation import validate_principles, validate_rubrics


def documents(paths: list[str], master: str) -> list[dict]:
    files = []
    for value in paths:
        path = Path(value)
        files.extend(sorted(path.rglob("*.txt")) if path.is_dir() else [path])
    return [document_record(path, master) for path in files]


def as_records(value, key: str) -> list[dict]:
    records = value.get(key) if isinstance(value, dict) else value
    if not isinstance(records, list):
        # Some compatible models occasionally omit the wrapper for a single
        # record even when the prompt requests a top-level array. Normalize
        # that recoverable shape before deterministic validation.
        record_field = "claim" if key == "principles" else "criterion"
        if isinstance(value, dict) and value.get(record_field):
            return [value]
        raise ValueError(f"model output must contain a `{key}` array")
    return records


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
    output = []
    for doc in docs:
        result = complete_json(system=load_prompt("stage1_system.txt"), user=principle_prompt(doc), model=args.model, max_tokens=args.max_tokens, provider=args.provider)
        for item in as_records(result, "principles"):
            quote = item.get("supporting_quotes", [{}])[0].get("quote", "")
            item["document_id"] = doc["document_id"]
            item["master"] = args.master
            item["principle_id"] = stable_id("principle", doc["document_id"], item.get("claim", ""), quote)
            output.append(item)
    return output


def extract_rubrics(principles: list[dict], framework: dict, args) -> list[dict]:
    output = []
    rubric_ids = set()
    for principle in principles:
        result = complete_json(system=load_prompt("stage2_system.txt"), user=rubric_prompt(principle, framework), model=args.model, max_tokens=args.max_tokens, provider=args.provider)
        for item in as_records(result, "rubrics"):
            item["principle_id"] = principle["principle_id"]
            item["framework_id"] = framework["framework_id"]
            item["rubric_id"] = stable_id("rubric", principle["principle_id"], framework["framework_id"], item.get("criterion", ""))
            if item["rubric_id"] in rubric_ids:
                continue
            rubric_ids.add(item["rubric_id"])
            # Provenance is copied from the validated principle so the model
            # cannot replace an exact quote with a paraphrase.
            item["source"] = {
                "document_id": principle["document_id"],
                "exact_quotes": [q.get("quote", "") for q in principle.get("supporting_quotes", [])],
                "locators": [q.get("locator", "") for q in principle.get("supporting_quotes", [])],
            }
            operation = item.get("operationalization")
            if isinstance(operation, dict):
                operation.setdefault("evidence_to_quote", item.get("applicability", {}).get("required_context", []))
            output.append(item)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--documents", nargs="+", required=True, help="complete .txt documents or a directory")
    parser.add_argument("--framework", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--master", default="Warren Buffett")
    parser.add_argument("--provider", choices=["anthropic", "openai"], default=None)
    parser.add_argument("--model", default=None, help="defaults to ANTHROPIC_MODEL")
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--stage", choices=["all", "principles", "rubrics"], default="all")
    parser.add_argument("--principles", help="validated principles JSONL for --stage rubrics")
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
        "model": args.model,
        "stage": args.stage,
        "dry_run": args.dry_run,
    })
    if args.dry_run:
        write_json(out / "documents.json", [{k: v for k, v in doc.items() if k != "text"} for doc in docs])
        print(f"dry-run: found {len(docs)} complete documents")
        return 0

    texts = {doc["document_id"]: doc["text"] for doc in docs}
    if args.stage in {"all", "principles"}:
        principles = extract_principles(docs, args)
        report = validate_principles(principles, texts)
        write_jsonl(out / "principles.raw.jsonl", principles)
        write_json(out / "principles.validation.json", report)
        if not report["valid"]:
            raise ValueError("principle validation failed; inspect principles.validation.json")
        write_jsonl(out / "principles.validated.jsonl", principles)
    else:
        principle_path = args.principles or str(out / "principles.validated.jsonl")
        principles = read_jsonl(principle_path)

    if args.stage in {"all", "rubrics"}:
        rubrics = extract_rubrics(principles, framework, args)
        report = validate_rubrics(rubrics, principles, framework, texts)
        write_jsonl(out / "rubrics.raw.jsonl", rubrics)
        write_json(out / "rubrics.validation.json", report)
        if not report["valid"]:
            raise ValueError("rubric validation failed; inspect rubrics.validation.json")
        write_jsonl(out / "rubrics.validated.jsonl", rubrics)
    print(f"wrote {args.stage} outputs to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
