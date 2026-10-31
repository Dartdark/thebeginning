# Swing Target exit-kind account replay

Continue the explicitly queued October 30 accounting correction. This is a historical
account replay of frozen trades, not a new strategy search or fresh holdout.

Inputs: Claude `86df2c0` (including the numeric ST_KIND fix), Codex CODE_BE
ledger at `70f708a`. Preserve the holiday repair in swing_target_bench.pt_trades.
Use the existing Lab, paths, Boot, and 50K/150K funded simulators without changing
their accounting, cost or payout policies. Legacy costs are $7.25/NQ plus one
tick per market/stop fill, divided by ten for MNQ; these are not measured native fees.

Rebuild the missing scratch dependencies without executing helper research sweeps.
The main build currently crashes on an ONB ML report row whose exit signal is
`open`, stamped midnight before entry. Exclude only explicitly identified open
report placeholders from the closed-trade lab and record each exclusion; fail on
any other invalid same-date geometry. Preserve the existing OND MaxEntryDelay
filter (OND is not in these funded rosters). Record source and input hashes.

For each account compare five frozen portfolios on identical circular 20-day
blocks, 500 trading days, seed 20261031, 500 histories:

1. BASE: the pre-ST historical roster in swing_target_bench.plans50/plans150.
2. REPLACE_OLD: adopted swap with the original string-kind adapter.
3. REPLACE_FIXED: identical swap with corrected numeric kinds.
4. EMPTY: the replaced allocation removed without ST.
5. ADD_FIXED: BASE plus ST at the adopted size (1/2 MNQ).

50K replacement: VB normal 2 -> 1 plus ST 1 (flagged VB stays 1).
150K replacement: DT 2 -> ST 2. Original 150K roster base quantities and the
simulator's integer flooring after cushion scaling remain explicit inherited
assumptions. No parameter selection. No new strategy economic definitions.

Report one-/two-year payouts, one-/two-year p5, blown share, completion share,
median time to sixth payout, paired outcome changes and Monte Carlo uncertainty.
Do not infer a portfolio gain from isolated trade improvement. A swap is supported
only if fixed REPLACE improves on BASE and EMPTY without a material risk increase;
otherwise report mixed/unsupported. Preserve uncertainty and current-roster drift
(50K subsequently replaced RS longs with T_ONESIDE). No plan/live edits.

Before simulation verify target-only cash delta, stop-only exit-minute effects,
holiday repairs, valid geometry and total daily/trade cash reconciliation.
Stop on a material input/accounting mismatch, save the blocker, and do not invent
portfolio results. Simulation checkpoints and the exact command permit resumption.
