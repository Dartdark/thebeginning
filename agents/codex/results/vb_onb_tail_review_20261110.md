# VB / ONB evaluation losses: protect progress; no proven costless tail fix

Summary: The user's 89% describes live evaluation failures, per their explicit clarification.
No new return test was run; this is a reconciliation of existing evidence across both branches.
The strongest existing management lead is reducing exposure near the profit target, not tighter stops everywhere.
The latest saved 150K study improves simulated passes 38.9% → 40.6% with half exposure above $6,000 profit.
This is WATCH, not an executable recommendation: fractional sizing, legacy costs, fill and calendar assumptions remain.

## Scope and provenance

Reviewed Codex head `b70cfb4f` and Claude head `72bf8eda` after fetching both branches.
Claude's current brief reports no active accounts; older root documents on Codex retain stale account status.
The user's main objective is avoiding fatal VB/ONB losses without damaging the evaluation book.
Their reported live 89% has no verified denominator or broker-ledger reconstruction in this review.
Separately, Claude's saved simulation reports 89% of failure days have **one component contributing
over 70% of that day's loss**. That is a different statistic: neither proves that 89% of failures
can be prevented by changing VB, nor substitutes for the user's live observation.

Latest Claude sources are byte-preserved in
[`../inputs/vb_onb_tail_review_20261110/`](../inputs/vb_onb_tail_review_20261110/), with hashes and source commit
in `manifest.json`. Upstream output identifies its generating code as a dirty working tree; preserving current
source does not prove exact historical reproducibility. These are reviewed saved results, not rerun outcomes.

## Why an account can fail before the strategy stop

VB's fixed 75-point stop risks $150 gross per MNQ, against a 40-point/$80 gross target.
At 8 MNQ this is $1,200 versus $640; at 15 it is $2,250 versus $1,200; at 20 it is $3,000 versus $1,600.
Fees and adverse execution add to losses. A stop beyond the remaining account cushion cannot protect the account.
The EOD trailing floor moves at the close but is enforced intraday. A daily loss pause is a separate constraint.

Existing November4 forensics record remaining cushions $931.34 / $1,939.60 on the 50K/150K,
versus nominal ONB stop risks $1,062 / $2,478 before costs. See
[`loss_forensics.md`](../inputs/eval_audit_20261104/loss_forensics.md).
Those account states illustrate the mismatch; they do not establish every live failure's cause.

For any prospective entry, compare its incremental executable loss, existing positions, outstanding orders,
costs and liquidation reserve with the actual floor distance. Opposite ONB/VB positions require a common
chronological price path; adding both independent worst excursions can exaggerate simultaneous risk.
An entry veto or earlier exit can reduce exposure, but can also remove the recovery that would have passed.
Gaps and delayed fills prevent calling any software threshold a guaranteed loss cap.

## What the existing tests say

Standalone VB bracket changes, 2018–22 design, fixed one NQ and stated research costs:

| Change | Net versus original | Drawdown / verdict |
|---|---:|---|
| Stop 75 → 60 points | +2.2% | Trade DD +16.5%; lower Calmar; failed |
| Stop 75 → 50 points | −18.9% | Trade DD +4.1%; failed |

Source: [`vb_recent_risk.md`](vb_recent_risk.md). Alternatives did not earn a 2023+ run.
These do not exclude every possible account-aware exit; they reject presenting a simple tighter VB bracket as a fix.

The older cushion/size studies also failed to improve passes per purchase fee: see
`analysis/outputs/vb_cushion_sizing_test_output.txt`, `analysis/outputs/eval_sizing_bench_output.txt`
and `LESSONS.md`. Fewer failures can become more expirations, which still consume the fee.

Latest saved 150K management comparison, **a different book**: VB15, ONB risk2750, Bridge5,
EOS risk1250, Twin2, Dual Thrust2; 2,234 starts from 2018-01-02 through 2026-09-01;
21-session horizon, inherited NQ costs divided by ten, continuously scaled portfolio paths:

| Policy | Pass | Trail fail | Expire |
|---|---:|---:|---:|
| That study's baseline | 38.9% | 60.0% | 1.2% |
| Half exposure when start-of-day profit ≥$6,000 | **40.6%** | **57.0%** | 2.4% |
| Daily stop −$1,000 | 30.2% | 59.4% | 10.4% |
| Daily stop −$1,500 | 35.8% | 60.7% | 3.5% |
| Half near finish + −$1,500 daily stop | 35.6% | 59.9% | 4.5% |

Source: preserved `eval_levers150_output.txt` and `eval_levers150.py`. The finish effect's reported
paired band is +0.8 to +2.8 percentage points, conditional on that model/history. The subsequent threshold
plateau search is post-result evidence, not fresh validation; do not select its best threshold anew.
The policy is recomputed each morning, not a permanent latch after first reaching $6,000.
Continuous half scaling can imply 7.5 MNQ VB and other fractional quantities; no live sizing follows.

An older 50K study's $750 daily stop produced 50.9% passes versus 50.1%, but clips liquidation exactly at
the threshold and uses a prematurely locking floor. Its small apparent improvement is not sufficient to
recommend it, and cannot override the newer negative 150K evidence. See `analysis/combine_levers_test.py`.

The more recent Codex frozen-book baseline uses VB20/Twin2 on 150K, without this study's DT substitution.
Under native-fee/30-calendar-day modelling it gives 48.93% / 37.02% passes on 50K/150K; adverse-minute
DLL stress gives 46.06% / 32.77%. See [`eval_focus_baseline_20261109.md`](eval_focus_baseline_20261109.md).
These quantify model sensitivity; they are not the baseline for the table above. Do not combine their percentages.
Existing common-price replay audits also retain UNKNOWN outcomes where sizing/history cannot be certified.

## Recommendation and remaining uncertainty

1. **Prioritize a verified near-target reduction.** Preserve early opportunity; reduce how much progress a late
   VB/ONB stop can erase. The existing $6,000/half policy is the fixed lead, not permission for another threshold sweep.
   Settle which book is intended first: the branches describe different sizes/components.
2. **Make the remaining-cushion mismatch visible in research.** For each fatal live loss, record pre-entry equity,
   floor, positions/orders, nominal stop, realized fills and earlier daily pauses. Distinguish initially unaffordable
   trades, deterioration after entry, gaps and pre-existing depletion. Do not assume an observed terminal stop was
   avoidable without sacrificing profitable trades.
3. **Judge protection by passes per fee and time/cash needed**, including expirations and correlated attempts.
   A lower failure rate alone is insufficient. Staggering accounts can reduce shared failure exposure but cannot
   rescue an individual account's oversized stop.

Near-target sizing addresses only part of the problem. In the separate saved VB20/Twin failure diagnosis,
53% of failed starts never reached +$1,000 and only 23% reached +$4,500. These are simulated accounts,
not proportions established for the user's live sample. A finish rule will not solve most early failures.
There is no demonstrated way here to remove most fatal stops while preserving the original book's opportunities.

Smallest justified follow-up is **verification of the existing frozen finish policy** against its actual intended
book: integer contract rules, native micro fees, actual 30-day expiry, continuing EOD trail, common-price
intraday floor checks, adverse/delayed liquidation, paired pass/expire results and successful duration.
Commit its exact policy/inputs and decision gates before new returns; retain UNKNOWN coverage and use no
threshold rescue. Independent review and frozen forward observation remain necessary before a trading decision.

No new economic definitions or returns, PowerLanguage, live/VPS/broker changes, messages to other sessions,
schedule changes, or resumed discovery programs. This report completes the requested evidence-based assessment;
it does not claim the follow-up verification ran.
