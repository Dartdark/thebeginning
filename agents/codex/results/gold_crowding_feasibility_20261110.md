# Gold crowded-long liquidation: REJECT EVALUATION FEASIBILITY

Summary: Built the release-aware positioning/event census; the frozen feasibility screen fails.
2018–22: 228 baseline downside entries, only 38 with high crowding, across 23 report clusters.
Only 20.4% of 30-calendar-day windows contain a crowded entry; minimum requirements were 40 entries and 25% of windows.
Profitability remains untested: 0 economic return trials, no recent/account tests or MultiCharts strategy.
Close this evaluation implementation; preserve data and the mechanism without widening thresholds to rescue it.

User authorized implementation/testing November 9, 2026 Pacific. This is the completed first gate, not a P&L backtest.
Hypothesis: [market map](gold_market_hypothesis_20261110.md).
Protocol: [gold_crowding_census_20261110.md](../plans/gold_crowding_census_20261110.md), frozen commit
`44df28ebf503f8337c7eaae89a37d5fa9e69f4ff` before counts.
Script: `analysis/codex_gold_crowding_20261110.py`; QA: `analysis/codex_gold_crowding_qa_20261110.py`.
Outputs: `analysis/outputs/codex_gold_crowding_20261110/{data_audit,census,qa}.json`, position states and event census CSVs.
Trials: 1 frozen no-return census; **0 economic definitions evaluated for returns**. Existing related failures remain counted.
Current Claude research snapshot inspected: `9810a5285ebba50f4e905b5ea7530eea1a0b514d`.

## Exact definition counted

- Managed Money net long/OI, percentile >=80% against the preceding 52 admitted reports. Net exposure does not measure leverage.
- Admitted ordinary Tuesday observations, no federal-holiday/Good-Friday/mourning weeks. Usable after Friday 16:30 Eastern
  (ordinary 15:30 release plus one-hour buffer), observation age <=14 calendar days. No invented catch-up releases.
- Omit the shutdown/catch-up observation interval and corrected gold March 26, 2019 row; trading blackout December 22, 2018
  through March 31, 2019. [Exact source/exclusion evidence](../inputs/gold_crowding_20261110/sources/clock_evidence.md).
- First minute-close crossing below the previous completed Globex session's low, from at/above it, during 07:20–11:00 CT.
  One/day. Prior session 17:01–15:59 CT, at least 95% observed minutes and final bar present; ATR15 known before the decision.
- Exclude already observable suspect continuous-roll jumps at 03:32/17:01 CT. Require complete planned next-open / 30-minute
  paths plus one-minute-later stress coverage. Inspect missingness only, not forward returns or stop outcomes.

This is a deliberately reduced released-position subset. It is not the complete latest-report strategy, and excluded
holiday/delay observations are not replaced with zero exposure. Only owned GC 2017–22 files loaded; no shared all-year
cache, 2023+ GC data, or mirror price/indicator series was used.

## Results of the no-return screen

| Item | Count / result |
|---|---:|
| 2018–22 weekday trading rows | 1,297 |
| Qualified downside entries before crowding filter | 228 |
| Crowded entries | 38 |
| Distinct reports represented by crowded entries | 23 |
| Complete rolling 30-calendar-day start windows | 1,275 |
| Windows containing at least one crowded entry | 20.4% |
| Median crowded entries per 30-day window | 0 |

| Year | Crowded entries |
|---|---:|
| 2018 | 3 |
| 2019 | 22 |
| 2020 | 3 |
| 2021 | 2 |
| 2022 | 8 |

| Gate frozen before counts | Requirement | Observed | Verdict |
|---|---|---|---|
| Event count | >=40 | 38 | FAIL |
| Report clusters | >=20 | 23 | PASS |
| 30-day opportunity coverage | >=25% | 20.4% | FAIL |
| Assumption-based power | Required gross mean <= optimistic 0.10 ATR ceiling | Approximately 0.0723 ATR | PASS under assumptions |

Power arithmetic uses an **assumed** 0.12 ATR 30-minute SD and report clusters as independent units. Net hurdle for t≈2
is 0.0500 ATR; assumed cost at median candidate ATR adds 0.0223 ATR. This is not an observed return, SD or expected edge.
Cost assumption is one MGC at $10/oz, $3 round-trip fees plus one $0.10 tick per fill, total $5; two-tick stress would total $7.
These costs enter only the feasibility calculation. No filled trades, realized commissions or executable stop losses
are reported. Stop/size draft fields in the census settings were not simulated.

The event-count failure is close to its arbitrary screening boundary; the larger practical concern is sparse and
clustered opportunity. Most 30-day windows contain none, and 2019 supplies most events. That fails this implementation's
precommitted evaluation-use screen. It does **not** establish that the 38 hypothetical trades lose money or that all
gold-positioning hypotheses are false. A rare trade can be profitable and still miss this research objective.

## Source QA and exclusions

Free pinned mirror supplies 326 position rows, October 4, 2016–December 27, 2022. Of these, 243 ordinary reports survive
the source/calendar mask and 191 have 52 earlier admitted observations for ranking. All 313 overlapping 2017–22 dates/OI
match owned Legacy gold data; Legacy is used only for date/OI cross-check, never relabeled as Managed Money.
Official July 17, 2018 gold code 088691 has OI 528278, Managed Money long 107775, short 134224, spreading 51880: exact sample parity.

Full data/output hashes and source identity are saved. The free mirror is a **current historical extract**, not an
authenticated original-vintage panel. Sample parity and OI equality do not prove every Managed Money cell's vintage.
Native MGC quote/fee parity and a dated GC contract/roll ledger are also unresolved. Those limitations independently
prevent deployment/promotion; this no-return rejection does not waive them.

Excluded trading rows reconcile to the census: warmup/no admitted report 25; no downside crossing 768; incomplete prior
session 41; stale report 165; shutdown blackout 70; remaining 228 events. No suspect-roll or planned-path exclusions occurred
after those checks in this sample. That does not certify all contracts or every missing prior-session low.

Maker QA: 18 checks pass, including decision-time publication availability, age, causal 52-report ranks, corrected-row
and shutdown exclusions, next-bar entry labels, horizon, counts and input/code hashes. One initial QA invocation hit a
pandas Series/timezone type error; corrected in the QA script only. Census rules/counts and economic trial count unchanged.
This is not independent verification.

## Stages stopped and next decision

No economic return preregistration/TEST admission, gross/net backtest, stop/latency/cost replay, price-only return
comparator, random-drop test, recent replication, account simulation, correlation estimate or MultiCharts code was run.
Sharpe, Sortino, PF, Calmar, Ulcer, drawdown and BASE/ADD/REPLACE/EMPTY gains are **not assessed**, not zero.

**Can strategy code be made? Yes in principle.** Release-aware state and signal code now exists; a trading strategy
still needs frozen execution rules and admitted native inputs. This version fails before that work is justified.
No parameter widening, shorter warmup, extra entry times or 2023+ look is authorized as a rescue by this result.
Keep the acquired fields for separately justified future research; a new gold lead needs a distinct source-supported
mechanism and its own gate. No claim of background searching, account protection or live change.

Reproduce:
```bash
/workspace/venvs/thebeginning/bin/python analysis/codex_gold_crowding_20261110.py --mode census
/workspace/venvs/thebeginning/bin/python analysis/codex_gold_crowding_qa_20261110.py
```
