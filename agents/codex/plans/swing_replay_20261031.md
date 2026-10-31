# Swing Target exit-kind repair: frozen account replay

Existing-strategy accounting replication, not a new alpha search. Source snapshot:
Claude a01be1b; read-only comparison with Codex 70f708ad. No live changes.

Use `analysis/swing_target_bench.py`'s existing five plans per account, plus the
relevant empty VB/RS/DT slots. Compare corrected and legacy exit-kind accounting
for the already-adopted VB replacement (50K) and DT replacement (150K), paired on
the same 500 circular-block histories, seed 1, block 20 days, horizon 500 trading
days; year one = 250 days. Existing funded simulators, costs and cushion rules.
No settings selected from results. Integer quantities are floored by those simulators.

Rebuild dependencies from owned inputs. Exclude MultiCharts exit rows whose Signal
is `open` (unfinished valuation, not completed fill), and report every exclusion.
Fail on any other reversed interval remaining after the existing OND entry-delay
filter. Freeze resampling dates to 2018-01-01 through 2026-10-09, the common original
research cutoff; later NQ data does not imply refreshed tickets for the other legs.
Retain original Swing ledger holiday repairs. Do not substitute MC v3 for that
ledger: that would answer a different comparison.

Report payout means, paired intervals, blown share, sixth-payout timing, empty-slot
controls and direction of corrected-versus-legacy changes. Decision: support an
existing replacement only if it improves the base AND empty control on relevant
payout/risk measures; overlapping uncertainty is inconclusive. No automatic
adoption, tuning, new placebo search or live strategy changes. Report code parity,
historical coverage, native micro fee and holiday-repair limitations explicitly.

If inputs or mechanics prevent a faithful replay, save a reproducible blocker and
do not manufacture account results. General extended-data/live reconciliation is
a separate pending task.
