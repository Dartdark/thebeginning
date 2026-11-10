# VB loss-side partial exit: TEST for a bounded evaluation screen

Summary: The user wants to change the evaluation book, with direct VB changes the unresolved priority.
Twin2, DT2, VB15 and finish mode are existing baseline changes, not new recommendations.
Test one loss-side partial exit against unchanged, reduced-size and empty-VB controls.
This is risk engineering on an existing entry rule, not a claim of a new forced-flow alpha source.
No new economic outcomes have been calculated for this definition at this evidence checkpoint.

## Evidence and feasibility

1. Existing VB buys strength above its midnight-open noise band and VWAP. Its entrant identity/forced flow
   is unverified; no new market story is supplied. The test concerns loss distribution under evaluation barriers.
2. At entry, the 40-point target and 75-point stop are known. Close floor(q/2) contracts at entry−37.5,
   leaving ceil(q/2) with the original bracket. No averaging down, add-back or hindsight stop label.
3. Both legs are MNQ exposure to the same NQ price path. There is no external hedge or later flow assumed.
4. Owned 1-minute NQ OHLCV, prior ATR15, source Twin/DT rules and other MC ledgers are available.
   Raw snapshot is `fe35af99`; local grid `/workspace/vb_risk_cache/g24.pkl` is a data-only cache.
   Tick chronology, actual micro fees/fills, and the original feed's complete ATR history are not certified.
5. Native assumed $1.25 RT/MNQ plus one adverse tick per market/stop leg. Splitting exit quantities does
   not double total per-contract commission. A gap can cross both stops; nominal loss reduction is no guarantee.
6. Prior VB design had 861 entries; exact current-data design counts are outputs, not presupposed.
   Paired start-date resampling will account for overlapping 30-day windows; four live accounts are not four
   independent validation trials. No power claim from the reported 89% attribution statistic.
7. Prior 50/60-point full-position stops failed, as did several cushion caps. Maroy's ladder sold half on
   favorable moves, unlike this loss-side trim. Targeted code/plan/tier searches found no identical loss-side
   half exit. This is one new fixed economic proposal; do not retune its distance/fraction after results.
8. Prediction: full-bracket losses shrink while recovery winners lose some profit. Risks shared with ONB/Twin/DT
   remain; the trim must happen before an account breach to help. Removing VB may outperform managing it.
   A higher standalone Sharpe or smaller stop is insufficient: account passes including expirations decide.

Decision: **TEST** — commit exact plan/code, verify disconnected mechanics, then design-only account screen.
Unknown coverage and inherited adverse-extrema aggregation limit positive conclusions; no live action follows.
