# VB parity-only target convention amendment; frozen stresses unchanged

Original preregistration: `agents/codex/plans/break_vb_onb.md`, commit **109a752**.
Original results: `agents/codex/results/break_vb_onb.md`, commit **f69ab0d**.
Review source: Claude branch **d82cbd39928e9d1cb63a883e66e3de019cb76dfe**,
`agents/codex/results/REVIEW_break_vb_onb_and_rest.md`, preserved under
`agents/codex/inputs/break_vb_onb/REVIEW_break_vb_onb_and_rest.md`.
User explicitly requests this amendment. Commit it BEFORE the new parity replay.

## Sole amendment and its evidence

Register **one parity-only target trade-through: 0.25 NQ point = one tick**. The prior owned-minute diagnostic
contains 896 MC target exits: none on exit bars with less than 0.25 point beyond target; 19 at 0.25, 7 at 0.50,
17 at 0.75, and 853 at >=1.00 point. The report Settings says "Fill limit price exceeded by 1 points".
This motivates an explicit reconstruction convention for this export; it is not a universal assertion about
every MultiCharts symbol/configuration, a new economic strategy, or a performance-selected target setting.

Rerun the unmodified VB baseline pairing with `through=.25`, using `codex_break_vb_onb.run_strategy` and its
unchanged `parity` function. Also reproduce and report the existing **through=1.00** baseline comparison.
No change to entry signals, costs, stop/target distances, maximum trades, holiday handling, date window,
warm-up, key construction, original engines or report file. Verify all those dependencies against the original
recorded hashes. Keep all prior outputs/reports intact; write a separate amendment report and output directory.

## Original parity gate, without relaxation

Keys: date / side / native 30-minute entry-bar identity on original report overlap, preserving unmatched rows.
Require ALL: >=98% matched from EACH list; >=99% matched entry prices within one .25-point tick;
>=95% matched gross trade P&L within $20 per NQ; gross correlation >=.98; absolute overlapping-list mean-net
gap <=max($20, 10% of absolute MC mean net). No fuzzy day-only pairing, selective date removal, extra match
search, or adjustment to any threshold. Gate passes only according to these original calculations.

**If .25 parity fails, stop before every stress family.** Save all unmatched rows by cause, separating verified
causes from hypotheses and unresolved cases. Include matching-key, entry-price and gross-P&L discrepancies.
No retry at another threshold or revised warm-up under this amendment.

## If parity passes: complete the original VB audit

Run exactly the original **314 VB stress scenarios** under the **1.00-point research target-through rule**
(execution stresses still include the originally registered 2.00-point cases). The .25 setting belongs only to
reconstructing the MC export. Report baseline differences under both fill conventions, including trade-count,
mean-net, drawdown and period results; do not use .25 results as the denominator for the 1.00-point stresses.
No .25 stress family, new rule, new best setting, portfolio change or rescue experiment is authorized.

Original master seed **8675309**, the same SeedSequence spawning and same noisy OHLC realizations as ONB:
100 noise (50 SD1 tick / 50 SD2 ticks), 6 indicator/anchor swaps, 3 timing shifts, 200 feasible simultaneous
±10% VB parameter draws with original rounding/calendar constraints and every raw rejected draw recorded,
5 execution cases. Reuse the original functions and parameter dictionaries without edits. Verify baseline
acceleration versus `candidates24`/`grid.execute` and the already-saved baseline; use original `metrics.perf`,
cost convention, noise/jitter definitions and source-checked read-only Grid24 cache. No cache rebuild.

Retain full 2018–22, 2023+, full-span and yearly all/long/short metrics; VB shorts are N/A. BENDS only if a
family has strictly >50% positive-net AND >=half the matching period's 1-point-baseline Sharpe, in BOTH periods,
with positive baseline Sharpe. BREAKS if median net<=0 OR median Sharpe<third of base, in EACH period;
otherwise MIXED/WATCH. Overall BREAKS if any family breaks, BENDS if all bend, else MIXED/WATCH. Preserve
all deterministic dependency flags, jitter ranges/rounding and per-run results; no verdict threshold changes.
Compute 2023+ 1-point-baseline 2,000-run ten-session-block bootstrap and daily permutations as originally planned.

Count this as completion of the existing **VB robustness trial**, not a new discovery. Disclose the extra
parity-only convention and every replay: one .25 baseline, one reproduced 1-point baseline, and conditional
314 new stress runs. Previously computed ONB runs are not rerun or selected. Both periods are already-seen
historical robustness evidence, not a new holdout. No new placebo, funded bench, sizing or live implication.

## Deliverable and boundaries

Script: `analysis/codex_vb_parity_stress.py`; report helper `analysis/codex_vb_parity_stress_report.py`.
Outputs: `analysis/outputs/codex_vb_parity_stress/`; report `agents/codex/results/vb_parity_stress.md`,
Summary <=5 lines. Preserve plan/review/data/code hashes, parity keys/rows, family/side/year tables, all seeds
and draws, and both baseline conventions. Use synthetic touch / one-tick-through fixtures, never a historical
return search, to verify the single switch. Report native close-stamped timing and MC inferred-minute limits.

Review context is accepted without rewriting old evidence: ONB's broad-clock jitter MIXED diagnosis remains
qualified by the review's open-session interpretation; RSI/Bollinger and XAU remain failed screens. Execution
diagnostics remain observational; quote logger, watchdog and Friday runbook remain proposals, no deployment.
Work/commit/push only **codex/work**. No plan/live/VPS/broker/API-key, logger or ranked-list changes.
