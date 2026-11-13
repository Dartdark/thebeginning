# Diversified trend (time-series momentum) across our 9 futures, PERSONAL account only (holds for days to months: not Apex-legal)
User 2026-11-13: "run the diversified trend test". Written before any result. Motivation: the big algo users of commodities / rates / FX
are slow trend books across many markets; arXiv 2607.01550 ('Is Trend Still Your Friend?', TIER_LIST F as a strategy source) says
short-term trend died in small-tick contracts (equity indices, FX) but not in large-tick ones (commodities, rates).

Universe: NQ ES YM GC CL NG ZN 6E BTC (CME). Price: last trade at or before 15:00 CT each weekday, roll jumps removed by
difference adjustment (analysis/roll_adjust.py; NG / BTC monthly windows added), so daily $ P&L per contract = point change x PV.
Signal (primary, published, no tuning): s = mean of sign(12-month), sign(3-month), sign(1-month) point change (252 / 63 / 21 days)
  -> s in {-1, -1/3, 1/3, 1}. Known at day t's 15:00 close, traded at that close, held to the next close.
Sizing: equal risk per market: contracts = s x $1,000 / (daily $ volatility per contract, EWMA of squared changes, 60-day center of
  mass, lagged); fractional contracts in the study (micro sizes are a separate capacity question).
Costs: commission ($7.25 NQ, $5 others) + 1 tick per contract traded, on every change of position.
Controls: (C1) vol-scaled LONG-ONLY in every market (s = +1): separates trend from just being long in a rising decade;
  (C2) each lookback alone (secondary, disclosed: 3 extra trials); (C3) random sign each month (100 runs) for a placebo.
Report: whole book and per market: annual $ P&L, Sharpe, Sortino, max DD, Calmar; by year; 2019-22 (design) vs 2023-26 (holdout);
  correlation with the personal book; large-tick (GC CL NG ZN) vs small-tick (NQ ES YM 6E) groups.
Pass: book Sharpe >= 0.5 in BOTH periods after costs, beats C1 (long-only) in the holdout, placebo p < 0.05. Then a personal-book bench
  (bench150.personal) before any plan change. Expectation set before running: CTA-style trend on 9 markets usually gives Sharpe 0.3-0.7.

## Result (2026-11-13, `analysis/outputs/diversified_trend_test_output.txt`): FAIL
TSMOM book 2019-26 Sharpe 0.62 (2019-22 0.83, 2023-26 0.37), $31.7k a year at $1,000 daily risk per market, max DD $75.9k, Calmar 0.42;
placebo p 0.040. Fails on the holdout Sharpe (< 0.5) and on C1: vol-scaled long-only 0.90 overall, 1.11 in 2023-26 (beta beat trend).
Secondary (disclosed): 12-month lookback alone 0.99 / 0.70, also below long-only in 2023-26. Large-tick group (GC CL NG ZN) 0.76 -> 0.06
(the paper's prediction does NOT hold here in the holdout); small-tick 0.23 / 0.24. Best single markets: BTC 0.85, GC 0.44, NQ 0.44.
Costs are negligible for this turnover (~$3.3k a year in total). Personal-book correlation not computed (personal_P.pkl absent; fails anyway).
