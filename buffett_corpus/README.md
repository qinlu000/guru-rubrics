# Buffett investment-style corpus (pilot)

This directory contains a first-party corpus for extracting investment-style rubrics from Warren Buffett's public shareholder communications.

## Source boundary

The pilot uses copies hosted by Berkshire Hathaway: annual shareholder letters and *An Owner's Manual*. The official index is <https://www.berkshirehathaway.com/letters/letters.html>. The corpus is intended for research and traceability; every extracted claim must retain its source URL, source year, section or anchor, and a short provenance note.

The full downloaded set covers the 1977–2024 shareholder letters plus the Owner's Manual. `manifest.json` records the downloaded file hash, format, size, and processed word count. `processed/` contains text extracted from the HTML/PDF files. Duplicate HTML/PDF versions of the same letter should be treated as one source during extraction.

## Recommended first pass

Use `selected_sources.json`. Its `recommended_mvp` contains 14 sources: 12 core or supporting letters, the 2023 recent restatement, and the Owner's Manual as the foundational principles document. This set deliberately spans early explicit selection rules, later valuation and risk definitions, crisis behavior, and recent restatements.

Suggested source precedence during normalization:

1. *An Owner's Manual* for canonical Berkshire principles.
2. Repeated, explicit formulations in shareholder letters.
3. Concrete examples and case discussions as evidence of application, not automatically as universal rules.
4. One-off commentary as a lower-confidence candidate requiring review.

## Extraction fields for the next stage

For each candidate claim, retain:

- `source_id`, `source_url`, `year`, `section`, and local evidence anchor;
- a short verbatim fragment and a faithful paraphrase;
- `principle_type`: selection rule, valuation rule, risk rule, behavioral rule, portfolio/capital-allocation rule, or governance rule;
- `applicability`: the decision situation in which the rule should be checked;
- `trajectory_evidence`: what the trading agent must say, calculate, do, or refrain from doing;
- `polarity`: required behavior, prohibited behavior, or conditional behavior;
- `confidence`: direct statement, repeated statement, or inferred operationalization;
- links to duplicate or corroborating sources.

The next artifact should turn each candidate into one atomic criterion. A criterion should check one observable behavior and return a boolean plus a brief evidence explanation, in the same spirit as HealthBench.

## Running the two-stage pipeline

The implementation lives in `pipeline/`. It reads complete processed documents, so a directory
argument means one API request per complete `.txt` document; it does not silently treat arbitrary
fragments as independent sources.

```bash
export ANTHROPIC_API_KEY=...
export ANTHROPIC_MODEL=claude-opus-5
python -m buffett_corpus.pipeline.cli \
  --documents buffett_corpus/processed/1977.txt \
  --framework buffett_corpus/configs/tradebank.json \
  --out buffett_corpus/runs/buffett_pilot
```

Stage 1 produces a source-grounded principle library. Stage 2 compiles those principles against
the TradeBank trajectory schema into atomic rubrics. The provider client is dependency-free and
uses Anthropic's Messages API; set `ANTHROPIC_BASE_URL` when routing through a compatible gateway.

Use `--dry-run` to inspect document discovery and output metadata without an API key. The current
validator checks required fields, exact-quote support, framework-field references, stable IDs,
atomicity warnings, and near-duplicate warnings. It deliberately leaves expert judgment and
trajectory-level applicability for later stages.
