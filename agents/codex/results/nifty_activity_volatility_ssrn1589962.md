# Nifty futures activity/spot volatility: reference only, no trading edge established

Summary: Unexpected futures activity correlates positively with Nifty spot variance;
expected activity correlates negatively in the author's fitted models.
No strategy returns, future forecast test or causal identification are supplied.
The reported persistence comparison omits the GJR asymmetric term; table/prose values also conflict.
Do not turn this into a sizing/filter rule; retain information-clock and model-validation cautions.

Source: P. Sakthivel & B. Kamaiah, *Futures Trading and Spot Market Volatility:
A Case of S&P CNX Nifty Index*, [SSRN1589962](https://ssrn.com/abstract=1589962).
Uploaded manuscript: accepted-series header for GITAM Review of International
Business; publication date not independently verified. Read all 15 pages.
PDF/hash: `agents/codex/inputs/ssrn1589962/`.
Evidence gate: `agents/codex/evidence/nifty_activity_volatility_ssrn1589962.md`.
Arithmetic script: `analysis/codex_ssrn1589962_audit.py`;
output: `analysis/outputs/codex_ssrn1589962_review/model_arithmetic.json`.
**Return trials: 0.** Quoted coefficients are author results; arithmetic checks
below are not a re-estimation or independent empirical replication.

## 1. What is it about?

The paper examines daily Nifty spot returns and near-month Nifty futures trading
volume/open interest, 2000-07-01–2008-02-28. It decomposes volume and open
interest separately with ARMA(5,5): residual = unexpected component, actual minus
residual = expected component (pp.6–7). Those components enter GARCH(1,1) and
GJR-GARCH(1,1) spot-return variance equations (pp.8–9).

It is an empirical volatility/activity association study, not a stock-index
direction forecast, strategy specification or execution experiment.

## 2. What does it find?

Author coefficient estimates from Tables 2/3, pp.14–15:

| Activity component in spot variance equation | GARCH | GJR-GARCH |
|---|---:|---:|
| Expected futures volume | -0.3486 | -0.826 |
| Unexpected futures volume | +0.0403 | +1.153 |
| Expected futures open interest | -2.0925 | -1.762 |
| Unexpected futures open interest | +0.1540 | +0.763 |

The author interprets surprise activity as information arrival and predictable
activity as associated with quieter markets. These are fitted associations,
not coefficient-sized returns or directly comparable economic impacts across
arbitrarily scaled activity variables. No return, Sharpe, drawdown, execution
savings or future forecast accuracy is reported.

Material verification limits:

- **Contemporaneous inputs are not a pre-trade signal.** The variance equations
  use activity components without a demonstrated prior-availability clock. Actual
  full-day volume is only complete at day end; dated OI needs its own release and
  receipt timing. A residual fitted using that activity does not predict the
  activity before it is observed. ARMA estimation is not documented as a rolling
  live-available forecast. No out-of-sample forecasting benchmark is supplied.
- **Association does not identify causal impact.** Common news can raise activity
  and volatility together. Calling regressors exogenous does not establish that
  futures activity causes cash volatility or that trading ahead is possible.
- **The persistence claim is incomplete.** Page 10 says ARCH+GARCH persistence
  falls from about 0.94 to 0.75. Printed Table 2 gives 0.3878+0.5659 = **0.9537**;
  Table 3 gives 0.150+0.601 = **0.751** but also prints **gamma=0.745**.
  Under the standard symmetric-innovation GJR calculation, feedback is
  alpha+beta+gamma/2 = **1.1235**, not 0.751. The usual finite-variance
  stationary GJR condition would therefore not be satisfied by the printed
  core feedback. Added exogenous variance regressors need further conditions;
  this arithmetic flags an unresolved model claim, not a full stationarity proof
  or proof that the underlying market is explosive. Table 3 was visually checked.
- **Prose/table conflict.** Page 10 gives the expected-volume coefficient as
  -3.483; Table 2 prints -0.3486. Use the table for the table above and preserve
  the discrepancy; do not infer a corrected estimate.
- **Significance markings need caution.** The tables mark some t-statistics as
  1% significant that do not clear the usual two-sided asymptotic-normal bar:
  examples include 2.148 and -2.315. The arithmetic artifact records selected
  normal-reference p-values; these are not a re-estimation of uncertainty.
- **Depth and direction are not measured by OI.** Open interest counts outstanding
  contracts, each with a long and short. Its surprise is not signed demand and
  does not directly measure executable bid/ask liquidity. The paper discusses
  spreads in its conclusion but does not estimate a spread or fill-cost model.

## 3. Why would it make money?

It establishes no money-making rule. The proposed explanation is that new
information produces unexpected activity and volatility together, while normal
activity may reflect liquidity. The introduction discusses information-mixture
and sequential-information theories; p.3 says this study is not intended to
verify those theories. Neither explanation supplies trade direction or shows
that a risk signal arrives before the risk.

Higher volatility can raise gross opportunity and execution costs simultaneously.
Lower volatility is not automatically profitable for any existing strategy.
An in-sample variance coefficient does not establish that changing size, skipping
trades or widening stops improves net payouts.

## 4. Can we build on it?

**Use the methodological caution, not a new trading foundation.** It does not
earn a strategy return test or a promising-strategy queue entry. There is no
verified NQ/ES transfer or incremental place in evaluation/funded/personal books.
Older Indian index results are neither a forced-flow mechanism nor evidence
overturning our failed VVG and volume-filter experiments in TIER_LIST.

A separately justified risk-forecast project would first freeze signal-availability
clocks, use expanding/rolling past-only expected activity, model expiry/roll
effects, validate positive and stable conditional variance, and compare against
lagged realized-volatility/ATR forecasts. Only demonstrated future forecast
improvement earns paired strategy/account tests at native integer size and full
costs. This paper alone does not justify that additional research budget.

Local instrument filenames contain no Nifty daily price/OI panel. The OF minute
header contains volume and book features but not daily near-month OI. No proxy
return test or external acquisition was attempted: the earlier specification,
forecast-evidence and economic gates fail independently of missing inputs.

Retain the lesson in EXECUTION_REFERENCES, E50: unexpected activity measured
afterward is not automatically a forecast, and open interest is not book depth.
No live strategy input, sizing rule, trading plan, rank or PowerLanguage changed.

## Verification and reproduction

Full-text source inspection, visual Table 3 check, exact-ID/related-research
search, local filename/header inspection, and deterministic model arithmetic.
The source checksum is recorded in its manifest. Reproduce the arithmetic with:

```sh
python analysis/codex_ssrn1589962_audit.py
```

No ARMA/GARCH fitting, historical return test, placebo, Monte Carlo or account
comparison was performed or claimed. No source instructions were executed.

For Claude: `agents/codex/results/nifty_activity_volatility_ssrn1589962.md`.
