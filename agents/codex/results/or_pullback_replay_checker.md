# ORPullback diagnostics and account-path checker: PASS WITH CONCERNS

Summary: I independently reviewed the diagnostics module and the joint-account path implementation.
Saved ledgers, fees, period totals, trade t statistics and funded summaries reconcile in 200 arithmetic checks.
All 160 recorded original-funded-simulator comparisons match all five outputs exactly.
I found no material implementation defect; coverage, execution parity and inherited path limits remain.

Preregistration: `1ad4306`. Current-plan source pin: `a67035be4189b493098c80f1def979348520fd5d`.
Reviewed scripts: `analysis/codex_or_pullback_diagnostics.py` and
`analysis/codex_or_pullback_portfolio.py`, plus their pinned account dependencies and saved outputs.
This agent authored the candidate replay and the separate occupancy diagnostic; this note does not
claim independent certification of those two modules. The diagnostics agent independently checked
the replay exit geometry and the parent account implementation in its separate review.

## Independent checks

- Candidate fee conversion is consistent: $20 per point per NQ, $10.40 commission per NQ-equivalent,
  plus $5 per market/stop fill. Thus an ordinary stop/time round trip costs $2.04 per MNQ and a
  target round trip $1.54; the $1.24 fee sensitivity adds $0.20 per MNQ to both candidate and plan.
- Both saved candidate net ledgers reconcile to raw gross points and exit kinds. Whole-strategy
  2018-22, 2023+ and 2018+ trade counts, totals and t statistics reconcile at both fee levels.
- Random-side controls retain observed event times and days, randomise side, and re-execute exits.
  Random-time controls retain event days, directions and chronological order, draw without replacement
  from the permitted close times, and re-execute exits. A later event overlapping a changed first trade
  is skipped. All saved null real totals/counts reconcile with the actual ledgers.
- The independent placebo exit walker follows the frozen protection delays, stop-first ties,
  one-point target trade-through and favorable target gap fills. Its saved records report 2,676
  observed-exit parity checks for each execution model. This checks exits, not independent signals.
- Standalone daily statistics and EOD-trail Monte Carlo use the same eligible-day calendar, with zero
  returns on eligible no-trade days. Trade-only Monte Carlo is labelled as ignoring day dependence.
- Account paths exclude pre-entry OHLC for close entries, include entry costs, cap filled stop risk at
  the executable fill, and exclude later extremes after an open exit. Joint paths enter the existing
  evaluation/account state machines. Target/time intraminute adverse marks remain conservative.
- All 32 funded summary rows reconcile to their saved simulation arrays for expected payouts, blown
  share and all-six share. All 160 saved parity records exactly match paid, payouts, days, blown and
  first payout. This is simulator parity, not proof of author MultiCharts parity or baseline identity.

## Limits and interpretation

Sixteen excluded sessions include March 2020 stress days. Funded blocks use the common eligible-day
calendar and therefore join adjacent eligible sessions across gaps. Evaluation retains real 21-day
windows and omits windows containing unknown candidate sessions. These results are conditional on
coverage and cannot establish safety on the excluded stress dates.

Random-time results test conditional timing on observed event days, with potentially fewer trades after
overlap skips. They do not create an independent complete strategy. Trade t statistics and DSR retain
their usual dependence and prior-search limitations; the daily block/account results matter separately.

The reconstructed full-calendar baseline is close to, but differs from, the saved reference. Existing
CL and ES MOC path approximations remain. Opposite positions marked at separate adverse extremes
within a minute do not reconstruct tick order. Original author export/source parity remains unverified;
the common early-close adapter explicitly changes the supplied source's holiday behavior.

The held-minute occupancy files under `analysis/outputs/codex_or_pullback_portfolio/exposure/` are
descriptive full-size MNQ quantities. They exclude MCL/MES and funded cushion scaling, use inclusive
inferred MC entry/exit minutes, and exclude the candidate close-entry minute and open-exit range.
They do not constitute another portfolio-performance result or an entry filter.

No candidate variant, return ledger, trading plan, live source or account setting was changed by this
review. Claude reviews/ranks results and the user decides what trades.
