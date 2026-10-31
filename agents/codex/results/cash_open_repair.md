# NQ Cash-Open Repair: REJECT — new standalone rule fails design; t6 not achieved

Summary: Built a new NQ-only entry rule from raw NQ/ES prices, not a combination of existing strategy trades.
Primary 5-minute rule: 141 design trades, PF 1.08, trade t 0.38, daily NW(5) t 0.41.
The 15-minute and stronger-dislocation variants also fail; none qualifies for validation or the requested t6 target.
Five models including two controls were tested; 2023+ returns/account benches were not run.
Reject this hypothesis; no fitted rescue, PowerLanguage, ranking, allocation or live change.

Plan: `agents/codex/plans/cash_open_repair.md`, **a9af875**, committed before new returns.
Evidence: `agents/codex/evidence/cash_open_repair.md`. Scripts: `analysis/codex_cash_open_repair.py`,
`analysis/codex_cash_open_repair_report.py`. Output: `analysis/outputs/codex_cash_open_repair/`.
Current research branch codex/work; latest Claude context5d1096d inspected without merging/editing its files.

## Rule as tested

**Instrument:** NQ; one position, one trade/day. **Timeframes:** 5 or 15 minutes for signals, one-minute fills.

1. At the cash open compare NQ and ES's overnight log returns, each from the preceding full cash session's
   exact15:00 close to today's08:31-labeled open (08:30 wall time, Central).
2. Estimate NQ-on-ES beta, residual mean and residual sample SD using only the preceding60 valid observations.
   Today's normalized NQ-specific deviation is z. No coefficient is fitted to trade profits.
3. If |z|>=1, wait for the first5-minute NQ bar to close. Buy only when NQ underperformed overnight and that
   opening bar rises; short only when NQ outperformed overnight and the opening bar falls.
4. Enter the next native minute open. Stop0.15 and target0.30 times the prior15-day calendar ATR, distances
   rounded up to a quarter-point. Stop/target active on the entry bar; no trail, BE or reentry.
5. Exit by11:00CT. No holiday/early-close entries. The preregistered quarterly-roll window and anchor failures
   skip before entry; no return-based day deletion. ES is an input, never a second traded position.

R15_Z1 uses the first15-minute bar. R5_Z2 uses5minutes and |z|>=2. BASE5/BASE15 follow the first bar on all
same-data/calendar-eligible days without the overnight gate; these controls cannot be selected as new strategies.
This is a new rule relative to the repository's existing RS intraday-continuation and ONB range-breakout entries.
Its underlying inventory/overnight-reversal idea has related prior failures; novelty does not supply an edge.

## Design results: 2018-22 only

Primary NQ costs: **$7.25 round trip plus one adverse tick ($5) per market/stop fill**; target exits have no extra
slippage and require a full point through. Native MNQ fees are separately modeled, not mini fees divided by ten.
Daily sample has1259 scheduled cash sessions, including zero-trade days. Annual metrics use252sessions/year.

| model | trades | win | total | avg | profit_factor | t_trade | t_nw5 | max_dd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R5_Z1 | 141 | 36.9% | $5,152.75 | $36.54 | 1.08 | 0.38 | 0.41 | $9,207.75 |
| R15_Z1 | 153 | 34.6% | $-15,499.25 | $-101.30 | 0.81 | -1.11 | -1.11 | $26,412.75 |
| R5_Z2 | 41 | 39.0% | $3,017.75 | $73.60 | 1.16 | 0.40 | 0.46 | $5,593.00 |
| BASE5 | 1082 | 38.6% | $35,460.50 | $32.77 | 1.08 | 1.02 | 1.13 | $16,664.25 |
| BASE15 | 1078 | 38.1% | $19,229.50 | $17.84 | 1.04 | 0.57 | 0.61 | $29,082.50 |

All three candidates fail the committed gate: >=100 trades, positive net, trade t>=2, daily NW5 t>=1.5,
PF>=1.20, at least4 positive design years, positive native-MNQ and four-tick stressed net.
R5_Z2 also has too few trades. No model was chosen; the full-history t6 claim is **not established**.

Whole/long/short metrics:

| model | side | trades | annual | sharpe | sortino | profit_factor | calmar | ulcer | max_dd | t_trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R5_Z1 | all | 141 | $1,031.37 | 0.17 | 0.30 | 1.08 | 0.11 | 5.35 | $9,207.75 | 0.38 |
| R5_Z1 | long | 70 | $2,984.87 | 0.64 | 1.28 | 1.50 | 0.59 | 3.00 | $5,045.25 | 1.43 |
| R5_Z1 | short | 71 | $-1,953.50 | -0.51 | -0.78 | 0.72 | -0.17 | 7.77 | $11,398.25 | -1.14 |
| R15_Z1 | all | 153 | $-3,102.31 | -0.50 | -0.76 | 0.81 | -0.12 | 23.42 | $26,412.75 | -1.11 |
| R15_Z1 | long | 79 | $1,909.97 | 0.39 | 0.72 | 1.26 | 0.32 | 4.43 | $5,891.75 | 0.87 |
| R15_Z1 | short | 74 | $-5,012.28 | -1.31 | -1.63 | 0.44 | -0.18 | 25.99 | $28,423.00 | -3.08 |
| R5_Z2 | all | 41 | $604.03 | 0.18 | 0.32 | 1.16 | 0.11 | 3.77 | $5,593.00 | 0.40 |
| R5_Z2 | long | 18 | $376.20 | 0.15 | 0.26 | 1.20 | 0.07 | 3.49 | $5,227.50 | 0.32 |
| R5_Z2 | short | 23 | $227.83 | 0.10 | 0.19 | 1.13 | 0.08 | 2.32 | $3,001.25 | 0.23 |

Yearly net per NQ, all sides:

| year | R5_Z1 | R15_Z1 | R5_Z2 |
| --- | --- | --- | --- |
| 2018.0 | $1,434.50 | $2,582.25 | $1,922.00 |
| 2019.0 | $-241.75 | $1,900.00 | $-701.25 |
| 2020.0 | $3,438.50 | $-10,452.25 | $2,555.25 |
| 2021.0 | $1,508.50 | $-363.75 | $-3,278.50 |
| 2022.0 | $-987.00 | $-9,165.50 | $2,520.25 |

The primary has only3 of5 positive years. Its long side is stronger (t1.43), still below the gate; selecting
longs after seeing this would be another trial, not a valid rescue. No short-only or long-only candidate was tested.

## Filter and cost controls

| model | removed_trades | removed_net | removed_t | p_random_net_ge_kept | p_kept_better_net_and_dd |
| --- | --- | --- | --- | --- | --- |
| R5_Z1 | 941 | $30,307.75 | 0.95 | 50.1% | 44.6% |
| R15_Z1 | 925 | $34,728.75 | 1.14 | 93.2% | 2.1% |
| R5_Z2 | 1041 | $32,442.75 | 0.96 | 40.5% | 46.9% |

Each filter is compared to1,000 equal-sized random subsets of its unfiltered base. R5_Z1 removes941 trades
that earn$30,307.75 in total; random subsets match or beat its net50.1% of the time. Its greater remaining
average does not establish incremental value. All removed groups make positive aggregate profit.
The stronger gate does not establish an improvement either. Controls share valid-anchor/warm-up/calendar masks,
and every kept trade matches its base's entry, direction and result exactly.

| model | net_MNQ | four_tick_NQ_net |
| --- | --- | --- |
| R5_Z1 | $442.66 | $1,627.75 |
| R15_Z1 | $-1,628.72 | $-19,399.25 |
| R5_Z2 | $280.66 | $1,997.75 |
| BASE5 | $2,988.82 | $7,815.50 |
| BASE15 | $1,367.78 | $-8,670.50 |

Native MNQ fee assumption: $1.24 RT plus$0.50 per slipped fill. Four-tick stress retains NQ$7.25 commission
and charges$20 per slipped fill. Positive primary dollar totals are weak relative to uncertainty; they are not a pass.

## Data, clocks and engineering checks

Only raw NQ/ES minute inputs and shared grid/execution/metric/calendar functions are used. No prior strategy
trade list, old portfolio P&L or ML model supplies entries or candidate performance.
Design price arrays are truncated at2022-12-31 before feature generation/execution. No2023+ candidate return,
plot or ranking was generated.2017 provides limited warm-up; the rule waits until60 prior valid observations.
Design eligibility census: {"calendar_roll_window": 100, "eligible": 1086, "holiday_or_early_close": 10, "missing_exact_anchor": 3, "prior_feature_warmup_or_scale": 60}.
Three dates lack exact anchors; no older convenient close or future-filled observation substitutes for them.
Predeclared roll/calendar exclusions are assumptions about valid data, not evidence that each excluded day
contains a contract switch. Continuous prices are not back-adjusted; surviving roll-related artifacts remain possible.

Every candidate has zero unobserved held minutes in this design sample. BASE5 has2, retained/inventoried;
controls are not repaired after outcomes. No source calendar violation or after11:00 exit occurs.
Next-open entries use08:36/08:46close labels, approximately08:35/08:45wall time, respectively.
The11:00exit is a bar-close fill. Stop gap fills use worse observed opens; OHLC minute ordering and actual
MNQ queues remain unverified. Shared engine MAE can include full exit-minute extremes; it is not a tick-path audit.

Synthetic checks cover prior-only features, future-anchor perturbations, missing preceding-close behavior,
calendar/roll guards, warm-up, entry-bar stops, worse gap stops, target-through and initial-zero DD.
Ledger checks reconcile price/quantity/costs, one trade/day, phase boundary and deadline. These are engineering
checks, not independent raw-signal replication, platform confirmation, or a statistical promotion pass.
No shared cache was built; NQ/ES grids existed only in this process. No scientific package was installed.

## Account placement and stopping

| Context | Result |
|---|---|
|50K evaluation|Does not advance: all new candidates fail design. No pass-rate estimate.|
|150K evaluation|Same failed design; no benefit inferred from another account size.|
|50K funded|Does not advance; no payout/blown comparison run.|
|150K funded|Does not advance; no payout/blown comparison run.|
|Personal A-D/current19|Does not advance; no addition/replacement recommendation or uncomputed marginal-benefit claim.|

The cheap-screen stop rule deliberately blocks2023+ validation, full bootstrap/account work and PowerLanguage
after a failed design. No account simulation or forward-log allocation was needed to reject these candidates.
No forced "t6" label, pooled old-strategy return series, fitted weight, changed threshold or post-results clock was used.
Related prior searches (RS, CO-OC, opening momentum, inventory failures) remain disclosed; five models here
are additional trials, not five fresh independent opportunities to claim significance.

## Reproduction and next step

```bash
/workspace/venvs/thebeginning/bin/python -B analysis/codex_cash_open_repair.py --phase design --prereg a9af875
/workspace/venvs/thebeginning/bin/python -B analysis/codex_cash_open_repair_report.py
```

Artifacts are created exclusively and checked against pre-existing bytes. Input hashes and final script/artifact
hashes are saved. No shared plan, root TODO, existing live source, broker/VPS/API setting or other branch was edited.
No validation or parameter search beyond the five frozen configurations. No independent checker/promotion claim.
Recommended next step: discard this hypothesis and research a different information source/mechanism, with a
separate preregistration; do not optimize this design failure into an asserted t6 strategy.
Claude review path: `agents/codex/results/cash_open_repair.md`.
