# Swing Target exit-kind correction: fixed-ledger account replay

Continuation of the open check in NEW_CHAT_BRIEF and the October 30 weekly review.
This is an accounting implementation rerun, not a new strategy or parameter search.

Freeze the current `analysis/swing_target_bench.py` rule, CODE_BE ledger, holiday repairs,
cost convention ($7.25/NQ plus one tick per market/stop fill), and its historical base
rosters. Use the common 2018-01-01 through 2026-07-07 source window (OT data ends then).
No new entry/exit decisions, filter, fit or source timing changes. Already observed
2023+ is historical validation. This does not certify the current live/funded roster.

Per account, compare five fixed views: historical base; ST addition (1 MNQ for 50K,
2 for 150K); adopted replacement (VB 2/1 -> 1/1 + ST 1, DT 2 -> ST 2); corresponding
slot empty (VB 1/1 with no ST, no DT with no ST); adopted replacement with legacy
text exit kinds. Both kind views retain exactly the same holiday repairs. Historical
50K roster contains RS longs, not the later T_ONESIDE swap. No plan edits follow.

Rebuild missing ignored caches using existing loaders and fixed rules only. Reuse
funded_lab / funded_bootstrap / funded_sim / funded_sim150. If using an existing
accelerated account engine, require exact parity with canonical simulator on synthetic
fixtures and sampled real paths before accepting results. Account scaling floors whole
contracts and checks the supplied intraday marked path. Preserve existing CLS/OT/MOC
path approximations and disclose them; this is not native broker execution evidence.

Use 1,000 paired 500-day circular-block histories, length 20, seed 20261030; report
1/2-year payouts, p5 year-one payouts, blown share, sixth-payout timing, and paired
differences with sampling intervals. Retain histories/results and input/source hashes.
Report the 2023+ cohort with the same settings; do not select a winner across cohorts.

Decision: the correction alone never establishes adoption. Describe whether the fixed
replacement improves base AND empty slot across payout/risk/speed, and whether the
old-to-corrected outcome actually strengthens. If mixed or small relative to paired
uncertainty, report adoption as not re-proven. Do not tune or run rescue variants.
