# arXiv shortlist for an evaluation-book complement

Summary: Prioritize repeated small, bounded-risk opportunities that complement the current book's concentrated losses.
Calendar-spread feedback is the best frequent-countertrend lead; drift bursts have the closest direct CME evidence.
Queue imbalance is the simplest frequent-signal building block; cross-impact is a lower-priority extension.
These are source-supported research leads, not verified high-win-rate CME strategies or measured pass-rate improvements.
No return tests, new trial reservations, purchases, live changes, or paused-program restarts were performed.

Author: **dot**. Reviewed November 11, 2026 UTC. Repository evidence inspected at `380070b6f0530ebf8ecc2bbccca6f916497ec803`.

## The target, sharpened by the user's clarification

The desired addition is a frequent, small-winner sleeve that offsets the evaluation book's large individual losses and helps pass sooner. That is a useful portfolio objective. The search therefore favors counter-moves and short-lived pressure effects over another breakout/trend model. The key question is not merely whether a candidate wins often, but whether its profits and losses arrive at useful times alongside VB/ONB/EOS/Bridge/Twin.

The current evaluation mandate is [TASK_eval_strategy_20261109.md](../TASK_eval_strategy_20261109.md). Its frozen baseline is [eval_focus_baseline_20261109.md](eval_focus_baseline_20261109.md): 50K VB 8 MNQ, ONB risk $1,100, Bridge Monday 2 MNQ, EOS $500; 150K VB 20 MNQ, ONB $2,750, Bridge 5 MNQ, EOS $1,250, Twin cap1 v2.1 2 MNQ. These are the inspected research books, not a claim about today's live installation.

Use the 150K book first and retain the unchanged 50K comparison. The earlier baseline's reported 30-calendar-day pass rates are 37.0%/48.9% for 150K/50K, or 32.8%/46.1% under its adverse-minute DLL assumption. Those existing research figures have not been rerun or independently verified here. A sleeve that earns after the account has already breached cannot rescue that evaluation.

## Ranked reading list

This is a bounded best-fit shortlist from this search, not an exhaustive ranking of arXiv. Four candidate foundations and three implementation companions are deliberately separated. The rankings reflect mechanism, evidence, frequency and current input feasibility together.

| Priority | Paper | Why it belongs | Current status |
|---|---|---|---|
| 1 | Calendar-spread feedback, arXiv 2501.03171 | Repeated contrarian trades with an explicit cross-contract mechanism | NEEDS DATA / EXECUTION / COMPLETE EXIT RULES |
| 2 | The drift burst hypothesis, arXiv 2601.08974 | Reversal evidence in actual CME contracts, rather than stock-to-futures analogy | NEEDS NATIVE QUOTES / CAUSAL EVENT RULE |
| 3 | Queue Imbalance, arXiv 1512.03492 | Small, fast pressure signals with a simple probability model | NEEDS NATIVE QUOTES / COST GATE |
| 4 | Cross-Impact of Order Flow Imbalance, arXiv 2112.13213 | Tests whether lagged information adds something beyond an asset's own flow | LOWER PRIORITY / NEEDS MATCHED MULTI-ASSET BOOKS |
| Companion A | The Price Impact of Order Book Events, arXiv 1011.6402 | Defines pressure correctly | FEATURE / EXECUTION REFERENCE |
| Companion B | Market Simulation under Adverse Selection, arXiv 2409.12721 | Tests whether small winners survive realistic bad fills | EXECUTION REFERENCE |
| Companion C | A High Frequency Trade Execution Model, arXiv 1710.03870 | Connects prediction errors to actual fills and P&L | EXECUTION REFERENCE |

## 1. High-frequency lead-lag relationships in the Chinese stock index futures market

Li, Chen and Liu. [arXiv 2501.03171](https://arxiv.org/abs/2501.03171). [Inspected v1 full text](https://arxiv.org/html/2501.03171v1), Sections 2, 3.3, 4.4; Table 4.5.

**What is it about?** Trading the liquid leading contract against temporary near/next-month dislocations, not necessarily trading both legs.

**What does it find?** Roughly 700 CFFEX days, first 400 for calibration. Authors report OOS Sharpe 2.84–8.79 and 26–168 trades/day after spread/assumed fees. Win rates are unreported; execution delay/risk is omitted.

**Why money?** Proposed arbitrage feedback restrains relative overreaction.

**Can we build on it?** Conditional yes; CME transfer is untested. Need paired native quotes, receipt clocks, rolls and latency. Its 500ms feed differs from CME.

**Can a strategy code be made?** Conditional yes: fade `(F1−F2)−EMA50(F1−F2)` beyond the trained threshold; require spread ≤2 ticks, one-lot cap, daily flattening. Resolve intervening exits/reversals and protective stops first. A CME bracket version is a new adaptation.

## 2. The drift burst hypothesis

Christensen, Oomen and Renò. [arXiv 2601.08974](https://arxiv.org/abs/2601.08974). [Inspected v1 full text](https://arxiv.org/html/2601.08974v1), Sections 3, 5.1–5.4; footnote 24; Tables 3–4. The manuscript says November 2020; the 2026 arXiv posting is not a new 2026 sample.

**What is it about?** Detecting brief explosive CME price moves and subsequent reversal.

**What does it find?** ES 2010–17: 549 events at threshold 4.0, 67.2% five-minute reversals; threshold 4.5 yields about one event per fortnight. These are descriptive events, not OOS net trade wins.

**Why money?** Compensation for absorbing urgent demand is proposed; executable profit is untested.

**Can we build on it?** Conditional yes with native midquotes. Minute candles are a coarse adaptation; rarity limits usefulness.

**Can a strategy code be made?** Yes for its backward-kernel detector with five-minute drift/25-minute volatility bandwidths. Trading needs stops, fills and causal event confirmation: the paper selects a local extremum within five minutes. First-crossing or delayed confirmation changes that definition.

## 3. Queue Imbalance as a One-Tick-Ahead Price Predictor in a Limit Order Book

Gould and Bonart. [arXiv 1512.03492](https://arxiv.org/abs/1512.03492). [Inspected PDF](https://arxiv.org/pdf/1512.03492), Sections 5–6; Tables 4–5.

**What is it about?** Predicting the next midprice direction from best-bid versus best-ask queue size.

**What does it find?** Ten Nasdaq stocks, 2014: large-tick held-out AUC 0.752–0.805, versus 0.581–0.642 for small-tick stocks. The split is random 80/20, not chronological. Neither AUC nor fitted probability is a net trading win rate.

**Why money?** Uneven queues anticipate depletion; monetization is untested.

**Can we build on it?** Yes as a simple baseline. Futures costs/latency and overlap with VB/ONB remain unverified.

**Can a strategy code be made?** Yes for prediction: `I=(bid_size−ask_size)/(bid_size+ask_size)` and training-only logistic fitting. Trading needs native quotes, after-cost thresholds, entry/exit horizon and bounded risk. Minute aggressor volume is not queue size.

## 4. Cross-Impact of Order Flow Imbalance in Equity Markets

Cont, Cucuringu and Zhang. [arXiv 2112.13213](https://arxiv.org/abs/2112.13213). [Inspected v4 full text](https://arxiv.org/html/2112.13213v4), Sections 2, 4; Tables 8/11. Earlier versions used a different title; count once.

**What is it about?** Combining book levels and other assets' lagged order flow to forecast short-horizon returns.

**What does it find?** Prior-30-minute fits updated each minute improve relative forecasting, but mean OOS R² remains negative. The 2017–19 portfolio explicitly ignores costs despite a spread-based entry screen.

**Why money?** Delayed pressure transmission is proposed; contemporaneous fit is not forward alpha.

**Can we build on it?** Conditional, below the simpler baseline. NQ/ES needs synchronized events and a tradeable lag; another index need not diversify shocks.

**Can a strategy code be made?** Yes: lagged level-wise OFI, OLS/LASSO, next-interval forecasts and full-cost entry thresholds. Risk/exits need definition. Minute buy/sell bars cannot reconstruct limit additions/cancellations. No high-win evaluation benefit is established.

## Companion A. The Price Impact of Order Book Events

Cont, Kukanov and Stoikov. [arXiv 1011.6402](https://arxiv.org/abs/1011.6402). [Inspected v2](https://arxiv.org/html/1011.6402v2), Sections 2–4.

**About:** Price changes versus best-quote order-flow imbalance, including limit additions, cancellations and trades.

**Finds:** In 50 US stocks, depth-scaled OFI explains short-interval contemporaneous moves better than volume alone. This is not a future-return strategy test.

**Why money:** It supplies a mechanism for pressure and liquidity fragility, not demonstrated trading profit.

**Build:** Use it to distinguish genuine supply/demand changes from candle-color proxies. Useful when extending the user's three-paper pressure idea, with no permission to resurrect failed flow fades.

**Can code?** Yes for an OFI/depth feature extractor from best-bid/ask prices and quantities. A directional strategy additionally needs a lagged forecast and explicit execution/risk rules. Quote changes are not recoverable from OHLCV or total buy/sell volume alone.

## Companion B. Market Simulation under Adverse Selection

Lalor and Swishchuk. [arXiv 2409.12721](https://arxiv.org/abs/2409.12721). [Inspected v1](https://arxiv.org/html/2409.12721v1), Sections 4–5 and appendix.

**About:** How fill assumptions change market-making outcomes on ES, NQ, CL and ZN.

**Finds:** Including adverse fills and lowering favorable-fill probability materially worsens simulated performance. This is a simulation comparison, not a long independent trading record.

**Why money:** No new alpha claim. Its value is preventing fictitious spread-capture profits caused by filling good orders while missing bad ones.

**Build:** Essential for the desired small-winner sleeve: passive scalping can concentrate losses during precisely the violent moves the user wants to offset. The paper's fixed probability, 0.2 in its illustration, is not a portable CME fill constant.

**Can code?** Yes as a conditional-fill/replay stress harness, not a stand-alone directional strategy. Need bid/ask paths, order lifecycle, queue priority, partial fills, cancellation latency and liquidation costs. Shared minute-bar target assumptions do not establish native passive-fill quality.

## Companion C. A High Frequency Trade Execution Model for Supervised Learning

Dixon. [arXiv 1710.03870](https://arxiv.org/abs/1710.03870). [Inspected v3 PDF](https://arxiv.org/pdf/1710.03870), Sections 4–5.

**About:** Converts classifier outcomes, fills and inventory rules into a trade-information matrix and expected P&L.

**Finds:** Uses ESU6 order-book data from August 2016. The illustrative strategy comparison includes perfect-information/zero-latency conditions and clearing/equity-member fees of $0.35 per contract; these are not the user's retail costs.

**Why money:** It explains how predictive information might improve quoting and adverse-selection outcomes. High classification accuracy alone cannot establish profitability.

**Build:** A good companion to queue imbalance: compare errors in the states that actually fill, not just unconditional accuracy. The short historical window is not strong regime validation.

**Can code?** Yes as a research/execution evaluator once prediction probabilities and native conditional fills exist. It does not supply an immediately deployable MultiCharts scalper or proven fast-pass strategy.

## One recent, tempting paper deliberately ranked below the shortlist

**Explainable Patterns in Cryptocurrency Microstructure** — [arXiv 2602.00776](https://arxiv.org/abs/2602.00776), [v1 full text inspected](https://arxiv.org/html/2602.00776v1), Sections 3–7.

**About:** CatBoost forecasts three-second returns from one-second Binance perpetual book/trade features. **Finds:** Authors describe purged nested time-series validation and maker/taker backtests, but large outcomes depend on asset and the October 2025 crash; latency is not modeled. **Why money:** Pressure/adverse-selection features may carry short-lived information; reported economic results are not CME evidence. **Build:** Keep the feature library, not the crypto return headline. Fees, threshold-selection details and latency need reconciliation. **Can code?** Conditional yes with source-equivalent book data; not from the current minute bars. Maker losses during stress are particularly relevant to the requested offset. Lower priority than a simple transparent baseline.

Daily diversified deep-momentum papers were screened but not promoted: they are not the requested short-horizon, small-winner complement. Existing noise-band, generic ORB, first-half-hour momentum, one-minute pairs, absorption, innovation-fade and liquidity-vacuum families are not new simply because another arXiv title describes them.

## How these ideas could fit the book: hypotheses, not measured correlations

1. **Calendar-spread feedback:** The desired pattern is frequent modest gains from temporary relative dislocations rather than extended outright trends. Trade only if a native source/execution audit establishes a distinct viable effect. It may help on false breakouts but can also accumulate repeated losses as fair-value relationships shift. Do not assume two expiries mean two independent risks.
2. **Drift-burst reversal:** Most plausible after urgent pressure exhausts, potentially the opposite environment to a successful breakout. Sparse events may add little pass-speed benefit. Continuing trend/shock risk can generate the very concentrated losses being avoided; the stop and loss distribution are part of the strategy, not an afterthought.
3. **Queue/lagged-flow signals:** Potentially many brief opportunities. They may diversify holding duration without diversifying shock direction. A deliberately selective classifier can also trade too infrequently after costs. Measure the opportunity count after all execution gates.
4. **Passive market making:** Do not label it an offset merely because its equity rises smoothly in ordinary periods. Joint losses during liquidity withdrawal must be examined before it gets that role.

The user is not asking to replace a goal with a warning about win rate. The target remains frequent winners, with a small enough realized loss tail that the sleeve helps the existing evaluation path.

## Smallest justified next work, without starting returns

### Shared input/rule admission

- **Native top-of-book panel:** ES and NQ first, with contract IDs, exchange and receive timestamps, bid/ask prices and quantities, trade prints/size, sessions, rolls and missing-event markers. Use 2018–22 design history where genuinely available and later chronological history without calling previously seen years untouched. Native micros are separate markets, not a fee-only rescaling.
- **Paired maturities:** For calendar feedback, simultaneous front/next contracts and a point-in-time liquidity/roll selector. A stitched continuous future, two unrelated indices or daily curve series is not equivalent. No newly verified free complete panel was found or claimed here.
- **Event clocks:** First crossing versus confirmed extremum must be explicitly different. Lagged book features must exclude all future events; later trade-through may label a fill but cannot choose an earlier signal.
- **Implementation completeness:** Recover all exit/reversal rules for calendar feedback. For each adaptation, write one causal event-to-entry-to-exit example; state every new stop/target/session choice as our choice, not the paper's.

Owned-input evidence checked: repository filename tree, the current search profile, [owned-input reconciliation](eval_owned_data_reconciliation_20261109.md), [pressure reconstruction](pressure_papers_reconstruction_20261110.md), and the prior flow-result specifications. A direct first-lines connector read of `data/OF_1min_2018_1.csv` returned empty content; therefore it was not a fresh row/schema audit. Existing documented aggressor aggregates and minute prices are owned, but do not establish native queue/depth histories. No new bulk download, vendor signup or paid data request occurred.

### Later acceptance contract if a candidate earns a TEST verdict

Before any return inspection, preserve the current pause and authorization boundaries, commit exact rules/code, count adaptations and controls, and fix the cost/slippage/risk specification. The intended outcome measures are:

- Paired probability of passing before the actual deadline, timeout rate, breach probability and pass-time distribution. Show conditional pass times separately from failures/timeouts.
- Candidate P&L during the baseline's worst single-trade and worst-day episodes; whether offsetting profit arrived **before** breach/DLL lockout. Also evaluate normal days to avoid accepting a sleeve that helps only a selected tail sample.
- Maximum single loss, adverse excursion, expected shortfall, consecutive losses and daily loss clustering. A nominal stop is not a guarantee of the realized maximum loss.
- BASE/ADD/REPLACE/EMPTY at predeclared integer size, same calendar starts and native fees; freezes include the replaced slot and account netting/order-priority behavior.
- Delayed-entry and stressed-fill results, including canceled/missed/partial fills and correlated shocks. No trade at a stale quote or at the signal bar's own favorable price.

These are proposed evaluation criteria and research preparation, not new acceptance thresholds fitted to outcomes. Existing task-specific preregistration rules remain controlling. No result here establishes a safer live position size or an account pass forecast.

## Existing work and budget preserved

The [three-paper reconstruction](pressure_papers_reconstruction_20261110.md) already covers the user's supplied papers and screenshot; this shortlist adds distinct sources rather than duplicating that work. The prior [flow innovation](flow_innovation_relaxation.md), [absorption](flow_absorption.md) and [liquidity-vacuum](liquidity_vacuum_refill.md) rejections remain closed. A paper's title, market or timeframe alone does not grant a fresh trial.

Scout metadata at the inspected head records 4/10 hypotheses and 10/30 economic definitions, null lease, and a historical `ready` value. The later active evaluation task explicitly preserves paused lab/scout/t6/Hunt programs. This review neither interprets stale metadata as permission to restart them nor changes counters, history, continuation or schedules. Zero return tests and zero new economic reservations were made.

**Recommendation:** Take calendar-feedback and causal drift-burst feasibility to the research builder first, with queue imbalance as the transparent high-frequency baseline if native quotes become available. Keep the execution companions attached to that work. None is ready for a plan change; all useful findings and blockers are retained without claiming the search has found a proven winner.
