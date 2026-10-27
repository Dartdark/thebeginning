# NQ RTH gap-down long: TEST a fixed independent reconstruction

User request, 2026-10-27: the referenced original code/trade logs do not exist;
test with the written description and available repository data. This is a
separately authorized single-candidate reconstruction. The completed Hunt v2
budget, progress file and paused automation are not reopened or changed.

## Evidence questions, before new market inputs or returns

1. **Participant/cause.** The post proposes overnight price pressure and an
   RTH liquidity/inventory reversal. No observed compulsory net order, size or
   causal participant evidence is supplied. Treat this as a falsifiable return
   hypothesis, not an authenticated forced flow. General equity daytime drift
   is an important competing explanation.
2. **Direction/clock/size.** Long only if the first RTH opening price is below
   the previous cash-session close. Source session09:30–16:00NewYork equals
   08:30–15:00Chicago. Native data use close-labelled one-minute bars, so the
   opening print is OPEN08:31. Observe that first bar and enter OPEN08:32,
   physically08:31CT. This conservative one-minute delay avoids conditional
   access to the already observed opening print. One MNQ is the executable
   research unit; the source's $2,000/NQ stop is100points, not$2,000/MNQ.
3. **Transmission.** This trades the same NQ underlying named in the post;
   no cross-asset proxy or reconstructed 6J series is involved. Continuous
   contract roll identity remains a source limit unless the exports document it.
4. **Inputs.** Supplied post and README are claim sources only. Original Python,
   trade logs, CSV tables and raw author inputs are absent; do not pretend exact
   replication. Use existing native NQ day exports and the repo's named-zone,
   calendar, grid, execution, metrics, resampling and account helpers. Archive
   exact text and input hashes. No download, purchase or account change.
5. **Costs/failure.** Primary native MNQ fee1.24RT plus .25point per market/stop
   fill: $2.24RT. Stops are entry-active, touch triggers, adverse gaps fill worse
   than the stop. Source-like and severe costs are diagnostics, not selection.
   Event-day overlap with the book is not an entry filter. No position before
   the first eligible RTH entry; preplanned session exit, early closes included.
6. **Power.** Roughly250cash sessions/year and an unknown down-gap fraction
   could supply hundreds of design events; this is an assumption, not a measured
   count. Require100resolved design events and show observed support before any
   significance inference. The author reports742selected trades, but that is
   neither our support measurement nor our trial count. No SD estimate is
   invented before the screen.
7. **Selection/falsifiers.** Existing gap/reversal families are already in
   TIER_LIST (`co_oc_reversal_test.py`, `es_mean_reversion_test.py`); neither is
   certified as this exact long-only100point-stop rule. Preserve those failures
   and the author's side/stop/threshold/regime search. Positive selected charts
   do not confer a clean holdout. Failure versus realistic costs, always-long
   RTH, same-exit placebos or current BASE/EMPTY books rejects promotion.
8. **Risk/book.** Long NQ can lose with VaultBreak/DualThrust/RelativeStrength
   and other long equity legs. A nominal100point stop is not a hard loss cap.
   Intraday loss paths and account rules, not a daily correlation or a smooth
   combined screenshot, determine funded/evaluation fit. Full book paths and
   known missing2020-11-30baseline coverage must remain explicit limits.

**Decision: TEST the fixed claim independently, with no parameter search.**
The missing author files prevent source parity, not a transparent reconstruction
of this simple rule. Pre-register the execution differences before market values.
