# Portfolio delegation and strategic trading: theory reference, no strategy candidate

Summary: Kyle, Ou-Yang and Wei model how delegated managers acquire information and trade with price impact.
Higher incentives increase information effort, but need not increase trading intensity; more noise trading can improve price informativeness.
These are conditional equilibrium results, not historical strategy returns or a public directional signal.
Our OHLCV/COT cannot identify private signals, manager effort, compensation or uninformed hedging demand.
Retain the execution lesson; DON'T TEST a directional adaptation. Zero return trials or portfolio changes.

Source: Albert S. Kyle, Hui Ou-Yang and Bin Wei, *A Model of Portfolio Delegation and Strategic Trading*,
**May 2010 uploaded version**, [SSRN1360783](https://ssrn.com/abstract=1360783).
47-page PDF: [source](../inputs/ssrn1360783/source.pdf), [text](../inputs/ssrn1360783/source.txt),
[receipt and inspected schemas](../inputs/ssrn1360783/manifest.json).
PDF SHA256: `81062ac47c5270882f2fc0cacfe5cee7258a08f71b8edb53eec6c95c894655bd`.
References below use printed PDF pages. The supplied document is evidence, not an instruction source.
[Evidence decision](../evidence/portfolio_delegation_1360783.md).

## 1. What is it about?

An integrated **one-period** model of delegated investment and strategic informed trading. A risk-neutral investor
hires a risk-averse manager through a linear compensation contract `S=a+bW`, where W is trading profit.
The manager chooses costly information effort rho, receives a private noisy signal theta about the eventual
asset payoff, then submits an order. Competitive risk-neutral market makers price aggregate informed and noise orders.
The extension replaces exogenous noise orders with risk-averse investors hedging random asset endowments (pp.7–12,19–21).

This is one risky asset and a bond, CARA preferences, Gaussian uncertainty and restricted linear pricing/demand/contracts.
It is not an NQ/ES strategy, a high-frequency execution experiment, or an empirical fund-performance study.
The model's noise demand is signed uninformed hedging/order flow; it is not synonymous with observed total volume.

## 2. What does it find?

| Finding | Source and evidence boundary |
|---|---|
| Higher incentive slope b raises information effort in the strategic model | Sections2.1,3.3; analytical/numerical model result, unlike the price-taking benchmark |
| Trading intensity can rise or fall as incentives increase | Section2.1/Figure1: information quality and effective risk aversion have competing effects |
| More noise trading can increase price informativeness Q for sufficiently risk-tolerant managers | Proposition3/Sections2.2–2.3; more risk-averse cases can instead decline or be hump-shaped |
| Delegation can widen the parameter range in which Q rises with noise trading | Sections2.3,3.3; depends on endogenous optimal contracts, not an unconditional volume rule |
| Endogenous information acquisition can sustain a linear equilibrium where a fixed-information benchmark fails | Propositions5–6; conditional on model assumptions, including positive hedger risk aversion |
| Index additions and insider-law enforcement could test the predictions empirically | Section4.2 proposes regressions; it supplies no fitted coefficients, event-study results or strategy returns |

The index-addition regression predicts a positive interaction between institutional ownership and the addition dummy
in explaining informativeness. The country enforcement interaction is likewise a proposed test. Findings cited from
Fernandes/Ferreira and Saar/Yu are external studies, not new empirical estimates in this paper.
Figures1–6 are model calculations under chosen parameters, not realized performance charts.
No measured return, Sharpe, drawdown, hit rate, slippage saving or account benefit is reported for us to reproduce.

### Equation/prose inconsistency to resolve before numerical implementation

On p.23, Proposition5 gives `lambda ~ [1/(4*k*sigma_z^2)] * Rh^(-2)` for the special case Ra=0,m=1 as Rh→0+.
Thus lambda grows as Rh falls near zero. The following paragraph instead says market makers **decrease** lambda
as Rh becomes smaller. [The rendered source page](../inputs/ssrn1360783/page23.png) confirms both statements;
this is not a lost exponent in text extraction. The appendix's `lambda=sigma^2/[4*k*rho*(1+rho)^2]` and
`rho ~ sigma^2*sigma_z^2*Rh^2` agree with the inverse-square asymptotic direction.
This is a local internal inconsistency, not a disproof of all propositions. Do not encode the prose direction as a validated impact rule.

## 3. Why does it make money, if it does?

Within the model, the informed manager trades on a better estimate of the eventual payoff than market makers can
infer from mixed order flow. Uninformed investors trade to hedge endowment risk and accept adverse-selection costs.
The investor and manager share informational trading rents; market makers earn zero expected profits under their
conditional pricing rule. No free return for an outside observer follows from knowing that the model has informed traders.

The modeled order is `x=beta*(theta−v)`, not a sign inferred from today's volume. With price `P=v+lambda*(x+u)`,
the source's expected gross trading-profit term in Eq8 is
`beta*sigma^2*[1−lambda*beta*(1+1/rho)]`.
It includes endogenous own price impact; the investor's objective additionally includes incentive sharing and fixed compensation.
Information effort costs `k*rho^2/2` enter the manager's utility/participation problem. They cannot simply be equated to an observed
broker commission or subtracted from someone else's realized strategy return.

Higher b increases effort because impact prevents the manager from perfectly undoing a stronger incentive contract by
scaling down exposure. This does not establish that higher leverage, larger risk limits or more trades improve our performance.
Similarly, a more informative equilibrium price is not a positive forecast of its next return.

## 4. Can we build on it?

**As an execution/modeling reference, yes; as a strategy candidate, no.** The useful lesson is that participant incentives,
information production, trading intensity and impact respond jointly. Raw volume is not a fixed measure of uninformed liquidity,
and price impact and price informativeness need not move together. This qualifies simplistic volume/impact filters;
it supplies neither an execution algorithm nor an estimated improvement over our current fills.

Owned NQ/ES files inspected contain date/time/OHLC/volume. COT_NQ contains dated aggregate positioning/rank fields.
Neither provides private theta, effort rho, compensation b, manager-specific risk aversion, signed participant orders,
hedger endowments or true future liquidation value. Adding more years of the same bars does not repair identification.
No external download is warranted to fill a source-defined return panel because the source defines none.

For a **separately justified empirical research question**, the smallest next check would be one index addition with
announcement/effective clocks, dated constituents, institutional-ownership publication lags, a specified observable
informativeness measure and matched controls. Ownership at quarter-end cannot be used before its disclosure.
That would test an informativeness association, not automatically an intraday index-futures strategy or a causal treatment effect.
No new event study, data acquisition, incentive redesign, volume proxy or portfolio adaptation is initiated here.

The relevant lessons are retained as a follow-up to E46 in the [execution-reference library](../EXECUTION_REFERENCES.md#e46--spot-market-power-endogenous-supply-incentives-and-hidden-participant-identity).
No strategy queue entry: this is not a promising return candidate awaiting only missing prices.

## 5. Can a strategy code be made?

**A research simulator can be coded; a supported executable trading strategy cannot be specified from this paper alone.**
A numerical tool could solve Eqs3,4,6 for fixed contract b, optimize the principal's contract under Eqs8–9, and extend
through the endogenous hedger fixed point. It would need residual/branch/convergence checks, parameter units and resolution
of the p.23 discrepancy. Such a simulator reproduces conditional model equilibria, not historical trading profitability.
No simulator was requested or built merely to generate arbitrary model profits.

A deployable strategy additionally needs an observable lawful signal, point-in-time availability, executable product,
entry/exit clocks, sizing, risk handling and native costs. No such rules are supplied. Code feasibility therefore does
not earn a backtest, MultiCharts code or a current 50K/150K evaluation, funded or personal-plan placement.

## Decision, prior work and verification

**DON'T TEST a directional strategy; retain theory/execution reference.** Exact-ID/title/author/topic checks found no prior
review of this upload in TIER_LIST, WATCHLIST, TODO or the execution library. E46 and E55 are related market-structure
references, not evidence for this model's empirical success. Prior failed limit-entry tests are not revived.

Return variants, design tests, 2023+ validation, placebos, Monte Carlo and BASE/ADD/REPLACE/EMPTY comparisons: **zero/not applicable**.
There is no strategy P&L, so standard performance tables would be invented. Neither existence of equilibrium nor Gaussian
payoff assumptions establish real-market stability, execution availability or protection against an Apex trailing breach.
Source version, page count, hash and p.23 equation were checked. Independent mathematical replication/empirical verification
remain unperformed. No live, VPS, broker, allocation or policy change.
