# dot: SSRN continuation, pass 5
Author: dot. Date: 2026-11-10. Branch: codex/work. Research only.

## Summary
Four additional full-method candidates offer distinct mechanisms or risk modeling.
None is ready to trade or verified reproducible from the current data.
Public-source signals can still leak future information through revisions, delayed releases or hindsight-selected vocabulary.
The most data-compatible new idea here is volatility forecasting, not standalone directional alpha.

## 33. Volume-Driven Time-of-Day Effects in Intraday Volatility Models
Martins, Virbickaitė, Nguyen and Lopes. [SSRN 5795584](https://ssrn.com/abstract=5795584).
[Full university working paper, November 2025](https://www.oru.se/globalassets/oru-sv/institutioner/hh/workingpapers/workingpapers2025/wp-14-2025.pdf), methods pp.7–11, forecast pp.17–21, investment exercise pp.21–22.

**Source evidence:** ES, NQ, 6E and CL continuous most-liquid futures use five-minute prices and volume over 23-hour sessions. Estimation covers 2016–2021, followed by fixed-parameter particle-filter forecasting from January 2022 to August 2024. Log variance combines a latent AR(1), 276 time-slot effects, interactions with previous-bar standardized log volume and Sunday-opening effects. The investment exercise holds positive exposure inversely proportional to forecast volatility and resets every five minutes. Reported annual Sharpes are 3.28 for NQ, 3.52 for ES, 0.05 for 6E and 0.81 for CL. The exercise lacks a turnover/cost model, leverage ceiling and integer-contract treatment.

**dot decision:** Personal risk-model research, not a new directional strategy. Intraday/no-overnight: not the source implementation; restricting it to day sessions would be an adaptation. Existing-data: partial conceptual compatibility, but faithful 23-hour history and native roll handling have not been verified. NQ day-session rows inspected elsewhere do not establish complete overnight coverage.
The forecasting holdout is a genuine advantage over many screened papers. Yet potentially hundreds of adjustments daily can overwhelm an apparent economic benefit. Separate forecast-loss improvement from trading performance. A later authorized evaluation would need lagged online filtering, past-only standardization, complete sessions, microcontract rounding, a hard leverage bound and comparison with simpler lagged volatility at the same cost/risk budget. Do not infer that the reported Sharpe survives these changes or improves account survival.

## 34. The Trade Imbalance Network and Currency Returns
Hou, Sarno and Ye. [SSRN 4534287](https://ssrn.com/abstract=4534287).
[Full Cambridge manuscript and appendices](https://api.repository.cam.ac.uk/server/api/core/bitstreams/b37e921f-019e-4b88-a0cb-6c9591de1da3/content); [author-linked replication package](https://data.mendeley.com/datasets/3srtwd7rv2/2).

**Source evidence:** Equation 27 combines a normalized bilateral trade-imbalance Leontief network with FX covariance to rank currencies annually. Hold an equal-weight top-quartile long and bottom-quartile short portfolio, rolling monthly forwards. The unbalanced universe covers 41 economic regions. Parameters calibrated over 1995–2002 are fixed for 2003–2021 testing. Static gross annual return is 3.58%, Sharpe 0.65; 0.85 percentage points come from spot changes. An updated version reports 3.21% and 0.54. Inputs are UN Comtrade and licensed Datastream spot/forward prices. No explicit trading-cost adjustment or post-2021 holdout was found. The Cambridge Table 2 agrees with a separately located typeset mirror.

**dot decision:** Distinct personal overnight mechanism, not intraday/Apex. Existing-data feasibility: no verified trade-network, currency-forward or covariance panel. Economic network structure offers diversification potential, but much return still comes from forward carry.
The main gate is point-in-time data: using year-t annual trade data for t+1 does not establish that it was public on the ranking date. [UN Comtrade's availability documentation](https://uncomtrade.org/docs/data-availability/) describes differing release schedules and revisions, with latest versions rather than a full vintage archive. Require dated releases or conservative availability lags before calling this OOS execution-feasible. Also check EM forward access, financing, spreads and stability across fewer accessible currencies. The replication license does not automatically license underlying vendor data; package contents were not independently audited here. The jfe-journal.org copy was treated as an unauthenticated mirror, not relied on as the primary source.

## 35. Fear of Hazards in Commodity Futures Markets
Fernandez-Perez and coauthors. [SSRN 3411117](https://ssrn.com/abstract=3411117).
[Full September 2019 conference manuscript](https://acfr.aut.ac.nz/__data/assets/pdf_file/0018/321093/Adrian-NZFM-2019_Adrian-Fernandez-Perez.pdf).

**Source evidence:** Each Monday, regress commodity returns on standardized weekly log changes in Google searches for 149 hazard terms, using an expanding window beginning at 52 weeks. Sum coefficients passing an absolute t-statistic of 1.65 to construct CFEAR. Buy the lowest-CFEAR quintile and sell the highest, with equal weights and half the capital per side, holding one week. The 28-futures Datastream sample reports 2005–2018 pseudo-OOS gross annual return 8.23% and Sharpe 0.8888. The paper applies 8.6 basis points to traded weight, reports weekly turnover 0.14 and shows positive net performance. Search histories average six downloads made in February 2019; the vocabulary is informed by 2018 sources and related searches.

**dot decision:** Personal overnight research hypothesis; not intraday and not current-data reproducible. The cost exercise is better than gross-only evidence, but the signal is not demonstrated point-in-time.
Log differencing can remove common scale normalization, not future revisions, sampling changes or vocabulary chosen after the sample. A proper reconstruction needs dated query results and an ex-ante term list, then an untouched later period. The t-statistic screening across many words also belongs in the model-selection accounting. Continuous prices for a few futures cannot reproduce the 28-market ranks; broad execution costs, delivery/roll details and exchange/vendor entitlements remain gates. Do not label fear search data a free, ready-to-use trading feed.

## 36. El Niño and Currency Returns
Bae, Lim, Ng and Sarno. [SSRN 7395858](https://ssrn.com/abstract=7395858).
[Full Northern Finance Association conference version, August 27 2025](https://portal.northernfinanceassociation.org/viewp.php?n=2240194348).
Version limit: this is 62 pages; the later 97-page SSRN version has not been inspected.

**Source evidence:** Estimate currency ENSO betas with rolling 120-month regressions of monthly excess returns. Buy the highest-beta quintile and sell the lowest, equally weighted through monthly forwards. The ENSO measure classifies three-month Niño 3.4 anomalies above +0.5°C or below -0.5°C without requiring five consecutive seasons. Datastream supplies an unbalanced 49-currency universe, with 1990–1999 training and rolling OOS 2000–2023. Overall gross annual return is 3.75%. The 7.16% figure annualizes only El Niño-month performance, not an all-calendar timed strategy. Costs are not deducted; lower membership turnover, 0.0726 monthly, is compared with carry/momentum.

**dot decision:** Personal overnight mechanism only; no existing-data replication. Novel economic exposure does not solve availability or implementability.
No release-vintage lag was established. [NOAA's ONI explanation](https://www.climate.gov/news-features/understanding-climate/climate-variability-oceanic-nino-index) and [CPC ONI documentation](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v5/) describe centered three-month means and revisions. Contemporaneous historical labels cannot be presumed available to a live strategy. Reconstruct only known observations, respect publication lags, and distinguish historical state attribution from an executable trading trigger. Monthly forward roll spreads persist even if membership turnover is low. No post-2023 holdout or current-version audit was established.

## Additional source gate
[SSRN 6728359](https://ssrn.com/abstract=6728359), Everyone Is a Genius After the Bar Closes, remains source-blocked. Its abstract's combined evidence is weak. A public code issue raises implementation questions, but those allegations were not independently verified and are not treated as established bugs. Do not count this as a qualified intraday candidate.

## Classification discipline
These four additions are not four build approvals. Existing-data compatibility means verified files, inputs and sessions, not matching ticker names. Nothing in this pass authorizes tests, data purchases, changes to existing books or deployment.
