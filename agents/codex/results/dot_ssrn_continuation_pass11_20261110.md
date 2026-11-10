# dot: SSRN continuation, pass 11
Author: dot. 2026-11-10. Fixed-income research, not an implementation authorization. No tests or portfolio changes.

## 49. Yield Curve Momentum
**Sihvonen, SSRN [3965229](https://ssrn.com/abstract=3965229).** Published [Review of Finance, 2024](https://doi.org/10.1093/rof/rfae003). Reviewed the [author-linked December 2022 draft](https://www.dropbox.com/scl/fi/urn8dscco1o8kdh5nx9w2/YieldCurveMomemtumDec22.pdf?rlkey=e1jclpexczeg18ry3xnoienbe&dl=0), not the inaccessible final article. [Author source page](https://sites.google.com/site/mesihvonen/research).

August 1971–December 2019 reconstructed Liu–Wu zero-coupon Treasury yields, mainly maturities 1–10 years. Monthly excess return is log bond-price change minus one-month bill yield; maturity resets monthly. Buy next month when the preceding month's excess return is positive, otherwise bills. Equal-weight maturity strategy Sharpe 0.50 versus buy-and-hold 0.36; Bloomberg Treasury index implementation 0.55 versus 0.44. A separate forecast test trains for 15 years; Clark–West significance is stronger at 1–7 years, weaker at eight, absent at nine/ten. One-month lookback was selected after examining other horizons. Draft does not establish itemized net futures costs; cross-maturity momentum Sharpe is only 0.087.

**Assessment:** Directional duration timing, primarily yield-level changes, not a duration-neutral curve spread. Forecast holdout evidence is meaningful but not untouched postpublication trading validation. The [2024 author explanation](https://cepr.org/voxeu/columns/yield-curve-momentum-implications-theory-and-practice) claims survival under professional costs and futures implementation, without enough details to attach draft Sharpe to a net ZN rule.

**Tags/build gate:** Personal monthly; no intraday fit. Existing ZN prices are an adaptation, not verified reconstructed-bond or futures replication. Require final cost/contract specification, duration and CTD mapping, signal/fill timestamps, roll/financing and modern holdout. More specific than broad trend, but not a fresh proven independent signal family.

## 50. Yield Curve Premia
**Brooks and Moskowitz, SSRN [2956411](https://ssrn.com/abstract=2956411).** SSRN record dates July 2017; reviewed the [June 2019 Yale-hosted full paper](https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/3/2021/08/Yield-Curve-Premia.pdf), including appendix. Versions must not be silently equated.

JPM government-bond portfolios span 13 countries and 1–5, 5–10, 10–30-year buckets, with USD-hedged returns. Level uses equal-duration exposure; slope is duration-neutral long-long-maturity/short-short-maturity; butterfly buys middle against wings with zero duration/minimal slope. Signals are real yield versus expected inflation, past-year return and yield minus local three-month rate. Cross-country ranks are demeaned/standardized, sides scaled to $1 and duration seven; composite volatility weights are in-sample. Multi-style slope/butterfly Sharpes are 0.73/1.16 versus momentum-only 0.26/0.04, gross of costs. “Live/OOS” is retrospective tradable-bond data, not live management. Main carry omits rolldown. Body sample March 1995–April 2016 conflicts with captions March 1986–March 2016; slope and butterfly momentum exclusion months also differ.

**Assessment:** Genuine curve-relative-value foundation, more distinct than directional ZN timing. Still dependent on broad bond portfolios, leverage, shorting, FX hedging and cost assumptions. Extra macro lag does not prove real-time vintages. In-sample risk scaling and full-sample PC comparator weights limit the interpretation of the reported Sharpe comparison. Resolve sample and formula inconsistencies before coding.

**Tags/build gate:** Personal monthly; no intraday or exact current-data qualification. Public yields or one ZN export do not provide executable multi-maturity holdings and historical duration/CTD ledgers. Potential diversification is a hypothesis, not demonstrated improvement to this user's book.

## Repository reconciliation
Neither exact title/ID appeared in the inspected codex/work TIER_LIST, MINED_INDEX or prior research index. They deepen existing Value/Momentum/Carry foundations rather than provide wholly new families. Preserve prior failed ZN release, auction, pit-open, month-end and cross-asset screens; these papers neither test nor rehabilitate them. No old experiment was reopened.

## Decision
Retain both as conditional Personal references. Curve-relative-value research requires more infrastructure than the simple one-month duration rule, while the latter has more obvious overlap with existing trend. Neither should be described as immediately buildable from current files.
