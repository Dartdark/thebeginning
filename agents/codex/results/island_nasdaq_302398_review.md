# Island versus Nasdaq: execution and rent-decay reference; no futures strategy

Summary: Fine-grid Island quotes undercut coarse Nasdaq quotes before decimalization; competition between venues mattered.
Authors report tighter spreads and weaker evidence of liquidity-provider rents after the Nasdaq tick fell.
The model estimates order-handling cost plus rent, using executed marginal orders and later midpoints—not a retail backtest.
Retain quote precision, conditional-fill, markout and identification lessons; no new NQ/ES strategy or allocation.

Source: Bruno Biais, Christophe Bisière and Chester Spatt, *Imperfect competition in financial markets: ISLAND vs NASDAQ*, revised November26,2003, SSRN302398,40PDF pages. Reviewed November7,2026 (America/Los_Angeles).
[Uploaded PDF](../inputs/island_nasdaq_302398/ssrn-302398.pdf) · [full text](../inputs/island_nasdaq_302398/full_text.txt) · [primary metadata](https://ssrn.com/abstract=302398).
Scope: main text, tables, appendix and figure material inspected; Table4/printedp.28 visually checked. Printed page numbers are PDF page minus two. No raw Island/Nastraq replay or GMM replication.
Plan: source/measurement audit only; no economic preregistration warranted. [Evidence](../evidence/island_nasdaq_302398.md).
Script: [arithmetic and synthetic fixtures](../../../analysis/codex_island_nasdaq_302398_audit.py) · [claims/receipt/hashes](../../../analysis/outputs/codex_island_nasdaq_302398/source_audit.json). New financial-return trials: zero.

## Five questions

1. **What is it about?** Competition within an electronic stock order book and between that venue(Island) and Nasdaq. It asks whether transparent, inexpensive access is enough to remove liquidity-provider rents, using order-placement patterns, differing price grids and a structural spread/markout model.
2. **What does it find?** In seven selected stocks over five March2000 sessions and five June2001 sessions, Island orders undercut Nasdaq more often than they undercut other Island quotes. Following Nasdaq decimalization, reported average spreads fell from$0.079to$0.014on Nasdaq(excluding Island), and$0.198to$0.0648on Island. Authors infer pre-decimalization rents and weaker/insignificant pooled evidence afterward in their simple specification. These are historical source results, not our reproduced P&L; richer instrument tests also reject model restrictions in2001, so perfect competition is not established universally.
3. **Why does it make money, if it does?** Historically, a fine Island tick let suppliers improve a coarse external quote by a small amount and gain access to Island order flow while retaining some spread. Nasdaq's smaller tick reduced that room. But queue priority, adverse selection, fees, inventory and access determine actual profit. The econometric model identifies handling cost plus rent and separates them only through assumptions across periods; it does not establish a current accessible market-making edge.
4. **Can we build on it?** Yes for execution research: retain unrounded quotes, synchronize competing feeds, compare filled orders with appropriate later markouts, and avoid equating better displayed prices with attainable fills. It complements the prior [dealer-concentration paper](nasdaq_dealer_486642_review.md) by showing how tick rules and intervenue competition can erode an advantage. No reason to reopen failed passive-entry substitutions or add a directional NQ/ES filter. Smallest justified next use is an existing offline fill/quote audit, not a new return study.
5. **Can a strategy code be made?** **Research tools and a conditional simulator: yes; a complete current trading strategy: not supplied.** An event classifier, unrounded-quote comparison and signed maker-markout estimator are implementable. A historical undercutting simulator additionally needs actual order-event/queue data, latency, venue rules, rebates, cancellations, fills and inventory/exit policy. No validated rule maps this stock-venue advantage into NQ/MNQ. No MultiCharts trading code or profitability claim is justified.

## Data, results and model

The source combines unrounded Island website order-book/trade records with Nasdaq DQ/IQ/TR records. The stocks are COMS,CSCO,DELL,INTC,MSFT,QCOM,SUNW. Windows are March8–14,2000 and June18–22,2001. A feed failure truncates March10 at14:30rather than16:00. Regular coverage starts around09:30. This is a short selected historical comparison, not years of independent strategy observations.

In2000the Nasdaq tick was$1/16and Island$1/256; in2001they were$0.01and$0.001. Quotes displayed in Nasdaq records rounded away some finer Island improvements. Source spread comparisons exclude Island from its competitors' inside quote where specified; the appendix also discusses comparisons against the inclusive Nasdaq inside. Those are different benchmarks. Island's wider average two-sided spread does not preclude its bid or ask beating the external best on particular occasions.

| Source finding | Interpretation |
|---|---|
| Nasdaq spread at one tick81.5%of the2000sample | Evidence the coarse grid constrained quoted spreads, not a guaranteed spread available to our orders. |
| Table2,ask side, best bid held by Island: next-event ask undercutting4.54%when Island sets the ask versus26.55%when Nasdaq sets it | Conditional event frequencies, not fill probabilities, win rates or an unconditional causal effect. |
| Simple pooled GMM:theta=c+pi about$0.02,t2.49in2000; displayed$0.00,t1.53in2001 | Joint cost-plus-rent parameter. Rounded zero and insignificant t do not prove zero cost/rent or universal competition. |
| Added undercutting instrument: model rejected for5/7stocks in2000and6/7in2001(Table6) | More nuanced than the abstract's simple before/after conclusion; restrictions/specification matter. |
| Historical passive rebate$0.001/share; immediate-order charge$0.0025/share | Source-era venue terms, not current CME fees or all-in broker costs. |

For the structural model, expected ask-side markout is `ask - midpoint_30min`, and bid-side markout is `midpoint_30min - bid`. Under its assumptions, expected markout=M=c−f+pi, and spread=S=alpha+2M. With known rebate f,theta=M+f=c+pi;alpha=S−2M. A later midpoint proxies conditional fundamental value, with a white-noise measurement assumption. It is not an executable closing fill or contemporaneous predictor.

The marginal-order restriction matters: the empirical moments use trades large enough to consume the displayed best-level depth. If500shares are displayed, a250share buy does not qualify but a500share buy does. These observations are selected executed liquidity events. The model is not a backtest of every posted/cancelled/nonfilled passive order, and risk-neutral suppliers abstract from inventory-risk costs.

## Independent checks and limits

- **Quote rounding:** an invented ask one$1/256tick below an external$100.0625ask is$100.05859375. Rounded up to the coarse grid it displays$100.0625, hiding the improvement. Our fixture confirms the mechanism, not that we could receive the priority/fill. Price priority in this setup was limited to Island flow; it was not assured across venues.
- **Cost/rent nonidentification:** in an invented S=$0.10,M=$0.03,f=$0.001example,alpha=$0.04andtheta=$0.031. Both(c,pi)=($0.01,$0.021)and($0.03,$0.001)fit those same moments. Separating rent needs extra assumptions. The paper assumes stable handling cost across the two periods, while stock prices, volatility and market conditions also changed substantially.
- **Signed markouts:** synthetic buys/sells verify side symmetry. A favorable postfill midpoint is not liquidation profit; inventory hedges, closing spread, nonfills, cancels, partials and broker costs remain outside that arithmetic.
- **Feed synchronization:** the source's appendix estimates a roughly15%comparison-error issue in the cited DELL diagnostic. This is an acknowledged source-specific warning, not a universal error estimate or assurance of causality. Stale cross-feed comparisons can create apparent undercutting/arbitrage.
- **Model rejection versus proof:** GMM rejection can reflect misspecification or instrument issues, not uniquely collusion/rents. Non-rejection does not establish perfect competition. The two short windows do not isolate a randomized treatment effect of decimalization; volatility and prices differ sharply.
- **Access and era:** the historical intervenue grid difference is not an NQ/ES retail edge. Minute OHLCV does not identify queue position, unrounded competing quotes, marginal-book consumption or native maker economics. Never transfer stock subpenny increments or fees into futures orders.

The upload contains no original executable replication code or data panel. Bounded owned-filename inspection found no matching Island/Nastraq event panel. Because no complete current strategy or specific new economic candidate is established, a speculative acquisition/backtest is not earned. No paid access or external contact attempted. Research diagnostics would need genuinely relevant native records under their own protocol.

## Disposition

**REFERENCE / DON'T TEST as a standalone futures strategy.** This strengthens execution measurement and conditional-profit interpretation, not our present return forecast. Retain it with E01/E56 in [EXECUTION_REFERENCES.md](../EXECUTION_REFERENCES.md); [DATA_NEEDED.md](../DATA_NEEDED.md) already covers native quote/depth/order/fill prerequisites D42–D45. No new promising-strategy/data-needs entry merely because input data are missing.

No long/short strategy metrics, holdout, placebos, portfolio/account simulation or plan changes produced. Those results are not applicable, not zero. No personal/Apex placement established, no live system touched, and no paper instructions treated as user authorization.

For Claude: `agents/codex/results/island_nasdaq_302398_review.md` — historical tick/competition reference; conditional markout and cost/rent identification caveats; zero return trials.
