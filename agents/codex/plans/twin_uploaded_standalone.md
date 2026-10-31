# Uploaded Twin Continuation: standalone replication

User request: test the uploaded strategy individually. This authorizes this isolated task while unrelated research
and the pending live-reconciliation workflow remain paused. Work only on codex/work, never touch live/VPS files.
Evidence: `agents/codex/evidence/twin_uploaded_standalone.md`. Preserve the uploaded text under Codex inputs and hash it.

## Frozen rules and scope

The upload and the old checked source have identical executable tokens (strip brace comments and whitespace to verify).
Reuse `checks/candidates/twin_continuation/replica.py` as an imported library, never its writing CLI. Reuse the owned
`scratch_data/g24.pkl`; do not run build_lab or create shared research caches. Copy no existing simulator into a new one.
It extends grid.execute because working orders, internally aggregated bars and entry-tag-specific exits are required.

Run at most three fixed configurations: (1) exact default combined Twin, Qty 1 NQ, BO_MaxStopMult 0; (2) BO only,
UseMomentum false; (3) MO only, UseBreakout false. The latter two are diagnostic standalone opportunity sets, not
merely attribution of legs from the combined run. No best version is selected and no parameters are optimized.
Report combined BO/MO attribution separately as useful context. Long/short splits are diagnostics, not selected filters.

BO: 6h confirmed seven-candle swings, 15m Wilder ATR14, previous session range cap 2 x prior 50 sessions, stop at opposite
swing, target 2 ATR, 15:30 last fill, 15:45 exit. MO: full 10m oscillator cross +/-100, 08:40–09:30, first daily signal,
75-point stop, next-minute market entry, 14:51 time exit. Preserve IOG-off delayed protective orders and code holidays;
do not silently repair them. Daily reset logic and one-position interaction stay in the existing replica.

## Period, fills and known limitations

Grid starts 2017-12-01, ends 2026-10-09. Raw 2017 daytime starts earlier, but full overnight history does not.
The upload asks for six months' warm-up, so the **primary evaluation starts 2018-06-01** (six calendar months after
the grid starts); report full-2018 results separately only as a historical-replication sensitivity with short warm-up.
Do not rebuild/splice the grid, drop losing dates, or choose a start from performance.
Design = primary start through 2022; 2023+ is previously seen replication history, not untouched validation.

Commission $7.25/NQ round trip plus one tick per market/stop fill, target exits no slippage. Also show the source's
$6 total cost convention and one additional tick per fill as cost diagnostics, not strategy variants. Use existing
replica stop/limit ordering and report same-bar ambiguity, entry-bar exposure and targets filled at touch.

The replica interprets SetExitOnClose using the stated 17:00–16:00 session. Actual MC chart sessions can instead
trigger midnight exits; the archived v2 MC report also contains holiday inputs absent from the upload. Treat that
report as corroboration of a related version, never exact uploaded-code confirmation. No MultiCharts run is available.
Flatten overnight dates on exit for daily-return statistics; warn that this is not mark-to-market equity.

## Required outputs and decision

Use metrics.perf and resampling bootstrap/permutation, report trades/win/mean/t/Sharpe/Sortino/PF/Calmar/Ulcer/maxDD,
whole, sides, periods and years. Save all actual trade lists with source hashes and run configurations. At least
2,000 block-bootstrap/permutation samples; fixed seeds. One-NQ results plus correctly scaled one-MNQ diagnostics.
Monte Carlo via montecarlo.trade_mc/daily_mc at 1 NQ and 1 MNQ; the $2k EOD floor calculation is only a risk diagnostic,
not a valid Apex payout simulation if the source violates session/holiday/position restrictions.

Conditional random-side placebo: at each actual entry time simulate both directions with mirrored initial stop/target
and the same source time-exit schedule, using raw future bars only for execution. Check same-side reconstruction
against actual ledger first; if it differs, report the mismatch and do not call the placebo equivalent. Use 1,000
random sign assignments with paired opportunities; this is not a full system-level shuffled-signal simulation, because
changed exits can change later entries. Reuse archived full-system placebo evidence as historical context, not a new run.

Count three replay configurations, zero tuned candidates. Use the current trials count for DSR and label repeated
2023+ access. Classify WATCH if historical edge survives but platform parity/forward results are unresolved; REJECT
for the intended account if drawdown, rule violations or negligible net edge prevent use. Do not promote or deploy.
User requested standalone evaluation, so no portfolio addition/replacement or funded-roster optimization is run.
Finish with <=5 summary lines, exact differences/limitations, commit and push only authorized Codex paths.
