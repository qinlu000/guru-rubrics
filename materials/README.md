# Source materials for all masters

This directory tracks which first-party materials are selected, fetched, and processed for each master. It holds metadata only; downloaded files are not committed.

| File | Role |
|---|---|
| `masters_material_selection_v0.1.{md,json}` | The 11-master candidate source plan: source type, official URL, style dimensions, access mode, copyright handling |
| `material_acquisition_registry_20261011.json` | Source-of-truth inventory of selected and proposed materials, including ones still `pending_lawful_access` or `not_yet_screened` |
| `materials_list_20261015.json` | Input list for `scripts/fetch_materials.py` (the 2026-10-15 download) |
| `material_manifest_20261010.json` | Greenblatt, O’Neil, and Dalio sources with access, completeness, authorship, and style dimensions, including books that need a lawful local copy |
| `reselected_materials_20261010.json` | The Ackman, Soros, and Dalio URLs used for the 2026-10-10 strict run |
| `public_material_retrieval_20261010.json` | Hashes of the files fetched on 2026-10-10 and processed in the 2026-10-11 runs |
| `strict_materials_20261010.json` | Document and rubric counts of the 434-rubric strict run |
| `material_execution_status_20261011.json` | Execution audit of the 2026-10-11 expansion runs |

## Acquisition tracking

`material_acquisition_registry_20261011.json` keeps materials whose complete lawful text has not yet been obtained, with an explicit status. A source must not be silently removed because it is unavailable; only the formal corpus statistics exclude sources that have not passed the stated availability and provenance checks.

`material_execution_status_20261011.json` records the execution audit separately from acquisition. All 12 complete public files in the 2026-10-10 retrieval manifest were processed. Four Munger records lacked a contiguous source quote and remain in `principles.rejected.jsonl`; the source documents themselves remain in the run directory. Greenblatt's three interview PDFs use a recorded `pdftotext -raw` extraction to preserve two-column reading order. The 434 strict rubrics remain the canonical public subset; expansion runs are reported separately, and none of these automated results constitute expert review.

Dated records are snapshots: file paths inside them (for example `buffett_corpus/...`) refer to the repository layout at the time they were written.
