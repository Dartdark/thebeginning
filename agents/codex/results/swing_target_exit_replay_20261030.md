# Swing Target exit-kind replay: 150K supported; 50K tradeoff remains

Summary: the corrected 150K DT-to-ST replacement improves first-year and
two-year payouts and failure rate versus both its old roster and empty slot.
The 50K VB-to-ST replacement lowers failures but reduces first-year payouts;
two-year payouts do not beat the empty slot. The exit-kind fix itself has a
small, non-monotonic account effect. Keep the correction; do not claim both
adoptions "can only strengthen." The 50K choice needs a current-roster review.

Scope: the outstanding replay in `NEW_CHAT_BRIEF.md` at source commit `86df2c0`.
Plan: `agents/codex/plans/swing_target_exit_replay_20261030.md` (a925c43;
precision extension 875f4e5). Script: `analysis/codex_swing_target_exit_replay.py`.
Outputs: `analysis/outputs/codex_swing_target_exit_replay/`.
No new strategy variants, rankings, plan changes, or live changes.

## Results: 5,000 paired histories

Means are payouts received, not trading P&L. Days to sixth payout include
unfinished accounts as infinity, following `Boot.compare`.

| 50K original roster comparison | 1y payouts | 2y payouts | Blown | Median days to sixth |
|---|---:|---:|---:|---:|
| Original plan, VB 2/1 | $9,940 | $12,104 | 7.0% | 240 |
| VB 1/1 + ST 1 | $9,766 | $12,189 | 5.9% | 241 |
| VB 1/1, replacement slot empty | $9,314 | $12,213 | 5.5% | 260 |

Relative to the original 50K plan, the adopted replacement's paired first-year
change is **-$174 [90% interval -$244, -$105]**, two-year change
**+$85 [+$10, +$162]**, and failure-rate change **-1.18 percentage points
[-1.80, -0.56]**. Against the empty slot it gains $452 in year one but changes
two-year payouts by -$24 [-$74, +$27] and failures by +0.36 points
[-0.06, +0.78]. It earns faster than the empty slot, but does not establish
a two-year advantage over it. The prior claim of improved first-year payouts
and speed over the old plan is not reproduced.

| 150K original roster comparison | 1y payouts | 2y payouts | Blown | Median days to sixth |
|---|---:|---:|---:|---:|
| Original plan, DT 2 | $17,817 | $20,059 | 2.2% | 209 |
| DT 2 replaced by ST 2 | $18,024 | $20,157 | 1.7% | 204 |
| DT slot empty | $16,840 | $20,058 | 2.1% | 228 |

Relative to the original 150K plan, the adopted replacement gains
**$207 in year one [+$123, +$292]**, **$98 over two years [+$28, +$170]**,
with **-0.54 percentage points failures [-0.90, -0.18]**. Against the empty
slot, the corresponding changes are +$1,184 [+$1,111, +$1,257], +$99
[+$35, +$163], and -0.42 points [-0.74, -0.10]. That supports the original
150K replacement within this frozen bench, subject to the limitations below.

The correction versus the **same replacement with legacy text encoding**:

| Account | Paired 1y change, 90% interval | Paired 2y change, 90% interval |
|---|---:|---:|
| 50K | +$5 [-$3, +$12] | +$2 [-$8, +$12] |
| 150K | +$12 [+$1, +$23] | -$2 [-$16, +$11] |

The account benefit of the encoding fix is small and not consistently positive
on every metric. Higher trade nets alter cushion-sized quantities, payout dates
and exposure to later losses; account outcomes are not monotonic in a trade's
P&L. The first 500 histories even put both replacements below their original
plans on two-year payouts. That sign changes at 5,000 histories; retain the
500-run artifacts as evidence of Monte Carlo variability, not as the verdict.

For Claude: review `agents/codex/results/swing_target_exit_replay_20261030.md`;
the 150K replacement is supported in the old bench, while the 50K decision
requires an explicit risk-versus-first-year-payout tradeoff and a current-roster
check incorporating T_ONESIDE. Do not adopt another row from this replay merely
because its point estimate is higher.

## Method and checks

Use the existing `swing_target_bench.pt_trades`, `OTB.lab_for`, `FB.Boot` and
funded simulators. Each account size uses 5,000 paired 500-day histories,
20-day circular blocks, seed 20261030; first-year payouts use 250 days.
Keep all five original comparisons, plus the adopted replacement's empty slot
and the adopted replacement using the former text exit kinds. The first
500-history run is retained in `n500/`; the precision extension is in `n5000/`.

The saved ST ledger has 602 trades, 2018-02-09 through 2026-10-08. Its three
holiday holds receive the existing last-bar flatten correction. The original
reasons are 265 targets, 47 stops, 36 break-even stops and 254 time exits;
after the holiday correction, 264 target exits retain limit treatment.

Accounting checks pass: corrected trade nets and daily closing P&L both total
$198,478.35 per NQ. All non-holiday corrected nets also match the source ledger
row by row. The legacy encoding totals $197,158.35: the corrected total is
$1,320 higher, exactly 264 targets times $5. This trade-level improvement does
not impose monotonicity on whole-account payouts or survival.

Rebuilding the lab exposed one unfinished funded ONB ticket, 2026-10-12: the
MC report labels its exit `open` and stamps it at midnight before its entry.
The standard builder crashes on its empty minute slice. The replay verifies
that source label and excludes the unfinished ticket, preserving the 343
completed trades. It does not invent a realized exit or change the shared loader.
The preparation log records this explicitly.

## Interpretation limits

- These comparisons preserve the **original pre-adoption rosters** from
  `swing_target_bench.py`. The 50K roster has RS longs, not the later T_ONESIDE
  substitution. This is a replay of the original adoption evidence, not a
  validation of today's entire funded roster.
- The rebuilt grid reaches 2026-10-30, but the saved strategy reports have
  different endpoints. No fresh signals were invented to extend them. This
  therefore cannot be compared with the old printed table as an isolated
  exit-kind effect: the seed and rebuilt data also differ. The paired legacy
  control within this replay isolates that effect.
- Paired 90% intervals describe simulation precision conditional on this
  historical input and simulator. They do not establish future trading returns
  or account risk. Broader source-data, path-model and rule assumptions remain.
- Existing bench conventions are retained, including its CL/overnight adverse
  path proxies, micro cost assumptions and the original half-day adjustment.
- Payout caps hide some speed gains. Assess first-year payouts, time to the
  sixth payout and failures alongside two-year payouts; do not select another
  winner from this table without separate confirmation.

## Reproduce

Install the dependencies in `agents/codex/BUILDER_BRIEF.md`, including numba.
From the repository root, with a fresh cache directory:

```sh
python analysis/codex_swing_target_exit_replay.py scratch_data/st_exit_replay prepare
python analysis/codex_swing_target_exit_replay.py scratch_data/st_exit_replay 50 5000
python analysis/codex_swing_target_exit_replay.py scratch_data/st_exit_replay 150 5000
```

The driver builds prerequisite caches through existing functions and avoids
rerunning the research sweeps or slow one-history scoring in the cache builder.
It records the source ledger SHA-256, frozen plans, seed, counts, paired
intervals, summary CSVs and raw simulated histories. Syntax and whitespace
checks also pass.
