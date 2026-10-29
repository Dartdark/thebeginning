# Irish equity momentum: DON'T TEST for our plans
Summary: The paper tests monthly winner-minus-loser stock portfolios and finds little evidence of abnormal returns.
Table 2's full sample is February 1988–December 2006; none of its configurations has a bootstrap p-value below 0.10.
Weak growth-subperiod findings do not establish a live regime rule or profitability after implementation costs.
Useful lessons concern survivorship, concentration and inference; no new strategy or queue addition is justified.

Source: Fionnghuala O’ Sullivan and Niall O’ Sullivan, *The Profitability of Momentum Trading Strategies in the Irish Equity Market*,
[SSRN 2269045](https://ssrn.com/abstract=2269045), user-uploaded PDF.
SHA256: `907ad107078537619499322b67e486c6ca483d5bc6d314b1b767d3a1a153e083`.
Review date: 2026-10-29. Findings attributed to the source, not independently reproduced.
New return trials: **0**. No backtest plan/script applicable to this source-only review.
Repo context: codex/work `a2cdd722a7545f3967f3bef94be89b4024b4a13a`.

## 1. What is it about?

Cross-sectional momentum in Irish stocks: each month rank the available stocks on past returns, buy winners and
short losers. Ranking periods are 3, 6 or 11 months; holding periods are 1, 3 or 6 months. Portfolio breadth is
top/bottom 30%, top/bottom 10%, or five stocks on each side. Performance is monthly CAPM alpha using the ISEQ
market index and a one-month interbank risk-free proxy. This is not intraday breakout or single-index trend following.

Section 3 says the dataset includes dead/delisted stocks and historical availability. This is a useful attempt
to address survivorship. Rebalancing among remaining stocks when a name disappears still needs a careful
delisting-return and executable-liquidation audit in any replication.

## 2. What does it find?

| Source result | Interpretation |
|---|---|
| Table 2, full sample February 1988–December 2006: no significant positive alpha; bootstrap p-values all exceed 0.10. | No robust positive abnormal performance established across the displayed ranking/holding/breadth choices. |
| Broad 30% portfolio, 3-month rank / 3-month hold: monthly alpha 0.349%, t=1.051, bootstrap p=0.180. | Positive point estimate is not convincing evidence of an edge. |
| Broad 30% portfolio, 11-month rank / 3-month hold in the growth subperiod: alpha 0.546%, bootstrap p=0.060. | A weak subperiod finding, not a validated net strategy or a current entry rule. |
| Concentrated portfolios generally fare worse; returns/residuals are often strongly non-normal. | Extreme winners and losers may add noise rather than improve this particular implementation. This is not a universal concentration rule. |

The abstract/conclusion describe 1988–2007, but the methods and Table 2 specify February 1988–December 2006.
The growth-period dates also conflict: the text says September 1995, while Table 3's note says February 1995.
A reproduction must resolve the dates rather than silently choose the favorable one.

The paper uses Newey–West-adjusted statistics and 1,000 residual-bootstrap draws under zero alpha.
It does not establish a separate untouched validation period or a live-detectable growth-regime rule.
The many settings and subperiod looks weaken an isolated 10%-level result; no family-wide correction is reported here.
Non-normal returns do not automatically invalidate every t-test. Its independently resampled residuals also should
not be assumed to preserve serial dependence merely because the re-estimated statistic uses a HAC standard error.
Our existing block-bootstrap and multiple-testing controls remain necessary.

## 3. Why does it make money, if it does?

This paper does **not** establish reliable abnormal profit in its full sample.
The literature it reviews offers delayed information incorporation, behavioral underreaction/overreaction and
risk compensation as possible momentum explanations. These are hypotheses or findings from other studies;
the Irish tests do not establish a persistent mechanism we can exploit.

Long winners / short losers is not free to implement: short-sale proceeds do not remove margin, financing,
stock borrow, spreads, turnover or liquidation costs. The displayed alpha is not a fully audited after-cost
trading return, nor is it automatically skill relative to all relevant risk factors.
No scheduled forced participant or known directional flow is identified.

## 4. Can we build on it?

**As a research-method reference, yes; as the foundation for our next trading strategy, no.**

Retain three lessons: use the historical universe rather than today's survivors; examine sensitivity to portfolio
concentration and lookback/holding horizons; and test uncertainty/dependence rather than treating a good-looking
average or Gaussian approximation as sufficient. Most of this is already in our process.

Direct replication would need historical Irish stock total returns, listing/delisting history, exact portfolio
construction, the ISEQ benchmark, rates and implementation/borrow costs. Existing NQ/ES minute data cannot supply
those inputs. No current licence or data availability audit was performed. Monthly multi-stock holds do not fit
the current Apex intraday plans. A personal account permits longer holds, but that does not rescue a weak edge.

TIER_LIST already includes the different SSRN 3018366 cross-sectional momentum review and its failed daily
cross-asset futures adaptation (`analysis/xsec_momentum_test.py`). This paper does not directly refute all momentum,
including our distinct NQ/ES relative-strength strategy, and does not justify retesting the rejected futures branch.
A new market/timeframe is a new hypothesis requiring its own evidence, not a replication of these results.

## Decision and record

**DON'T TEST** for current plans. No strategy queue entry: useful methodological lessons do not establish
promising executable returns. No returns, account simulations, code or live changes were run.
No claim about payout improvement, correlations, Sharpe or current-market profitability is made.

For Claude: `agents/codex/results/irish_momentum_paper_review_20261029.md`.
