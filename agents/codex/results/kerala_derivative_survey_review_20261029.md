# Kerala derivative-trader survey: DON'T TEST as a strategy
Summary: This May 2024 paper describes self-reported trading practices among 300 Kerala equity-derivative traders.
It measures questionnaire responses, not verified returns, drawdowns or strategy profitability.
Only 130 of 300 agree/strongly agree that they prefer selling options; the paper's majority wording overstates this.
No executable edge or current-plan improvement is established; no deeper strategy test or queue entry recommended.

Source: Dr. Subeesh V. K. and Dr. Liya K., *An Analysis of Trading Strategies of Equity Derivative Traders in Kerala*,
International Education & Research Journal, volume 10, issue 5, May 2024, pp.132–136.
[SSRN 4921835](https://ssrn.com/abstract=4921835), user-uploaded PDF.
SHA256: `f292056fa12989d44e499432a43e6579e2fa39a72b2cff961b46e86894ac6ed7`.
Review date: 2026-10-29. Source-only review, not independently replicated. New return trials: **0**.
Repo context: codex/work `358fbc5a5526719e742e35b8c0eb77014a1c76f0`.

## 1. What is it about?

An emailed Google Forms questionnaire of 300 equity-derivative traders in Kerala, India.
Respondents rate agreement with statements about stop losses, risk/reward ratios, foreign indices, option selling,
algo trading, Greeks, put/call ratios, implied volatility, India VIX and costs.
The authors compare questionnaire scores across demographic and knowledge groups using t-tests and ANOVA.
No instrument-specific entry/exit protocol or account P&L dataset is tested.

## 2. What does it find?

Table 1 (p.133) reports these counts; agreement means Agree plus Strongly Agree, not independently observed behavior:

| Statement | Agree | Strongly agree | Total agreeing / 300 |
|---|---:|---:|---:|
| Decide a stop loss for every position | 47 | 128 | 175 |
| Prefer index derivatives over stock derivatives | 83 | 130 | 213 |
| Decide risk/reward for every trade | 89 | 104 | 193 |
| Prefer selling options to buying options | 42 | 88 | 130 |
| Always use an algo system | 8 | 13 | 21 |
| Trade based on foreign stock-index movements | 42 | 89 | 131 |

A mean questionnaire score above the neutral midpoint of 3 is not proof that a majority agrees.
The text's majority claims about option writing and foreign indices are not supported by the agreement counts:
130 and 131 of 300 respectively are below half. Its t-tests concern means, not profitable-trade rates.
Knowledge and some demographic groups differ in questionnaire scores; this does not establish causal effects
on technique use or prove that knowledgeable respondents earn more.

## 3. Why does it make money, if it does?

**The paper does not show that any surveyed practice makes money.** It contains no verified net P&L,
win/loss distributions, fees, margin analysis, forward test or comparison of profitable versus losing respondents.
The conclusion's suggestion that option writing gives better risk/reward than buying is unsupported by these data.

Selling options receives premium in exchange for contingent liabilities; receiving premium is not itself an edge.
Its attractiveness depends on option pricing, realized moves, hedges, costs and tail losses.
No volatility-risk-premium estimate is provided here. Stops and risk/reward plans likewise do not establish positive expectancy.

## 4. Can we build on it?

It can inform a survey of trader practices, but it is a weak foundation for our next strategy.
The data concern regional Indian equity-derivative respondents, not executable ES/NQ flows.
There is no forced participant, signed demand, known trading deadline or residual price response to exploit.
Neither buying what respondents like nor fading their preferences follows from the evidence.

Most useful prompts—track costs, define risk, examine execution and test external information—already exist in our process.
Turning foreign-index monitoring, IV or option selling into a rule would require a separate economic hypothesis,
point-in-time market data and its own evidence/preregistration. This survey does not pick a direction, horizon,
threshold or worthwhile candidate among those broad topics.

Sampling frame, response rate, collection dates and representativeness are not sufficiently established to extrapolate
to all Kerala traders or today's U.S. futures market. Self-report and selection biases remain.
Significance of an agreement score cannot substitute for economic magnitude or net strategy returns.

## Decision and next step

**DON'T TEST as a trading strategy.** No deeper strategy investigation is justified by the survey alone.
No strategy evidence sheet or verification-queue entry: no specific candidate has demonstrated a useful merit.
TIER_LIST and the current TODO queue were checked at the pinned head; no matching paper was found.
No backtests, data purchases, MultiCharts code, allocations or live/VPS changes were made.
Portfolio contribution, Sharpe, payouts and blow-up risk are unmeasured, not zero.

For Claude: `agents/codex/results/kerala_derivative_survey_review_20261029.md`.
