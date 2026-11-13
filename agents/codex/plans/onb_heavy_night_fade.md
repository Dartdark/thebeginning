# Frozen heavy-night fade against the current evaluation book

2026-11-13, before new outcomes. Evidence: `evidence/onb_heavy_night_fade.md`.
Book: ONB $3,500, MON_BR 5, TWIN 2, DT 2, JF 1, NBL 3, LDF risk $1,000.
Use the preceding audit's dates 2018-03-01 to 2026-10-12 and normalized trades.
No strategy/threshold changes after looking at recent results.

## Candidate and clocks

Only T_ONESIDE's heavy-night fade T leg. Existing `t_oneside_test.days` defines
night volume, median of previous 20 valid nights, overnight return and lagged
20-full-RTH-session range. Ratio >1.4; side opposite nonzero night return.
Market entry at open of close-stamped 08:30 bar (08:29 wall clock); market exit
at open of 08:45 bar (08:44 wall clock); stop 0.4 times lagged range, active
on entry bar, stop fills worse of level/open. No future morning VWAP/high/low
used in T signals. Exact source rule; OS leg excluded. Missing exit: skip and
count, do not forward fill for trade generation.

Variants (four definitions total, not an optimization):
1. Primary: T fade, both sides, 1 MNQ, $2.275 round trip per micro at assumed fees.
2. Same at 2 MNQ, no post-hoc size selection.
3. Primary with one-minute delayed entry (08:30 wall clock), same exit/stop rule.
4. Baseline: fade all valid nights at primary clock/stop. Control, not a candidate.
Long/short splits are reports, not selection variants. Existing historical
variants, clock caveats and multiplicity remain in force.

## Stages

1. Design 2018-22 only: native-cost primary must have positive gross and net,
   net t>=2, and random-side placebo p<.05 (1,000 independent draws, same event
   days, each side replayed with its own stop). Report whole and both sides,
   gross-cost bridge, yearly metrics, nonheavy/all-night comparator, lag stress.
   Failed gate stops candidate-dependent 2023+ and account tests.
2. If gate 1 passes, one historical replication on 2023+: positive net and t>=2,
   same placebo. Not a fresh holdout. Standard metrics, 2,000 block-bootstrap
   intervals, permutation DD and trade/daily MC at 1/2 MNQ. Check same days
   against frozen MC T-leg entries and report discrepancies.
3. If gate 2 passes, descriptive ONB-loss contribution (all signal dates first),
   worst book 5% dates fixed from the base, early profit before first $2k
   base crossing, negative/positive ONB dates. No conditioning candidate entries.
4. If gates pass, compare fresh 150K evaluations and a disclosed stressed start:
   start 150,000/floor146,000/target159,050 and 21 sessions;
   stress147,998.08/floor146,000/target159,050 and20 sessions.
   The stress is a historical scenario, NOT today's verified balance.
   $2,000 DLL, EOD floor trails without the funded lock. Paired starts and
   2,000 60-day block-bootstrap difference bands. Same histories across cases.
   Cases base, +T1, +T2, replacement of the most-overlapping base piece at T1,
   and empty slot. Determine replacement by design-period active-minute overlap,
   not P&L. Compare replacement to BOTH base and empty slot.
5. Account decisions require +T1's design difference >=0 and recent/stress
   improvement bands >0. A successful addition must also improve ONB-loss
   contribution before most base failures; otherwise it is income diversification,
   not the requested loss protection. No promotion from a point estimate alone.
   Failed account gate stops funded/implementation tests. Passing candidate
   proceeds to actual funded-base paired one/two-year payout/failure/timing tests,
   checker and frozen forward evidence; no live or strategy changes here.

## Path accounting and validation

Use existing portfolio paths and plan_150k_test.evaluation for canonical account
replay; do not call bench150.setup's unrelated funded cache builder. Reconstruct
the seven-piece base from the audit ledger and match its daily totals exactly.
Canonical adverse-path sums can overstate simultaneous long/short losses;
also replay a common-price low/high bound and close marking as sensitivity.
If an improvement depends on the path convention, report inconclusive.
Use actual Twin/Sunday intervals when reporting early-offset timing. Do not
confuse profits after a base account stop with protection before that stop.

Manifest includes plan/code commits, hashes of grid/ledger/inputs, libraries,
seed20261113, exclusions and source-version comparisons. Saved output/report
under analysis/outputs/codex_onb_heavy_night_fade and agents/codex/results/.
