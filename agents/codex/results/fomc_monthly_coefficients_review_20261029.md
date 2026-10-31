# Beyond the Announcement Window: WATCH for research methods; no strategy established
Summary: The uploaded FOMC paper is useful for attribution and data-timing controls, not a ready trading rule.
Its 1988–2023 baseline has 256 single-announcement months; the two-day window's estimated share is 33% on the published shock series.
The S&P 500's thirty-minute share is 22–35%; these are regression-coefficient shares, not returns or profitable-trade rates.
Payroll/CPI-day returns predict a later policy surprise in-sample, but no executable stock-return strategy is validated.
Keep current plans unchanged; do not rerun rejected FOMC rules or add a strategy-queue entry from this evidence alone.

Date: 2026-10-29. Review only. Plan / backtest script: not applicable. New return trials: **0**.
Evidence sheet: [fomc_monthly_coefficients_20261029.md](../evidence/fomc_monthly_coefficients_20261029.md).

## Source and scope

Saurabh Ahluwalia, *Beyond the Announcement Window: What Monthly FOMC Regressions Measure*.
[SSRN 7674953](https://ssrn.com/abstract=7674953), user-supplied 108-page PDF, marked not peer reviewed.
SHA256: `f7a297404ce44c9f5fb096c572b9ce136be8eab26c460983d5a8ebed3ead191e`.
Findings below are attributed to the uploaded version, not independently reproduced.
The PDF has two preliminary pages; printed page numbers below differ from PDF viewer positions by two.
Repo context: codex/work `c8b35a5928f5026283759bc7ff74679f4106f0a0`; Claude head inspected
`fac3eb86b02d50443bcc625179009d3c10a84339`. Authoritative rules and queue inspected on codex/work.

## What the paper actually measures

It asks whether a monthly stock-return regression on FOMC surprises measures an announcement response.
On the same observations, with identical regressors and controls, additive log returns imply:

`monthly coefficient = before-announcement coefficient + window coefficient + after-window coefficient`.

This exact accounting identity does not by itself identify causation or a tradeable prediction.
The main portfolio is a capitalization-weighted U.S. nonfinancial stock universe; some tests use the S&P 500
and French factors. It is not an NQ or ES strategy backtest.

## Decisive source results

| Source result | Interpretation and limit |
|---|---|
| Table 1, printed pp.35–37: 256 months with one scheduled announcement, 1988–2023. Published-series coefficients before/window/after are about −11.8/−7.4/−3.3, totaling −22.5 percentage points per 100 bp of surprise. | These are conditional regression slopes. They are not average returns obtainable by buying or selling on those days. |
| Table 1 and abstract: two-day share 33% on the published series; 37–63% on eight alternatives. Every two-day-share 95% confidence set includes 50%. | Concentration relative to the number of event days does not establish that most of the monthly coefficient lies in the window. Nor do the estimates establish that most lies outside it. |
| Table 1 Panel D / conclusion: the thirty-minute S&P 500 share is 22–35%. | This does not mean the remaining 65–78% is available as a drift trade after the announcement. The remainder includes earlier returns and other news. |
| Table 3, printed pp.45–46: ending the 65-day S&P predictor before the month changes the pre-announcement coefficient from −11.8 to −6.8; window coefficient barely changes, −7.4 to −7.3. | Part of the larger monthly estimate comes from how the shock is constructed. The change is significant holding the shock series fixed, but its interval includes zero after uncertainty in both orthogonalizations is included. |
| Table 4 Panel C / section 3.4, printed pp.59–63: market release-day return predicts the later raw surprise with slope −0.63 bp per 1% return (t≈−1.9), or −0.84 with six controls (t≈−3.0). | Prediction target is the later interest-rate surprise, not the stock return after an executable entry. These are in-sample regressions, not walk-forward P&L. |
| Section 3.4, printed pp.62–63: release-day covariance is larger after the cash open in point estimates, but before/after-open differences are imprecise. | This does not select an entry time or prove that waiting until the open leaves an edge. |

The two-day window includes the announcement day and next trading day, restricted to the month.
Forty-four of the 256 baseline windows also contain payroll or CPI releases (introduction, printed p.8).
Section 4 shows sensitivity to multiple-announcement months and exceptional 2020 observations.
These are reasons to report sample composition, not to discard difficult events to improve a trade result.

## Implications for our research

1. Attribute event-related results to separate pre-event, statement, press-conference and later-return windows.
   Use the same events and controls so the components reconcile; define non-overlapping boundaries first.
2. Check shock construction as well as input timestamps. A statistically cleaned surprise can share price inputs
   with the return being explained. Historical residualization or PCA also needs training-only estimation if used
   as a predictive feature. The paper's decomposition is valid as retrospective measurement; a backtest has a
   stricter information clock.
3. Keep future surprises as labels until the full measurement window has elapsed. A surprise measured over a
   thirty-minute window cannot justify a fill at the start of that window. Press-conference information has its own clock.
4. Distinguish a forecast of a policy-rate innovation from incremental net stock-return predictability. Require a
   calendar-only and a same-window price-only comparator before attributing a later strategy to policy information.
5. Retain event-level clustering, uncertainty from estimated predictors, release overlaps and calendar eras.
   Do not treat many intraday bars around one meeting as independent opportunities.

These are applications of existing RESEARCH_CONTROLS.md, not changes to the shared trading process or live setup.

## Can we build a strategy from it?

**Not directly.** It supplies no fixed entry direction, threshold, executable holding window, stop or net P&L.
It does not establish a forced buyer/seller in ES/NQ. A forecast of a hawkish surprise can still fail as a short
if equities already priced the information, or if growth news and discount-rate news offset one another.

The nearest research question is whether returns on already-completed payroll/CPI days add incremental
information about returns during a *subsequent* scheduled FOMC event. That is a new hypothesis inspired by the
paper, not its finding. It would first need a point-in-time forecasting target, fit/availability audit and a frozen
post-signal stock-return protocol. No direction or specification is selected here and no return trial was run.

Paper-cited data leads, **not downloaded or verified in this review**:
- [SF Fed monetary-policy surprise workbook](https://www.frbsf.org/research-and-insights/data-and-indicators/monetary-policy-surprises/).
- [SF Fed U.S. Monetary Policy Event-Study Database](https://www.frbsf.org/research-and-insights/data-and-indicators/us-monetary-policy-event-study-database/).
- [ALFRED vintage data](https://alfred.stlouisfed.org/) for release history. Release dates do not supply real-time survey consensus by themselves.

The historical Eurodollar-to-SOFR transition and statement/press-conference coverage require explicit schema/era checks.
Replicating the paper's stock sorts additionally needs CRSP and, for its growth characterization, IBES; our futures
minute data alone cannot reproduce those results. Pricing, licences and live release latency were not verified.

## Existing work, queue and decision

TIER_LIST already records failed pre-FOMC drift and statement follow/fade rules. WATCHLIST #23 retains the
different prior-day-liquidity / post-FOMC short hypothesis at weak significance. The new paper does not replicate
or validate those strategies and does not authorize reopening them with altered timing or filters.

Evidence verdict: **DON'T TEST as a ready strategy**. Retain the methodological reference and potential data leads.
No new Promising strategies awaiting verification queue entry: there is no demonstrated executable return edge
or sufficiently specified candidate to verify. Missing information alone is not the queue's merit requirement.

No design/recent trading returns, costs, payouts, Sharpe, blow-up probabilities or portfolio correlations were
computed. No MultiCharts code, strategy grade, trading allocation or live changes are supported by this review.

For Claude: `agents/codex/results/fomc_monthly_coefficients_review_20261029.md`.
