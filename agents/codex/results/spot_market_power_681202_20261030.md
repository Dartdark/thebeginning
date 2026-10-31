# Spot Market Power and Futures Market Trading: theory reference; DON'T TEST as a strategy

Summary: Muermann and Shore model how spot-supply control changes futures trading and hedging incentives.
They derive equilibria with incomplete hedging, concealed strategic positions, and manipulation; there is no empirical return test.
The profitable modeled roles require supply control or price-moving intermediate trades and specified market-maker beliefs.
No observable, timed outsider signal or current NQ/ES/CL net edge is established. No strategy earns a portfolio comparison.
Retain the participant-identification and endogenous-price-impact lesson; zero new return trials or live changes.

Source: Alexander Muermann and Stephen H. Shore, **Spot Market Power and Futures Market Trading**, March 2005,
user-uploaded `ssrn-681202.pdf`, 36 PDF pages. References below use printed page numbers, which match PDF page numbers.
This review concerns the supplied version; publication status and later revisions were not independently checked.
[Archived PDF](../inputs/spot_market_power_681202_20261030/source.pdf) ·
[extracted text](../inputs/spot_market_power_681202_20261030/extracted_text.txt) ·
[source receipt](../inputs/spot_market_power_681202_20261030/manifest.json) ·
[feasibility decision](../evidence/spot_market_power_681202_20261030.md).
PDF SHA256: `4541fe8a790ecc8ebd3d2a04569d4c50e0ce59113f0311c9409203c551620d41`.

## 1. What is it about?

The paper connects industrial organization to futures microstructure. A producer that controls physical supply
can alter the final spot price after taking a futures position. Competitive market makers anticipate that
incentive. When individual positions are hidden inside aggregate orders, imperfect inference can permit
strategic trading even without private information about future demand.

Section 2 studies observable positions and hedging; Section 3 introduces concealed positions and uncertain
aggregate hedging demand; Section 4 adds an earlier contract whose payoff depends on an intermediate futures
price. These are distinct models, not a single calibrated trading algorithm.

## 2. What does it find?

The findings are analytical propositions under specified assumptions, not independently replicated market observations.

| Source | Claimed theoretical result | Practical boundary |
|---|---|---|
| Section 2, pp. 5–11, Propositions 1–5 | Observable, fairly priced hedging trades distort the monopolist's production incentives. A risk-neutral monopolist abstains; a risk-averse one hedges partially. Price-contingent contracts cannot eliminate all profit risk in this setup. | Demand-contingent contracts provide an explicit exception: Proposition 2 permits complete hedging while retaining monopoly profits. This is not a universal theorem that all futures hedges must fail. |
| Section 3, pp. 12–19, Propositions 6–8 | A monopolist can conceal a randomized long/short position among hedgers' orders, subsequently adjust supply, and profit in equilibrium. Other hedgers reduce participation. | Individual positions are imperfectly observed; uniform stochastic hedger participation, linear demand and rational pricing beliefs are model assumptions. |
| Section 4, pp. 19–23, Proposition 9 | A trader without physical market power may profit from an earlier derivative position by later price-moving trades that are mistaken for a monopolist's orders. | The later trades themselves lose on average; the earlier position benefits. The initial contract pays on an intermediate futures price, a structure the authors call unusual (p. 19, footnote 13). |
| Conclusion, pp. 23–24 | Market power can deter hedging and reduce participation; index-triggered hedges can reduce moral hazard but introduce basis risk. | The oil-liquidity discussion is a 2005 interpretation, not measured evidence about current CL liquidity. |

There is no historical sample, estimated Sharpe, Sortino, profit factor, Calmar, Ulcer index, transaction-cost backtest,
out-of-sample validation, or Apex payout result. Figure 1 is a stylized two-state model illustration; Figure 2 is a timeline.
The appendix supplies mathematical arguments; inspecting those arguments is not an independent empirical test.

## 3. Why could the modeled trades make money?

In Section 3, the producer's hidden futures position changes its optimal subsequent physical production.
For linear demand, equation (12) on p. 13 gives `Q*=(a-bC)/2b` and `P*=(a+bC)/2`.
A long producer position raises its optimal spot price relative to a short position through its own supply choice.
Market makers cannot fully identify that position from aggregate orders, so the producer can receive more favorable
terms than under full observability. The modeled gain is at other participants' expense; it is not an unexplained
forecasting premium available to every futures trader.

Section 4 does **not** require the beneficiary itself to control physical supply. It instead requires its intermediate
trades to affect prices through beliefs about another participant's supply power, together with the earlier derivative
exposure. Ignoring the losing intermediate leg, its price impact, or that contract structure would not reproduce the model.

The monopolist randomizes direction in the concealed-position equilibrium. Therefore "a powerful producer exists"
does not identify a trade side before entry. The paper does not show that price-only momentum, volume spikes,
aggregate COT positions, or trading opposite commercial hedgers can reveal the profitable role.

## 4. Can we build on it?

**Retain as an execution/market-structure reference; do not launch a strategy backtest from this source.**

- **NQ/ES:** controlling the production of the underlying physical good is not a direct model of an index-futures trader.
  The paper provides no independent index demand variable or scheduled directional event.
- **CL/GC:** supply control is economically more relevant, but this paper assumes away effective storage (pp. 4 and 12,
  footnotes 1 and 8), which can constrain monopoly power. It does not estimate contemporary producers' inventory,
  supply discretion, futures positions, or reaction clocks. It specifies no outsider entry/exit rule.
- **All four Apex homes:** no intraday window, executable protection, integer sizing, or flat-by-15:59 CT rule is supplied.
  **Personal:** removing Apex constraints still does not supply the missing information or establish net expected return.

Owned-data inventory found continuous commodity/index OHLCV, aggregate COT archives and some order-flow inputs,
not identified producer futures inventories matched to physical supply actions and contemporaneous quotes.
Aggregate commercial positions cannot identify an individual monopolist's concealed side, and minute bars cannot
identify the price schedule, participant beliefs, or the model's demand slope. No substitute proxy was tested.

No data purchase/acquisition loop is justified: this is an evidence-gate rejection of a proposed trading foundation,
not a nearly executable rule missing one download. If a future concrete study supplies legally observable,
timestamped participant-linked positions and supply changes, the smallest useful next check is a no-return audit
of whether those observations were available before a specific decision and identify direction. A new strategy
would then require its own mechanism, costs, committed preregistration and normal validation gates.

## Verification status and repository disposition

Reviewed the supplied full text, model setup, propositions, appendix and references. Retained source bytes,
extraction, hashes and a zero-return-trial receipt. No market-data experiment, theoretical-profit replication,
paper-trading record or independent strategy verification is claimed.
Exact-title/SSRN/author searches found no prior entry; the existing failed CL/GC hedging-pressure study is a distinct
aggregate-position strategy and is neither revived nor independently refuted by this paper.

Useful lesson retained in the execution-reference library: identify the beneficiary, its supply/price-impact capability,
the full set of offsetting legs, and the observer's information clock before translating a model's profit into our edge.
No promising-strategy queue entry: there is no specific source-supported outsider rule with demonstrated merits awaiting
verification. No tier or plan edit, code for MultiCharts, account simulation, broker/VPS action or external message.

For Claude: `agents/codex/results/spot_market_power_681202_20261030.md`.
