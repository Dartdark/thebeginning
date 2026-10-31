# Overnight Rebound: fixed current-plan refresh

2026-10-25. Parent preregistration d94d815, initial result061b79c. Finalfetch revealed afde088:
user added SwingTargetv3 and PAPERTRENDv2, taking the common-scale personal portfolio from17 to19 legs.
Funded rosters also adopted SwingTarget; overnight baseline chronology limits still apply.

Commit before refreshed portfolio returns. Preserve all original17-leg results and source snapshots.
Use the published new MC ledgers and current personal_portfolio.py to add only SwingTarget/PaperTrend to the old common-scale baseline.
Verify other inputs and starterA–D unchanged; match published19-leg totals/annual/DD/year rounding at its own fee convention.
Replay NO candidate returns: use saved UNIFORM/SUNDAY2 daily series unchanged. Same20 BASE/ADD/EMPTY/REPLACE contrasts,
FULL replaces OvernightTick, startersONBML; same1.24/1.04fee assumptions,1,000 paired252-session10-day draws,5,000 historical annual-mean intervals.
Freeze wrapper and input hashes before all four financial runs; verify hashes after and reconcile saved simulations.
Save separate `personal19/` outputs and new snapshots under `plan_update_afde088/`, never overwrite originals.
This changes the user-adopted comparison baseline, not candidate selection, parameter fitting or economic trial count.
Current common scale is primary; a future intended aggressive allocation is not silently assumed adopted.
Use afde088 as an explicit as-of cut for this report. Later changes do not silently redefine its frozen comparison.
