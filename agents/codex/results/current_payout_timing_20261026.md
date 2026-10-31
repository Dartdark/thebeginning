# Current funded stacks: first-payout timing calculated

Summary: Current fixed allocations, 1,000 common-history simulations and $1.04 micro round-trip fees.
Median first full-cap payout: 53 trading days from funding on 50K, 45 on 150K.
From a fresh evaluation, including retries: 74 / 69 trading days (about 3.5 / 3.3 months).
There is a long tail; 83% / 92% of fresh funded accounts pay within six months.
These are historical planning estimates, with activation/approval/bank delays excluded.

Plan: `agents/codex/plans/current_payout_timing_20261026.md`, commit `43528dc94c13d9340ceee582fc48a8386245dd12`.
Script: `analysis/codex_current_payout_timing.py`.
Output: `analysis/outputs/codex_current_payout_timing_20261026/`.
New strategy variants/trials: **0**; two adopted allocations, measured at inherited, actual and stress fees.

## Rule as measured

Pinned adopted plan and canonical bench sources: Claude `7f0800ffc04d56bd878750369a4abc2316ee01d8`.
Archived under `agents/codex/inputs/current_payout_timing_20261026/` with source Git blobs and local run hashes.

- **50K:** VB 1/1, Swing Target 1, Overnight Tick/VIX 1, ONB ML $400,
  EOS $700, LDF 2, NFP $500, Bridge Monday 1, CL Sunday 2 MCL,
  ES MOC 2 MES, RS longs 1. Monday Long removed.
- **150K:** legacy base x1.5 (VB 3/1.5 before flooring, ONB ML $600,
  Monday Long 1.5 before flooring, EOS $1,050, LDF 3, NFP $750,
  Bridge Monday 1.5 before flooring, CL 3, MOC 3), RS both sides 1,
  Overnight Tick/VIX 2, Swing Target 2. Dual Thrust removed.
- Keep canonical integer cushion sizing, full size at $1,500 / $3,000.
  Quantities are floor(base x f + 1e-9), f clamped to [0.5,1].
- Evaluation unchanged: VB 8, ONB ADX30 $1,100, Bridge 2, EOS $500 on 50K;
  VB 20, ONB $2,750, Bridge 5, EOS $1,250 on 150K. Risk dollars scale before flooring.

**The event is the first full-cap payout request at a qualifying close:**
$1,500 on 50K or $2,500 on 150K. The account retains its $52,100 / $154,100
safety net, meets five $250 / $350+ days and best-day <50% consistency.
Thus the balance requirement for this first full-cap request is $53,600 /
$156,600. This does not estimate an earlier minimum-$500 withdrawal policy.
Approval, settlement and activation waiting time are not in the existing simulator.

## Results: current stack, actual $1.04 micro fees

All timing is **trading sessions**, counting the event day. A month is approximately
21 sessions. The primary median/quantiles include failures: no payout by day 500
is assigned +infinity. Recipient-only medians are separately available in summary.csv.

| Clock | Account | 10th percentile | Median | 90th percentile | Median months |
|---|---|---:|---:|---:|---:|
| Freshly funded | 50K | 19 | **53** | 187 | **2.5** |
| Freshly funded | 150K | 17 | **45** | 116 | **2.1** |
| Fresh evaluation, retries included | 50K | 33 | **74** | 179 | **3.5** |
| Fresh evaluation, retries included | 150K | 31 | **69** | 139 | **3.3** |

Percentiles describe dispersion across simulated market paths, not confidence
intervals around the median. A median is not a deadline or a promised bank date.

| Clock | Account | Payout by 2 months (42) | 3 months (63) | 4 months (84) | 6 months (126) |
|---|---|---:|---:|---:|---:|
| Freshly funded | 50K | 39.3% | 57.5% | 69.9% | **82.6%** |
| Freshly funded | 150K | 46.6% | 67.3% | 80.5% | **91.7%** |
| Fresh evaluation | 50K | 20.6% | 41.3% | 58.0% | **78.5%** |
| Fresh evaluation | 150K | 20.8% | 43.6% | 64.1% | **86.2%** |

For budgeting, allow roughly **three months after becoming funded**, or
**three to four months from a fresh evaluation**, with room for substantially longer.
An existing evaluation's elapsed time, balance and distance to its trailing line
do not reset to the fresh-account distribution. This is not a conditional forecast
for either live account and does not justify mapping a fresh median onto its original purchase date.

## Account outcomes and cost sensitivity

Fresh funded account, at most 500 sessions or until six payouts / breach:

| Actual-fee result | 50K | 150K |
|---|---:|---:|
| No payout before day 500 | 5.2% | 1.5% |
| Blown before six payouts / horizon | **6.2%** | **1.8%** |
| All six payouts | 93.2% | 98.0% |
| Mean payouts within horizon | $12,188 | $20,118 |
| Median sessions to sixth payout, including non-completers as infinity | 238 | 203 |

This updates the earlier answer's **5.0% / 1.0%** from the published 500-history
Swing Target table. Those are not inconsistent measurements of a single exact
probability: this run has actual micro fees, 1,000 newly fixed histories, and a common
July 2026 data end. Do not present 6.2% / 1.8% as precise live failure probabilities.
No payout is different from eventual blow-up: an account may receive one or more payouts before failing.

| Fees | 50K median from funding / evaluation | 150K median from funding / evaluation |
|---|---:|---:|
| Inherited bench (MNQ/MCL $0.725, MES $0.50) | 53 / 72 | 45 / 69 |
| **Actual assumed $1.04** | **53 / 74** | **45 / 69** |
| Stress $1.24 | 54 / 75 | 46 / 70 |

The former 87 / 95-session figures came from an older stack and a chronological
pipeline analysis. This calculation supersedes them for current-stack planning,
but the difference also includes methodology, fees and sample changes. It is
not an isolated estimate of the benefit of the new strategies.

## Method and verification

- 2,194 available account sessions, **2018-01-02 through 2026-07-07**.
  OT source has 536 trade rows; its later signals are unavailable. All portfolio
  and evaluation paths are truncated to the same end before sampling.
- Existing g24/ge/lab/CL/single-print caches reused; market grids not rebuilt.
  Canonical `fast_plan_lab`, `add_moc_mes`, RS, OT and Swing Target loaders retained.
  The canonical Swing Target bench uses the 602-row CODE_BE ledger plus its
  holiday-exit adjustment, before common-end truncation. This is that bench's
  reconstruction, not a new trade-for-trade replay of the 595-trade MC v3 report.
- Circular blocks of **20 whole market sessions**, 1,000 histories, 500 sessions
  each. Seeds **1,2,3,4**, 250 histories each. Whole-day strategy dependence is
  preserved; both account sizes and every fee scenario use the same histories.
- Evaluation and funding stay in the same history. Failed/expired evaluations
  restart next session. A funded breach before any payout returns to evaluation.
  Two phase medians are never added and phases are not sampled independently.
- Exact finite quantity-state tables reuse `codex_ob_v2_accounts.make_table`.
  Generic funded lookup preserves the canonical 50K/150K state machines.
- **8/8 synthetic parity cases**, covering profits, integer sizing, DLL recovery
  and trailing breach. **16/16 direct historical comparisons** match all five
  canonical outputs exactly (both account sizes; histories 0/17/333/999; 250/500
  sessions). All 12 output summaries reconcile to saved account-level CSVs.
- Sources, caches, MC inputs, code hashes, environment, allocations and seeds
  are recorded in `manifest.json`; raw histories and account results are retained.

Reproduce with the configured environment:

```sh
/workspace/venvs/thebeginning/bin/python analysis/codex_current_payout_timing.py
```

## What could make this wrong

History may overstate future edges or understate dependence across regimes.
Twenty-session blocks preserve local loss clusters, not every longer regime.
The canonical CL and OT paths use constant daily-adverse approximations and
MOC uses a close-based path. Missing intraminute sequencing and live order
failures remain limitations. Fees follow the existing real-fee fallback of one
round trip per active day where older caches have no explicit trade counts.
The 50K evaluation engine gives a pass priority on a same-minute pass/breach
tie; 150K requires the pass strictly before breach. These inherited engines
were not changed to improve timing.

No parameter, entry, exit, allocation, payout policy or live setup changed.
There is no new strategy promotion, side-specific edge test or fresh holdout claim.

Claude review: `agents/codex/results/current_payout_timing_20261026.md`.
