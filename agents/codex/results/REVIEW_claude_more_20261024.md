# Further Claude review: WATCH — correct replay logic before relying on affected figures

Summary: Reviewed SharedCap, IntradayMomentum30m, ORB→VWAP Fade, VWAP Drift, VIX sleeve, and the BB bench adapter.
SharedCap has two reproducible state bugs; the 30-minute study skips its documented 09:00 decision.
VWAP Drift's “whole 2018–26” trade statistics include 2017, while its daily metrics use 2018 onward.
These findings require corrections and reconciliation; they do not establish that any rejected strategy should trade.
Keep trading decisions unchanged while Claude checks the affected calculations.

Source: `claude/nq-trading-strategy-params-5h9d20` at `b007bc42fdc991e3cc8fe8c3423f177eb10411d8`.
Script: `analysis/codex_claude_more_review.py`. Output: `analysis/outputs/codex_claude_more_review/synthetic_checks.json`.
Trials run: 0 strategy trials; synthetic implementation checks only. No market-data backtest, bench, or live change.

## 1. SharedCap: a stale exit becomes a new entry (high)

**Claim:** `netted()` models MultiCharts netting and ignores exits for a leg already closed by another leg.

**Evidence:** [analysis/mnq_sharedcap_test.py, lines 88–105](https://github.com/Dartdark/thebeginning/blob/b007bc42fdc991e3cc8fe8c3423f177eb10411d8/analysis/mnq_sharedcap_test.py#L88).
At line 95, `held[leg] == 0` classifies any event as an entry. The tuples contain signed quantity changes, not order actions.
When an opposing entry closes a leg, its later scheduled exit therefore opens another position.
The original source explicitly distinguishes BuyToCover/Sell exits from Buy/SellShort entries in `checks/candidates/mnq_sharedcap/MNQ_Portfolio_SharedCap_v2.cs.txt`, lines 125–141.

**Small check:** ON shorts 3; NA then buys 2, closing ON and opening NA. ON's later BuyToCover must do nothing.
The extracted function instead emits a new +3 buy at that time, increasing the long position from 2 to 5.
The committed synthetic check reproduces this using the pinned function, without a strategy backtest.

**Effect:** The reported netted P&L and its gap to the author's report are unreliable. The intended independent-leg sum is a different experiment and is not invalidated by this particular bug.

**Smallest correction:** Preserve order action/type and originating leg in every event; an exit for an absent leg must be ignored.
Retain the synthetic regression check, then reconcile the corrected netted event ledger to the report before interpreting the remaining gap.
Do not infer how much P&L this bug added or removed without that reconciliation.

## 2. SharedCap: loss cap does not latch while flat (medium)

**Claim:** After realized plus open P&L breaches the cap, stop trading for the day.

**Evidence:** [analysis/mnq_sharedcap_test.py, lines 72–85](https://github.com/Dartdark/thebeginning/blob/b007bc42fdc991e3cc8fe8c3423f177eb10411d8/analysis/mnq_sharedcap_test.py#L72).
The latch requires `pos != 0`. A scheduled exit can realize a loss beyond the cap and leave the book flat, so the code fails to latch.
A later entry is accepted and then immediately flattened if it remains beyond the cap.

**Small check:** A 1-contract trade loses $20 before costs, with a $15 cap and $1 per contract fill.
Expected: stop at −$22 after two fills. Actual: the next entry is accepted and flattened, leaving −$24 after four fills.
This is reproduced in the synthetic output.

**Effect:** The cap can permit extra orders and costs after a breach. The direction and frequency of historical effects remain unmeasured.

**Smallest correction:** Latch on the realized-plus-open threshold whether flat or invested; flatten only if invested.
Process the state before permitting any later entry. Compare gross vs fee-inclusive cap accounting explicitly with the original source, which maintains its own gross P&L variables.

## 3. IntradayMomentum30m: documented 09:00 decision is omitted (medium)

**Claim:** Signals are considered at 09:00 through 14:30 closes.

**Evidence:** [analysis/intraday_momentum_30m_test.py, lines 28–30 and 74–87](https://github.com/Dartdark/thebeginning/blob/b007bc42fdc991e3cc8fe8c3423f177eb10411d8/analysis/intraday_momentum_30m_test.py#L74).
The first bar, `b=0`, closes at 09:00. But `can = 1 <= b <= 12 ...` excludes it.
The last bar exits the loop before signal evaluation. Actual first eligible decision: 09:30; final decision: 14:30.

**Effect:** With one entry per day, removing the first decision can change which trade is taken.
The documented rule and executable rule differ; this alone does not establish which one the original author intended.

**Smallest check:** Preserve the exact original source and chart/session settings; confirm whether the first allowed signal is 09:00 or 09:30.
If 09:00 is intended, correct the condition and rerun the frozen version. If 09:30 is intended, correct the report.
Do not silently change the strategy based on which version performs better.

## 4. VWAP Drift: trade and daily samples disagree (medium)

**Claim:** Whole-strategy metrics describe 2018–26.

**Evidence:** [analysis/vwap_drift_test.py, lines 85–141 and main reporting](https://github.com/Dartdark/thebeginning/blob/b007bc42fdc991e3cc8fe8c3423f177eb10411d8/analysis/vwap_drift_test.py#L85).
`run()` has no start-date restriction. The published by-year trade totals explicitly include 2017.
Later, daily series are reindexed to trading days from 2018, dropping 2017 daily P&L, but the metrics call still receives all `T.net`.
Thus its trade count/average and daily Sharpe/annual P&L describe different samples.

**Effect:** “Whole 2018–26” is not a single reconciled measurement. This is not evidence that the C verdict should change.

**Smallest correction:** Filter the trade table once to the declared evaluation window before producing trade, daily, side and Monte Carlo inputs.
Assert daily sums equal the filtered trade totals, with matching start/end dates. Recompute the quoted whole-period metrics from those inputs.

## Conclusions I support, and one shared improvement

- **ORB→VWAP Fade:** the explicit touch-vs-one-tick-through sensitivity is useful and supports stopping before adoption. It establishes execution sensitivity; it does not establish that every touch order would fail in practice.
- **VIX sleeve:** separating same-close hindsight, prior-close signals, and next-open execution is good. The negative result at the specified $30k sleeve size supports declining that allocation; it is not an optimization over every possible sleeve size.
- **VWAP Drift and IntradayMomentum30m:** both custom engines currently accept target touches. Before a promotion claim, report the exact target tick rounding and fill policy, and reconcile any departure from the repository's standard trade-through assumption to MultiCharts settings. Do not tune that policy to rescue performance.
- **BB bench adapter:** the prior review's fee-normalization concern applies to its reuse of `portfolio.paths()`. This is a shared adapter issue already reported, not an additional independent discovery here.

Priority: fix SharedCap's event semantics and cap state first; settle the 30-minute clock; then reconcile VWAP Drift's date window.
None of these checks authorizes changing a plan, live strategy, broker setting, or VPS file.

