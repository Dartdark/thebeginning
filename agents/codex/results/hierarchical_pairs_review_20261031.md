# Hierarchical futures pairs: DON'T TEST for current portfolios

Summary: DTW clustering, cointegration and Kalman/half-life signals trade Chinese daily futures pairs.
Authors claim validation annual return 13.318%, Sharpe 4.19 and maximum drawdown 1.359%, with uniform 0.1% commission.
Printed formulas, fitting boundaries and tradable-contract/cash accounting prevent trustworthy replication.
No new economic reason overturns our prior index-pairs failures; owned markets differ from the source universe.
Keep the model-versus-execution lesson; no new return test, portfolio comparison or promising-strategy queue entry.

Source: Shuo Yang, Ke Huang and Yao-wen Chen, *Research on Hierarchical Futures Pair Trading Strategy Based on
Machine Learning and Kalman Filtering*, SSRN 5017127. Read all 38 uploaded PDF pages, including Appendix A and
references. The document explicitly identifies itself as not peer reviewed. Indexed
[SSRN metadata](https://papers.ssrn.com/sol 3/papers.cfm?abstract_id=5017127) lists the 38-page posting on 2024-11-11;
an earlier 37-page version/related SSRN 4863414 was not read and is not a separate new family.

[Archived PDF](../inputs/hierarchical_pairs_20261031/ssrn-5017127.pdf) ·
[raw text](../inputs/hierarchical_pairs_20261031/full_text.txt) ·
[source claims](../inputs/hierarchical_pairs_20261031/claims.json) ·
[access/data-route receipt](../inputs/hierarchical_pairs_20261031/source_access.json).
[Arithmetic/header audit script](../../../analysis/codex_hierarchical_pairs_review_20261031.py) ·
[outputs](../../../analysis/outputs/codex_hierarchical_pairs_review_20261031/arithmetic.json) ·
[input receipt](../../../analysis/outputs/codex_hierarchical_pairs_review_20261031/owned_input_receipt.json) ·
[hash manifest](../../../analysis/outputs/codex_hierarchical_pairs_review_20261031/manifest.json).

Plan: none admitted. New economic return definitions/reservations/trials/account simulations: **0**.
This is a direct uploaded-paper review, not a new scout cycle. No progress lease, budget, earlier selection history,
paused t 6 or Strategy Hunt v 2 state was changed. Deterministic arithmetic is not a historical market test.

## Four questions

1. **What is it about?** Selecting Chinese futures pairs through Dynamic Time Warping and three-cluster k-means,
   screening within clusters for cointegration, then trading a dynamically estimated spread using Kalman filtering,
   a half-life-sized z-score window and delayed entry as a deviation begins reverting.
2. **What does it find?** Authors report experimental annual return 12.964%, Sharpe 4.35 and drawdown 2.396%; their
   validation reports 13.318%,4.19 and 1.359%. A classical same-pool comparator reports 6.326%,1.40 and 3.234% in
   validation. These are author claims, not independently reproduced net futures results. Our checks establish
   printed formula problems and unresolved reporting/accounting conventions, not corrected performance.
3. **Why could it make money?** If a genuinely stable economic relationship links the prices, temporary relative
   deviations may converge enough to exceed both legs' costs. The authors propose that clustering finds stable
   pairs and filtering improves timing. Those modeling tools do not themselves create a cash-flow obligation,
   prove mispricing, or explain why unrelated selected commodities must reconverge. No forced flow is identified.
4. **Can we build on it?** Retain conditional methodology, especially causal fitting and separation of a model
   residual from executable P&L. Do not prioritize a new strategy or data purchase from this paper. It lacks a
   credible specific new owned-data-compatible economic case and cannot be replicated without material guesses.
   Changing it to NQ/ES would revisit already weak/rejected pairs evidence rather than reproduce these results.

## Rule and chronology as described

JoinQuant daily data cover January 4,2016–November 20,2023 across Chinese exchanges (PDF 7–8). The authors describe
dominant continuous series, acknowledge position-weighted construction and nontradability, and say actual maturity
contracts/roll costs are needed in practice. Table 1's selected codes end in 8888; their exact provider construction
must be pinned. No assurance that a weighted synthetic close is a tradable dated-contract price.

Normalize clustering data, compute a DTW distance matrix, apply k-means and choose K using silhouette score.
Appendix A reports K=3/score 0.54. Within clusters select Engle–Granger cointegration p<0.05, yielding 25 pairs across
30 distinct futures (source counts). Some pairs combine economically distant assets, such as Chinese stock-index
and ferrosilicon futures or gold and soybean meal. Historical statistical selection needs more economic support
and multiplicity checks than a raw 5% threshold provides.

Use Kalman time-varying hedge estimates; calculate rolling spread z-scores using estimated half-life as window.
Entry is on **crossing back** above−1.25 for a long spread, or below+1.25 for a short spread (PDF 19–20). Given
z_c=−0.08, the printed rule closes a long near−z_c=+0.08 and a short near z_c=−0.08. It is not simply “enter on
first touching two standard deviations.” There is no reproducible maximum holding time or hard stop policy.
Paper wording on delayed entry sometimes says maintain a short position where the intended flat/wait state is
unclear; source code is needed to resolve actual behavior.

The authors distinguish clustering, parameter-testing and final-validation sets, but exact clustering/fit
boundaries, transformations, half-life fit/re-estimation dates, and frozen Kalman hyperparameters are not supplied
well enough for a chronological rebuild. They explicitly tried entry/exit thresholds and tuned noise parameters.
Their experimental endpoint is May 20,2022; validation extends that boundary to November 20,2023. The start of the
experimental result is not unambiguously fixed, though the narrative calls it a five-year backtest. No claim is
made here that full-sample leakage was proved; its absence is also unverified. Fixed asset pool is an admitted limit.

## Reported statistics — not our backtest

| Metric | Experimental | Validation, after May 20,2022 through November 20,2023 | Classical validation |
|---|---:|---:|---:|
|Annual return|12.964%|13.318%|6.326%|
|Cumulative return|67.068%|19.556%|9.237%|
|Sharpe|4.35|4.19|1.40|
|Maximum drawdown, magnitude|2.396%|1.359%|3.234%|
|Annual volatility|2.812%|2.998%|4.466%|
|Alpha / beta|0.13 /0.01|0.14 /0.02|0.07 /0.03|

Sources: Table 3/PDF 23; section 5.1/PDF 25 and Table 5/PDF 26. The conclusion instead says 13.314% for validation;
use the main-text/table 13.318% while retaining that inconsistency. The headline comparison is a bundled model
comparison on the same asset pool, not isolated proof that DTW, Kalman or half-life individually create alpha.
No trade count, win rate, profit factor, reconciled daily ledger or actual-size account payout record is supplied.
Metric boxplots are not independent confidence intervals or proof of generality.

**Costs are not simply omitted:** PDF 27 says a uniform one-thousandth commission rate was applied. Its notional/
margin basis, per-leg/per-side application, fees for hedge rebalancing, rolls, slippage and delayed execution are
not reconciled. Thus 0.1% should neither be labelled our verified all-in cost nor replaced by a guessed CME fee.

## Source problems independently checked

- **Spread scale:** Eq 11/PDF 19 visibly takes the square root of the average **unsquared** deviations, with
  inconsistent window indexing. This is not standard deviation. On a consistent window, deviations from its mean
  sum to zero: invented values 1,2,3,4 give that expression 0 rather than actual population SD≈1.118. The equation
  cannot establish valid z-scores as printed. It may be a typo; no claim that unavailable author code used it.
- **Covariance:** PDF 20 defines a parameter as delta/(delta−1) times an identity matrix. For 0<delta<1 this is a
  negative multiple, invalid as a covariance. An invented delta 0.1 gives−0.1111 on each diagonal. Their actual delta
  and code are unknown. Silently replacing this by delta/(1−delta) would make a new implementation assumption.
- **Annualization:** if 67.068% is compounded wealth growth over exactly five calendar years, its CAGR is≈10.81%,
  not 12.964%. The reported pair of numbers implies≈4.21 years if the annual figure is CAGR. Different starts,
  annualization/day-count conventions or an arithmetic annual return could explain a mismatch; no exact daily
  ledger permits reconciliation. This is a conditional check, not an assertion of corrected strategy performance.
- **Cash versus residual:** a change in estimated beta redefines `Y−beta*X`; it is not automatically a gain on
  held contracts. With both prices constant 100, beta moving 1→0.9 makes that residual rise 0→10 while held-book
  price P&L is 0. This invented example is an accounting requirement, not proof the authors made that P&L error.

Other replication gaps include noncausal interpolation risk (PDF 13 explicitly permits interpolation/forward fill),
unreported exclusions and stale legs, DTW constraints/distance-matrix embedding details, Kalman initialization and
Q/R, half-life estimation/caps, fit-versus-filter versus smoothing, exact decision/fill clocks, signed integer
quantity/multiplier conversion, margin/FX cash, legging, simultaneous pairs sharing contracts and all costs.
Fixing equations and choosing defaults before a future test is possible, but is a declared adaptation requiring
its own evidence; it would not independently reproduce this paper.

## Owned-data fit, prior research and disposition

Owned filename/header inspection finds no selected Chinese exchange panel. NQ/ES/YM/GC/CL/ZN are different markets;
in particular our ZN Treasury series is not the source's ZN 8888.XSGE zinc. An official JoinQuant SDK/provider-manual
check found an authenticated data route, not an owned/free downloadable replication package; no account, login,
credential access, purchase or contact was attempted. Bounded indexed title/code searches found no author
implementation. SSRN direct open returned 403 and was not retried; the owned upload supplied the full source.
There is no new worthwhile lead justifying a prolonged data hunt here.

TIER_LIST's *Beta from A to Z* study already tested Kalman index-pair variants with poor results. Its separate
signature-pairs study reports four CME combinations losing after both-leg costs. Those are prior repository
results, not rerun here and not proof every possible commodity pair fails. This paper supplies no matched modern
CME evidence or independently justified pair to overturn that family history. DTW is a selection method rather
than a new economic cause to reuse failed definitions.

| Home | Result of this review |
|---|---|
|50K/150K evaluation|No eligible strategy: source Chinese contracts/daily holding protocol do not establish intraday Apex fit|
|50K/150K funded|No eligible strategy; no BASE/ADD/REPLACE/EMPTY, payouts, breach probability or completion-time test|
|Personal|No admission: underdetermined source implementation, non-owned markets, no demonstrated incremental net edge|

No design gross/cost screen, historical validation, placebo/random-drop test, Monte Carlo or independent economic
verification ran. No code/stop change or portfolio allocation follows. **DON'T TEST now; no TODO queue entry.**
Deeper strategy investigation is not warranted from this source as it stands. Reconsider only with genuinely new
author code and contract-level cash/price/clock evidence or a distinct economically justified owned-market pair.
Retain [execution reference E44](../EXECUTION_REFERENCES.md#e 44--dynamic-pair-models-are-not-self-financing-contract-ledgers).

For Claude: `agents/codex/results/hierarchical_pairs_review_20261031.md`.
