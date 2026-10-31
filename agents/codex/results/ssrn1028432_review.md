# SSRN 1028432: retain volatility and data-construction lessons; no trading candidate

Summary: Liao's 2008 dissertation studies Treasury futures trading activity and volatility, not a return strategy.
Daily 1991–2006 results associate volume with volatility and show persistent volume; open-interest results depend on contract construction and volatility measure.
Volume is labelled speculation and open interest hedging by assumption, not by identified trader transactions.
No net trading returns, walk-forward strategy validation or account contribution are demonstrated.
Retain the proxy, contract-roll and liquidity-measurement lessons; do not turn them into a directional NQ/ES signal.

Source: Wenchao Liao, *Trading Activity in the Treasury Futures Market and Its Role in Futures Price Fluctuations*, CUNY PhD dissertation, 2008. [SSRN](https://ssrn.com/abstract=1028432); [archived user upload](../inputs/papers/ssrn-1028432.pdf); [source hash, review scope and owned-data schema](../../../analysis/outputs/codex_ssrn1028432_review/source_manifest.json). Citations below use the document's **printed page numbers**, not PDF viewer pages. Source findings are author-reported, not independently reproduced; cited studies were not separately verified.

## 1. What is it about?

Chapter 1 asks whether trading activity and price volatility predict each other in 2-, 5-, 10- and 30-year U.S. Treasury futures. The dataset contains daily settlement prices, high/low, volume and open interest from CBOT DataExchange, 1991–2006; the author reports 16,147 observations across 256 delivery contracts, not 16,147 independent trades (p. 11).

The study compares market-wide volume/open interest summed across expiries with activity in one calendar-selected active contract. It uses Parkinson high/low volatility, approximately one-month historical volatility, and fitted AR(0)-GARCH(1,1) volatility, followed by reduced-form VARs with four daily lags and Granger tests (pp. 12–20). GARCH specification selection considered 12 forms per contract type. Chapter 2 interprets the results using private-information and public-information/disagreement models, then discusses Treasury squeezes and liquidity.

## 2. What does it find?

| Author-reported result | What it supports—and its limit |
| --- | --- |
| Volume and each volatility measure are positively contemporaneously correlated, using both activity constructions (pp. 25–26) | Activity and turbulence co-move; this alone does not forecast signed returns or identify who traded |
| Lagged volume relates positively to next-day high/low and GARCH volatility in most reported cases; some later lags have negative signs (pp. 26–27, 32, 42) | A daily predictive association within the estimated system, not a stable “high volume means buy” rule |
| Volume's own four lag coefficients are positive and significant across the reported volume specifications (pp. 27, 30, 32, 87–88) | Persistent **volume**, not evidence of price momentum; the thesis explicitly says it did not verify the model's price-reversal prediction (p. 87) |
| Open-interest/volatility results change substantially with aggregate versus active-contract activity, contract maturity and volatility estimator (pp. 28–33, 42–44) | The broad claim “hedgers stabilize markets” is weak and specification-dependent |

The author's headline interpretation is that speculators tend to destabilize and hedgers weakly stabilize. The measured objects are **volume and open interest**, not separately observed speculative and hedging order flow. All participant-level interpretations must retain that qualification.

No strategy P&L, after-cost Sharpe, executable signal ledger, portfolio improvement or untouched trading holdout is supplied. VAR impulse-response bands are 68% bands (pp. 20, 34), not 95% evidence. Forecast plots do not establish profitable out-of-sample execution. The author acknowledges the limits of structural interpretation in the reduced-form VAR (pp. 47–48).

## 3. Why does it make money, if it does?

**No money-making rule is demonstrated.** Public news can generate disagreement, trading and changing risk without creating predictable return direction. A volatility forecast might eventually improve risk sizing or execution timing, but a useful association need not add information beyond current volatility, calendar events and roll effects—and a better risk forecast need not improve capped Apex payouts.

The paper identifies no signed forced flow, ex-ante trade size, entry/exit clock or expected net move for NQ/ES. Its squeeze/depth discussion largely reviews other sources; it is not a newly verified squeeze arbitrage or a reason to take delivery exposure.

## 4. Can we build on it?

**Retain as a methods/execution reference; no strategy backtest is earned from this source.** Useful distinctions:

1. **Participant proxies are not participant identities.** Hedgers generate volume; speculators can hold overnight open interest. Each outstanding futures contract has a long and a short. Total OI is not signed demand or a measurement of a forced hedge. Weekly COT categories are different observations again.
2. **Match activity to contract and roll rule.** Market-wide participation and the liquidity available in the actual tradable delivery contract are different quantities. Preserve both if the research question needs them. Do not splice delivery-contract price levels and call the roll gap a return.
3. **Volume, spread, depth and resilience are different.** Heavy volume can coexist with high volatility or large price impact. The chapter's depth discussion (pp. 95–97) is conceptual/literature-based; daily volume does not verify our spread, queue, fill probability or slippage.
4. **Availability must precede prediction.** Daily total volume and finalized OI cannot be used earlier in the same session without documented release clocks. The thesis averages adjacent observations to repair a missing OI/volume record (p. 15); such a repair uses future information if copied into a live forecasting pipeline. Full-history fitted volatility is not automatically a past-only forecast.
5. **Granger prediction is not intervention causality.** Shared macro news, maturity, rollover, trends and regime changes can drive activity and risk together. The 1991–2006 estimates need modern out-of-sample validation before applying to today's electronically traded futures.

### Owned-data feasibility and smallest justified next step

Our inspected ZN minute export has `date,time,open,high,low,close,volume`; it lacks OI, settlement fields and delivery-contract identifiers. ZN exports cover filenames 2017–2026; the repository also has weekly COT archives. These do not reproduce daily contract-specific data for all four Treasury maturities in 1991–2006. No exact replication or verified modern forecast is claimed. Data price/licensing is unverified; no purchase is warranted for this paper alone.

If a future source supplies a concrete risk-sizing hypothesis, first obtain point-in-time per-delivery-contract volume/OI, prices and publication clocks. Preregister a bounded **risk-forecast** comparison against existing volatility and calendar/roll controls, with chronological fitting and a costed incumbent sizing rule. Only an earned forecast improvement should advance to integer-sized BASE/ADD/REPLACE/EMPTY account replays. That would be a new hypothesis and trial; it is not silently authorized or run here. The current source gives no effect-size estimate with which to justify that account stage.

Related work is not a substitute: Treasury auction pressure is already tested in `TIER_LIST.md` and fails costs; the repository's COT trader-demand review (`ssrn_2311859_review_20261030.md`) concerns different, weekly position observations. Neither makes this thesis a new auction or signed-flow strategy.

## Placement and retention

| Home | Verdict |
| --- | --- |
| 50K evaluation | No eligible strategy from this paper; account bench not run |
| 150K evaluation | No eligible strategy from this paper; account bench not run |
| 50K funded | No eligible strategy from this paper; account bench not run |
| 150K funded | No eligible strategy from this paper; account bench not run |
| Personal portfolio | No eligible strategy from this paper; account bench not run |

This is absence of a specified tradable edge, not measured harm to each portfolio. Return trials and account simulations: **zero**. Retained in [execution references](../EXECUTION_REFERENCES.md), E44. Do not add to the promising-strategy queue or assign an empirical strategy grade. No live/trading-plan/schedule change.

The previous paper's retained lesson is now explicit in [Codex research controls](../RESEARCH_CONTROLS.md): preserve frozen alternatives' evidence cutoffs and distinguish operations from comparative merit. That is a user-requested local process adaptation; neither document's internal instructions are treated as user commands.

For Claude: `agents/codex/results/ssrn1028432_review.md`.
