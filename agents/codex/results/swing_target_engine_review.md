# Swing Target source and engine review: PASS WITH LIMITS

Summary: No material causal execution blocker found against the frozen plan.
The supplied deterministic suite and two independent short-side BE/gap fixtures pass.
Uploaded source omits the prose's breakeven rule and has exact-boundary/holiday limitations.
This is an execution-helper review, not independent raw-data replication, MC parity, return validation or promotion.

Scope: source `agents/codex/inputs/swing_target/Swing_Target_NQ.txt`, engine `analysis/codex_swing_engine.py`,
plan `agents/codex/plans/swing_target.md`. Script: `analysis/codex_swing_engine_review.py`.
Output: `analysis/outputs/codex_swing_target/independent_engine_review.json`. New economic trials: **0**.
Reviewed engine SHA256: `4a1fd508a58235bc0bbf658048a54a626063541adf4b0418f36ab7a1901e3add`. Source SHA256: `612d24c138db2afcff0c740db1a99d0e09aa8799f846c0cabd53391919bbe616`.

## Source/prose discrepancies

- **Breakeven absent:** source lines78–83 only set target/stop. No BE trigger or exit exists, so the uploaded code cannot
  itself produce the prose's31 BE exits. The separately frozen CODE_BE version addresses only this discrepancy.
- **Minute labels:** lines73–75 submit at08:45 into the bar labeled08:46; on the close-stamped proxy its open is normally
 08:45 wall time. Inclusive14:29 submission permits the14:30-labeled bar. Lines86–88 submit a market exit at14:59,
  filling at the open of the15:00-labeled bar, normally14:59 wall time. Labels must not be presented as verified broker clocks.
- **Exact session boundaries:** reset requires08:31 (46–59), storage/termination requires15:00 (92–95). Missing boundary
  bars and early closes can omit stored sessions or carry a position. Recomputing AvgRng at a later08:31 can change that carried bracket.
- **Execution:** header line18 admits level-price Python fills despite possible gap-through stops. Both directions are
  submitted together (73–75), so the parent's OCO/path treatment is a declared proxy, not source-proven MC behavior.
- **Prior searches:** header lines4–5 state several start times were inspected in both periods. Author trial count is
  unknown;2023+ is previously examined historical validation. No supporting MC trade export was supplied for the584-trade claim.

## What the engine checks establish

The parent's synthetic suite verifies post-entry path/MAE, causal BE, early disarming, worse-open entries, one entry/day,
inclusive last submission, next-native-bar orders, unrepaired missing15:00 carry, one-point target-through and fixed path sensitivity.
Independent additional fixtures verify short100 → low93.5 → bounce100 exits at BE, while the earlier high101 remains in MAE;
and a short stop nominally114 fills at a worse next open120, with400/NQ MAE.
Read-through found protective range updates occur after the08:31 close, and BE affects subsequent adverse movement.
No research-history cache or strategy return output was opened for this review.

`replay_market` omits a signal still open at dataset end. The parent must reconcile requested/closed placebo counts and disclose
unresolved signals, rather than silently count them as no-event zeros. This review does not independently verify those run-level counts.
The parent wrapper separately flags cross-date and late exits; finite-held-minute counts alone would not prove flat-deadline compliance.

## Howard reference

The [primary SSRN abstract](https://ssrn.com/abstract=6350238) describes ES volume-profile value-area breakout events during January2025–January2026.
It reports weaker first30-minute events and an economically insignificant unfiltered continuation signal. That supports an early-session
timing concern in its own setting. It does not establish this NQ prior-two-day price-level rule, a15-minute cutoff, or0DTE causation.
The full PDF returned403; no access bypass was attempted. Only the primary indexed abstract was verified.

## Limits

This uses the parent's helper plus synthetic fixtures, not a second end-to-end implementation or native tick replay.
It does not verify the reported trade count/PF, raw-history completeness, tick rounding, chart-template parity, broker fills,
portfolio benefit or account survival. Those remain the parent audit's separate tests and independent-review requirements.
No source, engine, live/VPS/broker configuration or key was modified. Only this review script, JSON and report were created.
