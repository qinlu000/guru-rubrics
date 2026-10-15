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
python -m rubric_pipeline.cli \
  --documents corpus/buffett/processed/1977.txt \
  --master "Warren Buffett" \
  --framework configs/tradebank.json \
  --out runs/buffett_pilot
```

The same CLI supports OpenAI-compatible chat APIs such as DeepSeek. The provider uses the
`response_format: {"type": "json_object"}` protocol and keeps semantic and source validation in
the pipeline, because compatible services do not all support strict JSON Schema:

```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://api.deepseek.com
export OPENAI_MODEL=deepseek-chat
python -m rubric_pipeline.cli \
  --provider openai \
  --documents corpus/buffett/processed/1977.txt \
  --master "Warren Buffett" \
  --framework configs/tradebank.json \
  --out runs/deepseek_pilot
```

For OpenAI itself, use `OPENAI_BASE_URL=https://api.openai.com/v1`. The API key is read only from
the environment and is never written to run outputs.

The CLI sends each complete document as one document-level input. It does not silently extract independent arbitrary chunks. For documents larger than the provider context window, use an explicit hierarchical configuration and retain the document-level merge step.

Outputs include raw and deterministically validated JSONL files, run metadata (including prompt hashes), and validation reports. A record that fails validation is dropped and listed in the report with its errors; the report's `rejection_rate` measures how often the model's output is not source-grounded. API keys are never written to outputs.

## Repository layout

| Path | Contents |
|---|---|
| `rubric_pipeline/` | Two-stage extraction code, prompts, and JSON schemas |
| `configs/` | Trajectory framework definitions (currently `tradebank.json`) |
| `corpus/buffett/` | Buffett pilot corpus: processed letter text, hash manifest, and selected-source list |
| `materials/` | Acquisition registry, fetch list, and run records; see [`materials/README.md`](materials/README.md) |
| `scripts/fetch_materials.py` | Downloads the public first-party materials in `materials/materials_list_20261015.json` |
| `tests/` | Unit tests (`python -m unittest discover -s tests`) |

Generated runs (`runs/`), raw downloads (`corpus/*/raw/`), and fetched materials (`materials_local/`) are ignored by Git.

## Master materials

[`materials/material_acquisition_registry_20261011.json`](materials/material_acquisition_registry_20261011.json) is the source-of-truth inventory of selected materials per master, including books still pending lawful access. The repository stores metadata only; it does not redistribute copyrighted books or restricted PDFs.

## Public material retrieval

Fetch the public first-party documents for all masters into a local, ignored directory with:

```bash
python3 scripts/fetch_materials.py --out materials_local
```

The script reads [`materials/materials_list_20261015.json`](materials/materials_list_20261015.json), also discovers the Wesco letters (Munger) and the georgesoros.com essays, records SHA-256 hashes in `materials_local/retrieval_manifest.json`, and skips copyright books and paywalled article bodies. Pershing Square (Ackman) blocks non-browser requests, so those letters must be saved from a real browser. For canonical O’Neil extraction, use a lawfully obtained complete copy of *How to Make Money in Stocks*.

## Corpus

`corpus/buffett/` contains the Buffett pilot corpus, source manifest, and selected-source list. `raw/` is ignored for Git commits; use the official URLs in `manifest.json` and `selected_sources.json` to recreate downloads. Processed text and provenance metadata are retained.

## Design choices

- Exact source quotations are required for principles and rubrics.
- A principle is not a trajectory rubric. Stage 2 maps a source-grounded principle onto the framework's observable fields.
- `not_applicable` means the trigger did not occur. `not_observable` means the trigger occurred but the trace lacks required evidence.
- Rubric criteria are atomic: one independently judgeable behavior per item.
- The API model proposes records; deterministic checks reject records with missing fields, quotes not found in the source document, or unknown principle IDs. Records are rejected, never repaired. Duplicate IDs are collapsed at extraction.

The later grader should report both behavior score and observability coverage, and should be calibrated against financial experts.
