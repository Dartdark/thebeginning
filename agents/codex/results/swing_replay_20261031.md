# Swing Target exit-kind replay: adoption gains remain inconclusive

Summary: Completed the pending corrected-exit funded replay, with 500 paired two-year histories per account.
The exit repair improves fixed-ledger cash by $132/MNQ, but changes neither selected replacement's two-year payouts or failures in this sample.
50K VB replacement versus base: first-year −$65, two-year −$83, failures +0.6 percentage point; 150K DT replacement: +$138, +$43, failures −0.4 point.
Both comparisons overlap zero uncertainty; the statement that adoption can only strengthen is unsupported.
No trading-plan, live, VPS or broker changes. Independent review remains pending.

Plan: `agents/codex/plans/swing_replay_20261031.md` (local preregistration 4c3819f, published b7cacb1).
Script: `analysis/codex_swing_replay_20261031.py`.
Outputs: `analysis/outputs/codex_swing_replay/`.
Trials: zero new economic definitions; existing five candidate plans/account, empty-slot controls and legacy-accounting diagnostics only.

## Comparison and scope

Source snapshot: Claude `a01be1bfd0a3c33bc2c6745b24acbf5c14e924c1`.
Use that snapshot's existing `swing_target_bench`, `funded_bootstrap`, funded simulators,
lab, single-print/CL/RS/DT/OT/MOC helpers. This is an accounting replication of an
already-tested strategy, not fresh out-of-sample evidence or a new standalone test.
Existing standalone metrics/placebos remain historical; no new rank is assigned.

Each account: seed 1, 500 paired circular-block histories, block length 20, 500 trading days;
year one = 250 days. Resampling pool: 2,262 source trading days from 2018 through October 9, 2026.
Every strategy keeps the same sampled days. Both existing account simulators floor
scaled per-strategy quantities to whole micros. 150K cushion reference = $3,000;
50K = $1,500; existing 0.5–1.0 cushion scaling retained.

Legacy versus corrected accounting holds plans, repaired trade ledger and histories
fixed. The three holiday repairs retain numeric kind 2 in BOTH cases. The revised
264 target exits use numeric kind 1 and 82 stop/breakeven exits numeric kind 0;
256 time/holiday exits use kind 2. The source's net column is not treated as the
account path: cash is recomputed from prices and the lab's costs.

Costs are the **existing NQ-equivalent bench convention**: $7.25/NQ round trip,
one 0.25-point tick per market/stop fill, then /10 per MNQ; MES/CL use the existing
helpers. These are not verified native micro fees or fills. No native-cost robustness
or new signal/execution model is claimed.

## Funded accounts

Mean payouts are dollars per account; failures cover two years. Sixth-payout days
use the existing simulator convention, assigning infinity to histories that do not
reach six; these are unconditional medians. The full five-plan sweeps are in the CSVs.

| Account / comparison | Year 1 | Year 2 | Failed by year 2 | Median days to payout 6 |
|---|---:|---:|---:|---:|
| 50K base, VB 2/1 | $9,854 | $12,262 | 5.8% | 242 |
| 50K VB 2/1 → 1/1 + ST 1 | $9,789 | $12,179 | 6.4% | 244 |
| 50K one VB_N contract removed, ST slot empty | $9,257 | $12,206 | 6.2% | 260 |
| 50K RS longs → ST 1 | $10,190 | $12,231 | 6.2% | 235 |
| 50K RS longs slot empty | $9,390 | $12,097 | 7.0% | 258 |
| 150K base, DT 2 | $17,823 | $20,093 | 2.2% | 210 |
| 150K DT 2 → ST 2 | $17,961 | $20,136 | 1.8% | 208 |
| 150K DT slot empty | $16,590 | $20,092 | 2.0% | 234 |

The VB replacement's first-year fifth-percentile payout is $0 versus $0 base;
its two-year fifth percentile is $0 versus $1,500 base. All three main 150K cases
have a two-year fifth percentile of $20,500. Payout-cap saturation explains why
most paired two-year differences are zero; it does not establish equivalence.

Selected replacement minus base, 95% intervals for the mean under this finite
simulation, from resampling the paired histories:

| Comparison | Year 1 difference | Year 2 difference | Failure-share difference |
|---|---:|---:|---:|
| 50K VB replacement | −$65 [−$309, +$168] | −$83 [−$314, +$145] | +0.6 pp [−1.2, +2.4] |
| 150K DT replacement | +$138 [−$150, +$431] | +$43 [−$239, +$323] | −0.4 pp [−1.8, +1.0] |

Against the empty slot, ST increases first-year payouts by $532 [+$333, +$729]
on 50K and $1,371 [+$1,102, +$1,656] on 150K. Two-year differences versus empty
are −$27 [−$212, +$157] and +$44 [−$187, +$270]. Thus a faster payout than an empty
slot does not itself justify replacing the existing strategy. The RS alternative
has faster first-year payouts but also does not dominate its base on two-year risk.
These intervals measure Monte Carlo uncertainty conditional on the empirical
pool/model, not uncertainty about the historical edge or future live outcomes.

## What the exit repair changes

Cash/path checks reproduce $132/MNQ extra closing cash, with 48 changed daily minima
and 345 changed minute paths. Corrected standalone cash is $198,478.35 per NQ over
the 602-ticket holiday-repaired ledger, reconciled to its day-ending path totals.

For the selected VB replacement, corrected versus legacy accounting gives year-one
+$7 [−$23, +$37], with identical two-year paid/failure outcomes. For the DT replacement,
year-one +$20 [−$14, +$58], again identical two-year paid/failure outcomes. Do not
translate improved trade accounting into an assumed portfolio improvement.

The old saved 500-history table is not this run's counterfactual: its original
scratch caches/pooled seed history were not retained in this snapshot. The exact
legacy-accounting control above is the appropriate repair-only comparison.

## Rebuild defect and checks

The documented `build_lab.py scratch_data` builds both grids but then crashes in
`portfolio.paths` on the ONB ML report's final row: October 12 entry 09:15 stamp
(mapped to minute 09:06), exit stamp 00:00 **on the same reported date**, Signal
`open`. It is an unfinished valuation, not a completed cross-date fill.
The research adapter removes only explicit `open` exits and records the row.
Five reversed OND holiday intervals are among nine rows already removed by the
existing OND MaxEntryDelay rule; that backup is not in these compared plans.
No source helper or live file was modified. The general build_lab bug remains for
Claude to fix upstream; this script's prep stage safely bypasses it.

`checks.json`: 602 tickets, numeric exit enums, three preserved holiday repairs,
cash/path reconciliation, finite result arrays, integer payout counts, bounded
cash payouts, valid binary failure flags, year-one paid ≤ year-two paid. All pass.
`excluded_report_rows.csv` records the one unfinished row and nine existing OND exclusions.
`manifest.json` hashes source inputs. Python 3.12.14, NumPy 2.3.5, pandas 2.2.3.
No PowerLanguage changed; no deployment acceptance or broker-fill verification.

## Limits and review handoff

- Rebuilt NQ bars extend through October 30, but the account pool deliberately stops
  October 9. Other report legs and the OT order-flow series have different endpoints
  (OT ends July 7). This retains existing helper behavior, including zero days after
  a ledger ends, and is not a complete common-coverage live-plan forecast.
- Existing MC holiday tickets/CL-OT conservative day paths and original Swing
  holiday-repair assumptions are inherited. This does not independently validate
  the current MultiCharts v3 signal ledger or every legacy strategy path.
- NEW_CHAT_BRIEF's closing plan pointer says RS → ST on 50K; TODO/TIER_LIST and the
  recorded adoption say VB reduction + ST. Both alternatives are shown; the user
  should not infer that either was silently changed here.
- Extended-data strategy reruns, dashboard refresh and October 12–28 missed-trade
  reconciliation remain pending. No account number or installed state was invented.

For Claude: review `agents/codex/results/swing_replay_20261031.md`; fix unfinished
report-row handling in the general builder; replace the “can only strengthen” claim
with the measured inconclusive outcome. No live or funded-plan change is requested.

Reproduce on a disposable checkout of the source SHA above, copy this script from
codex/work, use the repository dependencies, then run:

```sh
python analysis/build_lab.py scratch_data
# Its existing lab-stage failure is documented; g24.pkl/ge.pkl have been written.
python analysis/codex_swing_replay_20261031.py prep
python analysis/codex_swing_replay_20261031.py 50 500
python analysis/codex_swing_replay_20261031.py 150 500
python analysis/codex_swing_replay_20261031.py audit
```
