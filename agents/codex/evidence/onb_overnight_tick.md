# Overnight Tick/VIX against ONB losses: TEST frozen re-bench

Summary: Second candidate after the isolated T fade failed the current-book gate.
Use the existing MC-confirmed Overnight Tick/VIX rule at 1 MNQ, 2 MNQ sensitivity.
It closes at 03:00, so an offset could be banked before ONB. Earlier evaluation
tests were near-neutral; this is not assumed to improve the new seven-piece book.

Sources: `checks/candidates/overnight_tick/spec.md`, `SOURCE_SPEC.md`, existing
`NQ_Overnight_Tick_VIX.txt`; `analysis/overnight_tick_mc_confirm.py` and saved
confirmation output; the 2026-11-09 stop-day screen (already-seen selection data).
Earlier author interaction selection, 5 VIX lengths, proxy experiments and
old-roster sizing benches remain counted. This is not a new discovered alpha.

1. **Who/why:** author's hypothesis is closing selling/inventory absorbed
   overnight after a down cash day, conditioned on signed closing flow and VIX.
   No verified mandate or dollar flow size; retain that limitation rather than
   treating a return pattern as proof of forced demand.
2. **Clock/direction:** long after a down RTH day when closing RSV<0 and VIX>SMA25,
   or RSV>=0 and VIX<=SMA25. Flow through15:15 CT and VIX daily close are available
   before the 17:05 entry; Friday signal enters Sunday. Exit03:00 CT. No stop.
   Rules and thresholds are frozen, not selected to explain the new ONB tails.
3. **Transmission:** signed NQ flow and direct MNQ exposure. No cross-asset proxy.
4. **Data:** use the saved 5-min MC trade list, 2017-07 to2026-10, for frozen
   signals/actual report prices, common audit endpoint2026-10-12. Existing Python
   parity through2026-07-07 used owned aggressor-flow exports; raw OF ends then.
   Do not claim a new feature reconstruction beyond that date, substitute bar
   signs, or invent current live signals. No outside acquisition/cost required.
5. **Costs/gap:** $2.275/MNQ round trip at assumed native fees +1tick per fill.
   Already-seen full report t>4 after old costs warrants a native-cost screen.
   All nights eligible under the frozen rule are used, never only ONB losses.
6. **Power:** approximately300 design trades and200 recent trades; at $1,200/NQ
   assumed SD, mean ~$139 is required for t2 at300. Earlier net$325-374 is a
   plausible screen, not a new measured result.
7. **Duplicates:** old eval benches tied; recent five-piece active scan OT1 was
   +0.1pt (noise). Current seven-piece plus direct ONB loss attribution remains
   the new question. Late2026 MC trades were weak already, not a fresh holdout.
8. **Failure/diversification:** continued overnight selloffs, gaps and Sunday
   macro news can create large losses without a stop. Market orders take
   liquidity. Same-side exposure can compound Twin/Bridge; ONB itself usually
   starts later. Gains arriving by03:00 can help a morning buffer, but overnight
   losses can instead exhaust it first. Account paths, not annual correlation,
   decide. Replacing the most-overlapping design piece is tested against both
   the base and its empty slot. No separate account hedge or live changes.

Verdict: TEST exact frozen candidate. Information-clock and MC/feature coverage
limits must remain in the report. A useful book effect still needs independent
checking and future evidence; price-only/volume proxy re-invention is out of scope.
