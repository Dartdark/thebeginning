# dot: 6E data feasibility for the FX session paper
Author: dot. Date: 2026-11-10. Research-only data audit; no returns or strategy tests calculated.

## Verdict
The owned schema can express the source-defined US-session clock rule. Actual raw-row verification is limited to December 2017. This is conditional feasibility, not a claim that data are unavailable, and not admission of the full intended design/holdout period.

Paper: [Breedon and Ranaldo, SSRN 2099321](https://ssrn.com/abstract=2099321). The separately studied long EUR/USD interval is 08:00–16:00 New York, equivalent to 07:00–15:00 Chicago and 05:00–13:00 Pacific. It is same-day in the user's timezone. A 6E implementation remains a futures adaptation, not the original EBS spot replication.

## Actual inspected file
[6E_1min_2017.csv](https://github.com/Dartdark/thebeginning/blob/codex/work/data/6E_1min_2017.csv), blob 363d87c2f417bbd3cdcd619f4d0a7ef26b92ba45:
- 26,623 rows, 24 calendar dates, December 1–29, 2017.
- Columns date, time, open, high, low, close, volume.
- First timestamp December 1 at 00:02; final timestamp December 29 at 16:00.
- Zero duplicate date/time keys, malformed rows or nonnumeric fields.
- No contract identifier, expiry, adjustment, bid/ask, exchange/receipt timestamp or timezone field.

[Exporter](https://github.com/Dartdark/thebeginning/blob/codex/work/tools/exporters/NQ_Bar_Exporter.txt) documents HHMM bar-close timestamps in the chart timezone and recommends Exchange timezone. [Grid24](https://github.com/Dartdark/thebeginning/blob/codex/work/analysis/grid24.py) interprets bars as Central time. This supports a repository convention, not independent proof of the original chart settings.

The exporter writes the reserved word Ticks into the field named volume. Whether this represents traded-contract volume under the original platform/feed settings is not verified. Do not infer tick count or true contract volume solely from the keyword. This does not obstruct a clock-only price rule, but matters for volume-dependent sources such as SSRN 5795584.

## US-session leg: endpoint feasibility
All 20 nonholiday weekdays in the inspected sample contain 07:00, 07:01, 15:00 and 15:01 Central bars. Scheduled boundary observations and adjacent opening-price references are therefore present.

Eight dates have nine absent interior minute timestamps in total. These may be no-trade minutes or missing observations; cause is unknown. They do not automatically prevent a no-stop endpoint study, but complete intraday marking, adverse excursions and account-survival calculations are not established.

Christmas has neither required endpoint. It must not be silently treated as a zero-return trading day.

Since timestamps mark bar closes, a prospective 07:00 order could reference the 07:01 bar's opening price under an explicitly frozen convention. That is not a guaranteed executable fill. Clock scheduling is causal, but costs, spread, latency, holidays and exact exit conventions remain separate requirements.

## European leg
The 07:00 London start normally maps to 01:00 Chicago, with shifts during UK/US DST mismatch. All 20 inspected weekdays have 01:00, 07:00 and 15:00 boundaries; nine dates have 33 missing interior minutes across 01:00–15:00.

The first leg normally begins at 23:00 on the previous Pacific date. Do not count it under strict Pacific no-overnight criteria. December alone cannot validate DST-transition logic.

## Unresolved coverage and exact retrieval failures
- data/6E_1min_2018.csv: 17,364,008 bytes; raw fetch returned Transport closed.
- data/6E_1min_2026.csv: 13,558,442 bytes; raw fetch returned Transport closed.
- Other-year filenames were seen, but their raw contents were not successfully inspected in this audit.
- The smaller 2017 file was the successful fallback. No claim is made about complete 2018–2022 design data or 2023 onward validation data.

[The existing overnight roll helper](https://github.com/Dartdark/thebeginning/blob/codex/work/analysis/overnight_round.py) infers switches from large jumps in broad quarterly windows. It is not a native contract map. [Earlier 6E screen code](https://github.com/Dartdark/thebeginning/blob/codex/work/analysis/codex_scout_europe_fix.py) also warns that continuous exports lack native contract identity.

## What this establishes
1. Code-expressible, source-defined US-session timing with existing fields: yes, demonstrated on the inspected sample.
2. Full historical coverage and reliable execution-cost inputs: not yet verified.
3. Faithful original spot-market replication: no, 6E is a different instrument.
4. Positive net performance or improved account survival: not tested.

No strategy code, return test, live access or existing experiment was changed.
