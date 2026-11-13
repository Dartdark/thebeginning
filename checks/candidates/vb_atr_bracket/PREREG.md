# Vault Break with an ATR-scaled bracket (user 2026-11-12: "test the atr-scaled bracket")
Written before any result of this test. Motivation (analysis/outputs/vb_drawdown_diag_output.txt): VB's fixed 40 / 75-point bracket
shrank from 0.31 / 0.58 of the 15-day ATR (2018) to 0.07 / 0.13 (late 2026); time exits fell from 67% to 4%.
DISCLOSED: 2025-26 was already seen in that diagnosis (VB lost from Aug 2026), so the holdout is not clean; the
design choice below is made on 2018-24 only and fixed here.

Entries unchanged (VB v1, vault_break_v8_test.run(g, "v1")). Exit = target tp x ATR15 / stop sl x ATR15 (the day's boundary ATR,
known at the open, rounded to 0.25), time exit 14:30 unchanged. Costs $7.25 + 1 tick a market / stop fill, 1 NQ.

Variants (10):
  P  PRIMARY: tp / sl = the 2018-24 MEDIAN of 40 / ATR and 75 / ATR over VB's trades (the bracket's typical size in the
     design years, held constant relative to volatility). Computed in the script from 2018-24 only and printed.
  G  grid: tp in {0.10, 0.15, 0.20} x sl in {0.20, 0.30, 0.40}; the best on 2018-24 average R is reported as a
     secondary (selection disclosed; it counts 9 extra trials).
  F  control: the current fixed 40 / 75.

Unit: R = net / (stop points x $20) per trade (risk-normalised, because a scaled stop is bigger in $ when ATR is high; on a live
account the size would be set from the stop). Also $ per NQ.
Pass (P vs F): 2018-24 avg R >= F's, AND 2025-26 avg R > 0 AND > F's, AND 2023+ positive. Report: by year, win / exit mix,
Sharpe / Sortino / PF / Calmar / Ulcer on daily R, t, bootstrap 95% interval of 2025-26 avg R, DSR at N_items.

## Result (2026-11-12, `analysis/outputs/vb_atr_bracket_test_output.txt`, data to 11/06): FAIL
Primary P (0.163 / 0.305 ATR): avg R 2018-24 +0.032 vs fixed +0.059; 2025-26 -0.006 vs +0.051; 2026 -$115 per NQ vs +$5.
Best grid (0.20 / 0.20, selected on 2018-24): 2025-26 +0.007 R vs fixed +0.051. Every scaled variant is worse than the fixed bracket
in 2025-26. Since 2026-08-01: fixed -0.074 R, P -0.130 R. The bracket is not the cause; the entry's post-breakout drift is.
