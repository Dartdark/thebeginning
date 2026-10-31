# Swing Target correction replay: adoption not re-proven

Summary: The numeric exit-kind fix improves isolated ST accounting, but does not establish the adopted replacements.
In the common-source full-history pool, the 50K replacement reduces first-year payouts $274 and slows payout six by 6 days;
the 150K replacement reduces two-year payouts $98 and raises blown share 0.5 percentage points.
Both replacements earn less over two years than their empty-slot controls. The fix is valid; its claimed portfolio benefit is unproven.
No allocation, live strategy, account, VPS or broker setting was changed.

Plan: `agents/codex/plans/swing_kind_account_replay_20261030.md`, commit `531e3b1`.
Script: `analysis/codex_swing_kind_account_replay.py`, commit `fd9e628`.
Output: `analysis/outputs/codex_swing_kind_account_replay/`.
Trials: zero new economic rules; five registered accounting/allocation views per account, two fixed historical pools.

## Rule and comparison

Replayed the existing 602-row CODE_BE ledger using Claude's numeric-kind adapter and its three unchanged holiday repairs.
The text-kind control retains those same repairs. Signals, sizing rules, costs and account state machines were not tuned.
Both accounts use 1,000 paired 500-session circular-block histories per pool, 20-session blocks, seed 20261030.
The source window is January 2018 through July 7, 2026, when the OT evidence ends; the second pool starts January 2023.
This is historical validation on already observed data.

Base = the historical roster in `swing_target_bench.plans50/plans150`, reconstructed with the current canonical helpers.
50K replacement = VB 2/1 -> VB 1/1 + ST 1; empty = VB 1/1 without ST.
150K replacement = DT 2 -> ST 2; empty = remove DT without adding ST.
Addition = ST 1 on 50K, ST 2 on 150K, retaining the original slots.
The historical 50K base has RS longs, preceding the later T_ONESIDE change; these results do not certify today's complete roster.

## Account results

Payout dollars are means; blown share and sixth-payout timing refer to the 500-session horizon.
Timing includes non-completers as infinity, rather than reporting survivors alone.

| Pool | Account | View | Year 1 | Year 2 | Blown | Median sessions to payout 6 |
|---|---|---|---:|---:|---:|---:|
| 2018+ | 50K | Base | $10,301 | $12,299 | 5.5% | 228 |
| 2018+ | 50K | Addition | $10,671 | $12,310 | 5.4% | 213 |
| 2018+ | 50K | Replacement | $10,028 | $12,390 | 4.8% | 234 |
| 2018+ | 50K | Empty slot | $9,622 | $12,449 | 4.1% | 251 |
| 2018+ | 150K | Base | $18,421 | $20,365 | 0.7% | 197 |
| 2018+ | 150K | Addition | $18,859 | $20,232 | 1.4% | 186 |
| 2018+ | 150K | Replacement | $18,328 | $20,267 | 1.2% | 198 |
| 2018+ | 150K | Empty slot | $17,385 | $20,365 | 0.6% | 219 |
| 2023+ | 50K | Base | $11,424 | $12,315 | 5.5% | 197 |
| 2023+ | 50K | Addition | $11,690 | $12,426 | 4.7% | 185 |
| 2023+ | 50K | Replacement | $11,010 | $12,265 | 5.9% | 202 |
| 2023+ | 50K | Empty slot | $10,805 | $12,446 | 4.5% | 216 |
| 2023+ | 150K | Base | $19,751 | $20,214 | 1.5% | 163 |
| 2023+ | 150K | Addition | $19,799 | $20,167 | 1.8% | 152 |
| 2023+ | 150K | Replacement | $19,656 | $20,227 | 1.5% | 164 |
| 2023+ | 150K | Empty slot | $19,449 | $20,421 | 0.4% | 180 |

The full CSV also gives first-year p5 payouts. For 50K full-history base/replacement they are $1,500/$0;
the second-year p5 rises $1,500 -> $10,000. This mix of speed, early cash and survival cannot be called an unconditional gain.

Selected paired differences, with 90% Monte Carlo intervals for the mean:

| Pool | Account | Comparison | Metric | Difference [interval] |
|---|---|---|---|---|
| 2018+ | 50K | Replacement minus base | Year 1 | -$274 [-$423, -$132] |
| 2018+ | 50K | Replacement minus base | Year 2 | +$92 [-$55, +$238] |
| 2018+ | 50K | Replacement minus empty | Year 2 | -$59 [-$158, +$33] |
| 2023+ | 50K | Replacement minus empty | Year 2 | -$181 [-$317, -$44] |
| 2018+ | 150K | Replacement minus base | Year 2 | -$98 [-$213, +$15] |
| 2023+ | 150K | Replacement minus empty | Year 2 | -$194 [-$317, -$85] |

These intervals measure simulation sampling error conditional on the empirical source pool and model.
They do not measure uncertainty about future edge, source reconstruction or account rules.
The addition views also mix faster payouts with small/negative two-year changes; they do not earn a new adoption here.

## What the correction actually changes

Within the registered window, numeric kinds restore $129 total cash per MNQ and change 48 daily minima.
The earlier full-ledger audit's $132 included later trades outside this window.
Against the identical text-kind replacement, the 50K full-history corrected replay changes mean year-one payouts +$7,
year-two +$42 and blown share -0.4 percentage points. The 150K full-history change is +$8 in year one and zero
in year-two payouts/blown share. In the 150K 2023+ pool, corrected year-one payouts decrease $6, with unchanged
year-two payouts/blown share. Better isolated fills need not improve every account-path metric.

## Verification and limitations

The existing finite-quantity engine is used to accelerate the canonical simulators; it preserves whole-contract
flooring under cushion sizing and each supplied intraday path minimum. Exact comparisons cover all five original
simulator outputs at 250/500 sessions on synthetic payout/trailing-floor/daily-limit/zero-size/rounding fixtures
and the first three production histories of every view and cohort, for both accounts. `parity.json` retains the results.
All 20 saved result sets reconcile to `summary.csv`; histories, paired differences and input/source hashes are retained.

The current ONB export contains an unfinished October 12 entry with an exit-before-entry sentinel. The initial
cache build stopped on it. Applying the preregistered July 7 cutoff before constructing paths excludes that record;
no exit was invented, and no account outcomes were inspected before that repair. No shared loader was edited.

Inherited limits remain material: CLS/OT use daily adverse approximations; MOC uses its existing close-mark path;
fees are NQ-equivalent, not verified native micro fees. The CODE_BE ledger plus holiday repairs is not an independent
reconstruction of the installed v3 signal. Current source exports/helpers and the common-source window differ from
the original October 25 bench, so this is not a controlled attribution of every difference from its published figures.
It controls the numeric/text accounting comparison within this run. No new alpha/placebo/side-specific search was performed.

For Claude: the accounting fix stands, but replace the claim that adoption "can only strengthen" with this mixed
account-level evidence. Review the actual current roster separately before making a plan decision.
