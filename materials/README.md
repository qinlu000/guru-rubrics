# Source materials for all masters

This directory tracks which first-party materials are selected, fetched, and processed for each master. It holds metadata only; downloaded files are not committed.

| File | Role |
|---|---|
| `material_acquisition_registry_20261011.json` | Source-of-truth inventory of selected and proposed materials, including ones still `pending_lawful_access` or `not_yet_screened` |
| `materials_list_20261015.json` | Input list for `scripts/fetch_materials.py` (the 2026-10-15 download), plus four pre-2016 Soros essays |

## Acquisition tracking

`material_acquisition_registry_20261011.json` keeps materials whose complete lawful text has not yet been obtained, with an explicit status. A source must not be silently removed because it is unavailable.

No rubric run results are tracked yet. Earlier runs (2026-10-10 and 2026-10-11) used a superseded material selection and were discarded; their records remain in Git history.

Dated records are snapshots: file names and paths inside them (for example `buffett_corpus/...`) refer to files and the layout at the time they were written; those files remain in Git history.
