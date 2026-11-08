# Infinite Factor Structure: retain methodology; no strategy admitted

Summary: A theoretical reason that pooling state-dependent portfolios can invalidate a fixed-factor interpretation.
Under the paper's conditions, small principal components can retain systematic, priced risk as the portfolio menu grows.
This does not prove that every small sample component is useful or that adding same-market strategies diversifies our book.
Retain as a risk-model reference; no return trial, allocation, data purchase or live change is justified.

Source: Chernov, Kelly, Malamud and Schwab, *Infinite Factor Structure in Conditional Asset Pricing*,
October 11, 2026 version, SSRN7596842. Review date November 7, 2026, America/Los_Angeles.
[Owned PDF](../inputs/infinite_factor_7596842/paper.pdf), 240 pages, and
[extracted text](../inputs/infinite_factor_7596842/paper.txt).
Scope: focused review of introduction, setup/assumptions, Theorem1 and its discussion, conditional-stock setup,
Section5's example/pricing/covariance discussion, and conclusion. The long proof appendices were not exhaustively
read or independently verified. Figures are used through captions, not digitized or independently reproduced.
[Audit script](../../../analysis/codex_infinite_factor_7596842_audit.py) and
[receipt/hashes](../../../analysis/outputs/codex_infinite_factor_7596842/source_audit.json).

## Five questions

1. **What is it about?** The difference between conditional risk structure at a given state and unconditional
   structure estimated by pooling states. It analyzes expanding menus of characteristic-managed portfolios and
   individual-stock panels with persistent differences in their loadings.
2. **What does it find?** Under stated richness, nondegeneracy and convergence conditions, managed portfolios need
   not have an eigenvalue cliff: infinitely many fixed-rank eigenvalues grow with menu size. For stocks, common
   states and persistent firm differences can yield the analogous result. Under additional pricing conditions,
   generic expected returns load on infinitely many groups while maximal Sharpe stays finite. This is a population
   theorem and analytical illustration, not an original executable strategy backtest.
3. **Why does it make money, if it does?** The paper does not identify a forced trade or forecast the size/sign of
   individual premia. Nonlinear, state-dependent exposures can span systematic payoff directions missed by a few
   unconditional PCs. Their possible pricing explains why variance captured and expected returns spanned are
   different questions. It establishes neither net profits nor unlimited independent opportunities.
4. **Can we build on it?** Yes, when assessing risk-model assumptions or an already-justified portfolio estimator.
   Compare conditional structure with pooled structure, and test regularization versus fixed-rank truncation on
   chronologically evaluated net outcomes. This is a proposal for later justified work, not permission to optimize
   the current book or reopen failed strategies. No current account benefit is established.
5. **Can strategy code be made?** Diagnostic and estimation code, yes; a complete source-defined trading strategy,
   no. There is no NQ/ES entry, side, stop, target, exit, native size or executable cost protocol. A managed-stock
   implementation would additionally require point-in-time characteristics, an identified stock universe, actual
   portfolio weights, financing/borrow and turnover accounting. Code feasibility is not evidence of profitability.

## Source findings and assumptions

| Source | Interpretation and limit |
|---|---|
| §§2–3, pp7–16; Theorem1 | Work primarily uses second moments. Covariance differs by a rank-one mean term; the asymptotic conclusion extends by interlacing. Menus must retain exposure to arbitrarily many independent payoff directions; this is not true of every arbitrary duplicated strategy menu. |
| §4, pp16–21 | Stocks retain a conditional finite-factor structure. Persistent firm types and the support of common states matter for the unconditional conclusion. The symmetric benchmark can still have only one diverging eigenvalue. |
| §5.1, pp22–28 | Gaussian example produces a geometric staircase of growth constants; a steep staircase may resemble a finite cliff. This is a specified population model, not an empirical estimate from our sleeves. |
| §5.2, pp28–37 | Risk eigenvalues do not alone identify expected returns. Generic pricing claims require the paper's admissible-mean, no-arbitrage and limiting-group conditions. A theoretical unconstrained optimum is not an achievable integer-size account outcome. |
| §§5.3–5.4, pp37–41 | Small sample eigenvalues can mix meaningful population structure with estimation uncertainty. Direct inverse covariance is ill-conditioned near dimension/sample parity and singular above it. Regularization avoids a fixed-rank premise but introduces bias and does not guarantee better net results. |

The introduction and §5.2 cite another study's out-of-sample Sharpe falling from 3.7 to about 1.3 after truncating to
five PCs. These are cited external results, not an empirical result of this paper, our reproduction or a claim for
our futures book. The original empirical study was not independently audited in this review.

The paper's companion-method connection is already recorded in
[The Hidden Sharpe Ratio review](hidden_sharpe_7679420_review_20261107.md). Neither theoretical factor richness
nor an estimated population frontier supplies the native weights, costs or account-risk evidence missing there.

## Bounded check performed

The audit binds PDF/text/code hashes and checks the extracted text against the archived source. An elementary
zero-mean two-state example has one rank-one conditional systematic covariance in each state, with loadings on
different coordinate axes. Equal mixing gives diag(0.5,0.5), rank 2. This illustrates how pooling can increase rank.
It has zero expected returns, so it also illustrates why more covariance directions do not imply more profit.
This finite algebra check is not an independent proof of the paper's infinite-dimensional theorems, an empirical
test or an estimator benchmark. No market data, trade returns or economic trials were observed.

## Application to our project

Useful: avoid declaring low-variance residuals harmless solely from a pooled PCA cutoff; keep model assumptions,
finite-sample estimation error and the eventual executable portfolio objective distinct. A finite-rank model can
still be a useful approximation after costs and estimation error; the paper does not establish that retaining
every noisy direction is superior in a short sample.

Not established: that our NQ-heavy sleeves possess additional independent risk premia; that existing historical
covariance attribution is wrong; or that a new regime gate, ridge allocator, inverse-volatility sizing rule or
different model improves payouts/survival. Our existing finite-sleeve concentration findings remain descriptive
evidence on their actual history. Do not extrapolate the growing-stock/menu theorem into a small-account
diversification recommendation without matched data and a separately preregistered comparison.

Disposition: **METHOD REFERENCE / DON'T TEST as standalone alpha**. No promising-strategy queue or new data
request warranted. There is no eligible economic definition to preregister. No design, holdout, Monte Carlo,
BASE/ADD/REPLACE/EMPTY comparison or PowerLanguage strategy was run/written. Retained in the execution/risk
reference library as a companion to the existing population-frontier caution, not as measured execution savings.

For Claude: `agents/codex/results/infinite_factor_7596842_review_20261107.md`.
