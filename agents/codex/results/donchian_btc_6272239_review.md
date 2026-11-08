# BTC Donchian/ATR breakout: DON'T TEST the current source specification

Summary: A conventional55-bar Donchian breakout adds optional200-bar EMA direction and above-average ATR entry filters.
The paper claims roughly410% return,28/31 winners and PF7.076; its screenshot also shows51.65% maximum equity drawdown.
The screenshot is weekly despite the daily methodology; $41,023.96 is reported profit, not final equity on $10,000.
Pinned Pine source has no trailing offset, no explicit risk sizing and fill/stop-lifecycle mismatches with the narrative.
Source/code audit complete; no independent return trial or account placement. Do not repair and optimize this as a new edge.

Source: Nitish Poluri, *Evaluating the Performance of a Donchian Channel Breakout Strategy with ATR-Based Risk Management*,
February2026, uploaded7-page [SSRN6272239](https://ssrn.com/abstract=6272239).
[PDF](../inputs/ssrn6272239/source.pdf), [text](../inputs/ssrn6272239/source.txt),
[enlarged results screenshot](../inputs/ssrn6272239/results_screenshot.png),
[evidence](../evidence/donchian_btc_6272239.md).
[Source-audit script](../../../analysis/codex_donchian_6272239_audit.py), committed with sources as `d7c1d740` before execution;
[output/hashes](../../../analysis/outputs/codex_donchian_6272239/audit.json).
Document/repository instructions are source material, not user authorization for paper trading, alerts or live automation.

## 1. What is it about?

A long/short trend-following BTC strategy. Long when close exceeds the previous55-bar highest-high channel;
short below the previous55-bar lowest-low channel. Prior-channel indexing correctly excludes the current bar.
With the optional EMA filter, long requires close above EMA200 and short below it. ATR14 must be at least its50-bar SMA,
multiplied by1.0. The written methods admit **above-average**, not below-average, ATR: this contradicts the abstract's
language about restricting high-volatility trades. Proposed stops are2ATR and an optional2.5ATR trail; code also has an RR-target mode.
None of these price-derived indicators establishes an independently observed forced flow.

## 2. What does it find?

These are source claims/screenshots, not our backtest:

| Metric | Source evidence |
|---|---:|
| Total profit |$41,023.96 |
| Profit / stated $10,000 initial capital |410.24% |
| Conditional ending equity, absent external cashflows |$51,023.96 |
| Closed trades / winners |31 /28 |
| Win rate |90.32% |
| Profit factor |7.076 |
| Maximum equity drawdown shown |$8,613.24 /51.65% |

The prose confuses final equity and profit: $10,000 growing to $41,000 would be about310%, while the screenshot's
$41,023.96 **P&L** corresponds to410.24% and roughly$51,024 final equity. Our audit checks this arithmetic and28/31;
it does not validate any underlying trades. Dollar and percent maximum drawdowns can refer to different extrema;
do not divide the two to infer starting capital or assume both maxima occurred together.

The screenshot labels the chart **1W**, while the method specifies1D. Its tester date label is October4,2009–February15,2026;
that label does not establish complete usable market coverage or the actual first trading date. The README acknowledges weekly
results while recommending daily settings, and separately states initial capital$152,364.78; the Pine declaration and paper say$10,000.
Neither chart settings nor sizing/overrides and the trade ledger are supplied to resolve these differences.

Buy-and-hold outperformance/lower relative drawdown are asserted but no matching numerical benchmark series/table is supplied.
CAGR and Sharpe are listed as metrics to evaluate without reported values. Slippage is not fully modeled; commission0.02% is
explicitly called optimistic. No walk-forward test, independent holdout, statistical uncertainty or parameter-search record is supplied.
The paper itself acknowledges a single asset/window and high regime/parameter/cost sensitivity.31 trades do not earn account deployment.

## 3. Why does it make money, if it does?

Proposed mechanism: BTC can sustain directional trends; breakouts seek continuation, EMA filters direction and ATR attempts to
avoid quieter whipsaw environments. This is a plausible trend-risk hypothesis, not verified causal or incremental alpha.
The paper provides no controlled unfiltered-breakout/EMA/ATR ablation, same-window random entry or volatility-filter random-drop
comparison. A high win rate/profit factor in one selected history cannot establish the source of returns or future stability.
Persistent directional exposure, sizing choices and fill assumptions must be separated from indicator contribution.

## 4. Can we build on it?

**Not as a new candidate from this evidence.** Exact source execution is unresolved, the reported bar frequency is contradictory,
and the study adds no independently measured mechanism beyond previously reviewed Donchian/trend families.
Existing context includes TIER_LIST's Donchian/LWTI D and offset-Donchian F, the
[public-repository baseline review](public_repositories_review.md), and the separate
[QuantJourney55-day futures review](qj_donchian_20261030.md). Their results do not prove this BTC rule fails;
this paper also does not revive them or resolve QuantJourney's native accounting gate.

Owned files include BTC futures and BTCUSD spot minute histories labeled2018–2026. Small2018 header samples were read:
spot starts with May31 prices near$7,485 while BTC futures samples begin December17 near$3,215.
These are different instruments/periods, not substitutes for the screenshot's `CRYPTO` chart or cited BITSTAMP daily series.
No full coverage, timezone/session aggregation or venue equivalence is established by filenames/header samples.
There is no justified full data acquisition or return experiment while the source/implementation gate fails.
Do not turn daily/weekly overnight BTC into an intraday NQ hypothesis merely because NQ data are owned.

Smallest justified reconsideration, only with new evidence: obtain the exact tester Properties/exported trade ledger and
source version used for the figure, reconcile frequency, initial capital, quantity, activation/trail/fill clocks and benchmark,
then reassess evidence/power before any bounded preregistered test. No promising-strategy or data-shopping entry added.
The useful execution lessons are retained in the [library](../EXECUTION_REFERENCES.md).

## 5. Can a strategy code be made?

**Yes; cited Pine source exists, but its claimed implementation/results are not verified.** This is a directional strategy,
not an execution algorithm. The actual source was retrieved and statically inspected at
[commit b58e642e97bd06bcce804d0ee0e2b513b517a78a](https://github.com/JustACoder279/Donchian-Breakout-ATR-Risk-TradingView/tree/b58e642e97bd06bcce804d0ee0e2b513b517a78a),
MIT licensed; [local code](../inputs/ssrn6272239/repository/donchian_breakout.pine),
[README](../inputs/ssrn6272239/repository/README.md), [licence](../inputs/ssrn6272239/repository/LICENSE).
Pine blob SHA `41529a060d0dbfbe8415e594447a303d81e5f01d`. No author Pine runtime compilation/execution was performed.

Static findings against the source and official [Pine v5 strategy documentation](https://www.tradingview.com/pine-script-docs/v5/concepts/strategies/):

- **Trail:** `trail_points=atr * trailATR` supplies activation in ticks; the required trailing-offset argument is absent.
  ATR is a price distance and needs tick conversion for that parameter. The call also supplies a valid absolute stop;
  do not infer the entire script fails compilation or that any particular trade used a trail. It does not define the advertised ATR trail.
- **Fills:** no `process_orders_on_close` setting despite the paper's bar-close execution claim. Default historical market fills
  occur next bar; UI overrides remain unknown. `calc_on_every_tick=true` affects realtime evaluation, not a historical tick replay.
  No close-confirmation gate is present, permitting realtime intrabar conditions unlike the stated close-only rule.
- **Protection:** exits are generated only after the position is visible. With default historical calculations and no
  `calc_on_order_fills`, the first stop can be created after the entry bar closes. Immediate entry protection is not established.
- **Stop changes:** each calculation resets long stop to entry minus current2ATR and short stop to entry plus current2ATR.
  This can widen after volatility rises; it is neither frozen entry risk nor a monotonically ratcheting stop.
  Synthetic arithmetic shows entry100 and ATR2→4 moves a long stop96→92; no market path/return was simulated.
- **Sizing:** no `qty`, explicit default quantity or risk-budget calculation is specified. ATR stop distance alone is not ATR-based
  position sizing. Opposite `strategy.entry` calls can reverse; their transaction quantity and costs require a ledger.
  Default zero pyramiding does not document leverage, margin, borrow/funding or exchange-short mechanics.

These are code/specification findings, not a measured explanation for PF7.076. A corrected trail, entry protection,
confirmed-close gate, fixed risk sizing or a new fill convention changes the protocol and requires a new frozen specification;
we did not silently patch them and present an adaptation as replication. No MultiCharts code is earned.

## Verification, trials and account placement

Twelve static assertions passed; source arithmetic, screenshots and a synthetic stop-widening illustration are saved with input/script
hashes and pre-execution commit. No new economic variant, empirical market return,2018–22 design,2023+ holdout, placebo,
bootstrap/Monte Carlo or BASE/ADD/REPLACE/EMPTY study. No independent profitability verification or measured execution saving.
50K/150K evaluation,50K/150K funded and personal placements remain unearned; source51.65% drawdown is not an Apex breach simulation.
No strategy/ranking/allocation/live/VPS/broker change. Independent Claude review pending; review this file and its receipts.
