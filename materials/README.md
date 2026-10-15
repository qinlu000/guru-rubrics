# Source materials for all masters

This directory tracks which first-party materials are selected, fetched, and processed for each master. It holds metadata only; downloaded files are not committed.

| File | Role |
|---|---|
| `material_acquisition_registry_20261011.json` | Source-of-truth inventory of selected and proposed materials, including ones still `pending_lawful_access` or `not_yet_screened` |
| `materials_list_20261015.json` | Input list for `scripts/fetch_materials.py` (the 2026-10-15 download), plus the four pre-2016 Soros essays used in the strict run |
| `rubric_runs_20261011.json` | Run records: `strict_20261010` (document and rubric counts of the 434-rubric strict run) and `expansion_20261011` (execution audit of the expansion runs) |

## Acquisition tracking

`material_acquisition_registry_20261011.json` keeps materials whose complete lawful text has not yet been obtained, with an explicit status. A source must not be silently removed because it is unavailable; only the formal corpus statistics exclude sources that have not passed the stated availability and provenance checks.

The `expansion_20261011` record in `rubric_runs_20261011.json` keeps the execution audit separate from acquisition. All 12 complete public files fetched on 2026-10-10 were processed. Four Munger records lacked a contiguous source quote and remain in `principles.rejected.jsonl`; the source documents themselves remain in the run directory. Greenblatt's three interview PDFs use a recorded `pdftotext -raw` extraction to preserve two-column reading order. The 434 strict rubrics remain the canonical public subset; expansion runs are reported separately, and none of these automated results constitute expert review.

Dated records are snapshots: file names and paths inside them (for example `buffett_corpus/...`, `strict_materials_20261010.json`) refer to files and the layout at the time they were written; those files remain in Git history.
