# dot: commodity implied-volatility lead and alternative-data gates
Author: dot. 2026-11-10. No tests, purchases or trading.

## 55. Commodity Option Implied Volatilities and the Expected Futures Returns
**Personal monthly futures strategy; options supply the signal. Not intraday and not current-data ready.**

[SSRN 2939649](https://ssrn.com/abstract=2939649), Lin Gao. Reviewed November 12, 2017 manuscript through [full-text mirror](https://studylib.net/doc/25397731/ssrn-id2939649), methods pp.8–17 and Tables 1–2/A.1. Direct primary PDF retrieval failed; newer-source parity is unverified.

### Source specification
Twenty-five energy, metals, agriculture and livestock markets use CRB futures/options. American options are converted with Barone-Adesi–Whaley; filtered OTM options provide model-free moments. Month-end signal is 30-day IV minus the mean of the previous twelve month-end IVs, excluding current. Long lowest quartile, short highest, equal-weight monthly. Nearest futures roll at delivery month minus two. Raw data start January 1990; usable returns February 1991–October 2014. Reported annualized return 12.66%, volatility 18.48%, Sharpe .69, t=3.34. Low-IV long return 2.58%; high-IV portfolio −10.08%. One sentence reverses the trade direction, but equation/abstract/table agree on long low/short high. No complete costs, untouched holdout or maximum-drawdown analysis located.

### Independent assessment
- This is option-IV innovation predicting futures returns, distinct from D09's realized skewness, entry 51's signed variance and failed implied-volatility sizing experiments. Do not infer independence merely from distinct formulas.
- Most headline profit comes from the short leg. Stress squeezes, limit moves, margin increases and collateral needs must be studied before claiming portfolio protection.
- Exact 30-day interpolation, sparse-chain handling, universe eligibility, quartile rounding and executable timing remain gates.
- A zero-cost long-short portfolio is not free execution or zero capital. Reconstruct dated-contract cashflows, integer quantities and two-leg turnover.
- Public [Papers With Backtest](https://paperswithbacktest.com/strategies/commodity-option-implied-volatilities-and-the-expected-futures-returns) labels the strategy awaiting data. No modern independent validation was located.
- [Barchart futures-options coverage](https://www.barchart.com/solutions/services/futures-options) reaches the early 2000s with exchange variation, not verified 1990 CRB parity. [EDI/CRB](https://www.exchange-data.com/edi-and-the-commodities-research-bureau-team-up-to-deliver-the-best-quality-commodity-pricing-data/) describes licensed products, not free unrestricted access.
- [CME settlement-access FAQ](https://www.cmegroup.com/articles/faqs/access-to-cme-group-settlement-data-faq.html) distinguishes publication from free midnight-Central availability. Same-settlement signal/fill cannot be assumed. Historical receipt clocks and lawful use require separate verification.
- Current broad commodity daily panels are unadmitted and do not include the required options surfaces.

**First gate:** authenticate a current source and reconcile one complete historical options chain to signal, rank and next executable futures price. Keep below simpler curve-data leads until costs and modern validation exist.

## Source-gated reserve: ENSO soft-commodity prediction
[SSRN 6789516](https://ssrn.com/abstract=6789516), 2026. Indexed primary abstract only: five soft commodities, January 2000–January 2026, climate/price features and expanding models. Claimed ENSO increment is approximately .10 Sharpe over price-only; climate-only power is negligible. Exact signal, costs, holding horizon and claimed frozen holdout could not be authenticated in full text.

**Assessment:** not a standalone climate edge or verified intraday rule. Different instruments from entry 36, shared climate-vintage gate. [NOAA PSL Niño 3.4](https://psl.noaa.gov/data/timeseries/month/Nino34_CPC/) is not automatically ONI. [CPC monthly index documentation](https://cpc.ncep.noaa.gov/data/indices/Readme.index.shtml) and [ONI revision policy](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_change.shtml) require identifying the actual series and historical releases, not applying a generic one-month lag. [RONI's February 2026 introduction](https://www.weather.gov/media/notification/pdf_2026/pns26-05_Relative_ONI.pdf) must not silently change a later extension. Unnumbered.

## Source-gated reserve: agricultural news embeddings
[SSRN 7298998](https://ssrn.com/abstract=7298998), 2026. Indexed primary abstract only: full-story embeddings for fourteen contracts, daily 2009–2023, two-stage ridge comparisons. The headline Sharpe near 2.5 is not verified as net. The abstract says sub-daily versions underperform. Full methods, article clocks, executable fills, costs, encoder selection and holdout remain unavailable.

**Assessment:** daily personal alternative-data reserve, not an intraday nomination. FinBERT's model vintage requires auditing independently of regression chronology. [NIST's Reuters TRC2 documentation](https://trec.nist.gov/data/reuters/reuters.html) gives January 2008–February 2009 corpus dates, narrower than commonly repeated descriptions. This flags possible early-sample overlap, not blanket contamination of all later years. Verify exact checkpoint, base-model snapshots and a truly post-checkpoint holdout. [ProsusAI's model card](https://huggingface.co/ProsusAI/finbert) licenses weights noncommercially; code, model and news rights are separate. DATA_NEEDED D17's existing news-vintage gaps are related but not the same strategy. The related thesis is embargoed; no restricted access attempted. Unnumbered.
