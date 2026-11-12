# Pre-registration: order-flow-entropy gate on Dual Thrust v4 (2026-11-11)

Ingredient: Singha, arXiv 2512.15720 (low order-flow entropy -> larger next moves, no direction). On the push engine
(TIER_LIST D) the 1-min-bar proxy gave 1.11x larger moves. Mechanism fit: Dual Thrust is a breakout with a fixed 50-pt
stop / 100-pt target, so it pays when the breakout bar starts a large move; a size gate is the right kind of filter.
Written and committed BEFORE any DT-by-entropy number was computed. Script: `analysis/dt_entropy_test.py`.

## Engine (unchanged)
Dual Thrust v4 as rebuilt in `analysis/dual_thrust_test.py` (DT.load / DT.setups / DT.run, its costs).

## Entropy at the signal
24h NQ minutes (`jump_lib.minute()`, RTH + overnight files). Closes of the 31 minutes ending at the signal bar
(sig_time) -> 30 one-minute changes -> symbols up / flat / down -> Shannon entropy of the 9 consecutive-pair states.
Fewer than 20 minutes found -> no entropy, the trade counts as 'rest'.

## Primary test (frozen)
Gate on = entropy <= the 30th percentile of DT signal entropies in 2018-2022 (the cut is fixed from the design period
and reused unchanged on 2023+).
1. Design 2018-2022: mean net (gate on) - mean net (rest) > 0, Welch t >= 2.0; and a placebo: the same number of
   trades drawn at random from the design trades, 2,000 draws, p < 0.05 that a random subset's mean beats the gated mean.
2. One look at 2023+: same sign, Welch t >= 1.5.
3. If both pass: as a SIZING ingredient (gate on 2 MNQ -> 3 MNQ? or rest 2 -> 1?) on the 150K eval bench (bench150
   LIVE_EVAL) and the funded bench, add and replace, before any change to the live DT chart.

## Information only (never chosen from)
Cut at the 20th / 50th percentile; longs and shorts separately; |move| of the gated trades (MFE, MAE in points).
