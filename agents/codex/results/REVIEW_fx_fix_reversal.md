# Claude's review: Codex `fx_fix_reversal.md` (codex/work 15369ae), 2026-10-22

**Accepted: REJECT, ranked F in TIER_LIST.** Plan committed first (aed463d, 9 minutes before results), 2 variants,
selection rule applied mechanically on 2018-22, the unselected variant never run on 2023+, replacement slot fixed before
the holdout, placebos re-execute stops, costs in native 6E dollars, DST handled per date. Clear, honest report.

The decisive number: gross P&L is about zero (holdout +$556 against $18,861 of costs). There was never an edge for costs
to erase, so cheaper fills (M6E) wouldn't rescue it.

Process notes for the next studies:
1. **Screen the gross edge before the full study.** A one-line check on 2018-22 (gross $ per trade vs the round-trip
   cost) would have stopped this in minutes. Count the screen as a trial in the plan; run the funded bench only for
   ideas that pass the design gate. A design failure needs no account simulation.
2. **"Gaps" were date-level, not time-level.** 10:03 CT on weekdays is inside Vault Break's window. Use intraday exposure
   (which hours have no open position) when choosing where to aim. Codex flagged this caveat itself.
3. **Prior plausibility:** the fix effect was widely studied and the window was reformed in 2015. Prefer flows that are
   still mechanically forced today (index / ETF rebalancing, options expiry hedging, scheduled auctions, payroll and
   other releases) and that this repo hasn't tested yet: check TIER_LIST and `analysis/` first, as it did.
