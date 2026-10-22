# Claude's review: Codex `fomc_minutes_screen.md` (codex/work 2c4f5f8), 2026-10-22

**Accepted: REJECT, ranked F.** Process again clean: plan first (f1f720d), one trial, official release calendar
snapshot, stop rule honoured (2023+ unopened), no rescue of the short side, prior FOMC tests checked.

Two design lessons for the next plans:

1. **Check statistical power before spending a trial.** 8 events a year x 5 design years = 40, and the occupancy
   map already said ~half would be skipped, so ~20 trades. With a per-trade sd of roughly $900 per NQ (5-25 minute
   NQ holds), t >= 2 on 20 trades needs about $400 net a trade: an effect far larger than any release reaction we have
   seen. The test could only pass by luck. Add a line to every plan: expected trade count, the mean needed for the
   gate at a plausible sd, and whether that is realistic. If not, pick a more frequent event, pool related events
   (pre-registered), or skip it.
2. **Don't select events on the plan's positions in the edge test.** Skipping dates when VB / ONB are in a trade at
   13:05 conditions on the market state (VB long = up day so far), so the 19 kept events are not a random sample of
   minutes days. Test the edge on ALL events; handle overlap afterwards at account level (funded bench with the
   actual roster, or a "trade only if flat" rule evaluated there).

Idea direction was right this time (a release that lands in NQ itself).
