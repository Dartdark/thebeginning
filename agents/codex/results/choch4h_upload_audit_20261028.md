# CHoCH upload follow-up: supplied daytime files do not repair overnight coverage

Inspected all nine user uploads by SHA256 and date/time columns. No OHLC columns were parsed and no new strategy returns were run. Original files remain in the uploaded-attachment workspace; raw data were not re-exported to GitHub or substituted into `data/`.

| Upload years | Finding |
|---|---|
| 2018–2025 | All eight are byte-for-byte identical to the corresponding existing `data/NQ_1min_YEAR.csv` daytime files |
| 2026 | Newer daytime file: 89,528 rows, January 2 through October 21, 2026; retained separately |
| All nine | Earliest timestamp 08:00 CT; latest 15:15 CT; zero 17:01 rows and zero rows after 17:00 |

These uploads do not contain the missing 17:01 CT minute or any overnight history. The frozen 2018–22 CHoCH input is unchanged, so rerunning the same data would not constitute new evidence. The newer 2026 daytime file cannot fix that design-period issue. The previously saved two-pivot tests and all limitations remain intact. Do not infer failure or success of CHoCH from the coverage problem.

Reproducible audit: [`analysis/codex_choch4h_upload_audit.py`](../../../analysis/codex_choch4h_upload_audit.py).
Results including all nine checksums: [`coverage.csv`](../../../analysis/outputs/codex_choch4h_upload_audit_20261028/coverage.csv).
Prior result: [frozen test and exact missing-minute evidence](choch4h_20261028.md).

No parameter, chart anchor, pivot definition or execution rule was changed. Additional economic trials: zero. Existing multiplicity/history, other work, research automations and live settings are unchanged.

Placement remains: personal unverified/no earned slot; 50K funded and 150K funded no place as written because of multiday holding; 50K evaluation and 150K evaluation the same holding restriction and no valid account comparison. No account gain or harm is measured here.

Recommended next step: a **fresh, complete 24-hour-session NQ one-minute export**, especially 2018–22, including the first minute after the 17:00 CT reopen. Supply its close/open timestamp convention and session/timezone settings. If using separate files, the corrected overnight export is needed, rather than these unchanged daytime files. Original overnight files already in the repo are also known to have the first-minute problem, so simply resending them would not fix it. Resolve whether the missing 17:01 is an export omission or source timestamp convention before relabelling or imputing any observation.

For Claude: review `agents/codex/results/choch4h_upload_audit_20261028.md`; nine-file audit complete, overnight blocker persists, no economic rerun justified.
