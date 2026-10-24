# ORPullback portfolio implementation review: PASS WITH CONCERNS

Summary: The requested joint-account comparison is now implemented and reproducible from frozen inputs.
I independently reviewed the account runner and checked its output structure and simulator parity records.
All160 original-simulator five-output checks pass; no account implementation defect was found in this review.
The negative addition/replacement conclusion is supported; missing stress sessions and source parity limit generalisation.

Scope: independent review by the diagnostics agent of `analysis/codex_or_pullback_portfolio.py`,
the source/replay timing contract and saved account outputs. I authored the separate diagnostics module;
its implementation is subject to another agent's review, not independently certified by this note.
Preregistration: `1ad4306`; current-plan sources pinned to `a67035be4189b493098c80f1def979348520fd5d`.

## Checks

- Close-entry account paths correctly exclude the entry minute's pre-entry range and charge fees from entry.
- Stops cap the final adverse minute at the executable stop/gap fill, while open exits exclude subsequent extremes.
- Current-plan and candidate paths are combined before account checks, with integer funded cushion quantities.
- Both candidate modes receive the same calendars, paired draws, costs and allocation controls.
- All160 saved original-funded-simulator checks match paid, payouts, days, blown and first payout exactly.
- Outputs contain32 funded rows (2fees x2cohorts x8allocations) and48 evaluation rows (2fees x3cohorts x8allocations).
- Standalone net calculation uses$20/point perNQ, $10.40/NQ-equivalent commission and$5 per slipped fill.
- An independently written arbitrary-event exit walker matches every2,676 observed exit minute/kind/gross result
  in each mode before generating the random controls; this verifies exit geometry, not independent signals.
- Trade totals, standard metrics and null-control totals agree. Candidate trades are never selected by plan occupancy.

## Result supported by the reviewed output

At$1.04 micro fees on the common2018+ coverage universe, BASE returns$11,947.50 expected two-year payouts,
8.3% blown. Adding the reported-rule model at1MNQ changes payouts by−$336.50 (paired95% interval−$525 to−$147.46)
and increases blown risk2.4percentage points. At2MNQ, payouts fall$2,925 and blown risk rises24.1points.
Replacing VB with2MNQ also loses to BASE and the empty-VB control. Evaluation pass rates likewise fall.
These results justify retaining the current plan under this test, without claiming new live evidence.

## Concerns that must remain visible

1. Sixteen incomplete sessions are excluded, including2020-03-09,03-12,03-16 and03-18. Thus the study omits
   important stress episodes; bootstrap histories are conditional on coverage and join adjacent eligible sessions.
   Evaluation omits any21-day window containing an excluded session rather than shortening its horizon.
2. Full-calendar baseline reconstruction is close to the saved benchmark, not identical: year1$9,193.50 versus
   $9,180; year2$11,976 versus$11,982; blown7.7% versus7.6%. Exact simulator parity does not establish exact
   identity of every historical baseline input. Keep that distinction and the matched comparison universe explicit.
3. No original author trade ledger or MultiCharts export establishes author/source execution parity. The early-close
   adapter and two protection timings are disclosed models; close fills remain an execution assumption.
4. Existing CL and ES MOC path approximations are inherited. Summing per-leg adverse minute marks is conservative
   and does not reconstruct the tick order of simultaneous hedging gains/losses.
5. The random-time control retains observed event-day/direction templates and allows overlap-driven trade skips.
   It tests conditional entry timing, not a completely independent strategy. The primary2023+ p=.342 fails this control.
6. Primary2023+ trade t=1.955 and full-sample DSR=.559 do not clear current promotion gates. No rounding to t2
   and no promotion claim are warranted. Prior author search size and original freeze provenance remain unknown.

No plan ranking, live allocation, broker setting or infrastructure change is authorized by this review.
