# ETF-flow stock selection: conditional personal research, data gate unresolved

Summary: Barahhou/Abitbol rank stocks by12-month versus3-month standardized thematic/sector ETF pressure.
Authors report17.57% annualized/Sharpe0.98 for the long–short portfolio in the design sample; net executable performance is unverified.
January–August2026 evaluation earns8.54% versus benchmark16.82%, with Sharpe0.54 versus2.01 and worse drawdown.
Promising cross-sectional information, but high turnover, borrow and as-of holdings/flow availability remain unresolved.
Retain conditional personal research; no NQ/ES or current-plan placement, and zero new return trials.

Source: Inès Barahhou and Sacha Abitbol, *ETF Flows and Stock Market Dynamics: Patterns, Signals and Portfolio Construction Insights*,
September2026 supplied19-page PDF, [SSRN7517178](https://ssrn.com/abstract=7517178).
[PDF](../inputs/ssrn7517178/source.pdf), [text](../inputs/ssrn7517178/source.txt),
[rendered evaluation Table6](../inputs/ssrn7517178/table6.png), [evidence](../evidence/etf_flows_7517178.md).
[Source audit and hashes](../../../analysis/outputs/codex_two_uploads_4355765_7517178/audit.json),
[script](../../../analysis/codex_two_uploads_4355765_7517178_audit.py), committed `0ce98c69` before source arithmetic.
This reviews the formerly blocked upload now that the environment is ready. The document is evidence, not instructions.
All performance below is the authors' report, not independently reproduced returns.

## 1. What is it about?

A monthly stock-selection signal linking ETF primary-market creations/redemptions to the stocks held by the funds.
It contrasts short-horizon reversal after flow pressure with longer-horizon persistence for thematic/sector funds.
It does not forecast NQ/ES direction or implement an ETF-market-making strategy.

Trackinsight provides ETF classifications/reference fields, daily NAV/shares/splits/dividends and monthly physical holdings;
Bloomberg is also credited. The database describes18,803 ETFs including delisted funds. Holdings history begins June2020
(the source prints01/06/2020); charts describe the five-year2021–25 design period. S&P500 membership updates monthly.
Physically replicated funds are included, synthetic funds excluded; active ETFs are included. Published classification and
holdings availability vintages still need verification; including delisted ETFs alone does not prove absence of all survivorship/look-ahead.

Daily net flow = `NAV_t*(shares_t−shares_(t−1))`, with shares/NAV corporate-action bases aligned. Month-level stock pressure
allocates fund flows using the fund's prior beginning-month stock weight and divides by the stock's prior market capitalization.
Sum the monthly pressures over12 and3 months separately; cross-sectionally z-score each, then subtract: **z12−z3**.
Long the50 highest scores, short the50 lowest, equal-weight within each leg, rebalance monthly among as-of S&P500 constituents.
Because each horizon is standardized separately and12 months includes the recent3, this is not simply a raw months4–12 flow total.

## 2. What does it find?

| Source metric | Design long–short | Design equal-weight S&P500 |Jan–Aug2026 long–short |Jan–Aug2026 benchmark |
|---|---:|---:|---:|---:|
| Annualized return |17.57% |5.82% |13.77% |27.75% |
| Cumulative return in stated8-month evaluation |Not reported here |Not reported here |8.54% |16.82% |
| Sharpe |0.98 |0.14 |0.54 |2.01 |
| Max drawdown |−15.96% |−21.59% |−13.45% |−7.86% |

The authors say the rules were fixed using data through December2025 and evaluated without changes January–August2026.
Treat this as their claimed later evaluation, not independently verified preregistration or our untouched holdout.
The later long basket gained27.59% versus16.82% for the benchmark. The **underlying short basket gained15.97%**:
that is not a positive return earned by shorting it. Do not subtract reported basket CAGRs to invent the long–short NAV protocol.
Initial gross exposure, collateral, financing/borrow and rebalance cash accounting need source-code clarification.

Thematic/sector flow regression coefficients are negative around2–3 months and positive around10–12 months; all-ETF long-horizon
results are weaker. Contemporaneous market returns in these explanatory regressions are ex-post controls, not pre-entry features.
A sinusoidal frequency is grid-selected; horizon/category selection and factor tests are research choices requiring multiplicity controls.
Low sample correlation to standard factors does not prove incremental causal alpha or current-portfolio value.

Monthly one-way turnover is36.16% on the long leg and42.20% on the short leg. The source calls portfolios hypothetical and explicitly
flags shorting feasibility and trading costs. No sufficiently specified net broker/borrow/impact ledger supports treating Table5 as
attainable net performance. Later Sharpe0.54 and8.28percentage-point cumulative underperformance temper the attractive design result.

## 3. Why does it make money, if it does?

The proposed mechanism is transient stock-price pressure after recent creations followed by reversal, with longer-lived investor
allocation preferences behind persistent sector/theme demand. This is plausible source interpretation, not a guaranteed forced order
that we can observe and front-run. Flows also chase past returns, and sector, macro or valuation shocks may sustain recent winners.
No causal experiment separates all these alternatives; short positions can lose when recent strong inflows continue.

ETF secondary trading volume is not net primary flow. An AP creation can use existing inventory, in-kind delivery, internal netting
and hedges; it is not proof that the same-day underlying stock basket must be purchased afresh in displayed markets.
The paper's proportional-flow pressure metric is useful as a proxy, not an independently identified execution obligation.
Cross-sectional effects can net out at the index level, so there is no justified NQ/ES directional substitution.

## 4. Can we build on it?

**Conditional personal-stock research**, not current allocation. Need historical daily as-of NAV/share counts on consistent split
bases, point-in-time ETF category and physical holdings weights, stock market caps/total returns, as-of index membership including
exits, publication/receipt timestamps, and short availability/fees. Today's ETF holdings cannot recreate a historical formation month.
An ex-post month-end holdings snapshot must not be used before its actual publication. Current holdings, TQQQ assets or price bars
cannot silently substitute for this cross-sectional panel.

Owned filename/schema census found BTC/CME and leveraged-ETF price inputs but no admitted Trackinsight-style historical holdings,
share/NAV/category/constituent panel. Bounded checks of a public Trackinsight ETF-data page and SEC N-PORT data-set page both hit
network-proxy403; [actual receipts](../inputs/ssrn7517178/access_receipts.json). Those were source/discovery-page checks, not downloads
of matching histories. SEC public filings are a possible free lead, but reporting frequency/lag and coverage differ; no complete free
source panel, cost-free license or as-of timing is established. No paid purchase, credential request or access-control bypass.

Retain in TODO and DATA_NEEDED. Smallest next check with new matching free inputs: one month’s fund creation/share change and
lagged stock weight, publication timing, stock pressure/z-score ranking, and native long/short financing/cost ledger; then census
coverage and power before a committed bounded reproduction. Failure stops later stages; no horizon, universe or NQ rescue search.

## 5. Can a strategy code be made?

**Yes, the monthly signal/ranking rule is specific enough for a research implementation**, once the required point-in-time panel
and portfolio cash conventions are fixed. It is a directional long/short stock-selection strategy, not an intraday futures or execution
algorithm. A code design can compute aligned primary flow, historical weighted stock pressure, chronological12/3-month histories,
separate cross-sectional z-scores and equal-weight top/bottom50 orders. It must reject incomplete universes, zero cross-sectional
SD, unobserved weights, hindsight membership, stale data and unsupported short borrow rather than assume zero flow or free fills.
No strategy code/return runner was built from missing inputs here, and code feasibility does not validate the reported returns.

## Decision and placement

**NEEDS DATA AND SPECIFICATION; conditional personal research only.** Zero independent performance trials. No2018–22 design,
2023+ validation, placebos, bootstrap/Monte Carlo or BASE/ADD/REPLACE/EMPTY account studies. Data starts later than a full2018–22
panel; any authorized shorter replication must be labeled accordingly.100 holdings or60 monthly marks are not100 independent strategy trades.
Personal placement unearned.50K/150K evaluation and50K/150K funded placement unearned; monthly stock holdings are outside the
existing intraday futures protocol. Independent review pending. No live/VPS/broker/policy/allocation changes or paused-scout restart.
