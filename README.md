# Investor-style rubrics

A reproducible pipeline for extracting investment-style rubrics from complete primary-source documents and compiling them for a trading-agent framework.

The current pilot uses Warren Buffett's Berkshire Hathaway shareholder letters and *An Owner's Manual*. The workflow has two explicit stages:

1. **Principle extraction:** read a complete source document and produce source-grounded principles with exact quotations, conditions, exceptions, and provenance.
2. **Framework compilation:** combine validated principles with a canonical trading-agent trajectory schema (currently TradeBank-oriented) and produce atomic, observable rubrics with pass, violation, and missing-evidence conditions.

Applicability to an individual trajectory is evaluated later. Rubric generation is never fitted to one agent episode.

## Quick start

The code has no runtime dependency outside Python 3.11+ and the standard library. Set an Anthropic key and model name before running API calls:

```bash
export ANTHROPIC_API_KEY=...
export ANTHROPIC_MODEL=claude-opus-5
python -m buffett_corpus.pipeline.cli \
  --documents buffett_corpus/processed/1977.txt \
  --master "Warren Buffett" \
  --framework buffett_corpus/configs/tradebank.json \
  --out buffett_corpus/runs/buffett_pilot
```

The CLI sends each complete document as one document-level input. It does not silently extract independent arbitrary chunks. For documents larger than the provider context window, use an explicit hierarchical configuration and retain the document-level merge step.

Outputs include raw and deterministically validated JSONL files, run metadata, and validation reports. API keys are never written to outputs.

## Master material selection

The first ten-master source plan is recorded in [`masters_material_selection_v0.1.md`](masters_material_selection_v0.1.md) and [`masters_material_selection_v0.1.json`](masters_material_selection_v0.1.json). The manifest stores source type, official URL, style dimensions, access mode, and copyright handling; it does not redistribute copyrighted books or restricted PDFs.

## Corpus

`buffett_corpus/` contains the existing Buffett pilot corpus, source manifest, selected-source list, 20 draft rubrics, and review notes. `raw/` is ignored for Git commits; use the official URLs in `manifest.json` and `selected_sources.json` to recreate downloads. Processed text and provenance metadata are retained.

## Design choices

- Exact source quotations are required for principles and rubrics.
- A principle is not a trajectory rubric. Stage 2 maps a source-grounded principle onto the framework's observable fields.
- `not_applicable` means the trigger did not occur. `not_observable` means the trigger occurred but the trace lacks required evidence.
- Rubric criteria are atomic: one independently judgeable behavior per item.
- The API model proposes records; deterministic checks reject missing fields, missing source support, unsupported framework fields, and duplicate IDs.

The later grader should report both behavior score and observability coverage, and should be calibrated against financial experts.
