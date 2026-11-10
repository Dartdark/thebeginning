# Frozen VB loss-side partial exit, evaluation-first

User steering: the book is being changed; Twin2, DT2 and other methods already exist, but VB's loss mechanics
remain the priority. Do not present finish mode or these additions as a new solution. No live changes.
Evidence: `agents/codex/evidence/vb_loss_split_20261110.md`. Plan/code committed before economic results.

## One proposal, four total definitions

150K only: existing VB15, ONB ADX30 risk2750, Bridge5, EOS risk1250, Twin cap1 v2.1 2, DT v4 2 MNQ.
Existing per-account finish mode at morning balance≥156000: each quantity rounds half to nearest whole,
minimum1 if original quantity>0. This is the single-account protocol, NOT a replay of group-mean copier sizing.

- BASE: existing VB entries, target40/stop75, normal15 and finish8 MNQ.
- SPLIT: same total entry quantity, floor(q/2) stop37.5 and ceil(q/2) stop75; target40 for both.
  No replenishment; the remaining leg preserves the baseline busy interval, maximum3 entries/day.
- REDUCED: same original bracket, floor(.75q), minimum1, i.e.11 normal/6 finish; approximate nominal-risk control.
- EMPTY: remove VB; retain all other components and their existing finish policy.

SPLIT normal full-stop gross loss is7×37.5×2+8×75×2=$1725 vs BASE$2250, before gaps/costs.
This arithmetic is not a backtest or guaranteed account loss bound. All contracts are integer.

## Information and execution

Use canonical `candidates24.vault_break24` signals and `codex_break_vb_onb.vb_engine`, midnight anchoring,
prior ATR15, 30-minute decisions, next-minute-open entry, 10:00–14:30, early11:00/11:30, max3/day.
Full-leg replay fixes the entry sequence; shallow leg uses `grid._walk` from that same entry through the full-leg exit.
Research target requires1point through. Nearest-extreme OHLC convention and gap-open stop fills retained.
The remaining leg never exits earlier, so the changed stop cannot create extra full-flat re-entry opportunities.
Split exits must reconcile contract-weighted trade, daily and path cash.

Assume commission1.25RT/MNQ; one adverse tick on market/stop legs, none on target exit.
VB entry/exit slippage is charged on its actual leg, not lumped onto the later exit. Other component path
conventions remain those of the committed `codex_eval_focus_baseline_20261109.py`.
Reuse its raw-file provenance checks, frozen Twin loader, MC/Bridge normalization and cost bridge;
add DT using existing `dual_thrust_test`/`funded_lab.with_slippage`, not a new port.

Account: start150000,target9000,ongoing EOD trail4000,DLL2000,actual30-calendar-day exclusive deadline.
Floor breach beats a target in the same minute. Evaluate both ideal DLL threshold clipping and adverse-minute
liquidation. Neither protocol certifies exact fills or a true mathematical bound on live execution.
Inherited per-sleeve adverse extrema can be nonsimultaneous; missing held minutes and source end dates
must be disclosed. This is a conditional screen, not an independently verified causal common-quote replay.

## Design gate before any new 2023+ SPLIT outcomes

Design starts≥2018-01-02 with the entire30-day horizon ending before2023; last admitted full-history start
is2026-09-01, matching the conservative common source-report coverage of the prior baseline.
Unchanged other-strategy full ledgers may be loaded, but evaluate new VB/SPLIT trades only through2022 first.
Four definitions, no additional distance/fraction/target/grid. Existing bracket/cushion trials remain counted.

Report pass/fail/expiry, fee-per-pass index1/p, median successful trading/calendar days, paired baseline→new
outcomes; 60-start moving-block bootstrap2000draws, seed20261110,90% interval on pass-rate difference.
For each of BOTH DLL protocols, SPLIT must beat the reduced-size control's pass rate and meet either:

- Efficiency: passes≥BASE+2 percentage points, pass-difference lower90% bound≥0, failures≤BASE.
- Safety: failures≤BASE−10pp, passes≥BASE−1pp, pass-difference lower90% bound≥−2pp.

In both cases successful median calendar days≤BASE+3. These are evaluation-risk gates, not alpha t-stat promotion.
If either protocol fails, reject this definition, stop its dependent validation and do not rescue thresholds.
Report standalone native-cost whole/long metrics by design year, Sharpe/Sortino/PF/Calmar/Ulcer/t/DD,
trimmed-trade fate (original target/stop/time), saved stop losses and foregone recovery gains. Shorts N/A.
Standalone profit retention is diagnostic, not a requirement to preserve the old book.

Only a survivor earns unchanged2023+ historical replication and paired/bootstrap/stress assessment using
the same gate; report era/year outcomes. No claim of fresh holdout. Any positive result remains WATCH pending
common-price/UNKNOWN-aware replay and independent verification; no automatic code/plan/live promotion.
No funded/personal scope expansion, paper scout, extra candidate, schedule or message to another session.

Pre-outcome input amendment: first launch stopped in raw-hash validation before any strategy generation.
The current2026 day/overnight files differ from the frozen `fe35af99` source. Materialize that exact committed
raw tree under `/workspace/vb_loss_split_source` and load both grid and DT from it; preserve the stop receipt.
No shared data, rule, cost, date, variant or gate changes. Commit amended code before rerunning.
The next launch also stopped before strategy generation because the inherited loader resolves Git blobs
relative to its data root. Give that isolated root separate Git metadata with an object-store alternate;
this preserves exact blob verification without changing or duplicating the shared repository's metadata.
