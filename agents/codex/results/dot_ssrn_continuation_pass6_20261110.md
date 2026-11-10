# dot: SSRN continuation, pass 6
Author: dot. Date: 2026-11-10. Research only.

## Summary
Two additional conditional mechanisms survive full-source review: slow speculative positioning and same-day FX session flows.
Neither is an approved strategy or proven improvement to the portfolio.
A paired variance-risk-premium audit shows why original predictive regressions need later independent evidence.

## 37. Speculative Pressure
Fan, Fernandez-Perez, Fuertes and Miffre. [SSRN 3279425](https://ssrn.com/abstract=3279425).
[Full accepted Griffith manuscript](https://research-repository.griffith.edu.au/server/api/core/bitstreams/ca96c9d7-804b-4bac-87cf-97227dc9caa3/content).

**Source evidence:** At month-end, average the prior 52 weekly noncommercial net-long ratios, (long minus short)/(long plus short). Demean across contracts and set weights proportional to the signal, normalized to total absolute weight one: 50% long and 50% short. Hold one month. The broader 84-contract study includes 43 commodities and 11 FX futures; class tests cover 1993–May 2018. Tuesday COT observations are explicitly dated to Friday publication. Gross commodity annual return is 4.12%, Sharpe 0.612; FX 2.51%, 0.470. Fixed-income performance fails. Cost evidence is break-even cost per traded weight, 235.1 basis points for commodities and 142.3 for FX, compared with an 8.6-basis-point literature estimate. It is not actual quoted net P&L. Inputs are public COT and licensed Datastream prices. No untouched post-2018 holdout was established.

**dot decision:** Personal overnight, not intraday/Apex. Existing-data replication unverified. A precise cross-sectional slow-position signal is different from the failed gold crowding threshold or a generic equity-index COT rank.
Friday date alignment is necessary but insufficient: require fills after the actual release time, not an earlier Friday settlement. Model contract rolls as trades, not only changes in portfolio weights. Broad market coverage, minimum contract sizes, exposures, liquidity, spread costs and capital scaling matter. Compare with carry/trend and the commercial-flow paper 24 before calling this an independent sleeve. No exact repository ID or meaningful title match was found; related positioning families remain relevant context.

## 38. Intraday Patterns in FX Returns and Order Flow
Breedon and Ranaldo. [SSRN 2099321](https://ssrn.com/abstract=2099321).
[Full QMUL April 2012 manuscript](https://www.qmul.ac.uk/sef/media/econ/research/workingpapers/2012/items/wp694.pdf), pp.4–10 and 14–15.

**Source evidence:** EBS spot transactions/executable quotes cover January 1997–early June 2007 for six pairs, with DEM before EUR. The useful EUR/USD rule shorts from 07:00 Dublin/London time to 08:00 New York, then buys until 16:00 New York, flat otherwise. The first entry is normally 02:00 New York but shifts during DST mismatches. The overlapping sessions are truncated at the next market's open. Gross directional annual log returns are about 8.4% and 10%; after firm EBS bid/ask costs they are 6% and 7%, with Sharpes 1.3 and 0.9. All other pair/session strategies lose after spreads. Year-by-year stability is shown, but no held-out OOS. Commissions, execution delay and market impact are not explicitly modeled. Customer-flow evidence supports local-currency selling during local business hours; order flow is explanatory, not a required signal.

**dot decision:** A more useful fully inspected intraday reserve, but not a validated 6E strategy. Personal spot implementation is distinct from a futures adaptation. Both legs close on the same New York/UTC calendar day. The 16:00 Eastern exit precedes the standard cutoffs already checked, but this is holding-time screening, not account-specific compliance certification.
6E is quoted USD per EUR, so the directional mapping is not inverted. [CME specifications](https://www.cmegroup.com/markets/fx/g10/euro-fx/specs?videoId=6375461729112) and its [spot/futures basis explanation](https://www.cmegroup.com/education/whitepapers/reconciling-fx-spot-futures-prices) make clear that futures remain a separate instrument.
Existing-data status is conditional: 6E minute prices could express the clock rule, but exact overnight coverage, native rolls, costs and dated London/New York daylight-saving calendars have not been verified. Do not assign EBS institutional returns to a micro/standard futures account. The data end in 2007, so later untouched evidence is essential. No test run.

## 39. Expected Stock Returns and Variance Risk Premia
Bollerslev, Tauchen and Zhou. [SSRN 948309](https://ssrn.com/abstract=948309).
[Published RFS paper](https://public.econ.duke.edu/~boller/Published_Papers/rfs_09.pdf).

**Source evidence:** Monthly variance risk premium is VIX squared minus the current month's realized cash S&P 500 variance. The latter sums 78 five-minute regular-session squared returns daily plus close-to-open returns. The 1990–2007 study forecasts cash-index excess log returns over three-month Treasury bills at multiple horizons, with strongest predictive evidence quarterly. It does not specify a complete executable position threshold, leverage policy, transaction-cost model or untouched trading P&L evaluation.

**dot decision:** Deprioritize as a fresh strategy. Personal quarterly timing only, not intraday. Current VIX and ES bars do not constitute faithful cash-index variance replication. Equity timing is not identical to the existing VIXY sleeve, but the broad VRP mechanism is already familiar and must face subsequent evidence rather than be rediscovered as new alpha. Overlapping quarterly outcomes and cash-to-futures substitution need explicit treatment.

## 40. A Comprehensive 2022 Look at the Empirical Performance of Equity Premium Prediction
Goyal, Welch and Zafirov. [SSRN 3929119](https://ssrn.com/abstract=3929119).
[Published RFS 2024 paper](https://www.ivo-welch.org/research/journalcopy/goyal2024comprehensive.pdf), section 3.1.3, pp.3513–3514.

**Source evidence:** The authors revisit 29 newer predictors plus 17 earlier variables, extending evidence through 2021. For the original authors' updated VRP series, original significance reproduces, but extended-sample t falls to 0.72 and the coefficient changes sign across sample halves. OOS prediction with Campbell–Thompson truncation is positive but insignificant; unconstrained OOS is substantially worse. Four simple timing variants underperform constant equity exposure by 2.6–7.0 annual percentage points.

**dot decision:** Independent counterevidence, not a new strategy or our own test. It does not refute every possible VRP implementation, but substantially lowers the priority of manufacturing an ES proxy strategy from paper 39. Predictive significance, economic timing value and account survival are separate claims. The broader paper is useful for evaluating other claimed market-timing signals before adding complexity.

## Additional exclusions
SSRN 2001981, Ensemble Properties of High Frequency Data and Intraday Trading Rules: full author manuscript inspected by the source review. Gross profit of only roughly 1.38–2.87 basis points per trade, costs excluded and a conditioning-window choice informed by the full sample. Cash-index noise bands, not a strong fresh futures candidate.
SSRN 4326098 and 6789516: weather-related leads remain full-source blocked; not promoted.

## Current conclusion
Paper 38 adds a transparent low-input intraday hypothesis worth a source/data feasibility check, not a performance claim for 6E. Paper 37 adds a distinct precisely lagged positioning design, but broad data and cost gates remain. No strategy or existing research result was changed.
