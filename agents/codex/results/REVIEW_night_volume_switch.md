# Overnight-volume switch implementation review: PASS WITH CONCERNS

Summary: I independently reviewed the diagnostics and portfolio modules and found no material implementation defect.
All 240 standard-stat rows and 32 funded summaries reconcile; all 160 saved simulator comparisons match exactly.
This supports the conditional historical test, not promotion: full-sample DSR 0.94625 remains below 0.95.
Missing stress sessions, original MultiCharts parity and live stop behavior remain unresolved.

Preregistration: `affb482`. Current context: `febc65f1573040abf9a697d1d3468e1bce48c4c0`.
Reviewed: `analysis/codex_night_volume_switch_diagnostics.py`,
`analysis/codex_night_volume_switch_portfolio.py`, their account dependencies and saved outputs.
I authored the candidate replay, so this note does not independently certify that module's signals.
The diagnostics module's separately authored exit walker checks replay execution independently.
No new candidate variant or price replay was run for this review.

## Checks

- Open-entry minute OHLC is held. The primary model retains uncapped entry-minute exposure until its
  explicit stop becomes active. Filled stops cap the exit minute at the executable rounded/gap fill;
  open exits exclude that minute's later range. Independently constructed synthetic paths confirm
  these distinctions, including an immediate entry-bar stop versus an unprotected entry minute.
- Fees are consistent: $1.04/MNQ plus one tick on each entry and exit gives $2.04 per round trip;
  the sensitivity is $2.24. The source stop geometry is not shifted by monetary costs.
- Source features are built from observed chronology before account filtering. Prior-night medians
  precede insertion of the current night, and range history records completed exact-15:00 sessions.
  Eligibility does not delete observations from those histories. This is a traced implementation
  property, subject to the replay-authorship limitation above.
- Standard statistics, bootstraps, nulls and the all-night fade control use the common eligible-day
  universe. The 866 eligible trades exclude the raw 2025-11-14 trade. Eligible no-trade days receive
  zero daily P&L; unknown dates are excluded rather than treated as zero.
- Random-side and random-time controls re-execute the appropriate stop and VWAP/time exits. The
  mirrored OS short is a null, not an additional source strategy. Null entry windows follow the
  committed information clock. The independent walker matches all 866 eligible exits per mode in
  minute, kind, phase, gross points and rounded stop. Quiet-night fades remain a diagnostic control.
- Matched random masks retain heavy-event counts separately within design and recent periods,
  then compare total net and drawdown. No random schedule or leg split enters the account allocations.
- Both fees and all eight allocations use common eligible calendars, paired whole-day histories,
  original funded cushion sizing and integer flooring. Evaluation retains real 21-day windows and
  excludes windows touching unknown sessions. It preserves the disclosed reference pass-first tie.
- Descriptive MNQ occupancy includes entry minutes and excludes open-exit ranges, keeps opposite
  positions separate for gross size, and reconciles current-leg trade counts to the cached lab.
  It excludes MCL/MES and account cushion scaling and is not a portfolio-performance result.

## Saved-output reconciliation

I independently checked all 240 standard-stat rows: 1,200 trade-count, total, average, trade-t and
calendar fields. All 36 placebo summaries reconcile to real eligible trades and their saved null
draws, and all six heavy/quiet control partitions reconcile in count and total. All 32 funded rows
reconcile to their saved arrays in nine payout/risk/completion fields each. All 160 saved original
simulator checks match paid, payouts, days, blown and first payout exactly.

The original account simulator and an accelerated implementation agreeing establishes simulator
parity. It does not establish identity with an author's MultiCharts export or with every saved
historical baseline input. The unchanged-cache pin and the small prior saved-reference discrepancy
must remain separately disclosed.

## Concerns and primary documentation

Eight dates are excluded, including 2020-03-09, 03-12, 03-13, 03-16 and 03-18. Funded block histories
join adjacent eligible dates across these gaps. These results therefore cannot establish behavior
on the omitted stress sessions. CL and MOC path approximations remain inherited; separate adverse
marks for hedged legs within one minute do not reconstruct tick order or prove pre-breach protection.

Full-sample t 4.43775 does not override DSR 0.94625 failing the 0.95 gate. Quiet-night removed means
are negative, but their small absolute t statistics provide weak evidence. The recent drawdown
random-mask p near 0.25 does not support a strong drawdown improvement claim. Historical replication
and unknown external search burden prevent interpreting these controls as fresh validation.

The source's `Ticks` means total volume only under the specified Trade Volume setting; intraday
`Volume` returns up-tick volume. The change from the earlier source is substantive.
See [Ticks](https://www.multicharts.com/trading-software/index.php?title=Ticks) and
[Volume](https://www.multicharts.com/trading-software/index.php?title=Volume).
Default signals calculate at bar close; built-in `SetStopLoss` has special intrabar/entry-bar behavior.
Thus the explicit stop's delayed activation is a material source difference, not an automatic repair.
See [signal calculation](https://www.multicharts.com/trading-software/index.php?title=How_Signals_are_Calculated)
and [SetStopLoss](https://www.multicharts.com/trading-software/index.php?title=SetStopLoss).

Adverse tick rounding is a disclosed benchmark adapter. Modeling an accepted stop at an adverse
activation open does not verify that a late broker stop would be accepted. The source has no breached-stop
market guard or independent final flatten. Its ordinary default exits precede early closes, so a missing
holiday list alone does not imply a default early-close violation. Native versus locally emulated stops
depends on platform/broker settings; explicit syntax does not prove disconnect protection.
See [Auto Trading](https://www.multicharts.com/trading-software/index.php?title=Auto_Trading).

Status is PASS WITH CONCERNS for the research implementation, not a clean promotion checker PASS.
Claude reviews/ranks results; the user decides trades. No live plan, source, broker setting or
infrastructure change is authorized by this review.
