# Variance risk premia: WATCH for monthly personal research; no intraday test
Summary: Zhou reviews variance-risk-premium forecasts across equities, bonds, currencies and credit.
S&P 500 monthly regressions, 1990–2016: three-month adjusted R² 9.61%, overlap-robust t 7.22.
This is in-sample predictive evidence, not a net strategy backtest or proof of an intraday ES/NQ edge.
Queue a source-parity/data check for monthly personal equity exposure; no return test or account change now.

Source: Hao Zhou, *Variance Risk Premia, Asset Predictability Puzzles, and Macroeconomic Uncertainty*,
16 May 2018, [SSRN 1783624](https://ssrn.com/abstract=1783624), uploaded PDF.
SHA256: `b44634a945a4e3aebf57f2c8ea8e8711164a46c8dbc9d88b5569321a6df8e315`.
Date: 2026-10-29. Repo snapshot: `fd8a54f386752423aba0dfdb19ad2d4a4659b694`.
Evidence: source review and source-code inspection only; empirical results not independently reproduced.
New return trials: **0**. [Evidence sheet](../evidence/variance_risk_premium_20261029.md).

## 1. What is it about?

The variance risk premium (VRP) is the risk-neutral expected future variance minus its physical expected value.
The paper reviews its ability to forecast asset returns/spreads and models linking it to uncertainty compensation.
Its “short run” is typically one to six **months**, not minutes or one trading session.

The theoretical expectations are latent. The empirical proxy is option-implied variance minus **trailing** realized
variance, both available at the decision time (pp.4–5). It is not implied volatility minus realized volatility.
For the monthly SPX illustration, Figure 1 (p.27) uses end-of-month VIX squared divided by 12 and prior-month
five-minute realized variance including overnight close-to-open returns, with compatible units.
The caption's wording around 78 intraday intervals plus overnight should be resolved from the original data/code
rather than silently choosing an implementation.

## 2. What does it find?

| Source result | Meaning and limitation |
|---|---|
| Table 1, p.23, S&P 500, Jan 1990–Dec 2016: three-month VRP slope 0.45, t 7.22, adjusted R² 9.61%. | Positive conditional equity premium; monthly observations with overlapping future returns. Hodrick-style overlap-robust t, not a strategy t-stat. |
| Adding log P/E: three-month adjusted R² 11.36%, VRP t 7.32. | Complementary explanatory information in this sample; no walk-forward portfolio result. |
| Table 1 one-month adjusted R² 4.93%, VRP t 5.20; 24-month adjusted R² 0.83%, t 1.68. | Forecast strength peaks near a quarter and fades; horizon selection/generalization needs separate validation. |
| Table 2, p.24, 1990–2008: six-month T-bill excess returns predicted over one-/two-month holds, t 3.23/2.03. | Short-maturity bonds, not automatically ZN futures. Prose says 2.02 for the second t; table says 2.03. |
| Table 3, p.25, 2000–2011: adding world currency VRP gives four-month R² 8.95%, an 8.00 percentage-point gain over interest differentials. | World currency VRP is not U.S. equity VRP; the paper notes different directional implications for these measures. |
| Table 4, p.26: firm VRP predicts next-period CDS spreads with rating-specific controls. | CDS spread prediction is not a demonstrated excess-return strategy or direct index-futures demand. |

Tables 2–4 summarize/reproduce cited studies; Table 1 updates the equity sample. No net trading ledger, Sharpe,
drawdown, costs, account payouts or implementable position-size policy is established by these tables.
Regression fit cannot be translated into “9.61% profit” or a win probability. Robust errors address dependence
under assumptions; they do not create an out-of-sample test or eliminate specification/publication selection.

## 3. Why does it make money, if it does?

The proposed economics are compensation for bearing uncertainty and adverse states. Investors pay for insurance
against variance/jump/tail shocks; higher insurance premia may coincide with higher required equity returns.
Recursive-preference models price volatility uncertainty; alternatives include jumps, disasters, habit and ambiguity.
These are interpretations/models, not independently identified causal trading flows.

Two distinct trades must not be confused:
- Equity allocation based on VRP seeks a higher conditional **equity** premium.
- Selling variance/options seeks the insurance premium and carries direct convexity/tail exposure.

A positive VRP does not guarantee either trade profits after costs. A high-VRP equity position can lose heavily
during a crisis before compensation arrives. The paper's model-positive VRP follows assumptions; the observed
implied-minus-lagged-realized proxy can be negative or contain forecast error.
It need not isolate “pure uncertainty” outside the structural model. The paper does not identify a compulsory
order, its dollar size or its intraday transmission into ES/NQ.

## 4. Can we build on it?

**Yes, a limited deeper source/data check for monthly personal equity allocation is warranted.**
The merit is a specific positive forecasting relation at an investable equity horizon, with strong reported
overlap-adjusted evidence and complementary information to valuation. It is not merely a missing-data idea.
This is a research lead, not a fully specified portfolio rule.

Smallest next step: obtain/pin the author or original-study monthly IV/RV series and construction code; establish
historical publication/availability times and unit/session conventions. The paper advertises an author homepage;
its current availability, licence and data cost were not verified. Check the exact target-return/risk-free definition
and whether the displayed multi-month returns are annualized before reproducing coefficients.

Repository VIX and SPY daily files exist, but directory presence is not an audit of coverage or as-of availability.
SPY daily returns or NQ/ES futures intraday variance would be **proxies**, not exact SPX five-minute source parity.
No verified source-parity SPX intraday RV or archived author monthly VRP series was identified.
Resolve these issues before committing a bounded preregistration and running returns. Then test an explicitly
defined exposure mapping, execution timing, integer sizing and costs against buy-and-hold and VIX-only/RV-only
baselines. Fit any model using matured labels and training-only data; use overlap-aware inference and purged splits.
A new threshold, holding period, SPY/futures substitution or allocation cap is our adaptation, not the paper's strategy.

### Prior work and duplication

TIER_LIST already has a different contrarian VRP ETF paper (SSRN 4841308), VIX regime tilts and implied-volatility
exit/sizing tests. They do not independently replicate this monthly equity relation.
[analysis/vix_regime.py](../../../analysis/vix_regime.py) uses a ten-day volatility difference and term-structure
regimes, with documented proxy fallbacks; that is not this paper's monthly variance difference.
[Implied Variance Budget Breach](implied_variance_breach.md) failed its frozen intraday design tests.
Do not revive that strategy or reuse its significance as evidence for this source.
TIER_LIST, WATCHLIST and TODO were checked at the pinned head; no exact SSRN/title replication identified.

### Placement and next gate

| Home | Present verdict |
|---|---|
| Personal portfolio | WATCH / NEEDS DATA: monthly equity-exposure lead queued; no allocation or account benefit established. |
| 50K funded | No eligible addition from this paper: no intraday rule, costed test or account comparison. |
| 150K funded | Same lack of qualification; no payout/risk result inferred from 50K. |
| 50K evaluation | No eligible addition; multi-month exposure conflicts with the intraday remit. |
| 150K evaluation | No eligible addition; no pass-rate or timing benefit measured. |

Account benches were not run; these verdicts are not measured harm to the five plans.
Multi-month exposure shares equity risk with the personal book; diversification and crisis loss timing remain unmeasured.
No options-selling strategy, account-size rescue, PowerLanguage implementation or trading-plan change is proposed.

Execution/measurement lesson retained in [the reference library](../EXECUTION_REFERENCES.md): high-frequency
realized variance can contain microstructure noise, and variance inputs must use compatible units and clocks.
This does not supply a spread estimate or execution saving.

For Claude: `agents/codex/results/variance_risk_premium_review_20261029.md`.
