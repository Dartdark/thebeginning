# Pre-registration: pooled entropy-gate test on the breakout engines (2026-11-11)

Last test of the 1-min-bar order-flow-entropy proxy (Singha, arXiv 2512.15720). It failed gate 1 on the push engine
(F) and on Dual Thrust (diff +$61 / NQ, t 0.67). One pooled test instead of one per strategy (LESSONS 2026-11-10:
no best-of-N). Written and committed BEFORE any number below was computed. Script: `analysis/entropy_pooled_test.py`.

## Engines (MultiCharts trade lists, as reported; costs $7.25 + 2 ticks per contract subtracted, per contract)
- Vault Break v1 (`mc_reports/... VB v1.xlsx`), both sides.
- Twin Continuation v2 (`mc_reports/... 1 Minute Twin Continuation v2.xlsx`), all signals.
- Noise area RTH Anchor (`mc_reports/... 15 Minutes NQ Noise RTH Anchor.xlsx`), LONGS only (the planned version).
Jump Fade, ONB, EOS and other time-of-day pieces excluded a priori (the gate predicts move size, not direction).

## Entropy and the cut (fixed, not re-estimated)
Signal time = entry bar stamp minus the chart's bar length (the last bar the signal could see). 24h NQ minutes
(`jump_lib.minute()`), 31 closes ending at the signal time, up / flat / down pair-state entropy (same function as the
DT test). Gate on = entropy <= 1.3505, the Dual Thrust 2018-2022 30th percentile.

## Primary test
Design 2018-2022 only. Per strategy: d_s = mean net(gate on) - mean net(rest), se_s = Welch SE. Pooled
z = sum(d_s / se_s^2) / sqrt(sum(1 / se_s^2)) (inverse-variance). Pass: z >= 2.0 AND placebo p < 0.05 (2,000 draws,
each strategy's gate-on set replaced by a random subset of its own design trades of the same size).
If it passes: one look at 2023+, same sign and z >= 1.5, then benches. If it fails: the bar-data proxy is retired (F)
and the idea returns only with tick / trade data.

## Information only
Each strategy's d_s and t; longs / shorts where both exist.
