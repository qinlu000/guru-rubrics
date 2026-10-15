# Buffett investment-style corpus (pilot)

This directory contains a first-party corpus for extracting investment-style rubrics from Warren Buffett's public shareholder communications. Material tracking for all masters lives in [`../../materials/`](../../materials/README.md).

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

To run the pipeline on this corpus, see the repository [README](../../README.md).
