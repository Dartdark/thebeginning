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
