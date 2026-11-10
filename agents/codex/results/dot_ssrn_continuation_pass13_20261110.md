# dot: monetary restrictiveness and currency-factor timing
Author: dot. 2026-11-10. Research only; no return tests or strategy changes.

## 52. Monetary Restrictiveness and Currency Returns
**Personal monthly FX; not intraday; not testable with verified current inputs. Distinct conditional lead, below entry 41 in implementation readiness.**

[SSRN 5096662](https://ssrn.com/abstract=5096662) lists April 15, 2025. Reviewed the complete [February 14, 2025 primary manuscript](https://www.bwl.uni-mannheim.de/media/Lehrstuehle/bwl/Area_Finance/Finance_Area_Seminar/FSS_2025/Sohnke_Paper.pdf), 38 pages; April PDF retrieval failed, so version parity is unverified.

### Compact source specification
Methodology pp.4–8 and Tables 1/3: fit M1 on country/month effects and common GDP/export/import slopes using the trailing 60 months. Estimate slopes in quarterly differences, then recover level effects/residuals. Rank negative residual divided by M1. Contemporaneous OECD vintages supply regressors and M1; lagged midmonth FX converts units. Sixteen economies enter estimation; USD is not traded. Monthly equal-weight long highest-restrictiveness quintile, short lowest, using one-month forwards. July 2006–May 2020 next-month spread: 0.42% monthly, t=2.29; seven-factor alpha 0.299%, t=1.99. Datastream quotes are midprices. No trading-cost, Sharpe or postpublication holdout results located. Longer signal-lag tables do not describe locking a forward for three years.

### Independent implementation assessment
- Vintage discipline is valuable, but the ranking month participates in estimation. Historical chronological sorting is not untouched prospective validation.
- Residual money supply is model-dependent, not a proven central-bank shock. Omitted demand and reporting changes can drive it.
- Authenticate exact archive publication clocks before the executable quote. Reconcile source units: current-price GDP and constant-price trade labels cannot be silently homogenized.
- Reconstruct missing observations, eligibility, quantiles and ties. G10-only or 6E-only substitutions change the experiment.
- Zero initial forward value is not zero trading cost or zero capital. Require spreads, settlement calendars, rolls, collateral and a capital-normalized NAV.
- [Fed's February 23, 2021 release](https://www.federalreserve.gov/releases/H6/20210223/) incorporated savings deposits into M1 retroactively to May 2020; see [technical explanation](https://www.federalreserve.gov/releases/h6/h6_technical_qa.htm). My inference: appending today's revised US series can distort every country's pooled-model residual, even though USD is excluded from traded returns.
- No matching entry was found in TIER_LIST, DATA_NEEDED or the first 51 entries. Entry 41 uses real-time industrial-production gaps, entry 23 meeting surprises, and S11 intraday carry. These are related FX exposures, not exact duplicates.
- No complete replication package or matching vintage inventory verified. [OECD terms](https://www.oecd.org/en/about/terms-conditions.html) require attribution and dataset-specific checks; [Dallas's old archive](https://www.dallasfed.org/research/international/oecd) ends too early. [Datastream](https://developers.lseg.com/en/api-catalog/eikon/datastream-web-service/) requires access rights.

**Smallest future gate:** authenticate latest paper, then reconcile one historical and one post-definition-change month from original vintages through normalized forward cashflows. No test is authorized by this report.

## Unnumbered reserve: Global Currency Hedging with Common Risk Factors
[SSRN 3264531](https://ssrn.com/abstract=3264531). Reviewed complete [November 2018 author manuscript](https://www.olsendata.com/data_products/client_papers/papers/201811-WieOpie-GlobalCurrencyHedging.pdf) and [May 2019 slides](https://abfer.org/media/abfer-events-2019/annual-conference/international-macroeconomics/28-P1-Global-Currecncy-Hedging-with-Common-Risk-Factors.pdf). [Published preview](https://www.sciencedirect.com/science/article/abs/pii/S0304405X19302880) confirms standalone strategy; full final paper remains unavailable.

Source summary, §§3–4/7 and Table 8: nine foreign G10 currencies, monthly forwards; 60-month currency betas on dollar/carry factors, expanding factor forecasts initialized with ten years. Predictors include forward discounts and changes in aggregate FX variance, TED spread and CRB raw industrials. Buy positive predicted currency returns, short negative. January 1997–July 2017 standalone mean 5.78%, volatility 7.38%, Sharpe .78, skew .20. Quoted bid/ask costs distinguish new trades and rolls. Separate hedge optimization is not the standalone strategy.

**Assessment:** Personal monthly reserve, not a new independent premium or ready complement. Entry 45 already times carry with cross-asset information; DCF adds a two-factor architecture. Source does not clearly resolve standalone gross notional/collateral. Draft Table 8 calls blends 50–50 while the equity-plus-FX mean equals the sum, not average; reconcile final source and overlay convention before using portfolio claims. Standalone maximum drawdown is not supplied. Historical expanding estimation does not remove publication-time selection.

[FRED TEDRATE](https://fred.stlouisfed.org/series/TEDRATE) was discontinued in January 2022. Replacing it with SOFR/OIS changes the strategy. [Currency Factors](https://www.currencyfactors.com/currency-data) offers recent factor data for academic use and uses 25% quoted spreads in net series; neither unrestricted trading rights nor an exact DCF feed follows. Owned 6E bars cannot reproduce the G10 forward panel. Keep unnumbered until final-source sizing, costs and modern continuity are resolved.
