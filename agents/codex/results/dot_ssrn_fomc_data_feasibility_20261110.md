# dot: entry 53 FOMC data feasibility
Author: dot. 2026-11-10. Metadata/source audit only; no signals or returns computed.

## Decision
Exact bid/ask replication is blocked. A price-only ES adaptation is conditionally codeable, but not admitted as current-data ready. The five-fresh-existing-data quota remains unfilled.

## What is actually verified
[Saved ES census](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/inputs/calvados_2379985_20261030/es_hedge_gate/owned_es_metadata.json) and [its metadata reader](https://github.com/Dartdark/thebeginning/blob/codex/work/analysis/codex_calvados_es_metadata_audit_20261030.py) establish prior inspection of 2018–22 annual OHLCV files, respectively 346,940; 349,251; 348,715; 353,073; 353,752 rows. This pass inspected saved records, not fresh annual raw contents or hashes. Known oversized-file Transport-closed failures were not repeated. No native contract ID, expiry, roll flag, settlement, bid/ask or receipt time is present.

The [FOMC coverage file](https://github.com/Dartdark/thebeginning/blob/codex/work/analysis/outputs/codex_scout_fomc_cycle/coverage.csv) marks 39 regular 2018–22 events complete, but [its code](https://github.com/Dartdark/thebeginning/blob/codex/work/analysis/codex_scout_fomc_cycle.py) tests 08:31/15:00 Central. Entry 53 needs prior-calendar-day and event-day 12:50 observations, subsequent entry reference, and 14:50 exit reference. The existing complete flag does not establish those endpoints.

## Calendar evidence and defect
The [retained official-header calendar](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/inputs/scout_fomc_cycle_20261030/calendar.json) supplies the 39 regular statement dates and 14:00 Eastern clocks. Original Fed tentative schedules published ahead of the relevant year corroborate their dates: [2018](https://www.federalreserve.gov/newsevents/pressreleases/monetary20170511b.htm), [2019](https://www.federalreserve.gov/newsevents/pressreleases/monetary20180525a.htm), [2020](https://www.federalreserve.gov/newsevents/pressreleases/monetary20190517a.htm), [2021](https://www.federalreserve.gov/newsevents/pressreleases/monetary20200702a.htm), [2022](https://www.federalreserve.gov/newsevents/pressreleases/monetary20210604a.htm).

Advance dates are stronger than reconstructed dates, but not proof of every advance release-time notice or actual receipt. The tentative March 18, 2020 meeting was not in the final regular-event seed; emergency/cancelled-event treatment must remain explicit. The [March 3 emergency statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary20200303a.htm) was at 10:00 Eastern.

[analysis/event_days.py](https://github.com/Dartdark/thebeginning/blob/codex/work/analysis/event_days.py) stops at September 16, 2026, omitting the official [October 28 statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm). No calendar file was changed. October price endpoints are unread.

## Execution and continuity gates
- [Grid24](https://github.com/Dartdark/thebeginning/blob/codex/work/analysis/grid24.py) uses calendar dates and bar-close-labelled Central minutes. Missing minutes remain NaN; duplicate keys are silently dropped. Both need explicit audit.
- A completed 12:50 signal can reference the next bar's open, labelled 12:51. That open begins the next interval; it is not automatically a full minute later or a guaranteed executable fill.
- The exporter uses chart timezone. Reader convention alone does not authenticate historical chart settings.
- Prior 24 hours is not prior trading row or 1,440 observed bars. Roll transitions and missing minutes can change the signal.
- Existing roll helpers infer switches from price jumps, not verified dated contracts. A formation-window roll matters even with intraday holdings.
- [grid.execute](https://github.com/Dartdark/thebeginning/blob/codex/work/analysis/grid.py) hard-codes NQ $20/point and $7.25 round-trip costs. Do not reuse unchanged for ES. Other ES scripts use inconsistent fee/slippage assumptions, neither authenticated for FOMC.
- OHLCV cannot reproduce source bid/ask, impact, latency or native MES execution. Actual intratrade marks are also necessary before survival claims.

## Next gate, not a new test
Inspect raw records only for the 39 event dates and previous calendar dates at 12:50/12:51/14:50/14:51, retaining source hashes and missing/duplicate flags. Resolve contract continuity and freeze observation/fill/cost conventions before any future signal or return replay. No files are declared empty because a connector read failed.
