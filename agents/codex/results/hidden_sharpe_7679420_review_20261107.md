# The Hidden Sharpe Ratio: METHODS REFERENCE / DON'T TEST as a trading strategy

Summary: The estimated equity Sharpe of about 7.4 (5.0 excluding microcaps) is a gross, model-based frontier estimate, not a realized strategy.
The efficient portfolio is left unidentified; upper/lower point bounds coincide by construction in 97% of broad-universe rolling windows.
Retain the estimation/implementation cautions. No futures rule, return backtest, account result or allocation follows.

Review date: November 7, 2026, America/Los_Angeles; receipt timestamps are UTC.
Source: Chernov, Kelly, Malamud and Schwab, *The Hidden Sharpe Ratio*, SSRN 7679420, October 28, 2026 version.
The 197-page [uploaded PDF](../inputs/hidden_sharpe_7679420_20261107/source.pdf) is pinned at SHA 256 `2bf44539a5e24b8086f87973a4d5165a891b9852745570d4afda30340ff97f8a`.
Reading scope: main text pp. 1–43 and implementation/threshold/inference/simulation appendices J–M, pp. 169–197;
Figures 1–8 inspected visually. The intervening proof appendices A–I were not exhaustively read or independently verified.
This is a substantive primary-source methods review, not a claim of a complete 197-page proof audit.

## 1. What is it about?

Estimating how high the population Sharpe ratio could be across a large menu of portfolios, without finding the
portfolio that attains it. The target is squared Sharpe, `mu' Sigma^-1 mu`.
When the number of portfolios is large relative to the number of observations, direct covariance inversion
overfits or becomes singular. Ridge regularization stabilizes it but attenuates information in low-variance
directions. The authors use higher-order debiased GRS statistics to estimate lower bounds, and an additional
restriction on the low-variance tail for upper bounds, with asymptotic confidence bands.

The empirical menu is monthly portfolios formed from US individual-stock characteristics, not ES/NQ entry signals.
The paper uses 132 stock characteristics,5,000 nonlinear managed equity portfolios and 240-month rolling windows;
the main full sample is January 1963–December 2025. Bond exercises additionally use 65 bond characteristics,
with a later 1986 start. See pp 28–32.

## 2. What does it find?

These are author estimates and visual transcriptions, not results independently reproduced on market data:

| Finding | Source and qualification |
|---|---|
| Approximate maximal annualized equity Sharpe 7.4;5.0 excluding microcaps | Abstract and pp 32–35; gross of trading costs. Nano stocks are already excluded. “All” means the paper's filtered managed-portfolio universe, not every conceivable investment. |
| Figure 2 broad-universe point bounds 7.34/7.34, confidence endpoints 6.45/8.01 | p 33 figure boxes; retain the exact displayed values separately from the approximate prose headline. These are frontier estimates/confidence bounds, not a realized Sharpe interval for our portfolio. |
| Figure 2 ex-micro point bounds 5.05/5.05, confidence endpoints 4.26/5.62 | p 33; source has its own unconstrained portfolio and liquidity assumptions. |
| Ridge squared-Sharpe shortfall factor about 1.8 | pp 34–35. Dividing Sharpe by `sqrt(1.8)` gives approximate ceilings 5.52 and 3.73 from the prose headlines; this arithmetic was checked, not the estimated factor. |
| Nonlinear managed weights expand the estimated frontier relative to linear weights | pp 40–42/Figure 5. This is a stock-characteristic comparison, not evidence that an arbitrary nonlinear futures model earns money. |
| Post-2004 characteristics add little in this experiment | pp 41–42. Conditional on this menu, publication-year admission and model; it does not establish that all new market research is useless. |
| Bonds raise point estimates; authors describe the increase as not statistically significant | pp 38–39. Text and figure numbers disagree; see below. No independent paired increment test was reproduced. |

The structural ridge shortfall is a result in the proportional regime with `P/T` staying positive. It is not a
universal claim that obtaining more observations for a fixed small strategy set can never improve estimation.

## 3. Why does it make money, if it does?

No net trading profit is demonstrated by the new estimator itself. It does not output the efficient portfolio's
identity, native positions, fills or a net cash ledger. It measures an opportunity frontier under assumptions.

The economic possibility is that expected returns are distributed across many portfolio directions, including
low-variance directions that shrinkage suppresses. Capturing those premia in practice still requires discovering
stable weights and trading them after information arrives, with actual turnover, borrow, funding, costs and
liquidity constraints. The paper's own microcap/cost qualification is explicit on pp 3 and 35.
Small covariance eigenvalues are not permission to invert noisy estimates or increase leverage.

## 4. Can we build on it?

**As a research diagnostic, conditionally; as a direct futures strategy, no.**
The useful lesson is to distinguish covariance variance explained from priced investment opportunities, and a
frontier estimate from a feasible portfolio's net performance. An eventual large, independently frozen research
universe might justify a diagnostic after checking the statistical assumptions. Our current small strategy book,
minute futures inputs, integer positions and path-dependent account constraints are a different application.

There is no source-specified futures side, decision/fill clock, holding period, stop, exit or costed gross edge
to preregister. Substituting NQ/ES price features for individual-stock characteristics would be a new model/search,
not replication. No return-test reservation or admission is justified here.

The smallest justified follow-up was completed: inspect the pinned author implementation and check the relevant
algebra, units and source consistency without market outcomes. Original stock/bond panels were not acquired or
admitted. A bounded filename check found no matching stock-characteristic/CRSP/JKP/bond files under `data/`;
this is not an exhaustive entitlement audit or a claim that every possible source is paid. Appendix M directs
stock-characteristic access to WRDS and mentions public JKP factor data; public linear factor returns do not
reconstruct the underlying panel needed for 5,000 nonlinear managed portfolios.

Deeper strategy development is not warranted from this paper alone. No new TODO strategy or data-shopping item
was added: an interesting estimator plus absent inputs is not a specific promising executable hypothesis.
Supporting lessons are retained in [EXECUTION_REFERENCES](../EXECUTION_REFERENCES.md#research-method-follow-up--estimated-frontiers-are-not-executable-sharpe-2026-11-07).

## 5. Can a strategy code be made?

**Research-tool code: yes. A tradable 7.4-Sharpe strategy from this paper: not specified.**

The authors already publish an MIT-licensed [Python implementation](https://github.com/DjoFE2021/HiddenSharpeRatio),
pinned here to `ddb27d4c420b271ba6c3f502062a61e1eaaf5bf3`. It accepts a matrix of excess returns and computes
statistics/bounds. The 8 saved documentation/source files establish an obtainable implementation, not a full
package audit, faithful empirical replication or trading performance. No author code was imported or executed,
and no environment dependencies were changed.

Static implementation cautions:

- Outputs in `get_all_lbs`/`get_all_ubs` are annualized **squared** Sharpe bounds. Take a square root only with
  a valid nonnegative bound, correct period and interpretation. A monthly annualizer is not a daily one.
- Those methods multiply the whole DataFrame by the annualizer, including diagnostic columns such as
  `zstar_drv1`. An annualized table's derivative column is not automatically the raw 1.8 factor.
- The README example highlights order 2 outputs; the paper's empirical choice is order 1 because higher-order
  confidence bands are unstable at its ordinary sample sizes. The adjusted order 1 upper output is
  `multi_ub_diagcorr`; an arbitrary `u_2` column is not a faithful reproduction of that procedure.
- The implementation normalizes the ridge grid to an average eigenvalue and suggests scaling by `P/T`.
  Paper-code normalization/centering/parity must be reconciled before an empirical replication.
- `multi_ub_diagcorr_pt` explicitly becomes the benchmark lower point estimate on the corner branch.
  That branch supplies no independent upper point estimate. Numerical clipping and asymptotic inference
  require separate validation before use on a new data-generating process.

## Material limits and source inconsistencies

1. **Tightness is partly constructed.** Figure 3/p 37 reports corner use in 97% of rolling windows for both “all”
   and “all ex micro.” Algorithm 2/Appendix K selects a threshold that makes the upper point equal the lower
   benchmark on this branch. The authors acknowledge this on pp 32,35,37 and 43. The upper-bound condition
   remains an assumption; passing its necessary consistency check does not prove it. The lower estimator
   avoids that extra condition but still relies on its own statistical assumptions.
2. **Statistical assumptions are material.** Assumption 1 assumes stable means/covariance and iid standardized
   innovations; p 10 explicitly calls the within-window iid premise an approximation. Confidence inference
   additionally uses random-design mean assumptions and finite 8-plus-epsilon moments (p 26). The confidence
   claim is unconditional under that model, not a general guarantee for a selected, serially dependent,
   changing-regime futures strategy book.
3. **Source consistency needs reconciliation.** p 38 prose says equities 7.7 to stocks-plus-bonds 8.7. Figure 4's
   all-universe duration-hedged boxes instead show 7.46 to 8.23 (p 39), with overlapping displayed confidence
   bands. These are not interchangeable empirical results. The source itself says simulated relative errors
   compare against a stock-level conditional oracle, which differs from the unconditional managed-portfolio
   estimand (p 191); that is not exact coverage verification of the target. On p 22, Eq 40 compares squared
   Sharpe to an unsquared SDF coefficient of variation, and Eq 41 uses the squared-Sharpe lower bound in
   the unsquared HJ inequality. These appear to require notation clarification relative to Eq 39. This review
   does not treat them as a refutation of the main theorems.
4. **Research clocks and selection are not our frozen protocol.** p 28 chooses characteristics using full-sample
   missingness, then ranks and fills residual missing characteristic values with the median. pp 41–42 admit
   characteristics by publication year. That does not certify exact month-level publication/receipt or original
   accounting-data vintages. Source preprocessing is not permission to use future-selected fields or impute
   our missing price returns. The full-sample frontier estimate is not a frozen 2018–22 strategy tested once
   on previously seen 2023+history.
5. **No account bridge exists.** Gross monthly stock/bond frontier estimates omit a tested native futures
   gross-to-net, margin, integer-lot, intraday floor and payout path. No evaluation/funded/personal earnings
   projection or BASE/ADD/REPLACE/EMPTY benefit can be inferred.

## What was independently checked

Run `/workspace/venvs/thebeginning/bin/python analysis/codex_hidden_sharpe_source_audit_20261107.py`.
[Script](../../../analysis/codex_hidden_sharpe_source_audit_20261107.py),
[audit output](../inputs/hidden_sharpe_7679420_20261107/source_audit.json),
[source claims/transcriptions](../inputs/hidden_sharpe_7679420_20261107/source_claims.json),
[access and pinned code receipts](../inputs/hidden_sharpe_7679420_20261107/access.json),
[evidence sheet](../evidence/hidden_sharpe_7679420_20261107.md).

The script checks source/code hashes, the population-series identity and lower-bound gradient on a fixed
algebra fixture, the square-root shortfall arithmetic, and selected static code behavior. Its PASS means only
those checks passed. It is not a simulation of tradable returns, proof/CLT validation, empirical reproduction,
economic verification or artifact admission for a return test.

New market-return hypotheses/definitions:0/0. Scout counts remain 4/10 hypotheses and 10/30 definitions;
existing trials/notifications and the separate unfinished discovery continuation are preserved. No lease was
claimed or released because no return proposal was admitted. No MultiCharts/live/trading/plan change.

For Claude: review this report, especially the corner-bound interpretation, figure/text discrepancy and
paper-to-code units before any later research-tool adoption. Independent economic verification remains pending.
