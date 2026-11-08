# The Bridge history: full-session NQ bars acquired; provenance limits remain

Summary: Exported 1,755,357 existing native NQ one-minute bars for calendar years 2018–22 into a new local folder, including evenings, overnight and Sunday reopens. Native total volume equals buyer plus seller volume on every row. Existing repository OF exports have a mislabeled total-volume field; preserved unchanged. Session gaps remain explicitly listed, and exact continuous-contract roll provenance is unverified. No strategy returns were calculated.

## Acquisition and preservation

- Read AGENTS.md and BUILDER_BRIEF.md; initial checkout was clean on `codex/work` at `c926a046`. Fast-forwarded existing remote work to `4fd0af16` before recording this task. Only research scripts, audit receipts, this report and the data-needs receipt are task changes.
- Shortcut: `C:\Users\dmoto\OneDrive\Desktop\The Bridge.lnk`; target `C:\Program Files\The Bridge\TheBridge-Hosted.exe`.
- Opened installed The Bridge v2.9.13. Status showed active backtest access. Data screen: `NQ.v.0`, Globex, 0.25 tick, Server data. Free Check availability returned Available / INCLUDED for 2017-05-21 to 2026-07-08 (end exclusive). Its output identified continuous/archive mode. No Request/download rebuild was needed: existing history already spans this window.
- Source: `C:\OFB\ofb_bars_NQ.csv`, 201,905,490 bytes; 3,210,351 rows, from 2017-05-21 18:01 ET through 2026-07-07 20:00 ET. Final session is partial.
- Source SHA256 before and after export: `2aef36dd53848cb50f90bc7007dcae7216428a3a13f95d668713fa07cc973377`. Original source and old exports were not edited.
- New local exports: `C:\CodexRepo\scratch_data\codex_bridge_20261108_01\NQ_1min_native_ET_close_2018.csv` through `..._2022.csv`, total 109,365,550 bytes. Calendar-year split; original nine columns and values retained. Raw exports stay local in ignored scratch_data; hashes are committed in the audit receipt. Export script refuses an existing destination; files use exclusive creation.
- Local supporting files: `audit.json`, `gaps_2018_2022.csv`, `daily_counts.csv`, `session_counts.csv`, `session_summary.json` in that folder. The installed manual's temporary text extraction is local there too, not committed.

## Fields and clocks

Installed primary manual, sections 3.1–3.3, 4.3, 10.2 and glossary; PDF pages 13–14, 23–24, 61, 65–66. Manual SHA256: `365d0fbe93235df41961b41763309bb25d3f2df5d96a13f6ad2ff2c1d0e74801`.

| Field | Definition / evidence |
|---|---|
| Date, Time | MM/DD/YYYY and HH:MM, America/New_York local wall time. Manual says minute **close** stamps; do not add another minute. Use timezone-aware ET→CT conversion if needed. Raw file has no explicit offset or timezone column. |
| Open, High, Low, Close | Native one-minute price bars from the same source as Bridge features; all observed prices satisfy OHLC ordering and 0.25 tick size. |
| Volume | Total traded contracts; identity verified as UpVol + DownVol on all 3,210,351 source rows. |
| UpVol | Buyer-initiated volume: manual calls the split aggressor-exact from the tape; glossary defines buyer aggression as trading at the ask. This is not an inference from an up-closing candle. |
| DownVol | Seller-initiated volume; glossary defines seller aggression as trading at the bid. |

The bar is only complete at its close. Actual historical receipt/processing delay is absent; no same-close executable fill or point-in-time delivery claim is established. Aggressor classification comes from vendor documentation, not an independent raw-tape reconciliation. Treatment of exceptional/unknown-side trades and corrections is not documented in the inspected sections.

## Observed overnight coverage

Outside-RTH below means close labels outside 09:31–16:00 ET; it includes postmarket as well as overnight. Session date assigns closes after 18:00 ET to the following calendar day.

| Year | Native bars | Outside RTH | Evening 18:01–23:59 ET | Midnight–09:30 ET | Sessions with both evening and morning |
|---|---:|---:|---:|---:|---:|
| 2018 | 349,082 | 250,427 | 92,210 | 147,058 | 258/258 |
| 2019 | 349,844 | 250,799 | 92,322 | 147,273 | 258/258 |
| 2020 | 348,926 | 250,031 | 92,447 | 146,382 | 259/259 |
| 2021 | 353,393 | 254,018 | 92,926 | 147,849 | 259/259 |
| 2022 | 354,112 | 254,917 | 92,604 | 147,313 | 258/258 |

All five years contain Sunday evening rows. No source rows are stamped 17:01–18:00 ET, consistent with the daily maintenance break. Normal observed sessions often contain 1,365 minutes before mid-2021; the gap list includes 866 instances of 16:15→16:31 ET. In 2022, 235 of 258 observed sessions have the exact contiguous 1,380-minute close grid from 18:01 through 17:00 ET. Shorter holiday sessions and occasional isolated missing minutes are retained rather than filled.

This verifies **full-session scope**, not a gap-free historical archive. There are 3,480 >1-minute intervals in the 2018–22 gap ledger, including maintenance, weekends, holidays and other holes. It is not a count of outages. No exchange-calendar/raw-tape reconciliation was performed, so individual missing minutes remain unclassified (no trades, halt, holiday or missing feed). Daily/session counts and every gap are available for later admission checks. Calendar-year export boundaries may split an overnight session; concatenate adjacent files before session analysis.

## Existing export discrepancy

Compared all 515,156 rows in the 20 existing `data/OF_1min_2018_*.csv` through `OF_1min_2022_*.csv` against native matching timestamps:

- Every timestamp matched; every legacy `upvol` matched native UpVol and every `downvol` matched native DownVol.
- Every legacy `volume` equaled native **UpVol**, rather than native total Volume. The sum identity failed on 515,145 rows; 11 rows have zero seller volume and consequently pass by coincidence.
- Example 2018-01-02 09:30 ET: native total/buy/sell = **537 / 313 / 224**; legacy = **313 / 313 / 224**.
- The existing exporter writes PowerLanguage `Volume`, `UpTicks`, `DownTicks`; this audit establishes the saved-file discrepancy, not the exact platform configuration that caused it. No MultiCharts instance or chart was opened or modified.

Use native Volume, or a verified buy+sell reconstruction, for future total-volume work. Earlier conclusions using the legacy total-volume field have not been revalidated here. The legacy exports also restrict rows to daytime windows, unlike this native export.

## Limits and next data check

The filename, matching legacy series and current UI support NQ identity, but the CSV carries no original contract identifiers, generation version, adjustment flag or roll ledger. Current UI `NQ.v.0` and the manual's continuous-builder instructions do not certify the historical splice/adjustment rule used for this particular file. Preserve its hash and obtain the existing build/roll metadata before research requiring native dated contracts or exact roll handling. No DLL was loaded, config/API-key file opened, authentication automated, purchase made, or broker/live/VPS control accessed. Opening the installed app refreshed its normal membership access; no settings were changed.

## Reproduction and receipts

Run from repo root with Python stdlib (executed using installed Python 3.7):

```text
python analysis/codex_bridge_history_audit.py --destination scratch_data/codex_bridge_NEW_UNIQUE_FOLDER
python analysis/codex_bridge_session_audit.py scratch_data/codex_bridge_NEW_UNIQUE_FOLDER
```

The first script reads only native bars and existing legacy research exports; second summarizes the new exports. No network or strategy engine is invoked. Source-wide checks: zero duplicate timestamps, non-increasing timestamps, negative volumes, total-volume identity failures, invalid OHLC rows or off-tick prices. Both scripts completed successfully. Committed receipts: `analysis/outputs/codex_bridge_history_20261108_audit.json` and `analysis/outputs/codex_bridge_history_20261108_sessions.json`. No trials/backtests run; no trading-plan conclusion.
