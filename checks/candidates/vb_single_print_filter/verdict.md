PASS WITH CONCERNS — replicates cleanly, has no leak and passes 5/5 gates, but it passes G1 only because it is pre-registered, and it is largely a stand-in for "the previous day was a wide range / up day".

## Replication (replica.py, built from spec.md and apex_strategies/NQ_Vault_Break.txt only; 1-min g24 grid, 2018+)
- **Vault Break trades:** both lists have 1,756 trades. 1,752 match on date and order (99.8%). P&L correlation is 0.966, and 98.2% of matched trades are within $15. Average net is $96.4 (replica) vs $97.9 (maker). The few mismatches are minutes where both target and stop were hit (the replica assumes the stop came first) and the knock-on trades.
- **Flag:** the replica flags 29.2% of sessions. Day-level agreement with `kept` is 99.5% (949/954 traded days). Trade-level crosstab: 516 trades both skip, 1,224 both keep, 12 the maker skips and the replica keeps, 0 the other way. One of the 5 disagreeing days, 2018-12-06, follows the 12-05 market closure, and the spec doesn't say which session counts as "previous" when there's a closure. The other 4 are borderline runs. The spec is clear enough.

## Gates (analysis/checker.py, N=193, t_threshold 3.47)
| Gate | Maker trades | Replica trades (`vb_single_print_filter_replica/`) |
|---|---|---|
| G1 significance | PASS, t 2.38 (kept $132.4 n1238 vs skipped $17.8 n518) | PASS, t 2.43 ($128.4 vs $11.1) |
| G2 holdout | PASS, 2018-22 +$73, 2023-26 +$156 | PASS, +$84 / +$151 |
| G3 years | PASS, 7/9 (2018 -15, 2025 -63) | PASS, 7/9 (2018 -30, 2025 -14) |
| G5 placebo (within-year shuffle) | PASS, p 0.0075 | PASS, p 0.0075 |
| G6 resampling | PASS, P(Sharpe≤0) 0.000 | PASS, 0.000 |

Notes on the gates:
- G1 passes only through the pre-registered route (t 2.38 is below the 3.47 threshold). I can't verify the pre-registration.
- G6 tells us nothing about the filter. The kept trades come from an already profitable strategy.

Standard metrics for kept vs all trades (maker trades):
- Sharpe 1.60 vs 1.44, Sortino 2.56 vs 2.22, profit factor 1.41 vs 1.29.
- Calmar 1.54 vs 1.54, Ulcer 2.58 vs 3.07.
- 2023+ Sharpe is 1.82 (90% CI 1.06–2.65) vs 1.58.
- 2023+ drawdown permutation: the kept trades' $11.7k max drawdown sits at the 41st percentile.
- Longs only, so there is no short side.

## Leak and trap checks
- **Look-ahead:** none. The flag uses only the prior session's bars closing 9:00–15:00. As a control I computed the flag from the trade day's own session, which is a look-ahead: it gives t = −11.95. The maker's labels match the prior-day version (99.5%), not the look-ahead one.
- **Lag-2 placebo:** taking the flag from two sessions back gives no effect (t 0.52), so the result is not a persistent regime label.
- **Clustering:** the day-level t (2.38) equals the trade-level t, so trades on the same day don't inflate it.
- **Costs:** the maker charges $17.25 per trade flat. The replica uses the repo standard. Results are the same.
- **Sensitivity to the run-length threshold:** 4 ticks t 3.12, 6 ticks 2.68, 8 ticks 2.38, 10 ticks 2.47, 12 ticks 2.04, 16 ticks 2.04, 24 ticks 1.56. The effect is smooth, with no knife-edge.
- **Concentration:** without 2020 the difference is $185/day with t 1.92. With P&L winsorised at 2.5% it is t 2.53.
- **Confounding (the main concern):**
  - The flag correlates 0.45 with the previous session's range/ATR.
  - Day P&L regressed on the flag plus previous range and previous return: flag coefficient −$115/day, t −1.05 (2018-22: t −0.52; 2023+: t −1.35).
  - A plain "previous return/ATR in the top 29%" skip gets about the same result (t 2.61, 51% overlap with the flag).
  - The single print adds little that is clearly its own beyond "yesterday was a wide up trend day".
- **What the filter costs:** total P&L goes from $162.9k (all) to $157.3k (kept). Skipped days are about break-even (+$20/day), so the filter improves risk-adjusted returns rather than adding money. On flagged days there are more stop-outs (23.4% vs 17.1%).

## What would most change my mind
1. Evidence that the pre-registration happened before the Vault Break test (a dated commit of the spec). Without it, G1 fails at t 2.4 < 3.47.
2. The flag staying significant (t ≥ 2) after controlling for previous range and previous return, on a bigger sample or on ES / a second breakout strategy.
3. Out-of-sample 2026-H2 results. The 2025 year was already negative (kept was worse than skipped).

Files are in `checks/candidates/vb_single_print_filter/`: `replica.py`, `replica_trades.csv`, `replica_flags.csv`, `robustness.py` and `checker_report.md`. The replica gate run is in `checks/candidates/vb_single_print_filter_replica/`.
