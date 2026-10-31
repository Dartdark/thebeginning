# Swing Target exit-kind account replay (2026-10-31)

Scope: close the unfinished account replay identified in NEW_CHAT_BRIEF/TODO and the weekly review. This is an accounting rerun of existing frozen strategies, not a new alpha trial or permission to alter plans/live systems.

Freeze Claude source at 86df2c0 and the existing CODE_BE_trades.csv ledger on codex/work. Rebuild research caches from owned CSVs using repository helpers only. Restrict account dates to 2018-01-01 through 2026-10-09 (the ledger's documented complete cutoff); keep all eligible days, never condition signals on plan occupancy. Record file hashes, versions, seeds, dates and ledger reconciliation.

Compare all five frozen allocations per account from swing_target_bench.plans50/plans150: BASE, additions and the existing replacements. Run corrected numeric exit kinds and legacy string kinds on the SAME histories, with corresponding EMPTY controls for VB normal-contract removal, RS longs, EOS and DT. Preserve the historical roster to isolate accounting; explicitly distinguish it from today's T_ONESIDE roster and the exact holiday-skipping v3 code.

Use funded_bootstrap.Boot and funded_sim/funded_sim150 unchanged: 500 paired 500-day histories (seeds 1 and 2, 250 each), circular blocks of 20 days, 250-day first-year horizon, cushion floors/integer sizing and refs 1500/3000. Preserve published NQ/10 fees for exact accounting comparison; disclose that this is not native micro fee validation. No parameter selection; no new strategy placebos needed for this adapter rerun.

Report first/second-year payouts, bad-case p5, blown rate, all-six share, median days to sixth payout (unfinished=inf), paired correction effects and paired allocation effects with bootstrap confidence intervals. Verify that unchanged BASE/EMPTY controls agree exactly and corrected trade nets reconcile to the ledger after documented holiday repairs. Do not presume improved standalone accounting improves account payouts or risk.

Decision: classify each existing adoption claim as supported / inconclusive / contradicted by this rerun, with uncertainty. No promotion or plan edit. Explicitly retain limitations: continuous rather than actual MNQ data, inherited whole-day OT/CLS adverse approximations and MOC marks, unknown source trial count, holiday repair differs from skipping holidays, historical validation not untouched holdout. Stop on missing material inputs or failed reconciliation; document actual blocker rather than inventing a substitute.
