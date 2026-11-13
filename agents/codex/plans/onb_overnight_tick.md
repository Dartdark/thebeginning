# Second ONB-buffer candidate: frozen Overnight Tick/VIX

2026-11-13, committed before new returns for this candidate. Evidence sheet
`agents/codex/evidence/onb_overnight_tick.md`. All existing selection history stays.

- Common book and dates match `onb_heavy_night_fade.md` / joint-loss audit.
- Frozen rule: existing Overnight Tick/VIX MC signal list, long only. Closing
  order-flow + VIX state after a down cash day, entry17:05 wall clock, exit03:00.
  Saved report 5-min stamps17:10 and03:05 correspond to bar opens17:05 and03:00;
  minute grid indices17:06 /03:01. Preserve report fill prices. No stop.
- Exclude a trade only for unresolved actual date coverage, missing endpoint
  prices, open report exit, or a detected contract-roll switch during the hold
  per existing `overnight_round.roll_minutes`. Record every exclusion before
  calculating results. No ONB-conditioned eligibility.
- Definitions: primary1MNQ, size2MNQ, one-minute delayed-entry stress at the
  observed17:07 grid open (same exit). No threshold/side/stop search. Costs
  $22.75/NQ equivalent = $2.275/MNQ round trip, including two slipped fills.
- Design gate2018-22: positive net, t>=2, random-side same-time/exit p<.05
  (1,000 draws). Unlike T's stop, OT has no stop so opposite gross is the exact
  same-time mirrored payoff. Run all and long/short metrics (short is empty).
- Then one historical2023+ replication: positive net,t>=2, placebo p<.05;
  prior full-sample evidence is disclosed, not described as a clean holdout.
  Standard metrics/yearly/native cost bridge/bootstrap/permutation/MC.
- Only after both gates pass: direct ONB loss-state and early offset analysis,
  then the same paired fresh/stressed 150K simulations, fixed target159050,
  21/20sessions, DLL2000, EOD trail4000, no funded floor lock. Stressed balance
 147998.08 is a historical scenario, not verified current account state.
- Fixed cases: base,+OT1,+OT2, most-overlapping design piece replaced byOT1,
  empty slot,+delayedOT1. Determine overlap before using its P&L. Same starts,
  source-compatible/corrected-Sunday and common-price/session sensitivities,
  2,000 paired60-day block bands. Compare replacement against base AND empty slot.
- Qualify only if primary design pass-rate differences are nonnegative and
  recent fresh/stressed improvement bands exclude0 above; also positive
  contribution on ONB-loss dates and before the base's initial loss crossing.
  Failures stop dependent funded/code tests; no size selection to rescue them.
- A passing candidate continues through funded1/2year payout/failure/timing
  benches, checker and separately frozen forward evidence, never auto-adoption.
- Reuse the prior audit code only for accounting; save OT outputs separately.
  Preserve the T rejection. New accounting fixes rerun unchanged definitions
  and are not erased from the run record. No trading/VPS/broker edits.
