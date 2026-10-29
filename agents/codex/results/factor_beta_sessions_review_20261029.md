# Factor beta by night and day: WATCH / NEEDS DATA for stock-basket replication
Summary: Ye, Jiang and Luo find opposite overnight/intraday factor-beta premiums in Chinese and U.S. stocks.
U.S. market-beta slopes are +5.198 bp overnight and −8.892 bp intraday per unit beta, not net strategy returns.
Lagged betas and cross-market checks justify a data/cost audit; no direct ES/NQ trading rule follows.
Queue the U.S. stock-basket idea for later verification; retain factor/session attribution in the execution library.

Source: Zhengke Ye, Danling Jiang and Yunfeng Luo, *Factor Beta, Overnight and Intraday Expected Returns in China*,
March 15, 2023, Global Finance Journal forthcoming in uploaded version;
[SSRN 4138715](https://ssrn.com/abstract=4138715).
SHA256: `5db6c00d5193ea11c2de312f1093a84b4ea4f4fd406450843524eda89084d3c0`.
Review: 2026-10-29. Source findings not independently reproduced. New return trials: **0**.
Context: codex/work `007af30d8601e3e2a51367fcfe04c6d383467441`. [Evidence sheet](../evidence/factor_beta_sessions_20261029.md).

## 1. What is it about?

Whether stocks with different estimated exposures to market, size, value, profitability and investment factors
earn different returns overnight versus intraday. Main sample: Shanghai/Shenzhen A shares, excluding ST stocks,
1994–2020. Additional samples: B shares and U.S. common stocks, the latter 1993–2020.

Betas are estimated from the prior twelve months of daily returns as of the previous month, requiring at least
fifty observations. The authors study next-month returns with portfolio sorts and daily Fama–MacBeth regressions.
This is cross-sectional stock selection, not a forecast that the entire index rises tomorrow.

## 2. What does it find?

Table 2, China: market, value and profitability beta premiums are positive overnight and negative intraday;
size and investment have the opposite signs in the joint regression. Some individual coefficients are weak,
so the summary must not imply every estimate passes every significance threshold.

Table 8 Panel B, U.S., 1993–2020; coefficients below are bp per session per one-unit beta change,
conditional on the other betas:

| Factor exposure | Overnight slope (t) | Intraday slope (t) |
|---|---:|---:|
| Market | +5.198 (10.24) | −8.892 (−10.92) |
| Size | +3.025 (12.37) | −2.157 (−4.89) |
| Value | −0.999 (−3.19) | +1.407 (2.65) |
| Profitability | −4.345 (−16.39) | +3.879 (7.79) |
| Investment | −1.265 (−7.06) | +1.790 (5.54) |

These are regression prices of exposures, not returns of five fully funded implementable strategies.
One-unit beta changes also differ materially from typical one-standard-deviation changes.
Do not annualize the market slope into a promised 13% return or assume a feasible portfolio has unit exposure
with all other risks and costs zero.

Some factor signs reverse between countries, especially size, value and profitability.
Differentials generally weaken for stocks associated with more sophisticated investors (ownership, price,
analyst coverage proxies). Alternative windows, samples and factor models provide robustness evidence.
The authors' cross-market “out-of-sample” tests are not a new post-publication forward record.

## 3. Why does it make money, if it does?

Proposed mechanism: different marginal investor groups dominate the open and close, creating and partly correcting
cross-sectional mispricing. Chinese market design, T+1 restrictions and auction participation differ from U.S.
conditions; the proposed clienteles can therefore imply different factor/session signs.

This is more developed evidence than treating an overnight/intraday chart as proof of manipulation.
Nevertheless, investor sophistication proxies and country contrasts do not uniquely identify a causal trading flow.
No mandatory participant, known order deadline or net index demand is established.
An exposure premium may also reflect risk or microstructure and need not survive implementation.

The paper reports gross portfolio-sort spreads as well as regressions, but does not provide a complete
native-cost, borrow-, financing- and auction-fill-aware account ledger. Short availability, T+1, suspensions,
price limits and costs can prevent realization of statistical spreads.

## 4. Can we build on it?

**Yes, for a later stock-basket replication/data audit; not as a ready NQ/ES strategy.**
The U.S. conditional market-beta pattern provides a specific starting candidate: prior-month beta-sorted
high-minus-low baskets measured separately overnight and intraday. The other factor findings remain the study
reference; no winning combination or threshold is selected here.

Do not replace these baskets with NQ long/ES short and call it a replication. Two equity futures cannot isolate
the paper's stock-specific five-factor exposures. Our NQ/ES Relative Strength rule and prior cross-asset momentum
tests are distinct hypotheses, not validations or exact rejections of this stock-basket result.
No exact source match was identified in the inspected TIER_LIST, WATCHLIST and TODO.

The smallest justified next step is no-return feasibility: verify point-in-time stock universe/returns,
factor series and estimation clocks, corporate actions, auction executions, borrow and actual fees.
Then count effective design sessions and compare plausible attainable exposure spreads with all-in costs.
If those prerequisites pass, a separate evidence update and committed, bounded replication plan must precede returns.
No data purchase, research cache or return screen starts from this review.

Important reproduction cautions:
- The paper defines RET as dividend-reinvested close-to-close, RID as price open-to-close and imputes RON.
  Preserve its exact compounding/adjustment formula and separately build executable cash P&L.
- Figure 3 estimates post-ranking portfolio betas with full-sample returns for visualization. Those fitted
  full-sample exposures cannot become trading-time features. The prior-month ranking beta clock is distinct.
- All factor construction and accounting inputs need point-in-time availability and fold-local estimation.
  Cross-market/schema differences, fifty-observation minimum and suspension/delisting handling need explicit audit.
- Opening/closing marks do not guarantee auction fills; baskets require enough capital and feasible integer shares.
  Ordinary overnight stock holds do not fit our current Apex intraday protocols.

## Decision and retention

**WATCH / NEEDS DATA**, later U.S. stock-basket research only. Record it in TODO's verification queue, clearly
outside a current plan allocation. Source merit: lagged exposures, significant conditional estimates and
cross-market evidence; missing: feasible net replication and portfolio contribution.
No promotion, new backtests, strategy code, live changes or claimed account savings.
Execution library E14 updated with factor-aware session attribution and ranking-versus-full-sample clock cautions.

For Claude: `agents/codex/results/factor_beta_sessions_review_20261029.md`.
