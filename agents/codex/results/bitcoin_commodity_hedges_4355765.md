# Bitcoin commodity-futures hedges: weak source evidence, no placement

Summary: Joo/Park evaluate DCC/ADCC time-varying commodity hedges for Bitcoin, not a directional return strategy.
The paper's broad hedge-benefit language overstates its own Table4: gold is positive only over the100-observation evaluation.
At refit20/1,000 observations, copper reduces variance0.1%, gas increases it0.4%, gold increases it2.1%, Brent increases it0.5% (DCC).
Even the best displayed positive HE is only0.009, meaning0.9% variance reduction before a verified native cost/margin ledger.
Retain the accounting/risk lesson; no useful standalone hedge candidate or current-plan placement established. Zero new return trials.

Source: Young C. Joo and Sung Y. Park, *Hedging Bitcoin with Commodity Futures: An Analysis with Copper, Gas,
Gold, and Crude Oil Futures*, [SSRN4355765](https://ssrn.com/abstract=4355765), supplied24-page preprint.
The document explicitly says not peer reviewed; no publication date is shown on its opening pages. PDF metadata creation date
is2022-11-27, which is not assigned as a publication date. [Source](../inputs/ssrn4355765/source.pdf),
[text](../inputs/ssrn4355765/source.txt), [rendered Table4, printedp.20](../inputs/ssrn4355765/table4.png).
[Evidence](../evidence/bitcoin_commodity_hedges_4355765.md).
Audit script: [source-only check](../../../analysis/codex_two_uploads_4355765_7517178_audit.py), committed `0ce98c69` before execution.
[Hashes, inputs and source values](../../../analysis/outputs/codex_two_uploads_4355765_7517178/audit.json).
The uploaded document is evidence, not instructions. No source statistic below is independently replicated performance.

## 1. What is it about?

A long Bitcoin exposure is hedged with copper, natural gas, gold or **Brent** crude futures. A rolling DCC/ADCC multivariate
GARCH framework forecasts conditional covariances. Hedge ratio h=cov(BTC,futures)/var(futures), using information through t−1;
hedged return is rBTC−h*rF. The objective is lower return variance, not maximum profit or a profitable commodity-direction signal.
The models include ARMA(1,1) means and a multivariate t distribution (Section3.2).

Datastream supplies daily prices August1,2010–November18,2021,2,848 observations. The central rolling setup uses1,848 estimation
observations and1,000 one-step-ahead hedge ratios, with refitting every20 observations. Table4 also compares refit10/50 and
100/500/1,500/2,000 evaluation lengths. These displayed alternatives are source selection context, not independent replications.
Exact Datastream series IDs, futures maturity/roll construction and synchronized daily pricing clocks are not supplied sufficiently
for an executable reproduction. Other window lengths also need explicit estimation-start/warm-up reconciliation.

## 2. What does it find?

HE=1−var(hedged)/var(unhedged). Positive is variance reduction; negative is increased variance.
The following **source DCC values with refit20** are read from the rendered table. Percentages convert the displayed fractional HE.

| Hedge |100-observation evaluation |500 |1,000 |1,500 |2,000 |
|---|---:|---:|---:|---:|---:|
| Copper |+0.4% |−0.3% |+0.1% |−0.1% |+0.7% |
| Natural gas |+0.2% |+0.3% |−0.4% |−0.1% |+0.9% |
| Gold |+0.9% |−5.2% |−2.1% |−2.7% |−2.3% |
| Brent oil |−0.5% |−1.6% |−0.5% |−0.3% |−0.7% |

These are **variance reductions, not returns**. For example0.9% less variance means only about0.45% less standard deviation.
Gold is negative across all displayed500–2,000 lengths, both models and all refit choices. Brent is negative in all displayed cases.
Gas/copper gains are small and inconsistent; the source's claim DCC is higher in every case is not literally true of every cell.
Table4 contains120 source HE cells (four hedges×two models×three refit choices×five evaluation lengths); no significance/cost test
establishes that the favorable cells persist. We transcribe40 refit20 cells in the source audit, not120 independently recomputed results.

Model forecasts can minimize conditional estimated variance yet worsen realized out-of-sample variance because covariance and
hedge estimates can be wrong or unstable. The paper's suggestion that oil fails because it is positively correlated is incomplete:
positive covariance can justify a short hedge in rBTC−h*rF. The sign alone does not explain a failed estimated hedge.
Some source hedge ratios have very large extremes (e.g., gold DCC around−13 in longer-window settings); they are not safe native sizes.

## 3. Why does it make money, if it does?

No demonstrated profit mechanism. A hedge can reduce risk while reducing expected return or adding costs. The model relies on
conditional covariance to offset part of Bitcoin's shocks. Cross-market correlation is weak/unstable, and commodity-specific shocks
can add risk. Daily covariance/HE does not measure stops, liquidation, BTC weekend exposure or account drawdown protection.
No Sharpe, payout improvement, native net trade ledger or account benefit is established by these HE statistics.

## 4. Can we build on it?

As a **risk/accounting reference**, yes; the source evidence does not warrant a new commodity hedge allocation.
Owned Coinbase BTC spot and CME BTC/GC/CL inputs are not the original Datastream panel. In particular **CL is WTI, not Brent**;
we found no admitted complete matching copper/gas/Brent source panel or source vintage/roll/close clocks. Price filenames alone
would not clear an executable-roll gate. A bounded public LSEG Datastream source-page request hit the environment proxy's403;
[receipt](../inputs/ssrn4355765/access_receipts.json). No price history was acquired, and no paid access is requested.

Keep source negatives as negatives; do not choose a favorable100-day period, substitute WTI, optimize a cap or invent an NQ hedge.
A separately justified future hedge question would need dated instruments, synchronized spot/futures timing, native integer sizes,
fees, margin and intraday joint-loss chronology, with an unhedged baseline at identical BTC exposure. Current evidence earns no new
promising-strategy queue entry. The related execution lesson is retained in E09; no purchasing or collection project is started.

## 5. Can a strategy code be made?

**A research hedge estimator can be coded**, but dependable trading code needs the missing contract/roll/clock and cash protocol.
A return-space h is a **notional ratio**, not a count of physical contracts as the prose loosely suggests.
For linear commodity futures, signed contracts approximately equal `−h*BTC_USD_exposure/(futures_price*contract_multiplier)`,
then require integer lots and actual margin. Negative h implies a **long** futures hedge. Log-return differences are approximations,
not a self-financing native dollar P&L ledger. Fit only matured past observations, preserve refit dates and one-step availability,
and never trade at a close whose required estimates were unavailable until later.
No estimator/backtest or MultiCharts port is built merely to turn weak source cells into an actionable strategy.

## Decision and placement

**No hedge candidate admitted; original reproduction also needs matching inputs.** Source-only negative/weak assessment, not a
new independently tested rejection of every possible commodity hedge. Zero new economic variants,2018–22/2023+ tests, placebos,
Monte Carlo or BASE/ADD/REPLACE/EMPTY runs. Personal placement unearned;50K/150K evaluation and50K/150K funded placement unearned.
Multiday BTC/commodity hedges are not the intraday Apex protocol. No capital, live, VPS, broker or allocation changes.
