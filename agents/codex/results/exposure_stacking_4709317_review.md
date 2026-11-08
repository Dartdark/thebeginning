# Exposure Stacking: research-tool reference, no portfolio adoption justified

Summary: The method learns weights for combining portfolios optimized under sampled inputs.
The source's favorable comparison is a small Gaussian experiment, not historical net trading.
The notebook measures return/variance; its fold objective uses reduced, unnormalized exposures.
Constructed checks confirm those interpretation limits, not historical failure or superiority.
Retain as an allocation-method reference; no strategy, sizing, live or trading-plan change.

Source: Laura Kristensen & Anton Vorobets, *Portfolio Optimization and Parameter
Uncertainty*, SSRN4709317, uploaded version dated February 4, 2026; first version
January 30, 2024. Read all 15 pages, including Appendices A/B.
Owned PDF and public author notebook: `agents/codex/inputs/exposure_stacking_4709317/`.
Hashes, source URL and license: `manifest.json` in that directory.
Audit: `analysis/codex_exposure_stacking_4709317_audit.py`;
results: `analysis/outputs/codex_exposure_stacking_4709317/checks.json`.
Return trials: **0**. Source inspection and constructed mathematical checks only.

## 1. What is it about?

Portfolio weights are highly sensitive to uncertain expected returns. The paper
generates portfolios under sampled market models, then combines their exposures.
Equal-weight resampling averages them; the proposed Exposure Stacking learns
nonnegative combination weights summing to one with a quadratic program.
It can in principle mix optimizers such as mean-variance and mean-CVaR, although
the illustrated comparison uses mean-variance only.

This is an allocation estimator, not an entry/exit signal. Its inputs would be
the already-admitted investment or strategy universe, scenarios/parameters,
constraints and risk targets. Those choices do not become validated through stacking.

## 2. What does it find?

The author simulation finds expected-mean uncertainty most influential on portfolio
exposures. Its main comparison uses 1,000 sampled efficient frontiers, 100 Gaussian
estimation observations, nine portfolios/frontier and the middle portfolio.
It compares equal averaging with 2-fold, 5-fold and leave-one-out stacking, then
evaluates risk/return using another 1,000 simulated samples (pp.5–8).

The authors report 2-fold stacking with lower risk and similar return to equal
resampling; 5-fold has higher risk and return, while leave-one-out is almost
identical to averaging. They explicitly call the study small/simple and defer
conclusions about practical gains. These are **author numerical findings**, not
our reproduction or evidence of an after-cost historical Sharpe improvement.

### Verified implementation and interpretation cautions

1. **The notebook statistic is mean/variance.** Its `risk_return` stores
   `pf @ cov_run @ pf`, then divides mean by that variance. This is not Sharpe,
   which divides excess mean by standard deviation. In a constructed example,
   halving exposure changes mean/variance from 2.5 to 5 while zero-rate
   mean/standard-deviation remains 0.5. This does not claim the actual source
   portfolios differ only by leverage; it shows why the metric must be named.
2. **Fold exposure has a budget mismatch.** Equations (3)/(4) and the notebook
   zero held-out rows but keep one global weight simplex; the remaining weights
   are not renormalized within each fold. With four identical fully invested
   portfolios `[0.6, 0.4]`, uniform weights and two equal folds, the fold
   prediction has total exposure 0.5 while its target has exposure 1. The
   mean squared exposure error is 0.13 despite identical inputs. An illustrative
   renormalized fold prediction gives zero error. The **final full-weight
   portfolio still has budget 1**; we do not claim the final allocation is
   mechanically half invested. The published objective is well-defined but is
   not ordinary same-budget held-out prediction. Renormalization is a different
   objective, not an automatically justified repair or a tested replacement.
3. **Equal weights need not be unique.** Appendix A shows equal weights satisfy
   the naive problem's KKT conditions. It does not establish uniqueness. For
   duplicated exposures `[1,0],[1,0],[0,1],[0,1]`, weights `[.25,.25,.25,.25]`
   and `[.5,0,.5,0]` yield the same `[.5,.5]` exposure and objective 0.5.
   Thus equal averaging is optimal for that naive objective, but not necessarily
   the only sample-weight representation.
4. **Terminology about unbiasedness is limited.** Solving the supplied model's
   optimization problem exactly is different from statistical unbiasedness for
   the unknown true optimal allocation. Nonlinear optimization can transform
   unbiased input estimates into biased exposure estimates. The paper's stated
   definition should not be interpreted as proving absence of estimation bias.
5. **Monte Carlo samples are not chronological market validation.** Partitioning
   independent simulated exposures is reasonable for that experiment; it is
   not a past-only rolling allocation test on real strategy returns. If derived
   from a common historical panel, shared estimation history remains shared.
6. **Notebook scope is pinned and limited.** We fetched the paper-linked notebook
   from mutable `main` on November 8, 2026 and retained its SHA-256. Its helper
   explicitly recommends the library `ft.exposure_stacking` instead. We inspected
   that helper and comparison code, not the current library implementation, and
   did not run its full 1,000-frontier study. Claims above apply to the inspected
   notebook and printed equations, not all package releases.

## 3. Why does it make money, if it does?

It provides no new alpha source. The proposed benefit is reduced allocation
estimation error by combining unstable optimized portfolios. That could improve
risk-adjusted investment outcomes, but fitting weights to exposure similarity
does not directly optimize net payouts, future returns or account survival.
There is no identified forced trader, signed flow, executable timing edge,
historical cost bridge or live benefit. CVaR recommendations are not proof of
tail-risk forecasting or of future worst-loss bounds.

## 4. Can we build on it?

As a **research allocation tool**, potentially; no current adoption is earned.
The missing item is convincing economic/chronological validation, not a new
market-price dataset to buy. Neither a promising-strategy queue entry nor a
DATA_NEEDED request is justified solely by this methods demonstration.

A separately justified allocation experiment would freeze the strategy universe,
past-only estimation and refit schedule; compare existing weights, equal allocation,
equal resampling and stacking at matched risk/capital; include realistic turnover,
native fees, margin, integer quantities and chronological account constraints.
Selection of folds/risk measures is additional fitting, not a free robustness check.
Already-seen strategy history remains historical validation. Source exposure-error
improvements cannot replace BASE/ADD/REPLACE/EMPTY account comparisons.

For Apex, averaging valid integer contract allocations can create fractional
positions, and rounding changes the result. Shared convex constraints can survive
a convex mixture when defined under the same model; integer sizing and pathwise
account-floor rules require separate replay. A historical CVaR constraint is not
an intraday liquidation guarantee. Do not apply these weights to live charts.

These caveats stop a new portfolio-return search here. No model-selection rescue,
funded bench, allocation change or new automation is launched from this upload.
No new measured fill/slippage/order-handling evidence warrants a separate
execution-library entry; keep this as a portfolio-method reference.

## 5. Can strategy code be made?

**Yes as an allocation/research module; no standalone directional strategy is
specified.** Public Python replication code exists and the paper gives a QP.
A module would accept admitted asset/strategy scenarios, generate constrained
sample portfolios, partition them, solve for mixture weights and output target
exposures. Its input conventions, fold interpretation and chosen metric must be
explicit. A live implementation additionally needs native integer sizing,
rebalance/cost accounting and account-risk checks. Code feasibility is not profit
evidence. This review implements only the bounded mechanics audit, not a new
portfolio optimizer or trading signal.

## Verification and reproduction

Downloaded the original notebook without executing it; retained its GPL notice.
Inspected the paper, public comparison/helper and all equation appendices.
Verified three deterministic constructions with NumPy and source-code checks.
No author forecast distribution/figures, historical return series or independent
economic verification reproduced. Reproduce the checks with:

```sh
python analysis/codex_exposure_stacking_4709317_audit.py
```

Source-suggested experiments are proposals, not instructions executed here.
No plan, tier, order, size or live setup changed.

For Claude: `agents/codex/results/exposure_stacking_4709317_review.md`.
