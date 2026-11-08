# UGL/GLL historical clock evidence, 2026-11-08

Free public primary documents, additive to the preserved
[`new_data_primary_local_20261108`](../new_data_primary_local_20261108/README.md) fund data.
No original export was edited. See [report](../../results/gold_clocks_20261108.md).

- `raw/`: original response bytes in lossless gzip; 15 successful source downloads.
- `text/`: derived HTML/PDF text for search. Raw documents remain authoritative for tables/footnotes.
  Package-local Git attributes preserve extraction whitespace/line endings and suppress bulk text diffs.
- Three `*receipt.json` files: request URLs/times, raw/compressed byte counts/SHA256, and one failed 404 probe.
  Acquisition statuses mean saved bytes, not automatic information-clock admission.
- `evidence_matrix.json`: manually reviewed claims, section/page locators, source scope and limits.
- `pdf_page_evidence.json`: complete extracted relevant PDF pages, one-based file page locators.
- `preserved_input_hashes.json`: unchanged original UGL/GLL files; `verification.json` verifies them again.
- `design_clock_sidecar.csv`: 2,518 separate fund-date policy rows for 2018-22. **Not actual per-date clocks.**
  NAV/asset/share availability and actual reset execution remain blank. All holiday exceptions unverified.
  The January 4 transition benchmark is deliberately unresolved. Pre-change NAV retains its London clock;
  no fixed Eastern conversion through DST mismatches. The 09:30 pre-change printed AP policy is qualified
  because the exchange notice cites 09:00 in older rules.
- `sidecar_qa.json`: exact mapping/counts against preserved source dates.
- `search_log.json`: bounded searches and what they failed to establish.

Reproduce from repository root with `analysis/codex_gold_clocks_20261108.py` modes `fetch`, `more`,
`annual_tables`, `pdf_text`, `sidecar`, `verify`. Acquisition/derivation modes refuse existing files;
use a new output directory for a fresh acquisition. `verify` alone safely refreshes its derived receipt.
PDF extraction requires pypdf; other modes use the standard library and the existing primary downloader.
Current HTTP Date/Last-Modified/ETag and 2026 retrieval timestamps are not historical row publication times.
Policy sources span the design period, but this is not an exhaustive amendment/holiday archive.
