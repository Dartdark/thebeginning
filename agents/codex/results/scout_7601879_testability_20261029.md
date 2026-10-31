# Buying Duration testability follow-up: NEEDS DATA

Summary: We checked whether SSRN 7601879 can support a justified return test now; it cannot yet.
Fresh author/institution searches found no accessible manuscript or author replication package.
Two more public forecast examples were found, but no complete point-in-time extension panel.
Owned ZN data cover 60 observed monthly endpoints; calendar/clock flags need audit. New return trials: 0.

Source: Soebhag, Verwijmeren and Martinetti, *Buying Duration: Index Rebalancing and Price Pressure in Government Bond Markets*,
[SSRN7601879](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7601879), written2026-10-12.
Follow-up date2026-10-29; repository head inspected: `bdad3b4c285572e92ca201557f7093f9ec07a528`.
**Metadata/abstract only; the paper's full text, methods and tables remain unread. No paper PDF/hash obtained.**
The [original review](scout_buying_duration_20261029.md) and [NEEDS DATA sheet](../evidence/scout_buying_duration_20261029.md) remain the earlier evidence record.
No trial reservation, preregistration, return calculation or code change to an economic test occurred.

## 1. What is it about?

Government-bond index duration adjustments around month-end and their transmission to futures prices.
The useful lead is a scheduled benchmark deadline whose US clock changed, creating a source-supported timing question.

## 2. What does it find?

The authors' abstract reports duration-scaled futures averages of 1.19 bp on the last trading day versus 0.07 bp otherwise,
with 47% of average monthly returns attributed to month-end. These remain **author claims**, not independently
reproduced net returns. Without the paper we cannot inspect exact contracts, normalization, entry/exit intervals,
costs, significance, exclusion rules or duration-state construction.

Independent primary documents corroborate a change in the US index snapshot from15:00 to16:00 New York
effective January14,2021, with dated early-close exceptions. That is14:00→15:00CT on ordinary days.
See [Bloomberg methodology, October15,2024, p.80](https://data.bloomberglp.com/professional/sites/27/Fixed-Income-Index-Methodology.pdf)
and the original review. It does not establish our net edge.

## 3. Why does it make money, if it does?

Benchmark tracking can concentrate demand into a known deadline. Carrying inventory before that demand might
earn compensation, but anticipation, offsetting flows and executable costs can consume it.
This mechanism does not determine a profitable window, justify a short reversal trade or prove every month requires buying duration.
The earlier fixed-clock ZN test lost money; its losses remain in the research history.

## 4. Can we build on it?

**Continue source/data acquisition; do not begin returns yet.** We attempted more than a missing-data checklist:

| New check | Actual result | Consequence |
|---|---|---|
| Author-hosted full text | Opened [Soebhag's Erasmus page](https://www.eur.nl/en/people/amar-soebhag), [Pure profile](https://pure.eur.nl/en/persons/amar-soebhag/), [Verwijmeren's personal site](https://sites.google.com/site/patrickverwijmeren/home) and [publications](https://sites.google.com/site/patrickverwijmeren/home/publications). No target manuscript/download found. | Full source remains unavailable through these routes. |
| Author code/data | Exact-title/author searches covering GitHub, Mendeley, Zenodo, OSF, Erasmus, Tinbergen and Robeco found no attributable package. | No frozen source implementation or source data acquired; absence from search is not proof none exists. |
| Free extension history | Opened public mirrored Bloomberg reports forMay2019 andAugust2019; priorMarch2020 example retained. | Three isolated examples, not a usable historical panel. |
| Owned futures inputs | Ran date/time-only census and hashes of all five2018–22 ZN files. | Availability is partly measurable; official event labels and executable paths are not certified. |

The May2019 report, p.1, shows Treasury forecast extension **+0.11years**, with index duration as ofMay23.
The August2019 report, p.1, shows **+0.12years**, as ofAugust19. Sources:
[May report](https://archr.com/wp-content/uploads/2019/05/BBG-BARX-Summary-of-May-Index-Duration-Changes-and-Projected-Duartion-changes-for-June-1st-2019.pdf)
and [August report](https://archr.com/wp-content/uploads/2019/08/BBG-BARX-MONTH-END-SEP-1.pdf).
Both four-page documents were inspected through the web reader; no local PDF/hash or redistribution permission is claimed.
An as-of date or month in a mirror URL does not prove original publication/receipt before entry.
The reports' Europe-wide figures also do not identify Germany-only demand.

[Bloomberg's access guide](https://assets.bbhub.io/professional/sites/10/Accessing-Bloomberg-Indices-on-the-Terminal.pdf), pp.5–6,
points to Terminal data fields and historical INP publications. We found no complete free forecast export.
No subscription, paid data, account or credential was used. The previously denied SSRN delivery endpoint was not retried.

### Timestamp census and power limits

[Reproducible census](../../../analysis/codex_scout_7601879_clock_census.py) ·
[Saved JSON output](../../../analysis/outputs/codex_scout_7601879_clock_census.json) ·
[Access receipt](../research/scout/runs/7601879_testability_20261029.json).
The script loads only date/time columns; it computes no return, fill, price statistic or strategy selection.

| File year | Observed monthly raw endpoints | Endpoints with each requested1359/1459/1500 timestamp |
|---|---:|---:|
| 2018 | 12 | 12 |
| 2019 | 12 | 11 |
| 2020 | 12 | 11 |
| 2021 | 12 | 11 |
| 2022 | 12 | 12 |

The 60 provisional endpoints include 36 calendar months before the snapshot change and 24 afterward.
They are a power ceiling, not 60 eligible independent source events; forecast conditioning and exclusions reduce the count.
No candidate variance or statistical power is estimated from prices.

The three raw endpoints lacking the requested late timestamps are 2019-11-29, 2020-11-27 and 2021-05-31.
**These are not three missing expected rebalance bars.** Holidays/early closes can imply a different official date or clock.
Notably 2020-11-30 has no daytime records, so a rule selecting the last observed data date labels November 27 instead.
A provider calendar cannot be reconstructed by taking the maximum observed date. Raw timestamp meaning/timezone,
early-close exceptions, path gaps and contract rolls still require verification.

### Smallest justified rule boundary

The evidence supports investigating expected duration demand around the applicable provider snapshot.
It does **not** yet supply an exact executable entry offset, forecast threshold, duration-to-ZN hedge map,
stop or liquidation protocol. We do not fill those gaps by moving the old13:59CT exit after seeing its loss.

An exact replication needs full-text rules/tables, source universe and scaling. A distinct adaptation would need those
source findings plus an independently available extension feature, an authoritative dated index calendar,
native contract/roll/bar-clock/cost checks and explicit failure/risk handling. Compare its identical-window calendar-only
baseline before any claimed incremental signal. The ordinary clock change alone cannot choose a trading window.

## Decision

**NEEDS DATA, not TEST.** No justified source-based return protocol is ready now. The next material gate is a
pinned manuscript plus sufficient as-published extension forecasts with original availability evidence, followed by
a no-return calendar/native-coverage audit. Do not spend a trial on an invented window or a selected subset of three reports.
A later TEST sheet and committed bounded preregistration must precede returns; existing cheap screens, trial limits
and account comparisons remain binding. No allocation, live system or VPS change follows.
