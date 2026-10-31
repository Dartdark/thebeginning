# Task: "try to break it": stress tests of Vault Break and Overnight Bias ADX30 (after Nick Radge, 2026-10-22)

Branch `codex/work`. A pre-registered robustness check, NOT an optimisation: nothing in the live plan changes unless a
strategy breaks. Commit the plan (all perturbations, their sizes and the pass / fail rule) before running anything.

## Why
Both are price breakouts that fail on ES / YM / CL / GC (TIER_LIST), i.e. NQ-only edges. Radge's test: a real edge should
bend, not break, when the implementation or data is perturbed.

## Baselines (reproduce first; must match the MultiCharts trade lists closely)
- Vault Break: `analysis/candidates24.vault_break24` (MC: `mc_reports/Backtesting Strategy Performance Report VB v1.xlsx`).
- Overnight Bias ADX30 (the evaluation version): `candidates24.overnight_bias24` with ADX 30 / StopAtrPct 0.25
  (MC-confirmed; settings in `apex_strategies/NQ_Overnight_Bias_ADX30.txt`).
Costs $7.25 + 1 tick per market / stop fill. 2018-26, with 2018-22 and 2023+ shown separately; longs and shorts separately.

## Perturbations (fixed list; each run once)
1. **Price noise:** add independent noise to every 1-minute OHLC (keep H >= max(O, C), L <= min(O, C)), sd = 1 and 2 ticks;
   50 seeds each. Signals AND fills use the noisy data.
2. **Indicator swaps:** ATR 10 / 20 days instead of 15; Wilder vs simple average; VB's VWAP anchored at 08:30 CT instead of
   midnight; ONB's opening range 08:30-08:45 vs 08:30-09:00 (if not its own setting).
3. **Timing:** entry one bar later (VB: next 30-min bar; ONB: next 15-min bar); exit one bar earlier / later.
4. **Parameter jitter:** every numeric parameter independently ±10% (rounded to its tick / minute grid), 200 random draws.
5. **Execution:** 2 and 3 ticks slippage per market / stop fill; targets need 2 points trade-through.

## Pass / fail (write it in the plan before running)
For each perturbation family report net $ per NQ, t, PF, max DD, Sharpe, 2023+ separately, and the share of runs with
net > 0 and t > 2. "Bends": most runs keep net > 0 and at least half of the base Sharpe. "Breaks": the median run loses
money or falls below a third of base Sharpe, in BOTH periods. Flag any single setting the edge depends on.

## Output
`agents/codex/results/break_vb_onb.md` (5-line Summary first), script `analysis/codex_break_vb_onb.py`, outputs under
`analysis/outputs/codex_break_vb_onb/`. No live, MultiCharts or plan changes. Count it as one robustness trial per strategy.
