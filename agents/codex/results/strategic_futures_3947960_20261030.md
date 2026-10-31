# Strategic Trading, Welfare and Prices with Futures Contracts: theory reference; DON'T TEST

Summary: Dastarac models strategic spot/futures trading under imperfect competition and symmetric information.
Large traders delay trades to limit impact; introducing futures changes incentives and raises their exposure to settlement-price risk.
Their opposing attempts to move settlement prices cancel in equilibrium, while modeled trader welfare falls.
The paper derives a spot/futures basis but neither models an outside arbitrageur nor tests executable net returns.
Retain the execution and basis-accounting lessons; no source-supported portfolio strategy or return trial is earned.

Source: **Hugues Dastarac**, *Strategic Trading, Welfare and Prices with Futures Contracts*, Banque de France
Working Paper **841**, October **2021**, supplied `ssrn-3947960.pdf`, **82 PDF pages**.
[Archived PDF](../inputs/strategic_futures_3947960_20261030/source.pdf) ·
[extracted text](../inputs/strategic_futures_3947960_20261030/extracted_text.txt) ·
[source receipt](../inputs/strategic_futures_3947960_20261030/manifest.json) ·
[evidence gate](../evidence/strategic_futures_3947960_20261030.md).
PDF SHA256: `69bbc140342f6203db6975cdfbc4a42fbed462a6a41da8e088ae3095de8e49ce`.
Page references below use printed Arabic page numbers; add two for PDF page numbers.
This is a review of the uploaded October 2021 version, not a claim about later revisions or publication status.

## 1. What is it about?

Why are futures traded when investors can already buy/sell their underlying assets, and how does strategic trading
change prices and welfare? The model has three dates: investors trade spot and futures at date 0; a liquidity shock
and new information arrive at date 1, when spot is traded and futures settle; the risky asset pays at date 2.
Futures pay `p1-f0`, not the asset's terminal fundamental payoff (Section 2, printed pp. 7–10).

Large buyers and sellers have different initial inventories but identical CARA risk preferences. Information and
initial inventories are public; participants account for their own impact on equilibrium prices. Without futures,
they spread transactions across dates to limit price impact, accepting exposure to future prices.

This differs from the previously reviewed [Muermann–Shore paper](spot_market_power_681202_20261030.md):
that paper relies on physical spot-market power and concealed participant positions in its strategic model.
Dastarac instead studies strategic buyers and sellers on both sides with symmetric information, without requiring
a physical monopolist or exogenous exclusion from either market. Their equilibrium outcomes must not be conflated.

## 2. What does it find?

All results below are analytical claims of the supplied model, not independent return replications.

| Source | Result | Boundary |
|---|---|---|
| Sections 3–4, pp. 10–19 | Large traders delay otherwise beneficial spot trades to limit impact; residual inventories create scope for sharing the future trading-price risk. | An endogenous trading delay, not evidence that delaying our signals improves execution. |
| Proposition 4, pp. 22–23 | Introducing futures leaves equilibrium spot prices unchanged: opposing strategic effects cancel. | Relies on the model's symmetric risk preferences and market clearing. Individual incentives need not imply an aggregate price move. |
| Propositions 5–7, pp. 23–25 | Spot sellers buy futures from spot buyers; the defined hedge ratio is negative. Spot trading accelerates; futures trading decreases with greater price uncertainty. | The hedge ratio is relative to expected date-1 trade net of the customer shock, not a universal rule for hedging current inventory. |
| Section 6, Theorem 1, pp. 25–28 | Greater exposure to settlement-price risk outweighs the benefit of faster spot trading, reducing modeled large traders' certainty-equivalent welfare. | Section 6 sets expected customer flow to zero. Interpret within the equilibrium existence regime; welfare is not a measured trading-return loss. Unmodeled liquidity customers' execution price/welfare proxy is unchanged. |
| Section 7, pp. 28–30 | A nonzero expected future supply shock can create positive or negative spot/futures basis despite zero interest/storage costs and no exogenous market segmentation. | Outside arbitrageurs and their equilibrium impact are explicitly left to future research; displayed basis is not a verified executable opportunity. |
| Appendix C, pp. 66–68, Theorem 2 | A theoretical contract whose payoff cannot be influenced raises welfare, with positive hedging demand and slower spot trading. | An explicit counterfactual exception to the claim that introducing futures reduces welfare. It is not an available exchange product specification. |

The paper reports **no strategy backtest, Sharpe, Sortino, profit factor, Calmar, Ulcer index, net-cost trading P&L,
out-of-sample strategy validation, or account payout comparison**. Introductory Treasury open-interest statistics
motivate the question; they are not a tested return sample or evidence of a currently capturable premium.

## 3. Why could it make money, if it does?

It does not demonstrate a profitable strategy for an outside trader. The modeled agents trade to improve the utility
of portfolios that include pre-existing inventory and future transactions. Once futures are available, each also
tries to change its settlement payoff through spot trades. Other large traders respond, preventing the intended
net price change while leaving participants with more risk than in the no-futures benchmark.
Thus an individually rational trade can be collectively costly. Neither a positive expected payoff on one leg nor
a motive to buy/sell establishes a net return or price pressure available to us.

The paper does discuss an apparent basis-arbitrage trade (Section 7): selling the expensive side and buying the
cheap side would lock in the displayed spread at the stated prices. But it also explains that counterparties may
not accept those trades at those prices and that a full model with arbitrageurs is missing (p. 30).
One cannot retain the displayed price schedule while inserting an outsider's unlimited execution and call the
result an implemented arbitrage.

The basis result uses the expectation `E0[Q]`, information at date 0, not the subsequently realized customer shock.
Substituting realized future order flow would introduce look-ahead. Likewise, measuring a basis is not estimating
an independent source of expected flow.

## 4. Can we build on it?

**Use it as an execution/market-structure reference; do not start a new strategy backtest.**

Useful lessons are: transaction slicing trades price impact against future-price exposure; derivative positions can
alter later spot execution incentives; individually motivated demand need not survive aggregation; and a welfare
comparison or raw basis is different from a tradable after-cost return. These fit the execution-reference library.

The model normalizes the interest rate and storage costs to zero, ignores margin constraints (p. 8), uses Gaussian
shocks and linear demand-schedule equilibria, and takes trader inventories and risk preferences as model inputs.
The main futures-equilibrium construction assumes sufficient liquidity-shock uncertainty relative to information
uncertainty for its concavity/existence argument (pp. 21–23). Footnote 22 explicitly leaves low-uncertainty existence
open: it is not evidence of actual infinite-profit trading or a proven absence of all equilibria.

Owned data include NQ/ES and commodity continuous futures bars, ZN futures, COT archives and some order-flow data.
Those do not supply the modeled participants' inventory paths, risk preferences, pretrade expectations of customer
flow, or their joint spot/futures price-impact schedules. Nor does the inventory establish matched executable cash
assets, futures, financing/borrow quotes, and settlement/delivery accounting for a native basis strategy.
For Treasury research in particular, auction dates and ZN bars alone are insufficient to price an actual cash/futures
trade: deliverable securities, conversion factors, cheapest-to-deliver choices, accrued interest and repo matter.

For NQ/ES, a future source-defined basis rule would require matched cash baskets or an explicitly justified hedge,
dividends/funding, synchronized quotes and both-leg execution costs. For CL/GC, storage, financing, delivery and
contract maturity matter. Shorting contango, trading generic spot-versus-future differences, or following/fading
commercial COT positions would be new unsupported strategies, not reproductions of this paper.

All four Apex homes lack a specified intraday directional event, actual integer hedge, protective exit and flat-by-15:59 CT
implementation here. A personal account removes some restrictions but does not resolve missing identification or
demonstrate a positive edge. No addition, replacement or EMPTY comparison is earned for any home.

No data acquisition was attempted: the evidence gate fails on a defined observable strategy, not a nearly complete
replication missing a file. If a separately justified execution/basis proposal arises later, first audit the exact
instruments, payoff dates, predecision observability and executable bid/ask/carry ledger without calculating returns.
Then require its own evidence and committed preregistration. This source alone does not authorize a proxy search.

## Record and disposition

Reviewed the supplied main text, definitions, propositions, welfare/basis conclusions, perfect-competition benchmark,
and the relevant non-influenceable-contract counterfactual and proof passages. The full PDF and extracted appendix
are retained; the algebra is not independently re-proven. No empirical result, theoretical numerical replication or
independent strategy-checker verification is claimed.

Exact SSRN/title/author search found no existing review. This is related to the previous spot-market-power paper,
not a duplicate; it also complements the existing execution references on slicing and endogenous price impact.
Retain the distinct payoff/basis lesson without reopening failed hedging-pressure or paired-commodity strategies.
Zero new return trials, parameters, portfolio simulations or measured execution savings. No promising-strategy queue
entry, tier change, trading allocation, MultiCharts code, live/VPS/broker action or external message.

For Claude: `agents/codex/results/strategic_futures_3947960_20261030.md`.
