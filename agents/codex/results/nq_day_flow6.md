# NQ Day Flow Six: WATCH — historical t6 achieved, execution not cleared

Summary: One fixed six-leg NQ composite reaches net trade t 8.04, daily t 7.11, Newey-West(5) t 6.77.
At one MNQ per sleeve: 3,615 tickets, $7,928/year, PF 1.49, closed-EOD DD $2,566.
2023+ adjusted daily t is 5.21; four-tick stress reduces full adjusted t to 5.89.
Two inherited holiday/session holds and unconfirmed combined netting block an Apex-ready or deployable claim.
Known-signal recombination, not new independent alpha; no ranking, allocation, live action or new PowerLanguage.

Plan: `agents/codex/plans/nq_day_flow6.md`, committed **d27cda2** before composite returns.
Design saved in **e1e924b** before validation. Scripts: `analysis/codex_nq_day_flow6.py` and `_report.py`.
Outputs: `analysis/outputs/codex_nq_day_flow6/`. Specification: `agents/codex/inputs/nq_day_flow6/strategy_spec.json`.
Trials: **one new combination**; no weight/parameter search. Source selections and earlier portfolio tests are prior trials.

## Rule as tested

Run the existing **Vault Break, ONB ML v2, Monday Long, Expiration Open Short, Late-Day Flow and NFP Fade**
as six virtual sleeves. Each source trade gets **one MNQ**, with the existing direction, stop, target and time exit.
For source inputs use `NumContracts=1`, and `RiskPerTrade=0` where present. Exact source/report hashes and defaults
are in the specification; this is an offline composition of actual MC tickets, not a new independent signal-engine rebuild.
The six intraday systems were taken from the prior seven-leg alpha study; overnight Bridge Monday was excluded in advance.

The broker target in a future combined manager is the sum of virtual targets, rather than independently submitted
chart positions. Opposing sleeves can coexist virtually with zero actual net exposure. Every sleeve retains ownership
of its stop/exit; repeated exits cannot create a new position. Reference target accounting passes synthetic checks.
It is intent arithmetic only: a delayed old-ticket exit can erase a new same-sleeve intent because the reference
lacks ticket-generation IDs and confirmed broker fill state. The independent review identifies this execution blocker.
Observed minute-grid maximum: **4 gross / 4 net MNQ**, versus a theoretical six-contract cap;
79 sessions contain opposing virtual sleeves. Exact same-minute order sequence is not independently verified.

## Results

Window: **2018-01-01 through 2026-10-09**, 2,262 repository-calendar sessions.
Primary cost is **$1.24 per MNQ round trip plus $0.50 for each market/stop fill**. Targets have no extra exit slip.
Charge every virtual ticket even when a net order manager might save fees. Gross $78,799.50, costs $7,637.60, net $71,161.90.
Native MNQ fills are not observed: this reprices NQ source prices with independently modeled micro fees.
All annual figures use 252 sessions/year. DD is closed/EOD, includes the initial zero, and excludes intraday open-equity DD.

| period | side | trades | win | avg | annual | sharpe | sortino | profit_factor | calmar | ulcer | max_dd | t_trade | t_daily | t_nw5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2018-22 | all | 1899 | 57.9% | $14 | $5,381 | 2.09 | 4.03 | 1.41 | 2.30 | 1.07 | $2,342 | 5.15 | 4.73 | 4.44 |
| 2018-22 | long | 1485 | 59.5% | $11 | $3,115 | 1.36 | 2.43 | 1.30 | 1.18 | 1.40 | $2,645 | 3.58 | 3.07 | 3.04 |
| 2018-22 | short | 414 | 52.2% | $28 | $2,266 | 1.67 | 3.97 | 1.85 | 2.99 | 0.50 | $757 | 3.92 | 3.78 | 3.46 |
| 2023+ | all | 1716 | 62.9% | $25 | $11,302 | 2.73 | 5.56 | 1.56 | 4.40 | 0.77 | $2,566 | 6.19 | 5.37 | 5.21 |
| 2023+ | long | 1391 | 64.7% | $23 | $8,454 | 2.18 | 4.51 | 1.52 | 3.24 | 0.97 | $2,610 | 5.30 | 4.29 | 4.36 |
| 2023+ | short | 325 | 55.1% | $34 | $2,849 | 1.67 | 3.25 | 1.70 | 2.18 | 0.67 | $1,308 | 3.21 | 3.29 | 3.30 |
| full | all | 3615 | 60.3% | $20 | $7,928 | 2.37 | 4.75 | 1.49 | 3.09 | 0.89 | $2,566 | 8.04 | 7.11 | 6.77 |
| full | long | 2876 | 62.0% | $17 | $5,412 | 1.76 | 3.46 | 1.42 | 2.05 | 1.18 | $2,645 | 6.39 | 5.26 | 5.27 |
| full | short | 739 | 53.5% | $31 | $2,516 | 1.66 | 3.50 | 1.77 | 1.92 | 0.53 | $1,308 | 4.99 | 4.98 | 4.77 |

Trade t treats tickets independently and is secondary to the daily statistics; same-day clustering is preserved
by daily aggregation and the daily Newey-West figures. Full NW(20) t is 7.20.
The design screen passed before validation; 2023+ is historical validation already used by the constituent research,
not an untouched holdout. T>=6 is an observed full-sample statistic, not an expected forward statistic.

| period | trades | total | sharpe | profit_factor | max_dd |
| --- | --- | --- | --- | --- | --- |
| 2018 | 338 | $-342 | -0.24 | 0.96 | $1,302 |
| 2019 | 317 | $970 | 0.83 | 1.15 | $928 |
| 2020 | 387 | $8,493 | 2.95 | 1.65 | $1,892 |
| 2021 | 414 | $8,050 | 2.90 | 1.53 | $852 |
| 2022 | 443 | $10,351 | 2.66 | 1.46 | $2,342 |
| 2023 | 439 | $11,703 | 4.03 | 1.84 | $894 |
| 2024 | 436 | $7,777 | 2.26 | 1.41 | $1,165 |
| 2025 | 448 | $12,645 | 2.96 | 1.57 | $2,017 |
| 2026 | 393 | $11,515 | 2.42 | 1.50 | $2,566 |

2018 loses money; no year or side was removed. 2026 is partial through October 9.

## Costs, uncertainty and prior selection

| case | total | t_trade | t_daily | t_nw5 |
| --- | --- | --- | --- | --- |
| primary | $71,162 | 8.04 | 7.11 | 6.77 |
| fee_1.04 | $71,885 | 8.12 | 7.18 | 6.84 |
| four_ticks | $61,697 | 6.96 | 6.19 | 5.89 |

Four adverse ticks per slipped fill still leave positive returns but **fail the adjusted t6 target**.
2023+ 90% ten-session/5,000-path bootstrap intervals:

| metric | actual | p5 | p95 |
| --- | --- | --- | --- |
| sharpe | 2.73 | 2.01 | 3.53 |
| sortino | 5.56 | 3.66 | 8.08 |
| pf_day | 1.85 | 1.55 | 2.24 |
| max_dd | 2566.32 | 1803.63 | 4563.95 |
| annual | 11302.49 | 7965.81 | 14925.27 |

Both sides' bootstrap/permutation results are saved. The 10,000-trade bootstrap is descriptive because
the tickets overlap; daily block resampling is the main uncertainty measure.
Latest tier parser counts **326 prior ranked items**, plus this combination; parsed variants
are 1,319, an incomplete lower bound. Daily DSR at the 10,000-search sensitivity is 0.99988.
Neither DSR nor t removes constituent-selection bias. Existing VB parameter searches, ONB model/filter selection,
and earlier books have already used these years. No claim of six newly independent alpha discoveries.

The 2,000 session-level gross-sign-flip null is exceeded in every draw in full and 2023+ (corrected p=1/2001).
It preserves dependence across same-day sleeves and subtracts fees, but is **not an executable random-entry or
random-side bracket placebo**. Individual source studies supply earlier execution-placebo evidence; this study
does not newly establish those results. No filter/random-drop search was introduced.

## Account and portfolio context

Standalone one-year EOD-only simulations, 5,000 ten-session paths, fixed one-MNQ sleeve quantities:

| period | trail | pnl_p50 | dd_p95 | p_loss | p_trail_hit |
| --- | --- | --- | --- | --- | --- |
| full | $2,000 | $7,804 | $3,110 | 0.8% | 10.6% |
| full | $4,000 | $7,804 | $3,110 | 0.8% | 0.8% |
| 2023+ | $2,000 | $11,310 | $3,616 | 0.3% | 13.3% |
| 2023+ | $4,000 | $11,310 | $3,616 | 0.3% | 1.5% |

These omit intraday liquidation, daily loss stops, payout/qualification rules and combined fills. They are not
evaluation pass rates or funded-account blow-up probabilities. In particular, $2k EOD-trail risk is material.
All four requested Apex contexts (50K/150K evaluation/funded) are **not cleared**: the frozen report tickets contain
session-hold violations, and current-book ADD/REPLACE/EMPTY account claims also lack causal joint overnight baselines.
No full current-account bench was invented from daily/proxy paths.

Current personal FULL19 at afde088, 2023+ pool, 1,000 paired 252-session ten-day histories:

| contrast | mean_year | dd95 | median_profit_dd95 | incremental_mean |
| --- | --- | --- | --- | --- |
| BASE | $49,138 | $7,796 | 6.27 | $0 |
| ADD | $60,403 | $9,211 | 6.48 | $11,265 |
| EMPTY | $37,806 | $7,938 | 4.74 | $-11,332 |
| REPLACE | $49,071 | $7,799 | 6.26 | $-67 |

BASE contains these same six legs. ADD doubles their exposure; REPLACE substitutes the basket for those six;
EMPTY removes them. The roughly $67 annual REPLACE difference is source/fee/bookkeeping reconciliation,
**not new alpha**. ADD's modest profit/DD point gain is not an allocation recommendation. Starter A-D controls
are saved separately; replacing only their present matching legs also changes which signals they contain.
The full-book correlation is 0.61; candidate net on book-loss days is $-28,047.
This is equity-index exposure, not protection. No missing personal dates or candidate money were silently remapped.
Baseline inherited fee, overnight-marking, and missing OT-history limits remain; daily DD does not verify margin safety.

## Execution failures and evidence limits

- **MON:** July 3, 2023 08:35 entry label, exit **17:05 that day**, after the shortened cash session and CME break.
- **NFP:** April 7, 2023 07:50 entry label, exit **Sunday April 9 at 17:05**. Both losing tickets remain in every total.
- 17:00+ exits are booked to the next CME date (July 4 / April 10), with original price-date stamps retained.
- 3,696 unobserved held minutes in aggregate: most are the NFP holiday/weekend span, not verified feed failures;
  other sleeves contribute 291, including MON's shortened session/break. No absent price was fabricated or gap trade deleted.
- All six reports say one-minute Bar Magnifier enabled. `report_settings.json` records each source fill-through,
  commission and slippage setting. Our costs are applied explicitly rather than accepting the reports' zero costs.
- Source limit fills, minute ordering, current source-file parity, roll-switch handling and native MNQ queues remain
  execution assumptions. The combined manager was not run in MultiCharts, and the target-position reference is not
  a complete signal generator, order router, calendar fix or deployable strategy file.

## Independent check and next step

Independent ledger/statistics review: `agents/codex/results/nq_day_flow6_independent_review.md`;
checker script/output: `analysis/codex_nq_day_flow6_checker.py`, `analysis/outputs/codex_nq_day_flow6_checker/`.
Verdict: **PASS WITH CONCERNS for historical accounting only**; all 3,615 tickets and 2,262 daily totals reconcile.
This is independent workbook arithmetic and inference, not a second raw-signal reconstruction or platform confirmation.

The requested **historical t6 composite exists**. Its constituents already belong to the research book; do not add
it on top automatically. Recommended next step: freeze a separate operational calendar/netting implementation,
then verify its changed trade list in a research MultiCharts run and a prospective paper log before any trading decision.
This frozen study retains its original rule and exceptions; no after-results repair, weight search or deployment was run.

Reproduce with the existing cloud interpreter, from the repository root:

```bash
/workspace/venvs/thebeginning/bin/python -B analysis/codex_nq_day_flow6.py --phase design --prereg d27cda2
/workspace/venvs/thebeginning/bin/python -B analysis/codex_nq_day_flow6.py --phase validation --prereg d27cda2
/workspace/venvs/thebeginning/bin/python -B analysis/codex_nq_day_flow6.py --phase diagnostics --prereg d27cda2
/workspace/venvs/thebeginning/bin/python -B analysis/codex_nq_day_flow6_report.py
```

Writes are exclusive and compare pre-existing bytes; original artifacts are preserved. Bookkeeping fixes for the
observed cross-date/after-reopen report exits changed neither source tickets nor weights. No scientific package or
shared price/account cache was installed/rebuilt, no root/shared plan edited, no other branch pushed.
Claude review path: `agents/codex/results/nq_day_flow6.md`.
