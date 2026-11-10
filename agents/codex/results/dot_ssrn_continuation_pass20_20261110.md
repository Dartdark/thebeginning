# dot: SSRN continuation, pass 20
Author: dot. November 10, 2026. Research only; no tests or strategy changes.

Three distinct personal-account research entries. None establishes a new current-data-ready or same-calendar-day intraday strategy.

## 59. The Pre-FOMC Drift in Long-Term Treasury Bonds
Pan and Peng, [SSRN 4764451](https://ssrn.com/abstract=4764451). [Full author manuscript, June 2, 2026](https://en.saif.sjtu.edu.cn/junpan/FOMC_new.pdf), printed pp.8–13, 23–26.

**Source:** Daily analysis covers September 1994–December 2025 and 250 scheduled announcements; futures January 2004–June 2025. Long ten-year Treasury futures from 19:00 Eastern on announcement day minus two to 12:00 on day minus one yields 7.26 basis points gross per event, t=2.82. Subsequent 12:00–17:00 interval averages −2.05 basis points. CME tick data; highest-volume contract selection. The text inconsistently calls the instrument ten-year note futures and E-mini Treasury futures. Attention conditioning uses day-minus-three unemployment Macro Attention Index; its real-time delivery and median estimation need clarification. No net trading ledger or untouched strategy holdout established.

**Assessment:** Distinct from pre-refunding #21, month-end #42 and post-FOMC reversal #53. Simple calendar rule is preferable for first feasibility work to adding an unverified attention feed. Crosses midnight, although within one normal CME session. Under the user's requested no-overnight category, retain as personal overnight rather than count as a same-day slot. Do not infer blanket account ineligibility from a calendar boundary.

Required: exact native contract, causal roll selection, scheduled-event dates and definition of day offsets, DST/holiday exceptions, observable entry quotes, commissions and exit fills. Existing Treasury filenames do not establish endpoint or native-roll coverage. Sparse event exposure and a positive mean are not account-survival or diversification evidence. No current-data admission.

## 60. Extreme Weather Forecasts and U.S. Natural Gas Futures
[SSRN 4326098](https://ssrn.com/abstract=4326098), earlier title *Extreme Weather Forecasts Impact on U.S. Natural Gas Futures Prices*. [Published 2025 full paper](https://iris.unibocconi.it/retrieve/80f68941-b412-43f3-992a-2a2a701b0398/Caselli%20Gandolfi%20et%20al.pdf). Draft-to-final numerical parity unverified.

**Source:** Population-weighted forecasts for 12 cities, 2010 Census weights and 50-year climatology. Long first NG maturity, short second, hold five business days following sufficiently cold forecasts with a one-day lag. Table 7's two-week forecast threshold is −3.2°C, based on observed-temperature deviations, not forecast deciles. April 1990–July 2019 result is reported as 12% CAGR and absolute Sharpe 1.3, without costs/slippage. Footnote 14 identifies NOAA Reforecast V2, generated using a fixed 2012 GEFS model. Dated climatology/threshold estimation, overlapping-signal sizing, native rolls and capital denominator remain unresolved. Every 100%-threshold row has zero CAR/CAGR; separate Appendix B is needed to resolve abnormal-return accounting. That supplement was unavailable.

**Assessment:** Distinct exogenous weather mechanism, not analyst-quality drift #47 or ENSO/FX #36. Personal multi-day curve spread only. Do not interpret the reported curve as verified account P&L.

[NOAA model documentation](https://psl.noaa.gov/models/) and [dataset paper](https://doi.org/10.1175/BAMS-D-12-00014.1) establish retrospective forecast generation. Lagging a 2012-model reforecast does not establish that the signal existed in 1990. This is a substantive point-in-time failure in the historical trading interpretation, not proof that a correctly reconstructed forecast strategy cannot work.

[Operational GEFS public-data terms](https://registry.opendata.aws/noaa-gefs/) do not establish historical coverage or rights to Bloomberg futures inputs. Need operational forecast receipts, causal climatology/thresholds and native maturity data. Current NG continuous bars cannot supply a two-contract executable spread. No current-data admission, no purchase or author outreach.

## 61. Prospect Theory and Currency Returns: Empirical Evidence
[SSRN 3629061](https://ssrn.com/abstract=3629061). [JFQA accepted full paper, July 15, 2026](https://jfqa.org/wp-content/uploads/2026/08/25793-FX_Prospect_Theory.pdf), pp.14–19, 47, 86–87; [journal acceptance](https://jfqa.org/2026/07/30/prospect-theory-and-currency-returns-empirical-evidence/).

**Source:** Monthly ranking uses 60 monthly simple spot returns, USD per foreign currency. Cumulative-prospect value uses exponent .88, loss aversion 2.25, gain/loss probability parameters .61/.69 and Equation 1's cumulative-tail weights. Buy lowest prospect-value quintile, short highest; rebalance monthly. Developed 15-currency to G10 universe, January 1990–February 2018. Gross mean .42% monthly, annualized 5.04%; annualized Sharpe .59. Appendix A9 bid–ask-adjusted mean .41% monthly, t=3.05. Post-2007 t=1.69 versus earlier 2.67. Its out-of-sample terminology refers to transfer from equity research, not an untouched chronological trading holdout.

**Assessment:** A distinct behavioral distribution signal, rather than another momentum lookback. Personal overnight research, not intraday. A 2026 acceptance date does not make the return sample modern.

Need within-group sizing, signal-formation versus execution sequence, both-side quote/cost treatment, native spot/forward returns and licensing, and a frozen modern holdout. Mechanism analysis uses CLS/CFTC data, but those are not necessary for the base price-distribution signal. Owned 6E alone cannot reproduce a broad currency sort. No current-data admission or portfolio benefit established.

## Additional exclusions without count inflation
- [SSRN 4024310 full published paper](https://repository.adu.ac.ae/bitstreams/30d15095-739e-4967-a33f-7233bf0644df/download): 388 FX technical-rule portfolios; four selected core rules all have negative modeled net annual means in January 1999–April 2020. Costs decline across historical periods. This argues against recycled moving-average/filter/channel variants, not all FX strategies. Range-breakout lookback labels conflict.
- [SSRN 1992153](https://ssrn.com/abstract=1992153): fourth-quarterly STIR carry overlaps existing carry research, uses obsolete benchmark instruments and assumed FX hedging; no verified SOFR-era net evidence.
- [SSRN 3865403, Federal Reserve full paper](https://www.federalreserve.gov/econres/feds/files/2021001pap.pdf): international yield-spread forecasting is not an executable costed futures strategy.
- [SSRN 4323569 vendor paper](https://s3.amazonaws.com/com.ravenpack.cms/pages/Developed_Markets_Sovereign_Bonds_Investing_Enhancing_Style_with_Sentiment459FBEB2.pdf): bond sentiment requires licensed news/index data; no established costed untouched holdout.
- [SSRN 3493732](https://ssrn.com/abstract=3493732), jump-only currency momentum/reversal: full source unresolved, so exact costs/rules not promoted.
- [SSRN 3536046 author digest](https://www.bayes-cid.com/pdf/issues/2023-summer/publications/CID%20Summer%20Han%20and%20Kong%20053023.pdf): 27-commodity lead-lag Lasso, 60-month rolling estimation; complete costs/rolls/holding frequency still require full paper. It is not admitted as intraday.
- Guo/Zhu's 2026 Chinese cross-commodity intraday work remains full-source and SSRN-identity gated. The separately surfaced Chinese pairs paper uses price indices and admits parameter selection involving both train and test periods; no verified net executable addition.

## Disposition
61 numbered research entries, not 61 strong strategies. The original five provisional intraday reserves and five failed existing-data baselines remain honestly labeled. These three additions do not fill either gap. No return tests, data acquisition, account access or paused experiments resumed.
