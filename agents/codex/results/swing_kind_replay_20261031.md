# Swing Target corrected account replay: 50K benefit not reproduced; 150K favorable

Summary: the exit-kind correction is valid, but it does not strengthen every portfolio result.
Across 500 paired histories per size, old/fixed swaps have identical two-year payouts and failures.
Fixed 50K swap vs BASE: first-year -$213, two-year -$95, failures +0.4 percentage points; earlier adoption benefit is not reproduced.
Fixed 150K swap vs BASE: first-year +$601, two-year +$357, failures -1.8 points; vs EMPTY it mainly improves payout speed.
These are historical-roster comparisons with inherited simulator limitations; no trading allocation was changed.

Plan: [frozen replay](../plans/swing_kind_replay_20261031.md), commit `0b72684`.
Code: [replay](../../../analysis/codex_swing_kind_replay_20261031.py), commit `7a1f2d9`;
[saved-output verification](../../../analysis/codex_verify_swing_kind_replay_20261031.py).
Evidence: [output directory](../../../analysis/outputs/codex_swing_kind_replay_20261031/).
New strategy definitions: zero. Five predeclared portfolio configurations per account size, no tuning or rescue reruns.

## Scope and inputs

Read the requested Claude-branch handoff, CLAUDE.md, TODO.md and LESSONS.md, then AGENTS.md and the current Codex builder brief.
The concrete unfinished task was the October 30 exit-kind correction's full funded account replay.
Claude source is pinned to `86df2c0` (code unchanged from `a01be1b`; only the brief changed).
The CODE_BE ledger at Codex `70f708a` matches Claude's copied `checks/candidates/swing_target/codex_be_trades.csv` byte for byte.
All research edits remain on codex/work. No shared strategy, ranking, live, VPS, or broker configuration was edited.

This replays the historical rosters encoded in `swing_target_bench.plans50/plans150`, not a new strategy backtest.
50K: normal VB 2 -> 1 MNQ plus ST 1; flagged VB stays 1. 150K: DT 2 -> ST 2 MNQ.
EMPTY removes the displaced allocation without ST; ADD retains BASE and adds ST at 1/2 MNQ.
Costs preserve the legacy bench: $7.25 per NQ round trip plus one tick per market/stop fill,
then divided by ten for MNQ-equivalent paths. These are assumed costs, not verified native micro commissions.
Simulators floor final cushion-scaled contract quantities. The historical 150K base's fractional intermediate
sizes (for example flagged VB 1.5) remain an explicit inherited assumption, rather than a new sizing proposal.

Circular 20-trading-day blocks keep all strategies on the same sampled days. Seed 20261031,
500 histories per account size, 500 trading days each; year one is 250 days. Each account comparison is paired.
Ten resumable checkpoints use contiguous slices of the one registered RNG history matrix, not ten reseeded samples.

## Input/accounting verification

- Rebuilt NQ/ES grids and missing plan dependencies using existing library functions, without helper research sweeps.
  Grid covers 2017-05-01 through 2026-10-30, with 2,451 trading rows; Boot uses rows from 2018 onward.
- The ordinary `build_lab.py` crashes on ONB ML's unfinished report entry dated 2026-10-12 09:15,
  whose matching exit is explicitly labeled `open` at 00:00. It is a marked open position, not a completed trade.
  The research adapter excludes that one explicit placeholder, restoring 343 closed ONB ML trades, and rejects other
  unresolved geometry. The shared builder remains unchanged and still needs this fix upstream.
- Kept all 602 ST records and the original repairs on 2018-05-28, 2022-06-20 and 2023-07-03.
  After repair: 264 targets, 82 stop/breakeven exits, 256 time exits.
- Numeric target kinds remove an extra $0.50/MNQ charge per target: total corrected ledger cash increases $132/MNQ.
  Corrected daily closes reconcile to reconstructed trade cash, and every corrected adverse-path mark is at least
  as high as its original counterpart. This does not establish monotone payouts through a stateful account simulator.
- Saved summaries and paired standard errors independently reconcile to all 20 checkpoint files. Bounds, payout counts,
  cap arithmetic, finite values, script hash and checkpoint identities pass. See [verification.json](../../../analysis/outputs/codex_swing_kind_replay_20261031/verification.json).

## 50K funded: original benefit not reproduced

Dollar columns are mean account cash payouts. Failure and completion shares refer to the full two-year horizon.
Sixth-payout timing treats unfinished accounts as infinity before taking the median.

| Frozen configuration | Year 1 | Year 1 p5 | Year 2 | Year 2 p5 | Failed | All six | Median sixth day |
|---|---:|---:|---:|---:|---:|---:|---:|
| BASE | $10,227 | $1,500 | $12,240 | $1,500 | 6.4% | 93.6% | 232.5 |
| REPLACE_OLD | $10,012 | $1,500 | $12,145 | $1,500 | 6.8% | 92.4% | 239 |
| REPLACE_FIXED | $10,014 | $1,500 | $12,145 | $1,500 | 6.8% | 92.4% | 239 |
| EMPTY | $9,536 | $1,500 | $12,300 | $3,000 | 5.6% | 93.8% | 256.5 |
| ADD_FIXED | $10,602 | $1,425 | $12,209 | $1,425 | 6.2% | 93.4% | 222 |

FIXED minus BASE: year one -$213 (paired Monte Carlo 95% interval -$434 to +$8),
year two -$95 (-$377 to +$187); failure +0.4 points (-2.0 to +2.8 points).
FIXED minus EMPTY: year one +$478 (+$266 to +$690), year two -$155 (-$367 to +$57), failure +1.2 points.
The swap does not meet the preregistered support criterion. It is not evidence of a reliably worse strategy either:
the sampling bands overlap zero, and the earlier published sample was different.
Do not characterize the original 50K adoption as re-proven by the accounting fix.

## 150K funded: favorable relative to DT, faster than leaving the slot empty

| Frozen configuration | Year 1 | Year 1 p5 | Year 2 | Year 2 p5 | Failed | All six | Median sixth day |
|---|---:|---:|---:|---:|---:|---:|---:|
| BASE | $17,477 | $5,500 | $19,799 | $20,500 | 3.6% | 96.4% | 212 |
| REPLACE_OLD | $18,086 | $8,500 | $20,156 | $20,500 | 1.8% | 98.2% | 205.5 |
| REPLACE_FIXED | $18,078 | $8,500 | $20,156 | $20,500 | 1.8% | 98.2% | 205.5 |
| EMPTY | $16,808 | $5,500 | $20,096 | $20,500 | 2.0% | 97.8% | 227 |
| ADD_FIXED | $18,576 | $8,500 | $20,151 | $20,500 | 1.8% | 98.2% | 195.5 |

FIXED minus BASE: year one +$601 (+$218 to +$984), year two +$357 (+$32 to +$682),
failure -1.8 points (-3.5 to -0.1 points).
FIXED minus EMPTY: year one +$1,270 (+$963 to +$1,577), year two +$60 (-$187 to +$307), failure -0.2 points.
The point estimates support the historical swap without higher failures; its clearest advantage over EMPTY is
earlier cash, not a firmly separated terminal payout total. ADD also looks favorable on this sample, but was a
control rather than a new selected allocation. No replacement of the existing trading decision is made here.

## What the exit-kind fix itself changed

For both sizes, every paired old/fixed history has the same two-year payout amount, payout count and failure flag.
Other account state/timing differs: run duration changes in 22/16 histories (50K/150K), and first-payout day in 3/8.
Only 3/1 histories change cash received by day 250, producing average differences +$2/-$8.
Thus the claim that the accounting correction makes adoption "only stronger" is not a valid portfolio conclusion.
Its isolated cash/path improvement is real; the account-level consequence has now been measured separately.

## Limits and next work

These intervals measure Monte Carlo sampling error conditional on the frozen historical days and model.
They omit uncertainty about future edge, fills, fees, source coverage and strategy selection. No fresh holdout,
new strategy metrics, placebo search or independent strategy-checker promotion is claimed; original standalone
ST evidence remains in the earlier Swing Target reports.

Inherited limitations remain: CL and Overnight Tick whole-day adverse proxies can invent simultaneous exposure;
ES MOC uses the bench's reconstructed path; the OT ledger's last trade is 2026-07-03 and its documented source
cutoff is 2026-07-07, with later missing history treated as zero by the legacy adapter. Different component report
cutoffs and old holiday trades remain in the historical baseline. The ST ledger's last trade is 2026-10-08.
This does not refresh all strategies onto extended live data.

The 50K live-plan documentation has since replaced RS longs with T_ONESIDE. These comparisons intentionally
retain the original RS-long roster to isolate the October 25 adoption and October 30 correction. Before treating
the 50K placement as validated for the current book, freeze and test the actual T_ONESIDE roster with matching
component coverage. The separate extended-data/live missed-trade refresh also remains open.

For Claude: review `agents/codex/results/swing_kind_replay_20261031.md`; revise the joint summary's
"can only strengthen" claim, distinguish the two account results, and handle the shared builder's explicit
open-position placeholder. No action on the VPS or live sizing follows from this report.

## Reproduction

Use codex/work with the committed plan/script. Create a separate source checkout at `86df2c0`.
From that source directory, use `Grid24()` and `Grid24('data/ES_1min_20*.csv', night_pattern='')`
to pickle `g24.pkl` and `ge.pkl` into an empty scratch directory. The ordinary build_lab command currently
fails at the open sentinel described above; these two grids are its unchanged first two outputs.
Run the replay script with arguments `SOURCE_CHECKOUT SCRATCH prepare`, then `SOURCE_CHECKOUT SCRATCH 50`
and `SOURCE_CHECKOUT SCRATCH 150`. Finally run `analysis/codex_verify_swing_kind_replay_20261031.py`.
Input hashes, exact rosters, fixed RNG settings, code hash, cache hash and dependency versions are saved with the outputs.
