# Jesse cross-check (2026-10-17)

Every current strategy ported to [Jesse](https://jesse.trade) (open-source Python backtest engine, v3.4), run on our own
1-minute NQ / CL data, and compared trade by trade with the MultiCharts reports. Setup for the user's PC (Docker Jesse +
Antigravity): `agents/JESSE_ANTIGRAVITY_SETUP.md`.

Run (data not in git; see NEW_CHAT_BRIEF 'Rebuilding the data'):
```
python3.12 -m venv jv && jv/bin/pip install jesse          # numpy 1.26 has no Python 3.13 wheel: use 3.12
python3 analysis/jesse/build_candles.py scratch_data
mkdir jt && cd jt && ln -s <repo>/analysis/jesse/strategies strategies   # Jesse looks for ./strategies
../jv/bin/python <repo>/analysis/jesse/run_all.py <repo>/scratch_data [Strategy ...]   # ~20 s per strategy
cd <repo> && python3 analysis/jesse/compare.py scratch_data   # -> compare_output.txt
```

## Result: Jesse confirms all nine

| Strategy | MC trades | Jesse | Same day, same side | P&L within $50 | Gross / trade MC vs Jesse |
|---|---|---|---|---|---|
| Vault Break (30 min) | 1,743 | 1,748 | 1,742 | 99.3% | $106 / $109 |
| Overnight Bias ADX 20 (old v2 report) | 997 | 996 | 996 | 97.3% | $285 / $283 |
| Overnight Bias ADX30 (combine) | 677 | 675 | 675 | 100% | $390 / $389 |
| Overnight Bias ML v2 (funded) | 344 | 329 | 329 | 99.1% | $656 / $693 |
| Monday Long | 451 | 410 | 410 | 99.5% | $435 / $480 |
| Expiration Open Short | 105 | 105 | 105 | 100% | $491 / $491 |
| Late-Day Flow | 898 | 897 | 895 | 99.9% | $111 / $112 |
| NFP Fade | 79 | 79 | 79 | 100% | $352 / $353 |
| CL Sunday Gap Fade | 97 | 97 | 97 | 99.0% | $680 / $683 |

Not ported: Vault Break SP (same entries as Vault Break; its single-print flag only sets the size) and Bridge Monday Long
(closed source).

## What stood out

1. **Overnight Bias ML traded unfiltered until its score had 60 days of history.** In Jesse (shorter warm-up) the
   first weeks of 2018 added 9 unfiltered trades that lost ~$4,700 per NQ. A live chart with too little history would do
   the same silently. **Fixed** in `funded_strategies/NQ_Overnight_Bias_ML.txt`: no trades until the score is ready
   (backtest unchanged when 90+ trading days are loaded). With the fix every overlapping trade matches; the 15 MC-only
   trades are January–March 2018, before our data has 60 days.
2. **Monday Long: the MultiCharts report (and the funded bench's `MON_MC`, built from it) includes 40 holiday Mondays
   the current code skips** (early-close Mondays, out at 11:45). They earned $65 a trade vs $480 for the rest, +$2,585
   per NQ over 9 years in total, so the bench is very slightly off (about +$29 a year per MNQ). No action needed.
3. **The old ONB v2 report held through holiday early closes** (exits stamped 17:15 on Presidents Day, Juneteenth, the
   day after Thanksgiving). Current files exit at 11:30 on those days; the ADX30 and ML reports already do.
4. **Vault Break: 5 of 1,742 trades flip between stop and target** (both inside one 1-minute bar; the engines break
   the tie differently). Net effect +$3 a trade in Jesse's favour; nothing to change.
5. Engine differences are small: Jesse fills a market order at the decision bar's close (MultiCharts: next bar's open),
   so entries differ by a median of 0–1 tick.

No strategy improvement came out of it. Jesse's optimizer was not used on purpose: tuning parameters would add trials to
`TRIALS.csv` without a pre-registered reason.

## Pitfalls (for the next port)

- Jesse builds 5 / 15 / 30-minute bars by **counting** 1-minute candles: the candle array must be continuous and start
  at midnight, or every bar is shifted (first run: bars ended at :01 / :31, VB matched only 4% of entries within a tick).
- A minute without trades must not set a bar's open: fill a missing minute with the next real open within its 5-minute
  block, else the last close (`build_candles.py`). With last-close filling the CL Sunday bar opened at Friday's close
  and missed the 2019-09-15 and 2026-03-01 gaps.
- Jesse's research backtest needs Postgres inside a "Jesse project"; `run_all.py` tells it this is not one
  (`jh.is_jesse_project = lambda: False`), which only skips storing trades.
- Timestamps are the exchange clock written as UTC (no daylight-saving jumps); CL is shifted to Eastern as its chart.
