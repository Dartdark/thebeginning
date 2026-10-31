# NQDB2 proxy test evidence: TEST (research only)

The user's 2026-10-24 **"test it!!"** authorizes an actual test with explicitly chosen missing chart settings.
This supplements, rather than replaces, `nqdb2.md`'s NEEDS DATA verdict for an exact source reproduction.
No new NQDB2 returns have been computed before this sheet and its associated preregistration.

1. **Who/why:** the upload is a price-breakout/VWAP continuation rule, closely related to Vault Break v8.
   No documented forced trader or independent flow exists. Hypothesis: rejecting a breakout after a four-bar
   decline of at least 0.10% improves total net P&L and drawdown. The test can disprove this claim.
2. **Before-trade information:** completed 30-minute bars, the previous 15 completed positive calendar-date
   high-low ranges, today's open/VWAP, and Close[4]. No dollar-flow estimate is available; this is a price test.
3. **Market:** NQ signal and one-NQ research geometry, with 40-point target and 75-point stop. MNQ account
   simulations scale dollars by 1/10, preserving that geometry; they do not apply the unmodified NQ dollar
   inputs to an MNQ chart.
4. **Data/cost:** existing NQ Grid24 cache, December 2017 through 2026-10-09, and one-minute magnifier.
   Total volume replaces the unavailable native MC up-volume. Midnight-aligned full-session 30-minute bars,
   IOG off, calendar resets and midnight SetExitOnClose are explicit assumptions, not verified source settings.
   Data costs $0; exact source parity still requires the original chart settings and MC export/split volume.
5. **Costs/occupancy:** $7.25/NQ commission plus one tick per market/stop fill; the target requires a one-point
   trade-through. No selection by existing-plan occupancy. The 10:00-14:00 decisions overlap VB/ONB/RS; this
   is principally a VB replacement candidate, not established diversification. Early-close protection is a
   separately labelled fixed safeguard, never silently added to the literal source.
6. **Power:** five years have roughly 1,260 weekdays and at most two attempts/date. Before returns, exact
   trade count is unknown. For 500-1,500 trades and $900-$1,100 per-trade SD, t=2 needs approximately
   $46-$98 net/trade; removing only 50 trades with SD $1,000 needs a losing mean near $283 for t=-2.
   The design gate can pass in principle; report realized counts and power without altering the gates.
7. **Prior tests:** TIER_LIST's existing Bridge Vault Break v8 and rejected VB Combined are acknowledged in
   the source review. This trial isolates the supplied default negative-drift veto on/off, on identical bars,
   range logic, volume proxy, exits and attempt cap. Historical 2023+ is already seen replication.

Failure/executable risk: downside is common long-NQ exposure; a 75-point stop risks $150/MNQ before fees,
gaps and slippage. Two successive entries can lose twice that; low trade correlation would not establish an
offset before a trailing-line breach. Literal holiday carries are retained and audited, never hidden by a
same-day portfolio calendar. The Apex-safe version has to demonstrate legal holds before account scoring.

**TEST** the declared proxy, with the plan committed first. No exact-source validation or live promotion claim.
