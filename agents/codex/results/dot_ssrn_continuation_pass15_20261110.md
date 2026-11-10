# dot: defensive portfolio methods and rebalancing comparators
Author: dot. 2026-11-10. Source research only; no portfolio tests.

## 54. The Best Defensive Strategies: Two Centuries of Evidence
**Personal defensive-portfolio method; monthly/overnight; not current-data ready or an intraday candidate.**

[SSRN 5815464](https://ssrn.com/abstract=5815464), [published FAJ paper, January 2026](https://www.tandfonline.com/doi/pdf/10.1080/0015198X.2025.2602270). Full indexed text, tables and appendices inspected; direct PDF/screenshot access failed, so visual verification is unavailable.

### Compact source specification
DAR4020 monthly ranks available factors by trailing 60-month correlation to global 60/40, buying lowest-correlation 40% and shorting highest 20%. Full universe is 25 factors across equity indices, bonds, FX, commodities and US stocks. Factor risk uses trailing ten-year volatility. Trend combines four asset-class sleeves driven by trailing 12-minus-1-month returns. Retrospectively normalized to 5% volatility, 1800–2021 gross DAR/trend IRs are .46/.97; 1985–2021 .28/.76. No transaction costs deducted. DAR and trend tend to protect different drawdown stages. The paper compares several long/short selection fractions before choosing 40/20. Historical “OOS” largely extends backward, not beyond publication.

### Independent implementation assessment
- This is a factor-portfolio hedge, not buying 40% bonds and 20% stocks. At full coverage the fractions select ten long and five short factors.
- Trailing factor risk estimation differs from the subsequent full/subsample realized-volatility normalization. The latter is retrospective and cannot be copied into causal sizing.
- Table 7 retains the funded 60/40 portfolio and adds derivative exposures. Overlay weights are not capital allocations that must sum to 100%. Reconstruct gross notional, financing, collateral and margin.
- The benchmark's crisis windows are not the hedge's own maximum drawdown. Optimizing away old 60/40 drawdowns can introduce new portfolio drawdowns outside those windows. Measure the entire combined wealth path.
- Monthly observations cannot demonstrate intraday trailing-loss-limit survival. The user's strategy portfolio is not a global 60/40 benchmark; historical correlation to one says little about the other.
- Early histories splice indices and synthetic pre-futures exposures, under changing market access and capital controls. They provide historical regime comparisons, not 222 years of executable derivative performance.
- Exact factor definitions and source series remain necessary. Resolve expanding-universe rounding, ties, warm-up, lagged fills and book-to-market versus dividend-yield descriptions before reconstruction.
- No exact DAR4020/5815464 entry found in TIER_LIST or DATA_NEEDED. Trend is already known: the repository's six-market personal-account adaptation records net Sharpe .46 and −17% drawdown. Preserve that result rather than implying the new paper replaces it.
- Existing exports do not supply all 25 factor holdings, licensed histories, costs or cashflows. Public article access does not grant rights to proprietary underlying data.

**Priority:** useful portfolio-design reference below simpler executable data-gated leads. First reconcile an actual monthly factor ranking and cash ledger, then define causal sizing and all-in costs. Any future validation must use untouched modern data and the user's actual combined portfolio. No such validation occurred here.

## Unnumbered comparator: stock–bond fund rebalancing
[SSRN 5122748](https://ssrn.com/abstract=5122748). Inspected [March 2025 primary paper](https://d1e00ek4ebabms.cloudfront.net/production/uploaded-files/w33554-c27954c3-8c17-44f5-a26f-1800436b6ebf.pdf), 62 pages; January 2026's 76-page revision remains unavailable.

Source summary: daily ES/10-year Treasury opposing-return portfolio, September 1997–March 2023. Prior-day information tracks simulated 60/40 weight drift across 0–2.5% reset thresholds, averaged with a monthly calendar signal. Final-five-business-day calendar exposure fades drift; first-business-day treatment differs. Full-sample calibration yields reported 9.92% annual excess return, Sharpe 1.08. Costs are discussed by reference rather than a complete ledger. Overnight holding and historical calibration are integral.

**Assessment:** same economic mechanism as the repository's already-tested pension/balanced-fund month-end RTH fade, which recorded ES Sharpe .40/t1.2 and negative quarter-end results. The daily two-leg source is not that proxy, but does not erase it or reopen trials. Resolve calendar indexing, reset/available-at sequence, dated contracts, notional versus contract/DV01 weights, turnover and collateral. No current-data admission or survival evidence.

[Jonathan Parker's January 2026 discussion](https://mitsloan-php.s3.amazonaws.com/wp-faculty/sites/72/2026/01/16194205/Parker-Discussion-Rebalancing-AFA-2026.pdf) and [Kent Daniel's September 2025 discussion](https://www.kentdaniel.net/discuss/2025/HMM.pdf) flag parameter selection, indirect flow identification and aggregate-cost extrapolation. Their comments are methodological scrutiny, not failed exact replications. Parker's .90 Sharpe summary does not establish which source revision changed what.

[Finance Paper Mill's September 2026 public summary](https://financepapermill.com/research/stockbond-portfolio-rebalancing) reports gross Sharpe .38 on an ES/ZN reconstruction through April 2026, largely predating publication. Full net and separate postpublication tables are inaccessible. Treat as qualified practitioner counterevidence, not independently verified exact replication.

## Existing D07 and curve-timing reserves
- **Goldman roll, SSRN 1716841:** [Mou's primary dissertation, Part I](https://www.wertpapier-forum.de/applications/core/interface/file/attachment.php?id=67585) describes phased short roll-from/long roll-into positions in 19 commodities, unwound over index roll days. No bid/ask costs included. Active-day annualization produces a higher headline than calendar-time Sharpe. Already D07; failed CL outright proxies are not calendar-spread replications. Native maturity pairs and historical index calendars remain gates.
- **Liquidity timing, SSRN 2682698:** [December 2014 predecessor](https://www.scribd.com/document/265723306/Trend-Following-Strategies-in-Commodity-Markets-and-the-Impact-of-Financialization) uses nearby/next-out log basis versus its 50-day average to trade nearby against roughly one-year deferred contracts, with a full-day execution lag. [2016 revision abstract](https://ssrn.com/abstract=2682698) reports much weaker pre-2005 than later evidence. Do not combine predecessor rules with revised results without full-version verification. Related curve family, not a fresh qualified allocation.
