# Constructing the Best Trading Strategy: methods reference; DON'T TEST as a standalone edge

Summary: Maymin and Maymin derive optimal positions given known conditional return moments.
The paper supplies no empirical signal, dataset, executable market rule or out-of-sample trading evidence.
Its expected-return optimum and information-ratio optimum solve different objectives, neither Apex payouts.
Estimation, instability and transaction costs remain material; a small parameter count does not remove overfitting.
Retain the sizing/cost lesson; no new return trial or portfolio change follows from this source.

Source: Philip Z. Maymin and Zakhar G. Maymin, *Constructing the Best Trading Strategy: A New General Framework*,
[SSRN 1896146](https://ssrn.com/abstract=1896146). Full uploaded PDF inspected, 33 PDF pages; printed pages cited below.
PDF metadata creation date October 11, 2011 is not independent verification of publication/revision history.
[Archived PDF](../inputs/ssrn1896146/source.pdf), [extracted text](../inputs/ssrn1896146/source.txt).
PDF SHA-256: `2a480a34a9c9c24af1a16c582f365257fd92da5989c20bc349c5215eee3bf2e6`.
Return trials: **0**. Evidence status: source review and analytical reasoning; no empirical replication or independent checker.

## 1. What is it about?

The framework separates an indicator H, known before trading, from a position function f(H), constrained by
|f| <= 1. The next-period return is R and the strategy return is f(H)R. It asks which position maximizes
expected return, then separately which maximizes mean divided by standard deviation, called information ratio.
That terminology is the paper's; it does not imply benchmark-relative active-return measurement here.

## 2. What does it find?

| Result | Conditions and interpretation | Source |
|---|---|---|
| Expected-return optimum is sign(E[R given H]) | Take the largest allowed long or short position according to the conditional mean; maximum gross expectation is E[abs(E[R given H])]. Values where the conditional mean is zero are not uniquely determined. | pp. 5–6 |
| Normal-case direction is the sign of a regression forecast | With jointly normal indicator and return, the conditional mean is linear. Nonlinear conditional means require a different fitted relationship. | pp. 6–8, 12 |
| Information-ratio optimum uses conditional first and second moments | Up to positive scaling, position is proportional to E[R given H] / E[R² given H], when a bounded scaling exists. Clipped positions are also considered under a fixed second-moment constraint. The denominator is the second moment, not just conditional variance. | pp. 19–24 |
| Maximum-return and maximum-ratio strategies differ | Their gross return and risk objectives differ even with the same indicator. The displayed normal-case comparisons are theoretical calculations, not observed strategy results. | pp. 25–30 |

No market sample, historical trading performance, net costs, Sharpe validation, drawdown or payout results are supplied.
The conclusion explicitly leaves empirical applications and estimation risk for future research (p. 31).

## 3. Why does it make money, if it does?

It makes a conditional statement: **if** the true future-return conditional mean is known, choosing its sign maximizes
gross expected payoff under the stated position cap. This does not establish that any available indicator predicts NQ,
ES or another market. No forced participant, mandate, hedge deadline or structural risk premium is identified.
The difficult economic and statistical work is obtaining a stable, tradable forecast before the return occurs.

Material qualifications:

- The paper acknowledges on p. 2 that the conditional distribution is unknown and unstable, and that estimation
  through time is outside its scope. Its p. 3 claim that a handful of parameters overcomes overfitting is therefore
  too strong: choosing indicators, samples, distribution families and parameter estimates still selects on data.
- These are frictionless benchmarks. The paper itself notes that a different strategy can be preferable after
  slippage, commissions and other costs (p. 2). Changing positions also depends on the position already held, so
  a realistic turnover-cost optimum generally needs that state as well as the indicator.
- A single-period notional cap does not model equity-dependent trailing floors, intraday liquidation, daily loss
  pauses, integer micro contracts, payout rules or joint portfolio exposure. Maximum gross return is not a
  recommendation to use maximum size on every positive forecast.
- The quoted approximately 1.324 information-ratio ceiling is for the maximum-expected-return strategy in the
  zero-drift normal case (p. 17), before annualization. It is not a universal Sharpe ceiling; the paper's separate
  maximum-information-ratio solution can exceed it (pp. 25–28).
- The equality discussion in the efficiency section overreaches (p. 19). E[abs(E[R given H])] can equal E[R] even
  when E[R given H] varies with H: it is enough that the conditional mean stays nonnegative. In that case the
  maximum-return rule stays long throughout. Predictability need not improve the capped directional strategy
  over buy-and-hold, and this theorem alone does not settle market efficiency or risk-adjusted compensation.

## 4. Can we build on it?

**As a modeling reference, yes; as a new standalone strategy, no.** The source supplies neither an indicator/horizon
nor an independently supported economic mechanism to freeze. Owned price bars cannot fill that gap without inventing
a new signal search. Opportunity count, forecast variance, plausible gross edge and portfolio hours consequently
cannot be specified from this paper; no data purchase or market-return backtest is justified by the source alone.

The useful future application is a benchmark for a separately justified, frozen predictive signal: compare a simple
direction rule against a conditional-moment sizing rule, fitted only on matured past labels, with identical clocks,
integer quantities, costs, turnover and existing protective exits. Include a no-trade region when the modeled net
benefit cannot cover execution costs and estimation uncertainty. That is a local extension, not a result tested here
or a cost-aware optimum derived by this paper. Validate incremental account effects with BASE/ADD/REPLACE/EMPTY
only if the earlier strategy gates pass; preserve the actual current portfolio and intraday loss paths.

Prior-work check: searched SSRN identifier, authors and optimal-indicator/conditional-mean terms in TIER_LIST and
Codex reports; no duplicate review identified. Existing position-sizing and payoff lessons overlap with execution
reference E37, which is updated rather than creating a competing strategy item. No promising-strategy queue entry:
there is no source-backed trading candidate awaiting verification. No trading tier is assigned to an untested theorem.

**Verdict: DON'T TEST as a standalone strategy.** Retain the method and limitations; no current-plan allocation,
execution improvement or account benefit has been demonstrated.

For Claude: `agents/codex/results/optimal_indicator_framework_1896146_review.md`.
