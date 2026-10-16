"""Summarize a pilot run: validity, observability, and whether rubrics separate the masters.

Usage: python3 scripts/analyze_pilot.py RUN_DIR  (RUN_DIR holds one subdirectory per master)
Writes RUN_DIR/analysis.json and RUN_DIR/analysis.md. Standard library only.
"""
from __future__ import annotations

import collections
import json
import math
import random
import re
import sys
from pathlib import Path

GENERIC_THRESHOLD = 0.35  # cosine to another master's nearest rubric above this counts as shared
STOP = set("""a an the of to in on for and or is are be been being it its this that these those with as by at from
if then than when while not no do does did should would could can may might will must agent trade trading position
stock stocks market investor investors price prices any all only more most less such which who whom what into out
over under about there their they them has have had was were so also each other own same very just""".split())


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z][a-z\-']+", text.lower()) if w not in STOP and len(w) > 2]


def rubric_text(r: dict) -> str:
    op = r.get("operationalization", {})
    return " ".join([r.get("criterion", ""), op.get("observable_behavior", ""), op.get("pass_if", ""), op.get("violate_if", "")])


def tfidf(docs: list[list[str]]) -> list[dict[str, float]]:
    df = collections.Counter(w for d in docs for w in set(d))
    n = len(docs)
    vecs = []
    for d in docs:
        tf = collections.Counter(d)
        v = {w: c * math.log((1 + n) / (1 + df[w])) for w, c in tf.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs.append({w: x / norm for w, x in v.items()})
    return vecs


def cos(a: dict, b: dict) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(w, 0.0) for w, x in a.items())


def main(run_dir: Path) -> None:
    framework_fields = set(json.loads(Path("configs/tradebank.json").read_text())["canonical_event_fields"])
    masters = sorted(p.name for p in run_dir.iterdir() if (p / "run_metadata.json").exists())
    summary, all_rubrics = {}, []
    for m in masters:
        d = run_dir / m
        principles = read_jsonl(d / "principles.validated.jsonl")
        rubrics = read_jsonl(d / "rubrics.validated.jsonl")
        pv = json.loads((d / "principles.validation.json").read_text()) if (d / "principles.validation.json").exists() else {}
        rv = json.loads((d / "rubrics.validation.json").read_text()) if (d / "rubrics.validation.json").exists() else {}
        by_id = {p["principle_id"]: p for p in principles}
        observable = [r for r in rubrics if set(r.get("applicability", {}).get("required_context", [])) <= framework_fields]
        summary[m] = {
            "documents": len(json.loads((d / "run_metadata.json").read_text())["documents"]),
            "principles_raw": pv.get("record_count", 0),
            "principle_rejection_rate": round(pv.get("rejection_rate", 0.0), 3),
            "principle_rejection_reasons": collections.Counter(e.split(":")[-1].strip() for r in pv.get("rejected", []) for e in r["errors"]).most_common(5),
            "principles_accepted": len(principles),
            "principles_flagged_for_attribution": len(pv.get("attribution_review", [])),
            "rubrics_raw": rv.get("record_count", 0),
            "rubric_rejection_rate": round(rv.get("rejection_rate", 0.0), 3),
            "rubrics_accepted": len(rubrics),
            "rubrics_with_warnings": len(rv.get("warnings", [])),
            "multi_behavior_warnings": sum(any("more than one" in w for w in x["warnings"]) for x in rv.get("warnings", [])),
            "required_context_within_framework": round(len(observable) / len(rubrics), 3) if rubrics else None,
            "principle_type": collections.Counter(p.get("principle_type") for p in principles).most_common(),
            "source_support": collections.Counter(p.get("source_support") for p in principles).most_common(),
            "inference_level": collections.Counter(r.get("operationalization", {}).get("inference_level") for r in rubrics).most_common(),
            "decision_types": collections.Counter(t for r in rubrics for t in r.get("applicability", {}).get("decision_types", [])).most_common(),
        }
        for r in rubrics:
            all_rubrics.append({"master": m, "rubric": r, "principle": by_id.get(r["principle_id"], {})})

    # Style separation: nearest-neighbour similarity within vs across masters.
    vecs = tfidf([tokens(rubric_text(x["rubric"])) for x in all_rubrics])
    pairs = set()
    for i, x in enumerate(all_rubrics):
        best_same, best_other, best_other_j = 0.0, 0.0, None
        for j, y in enumerate(all_rubrics):
            if i == j:
                continue
            s = cos(vecs[i], vecs[j])
            if y["master"] == x["master"]:
                best_same = max(best_same, s)
            elif s > best_other:
                best_other, best_other_j = s, j
        x["nn_same"], x["nn_other"], x["nn_other_j"] = best_same, best_other, best_other_j
        if best_other_j is not None:
            pairs.add((best_other, min(i, best_other_j), max(i, best_other_j)))
    for m in masters:
        xs = [x for x in all_rubrics if x["master"] == m]
        if not xs:
            continue
        summary[m]["shared_with_other_master"] = round(sum(x["nn_other"] >= GENERIC_THRESHOLD for x in xs) / len(xs), 3)
        summary[m]["mean_nn_same"] = round(sum(x["nn_same"] for x in xs) / len(xs), 3)
        summary[m]["mean_nn_other"] = round(sum(x["nn_other"] for x in xs) / len(xs), 3)
        # Distinctive vocabulary: terms most over-represented relative to the other masters.
        own = collections.Counter(w for x in xs for w in tokens(rubric_text(x["rubric"])))
        rest = collections.Counter(w for x in all_rubrics if x["master"] != m for w in tokens(rubric_text(x["rubric"])))
        n_own, n_rest = sum(own.values()) or 1, sum(rest.values()) or 1
        summary[m]["distinctive_terms"] = [w for w, _ in sorted(own.items(), key=lambda kv: -(kv[1] / n_own) / ((rest[kv[0]] + 1) / n_rest))[:15]]

    # Leave-one-out nearest-centroid master classification as a crude separability score.
    correct, confusion = 0, collections.Counter()
    for i, x in enumerate(all_rubrics):
        scores = {}
        for m in masters:
            members = [j for j, y in enumerate(all_rubrics) if y["master"] == m and j != i]
            if members:
                scores[m] = sum(cos(vecs[i], vecs[j]) for j in members) / len(members)
        guess = max(scores, key=scores.get) if scores else None
        confusion[(x["master"], guess)] += 1
        correct += guess == x["master"]
    separability = round(correct / len(all_rubrics), 3) if all_rubrics else None

    top_pairs = sorted(pairs, reverse=True)[:12]
    result = {"masters": summary, "loo_nearest_centroid_accuracy": separability,
              "confusion": [[a, b, c] for (a, b), c in sorted(confusion.items())],
              "most_similar_cross_master_pairs": [
                  {"similarity": round(s, 3), "a": [all_rubrics[i]["master"], all_rubrics[i]["rubric"]["criterion"]],
                   "b": [all_rubrics[j]["master"], all_rubrics[j]["rubric"]["criterion"]]} for s, i, j in top_pairs]}
    (run_dir / "analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))

    # Stratified sample for a human faithfulness check (claim vs. quote).
    rng = random.Random(20261015)
    lines = ["# Pilot analysis", "", f"Leave-one-out nearest-centroid accuracy (chance = {1/len(masters):.2f}): {separability}", ""]
    for m, s in summary.items():
        lines += [f"## {m}", "", "```json", json.dumps(s, ensure_ascii=False, indent=1), "```", ""]
    lines += ["## Most similar cross-master rubric pairs", ""]
    for p in result["most_similar_cross_master_pairs"]:
        lines.append(f"- {p['similarity']}: **{p['a'][0]}** {p['a'][1]}  ⟷  **{p['b'][0]}** {p['b'][1]}")
    lines += ["", "## Faithfulness sample (label each: faithful / over-inferred / distorted)", ""]
    for m in masters:
        principles = read_jsonl(run_dir / m / "principles.validated.jsonl")
        for p in rng.sample(principles, min(10, len(principles))):
            quote = p["supporting_quotes"][0]["quote"]
            lines += [f"- [{m}] **{p['claim']}**  ", f"  > {quote[:400]}", "  label: ___", ""]
    (run_dir / "analysis.md").write_text("\n".join(lines))
    print(json.dumps({m: {k: s.get(k) for k in ("principles_accepted", "principle_rejection_rate", "rubrics_accepted", "rubric_rejection_rate", "shared_with_other_master")} for m, s in summary.items()}, indent=1))
    print("separability", separability)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
