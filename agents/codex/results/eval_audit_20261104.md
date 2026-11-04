# Evaluation strategy and sizing audit — November 4, 2026

Summary: The current plans cannot be certified optimal; documented ONB stop risks exceeded remaining account cushions.
Audited 36 families/18 testable sources and 2,965 registered configurations, retaining 809,476 overlapping account scenarios.
Best identified 50K frozen nominee: ONBML at 20 MNQ with a prospective target guard, 45.1% pass/45.6% fail/9.3% expire.
Current-baseline missing risk inputs prevent an identified superiority claim; depleted-cushion failure remains severe.
No replacement earns the frozen recommendation gates; native execution/guard verification and user allocation review remain pending.

## Decision

The earlier pass-rate estimates are insufficient to establish that today's evaluation books are the best available.
The recent loss records expose a concrete sizing problem: fixed dollar-risk budgets can exceed the account's
remaining floor cushion. The broad comparison also found no demonstrated low-failure replacement. Preserve the
existing purchase/approval boundary; these research results do not select or install a new allocation.

The strongest fully identified 50K alternative among the four frozen nominees is ONBML at 20 MNQ with a
prospective account target guard. It still fails 45.6% of historical fresh starts. The 150K FC2B candidate
fails 65.2%. LDF reduces failures largely by expiring: 54.0% of its 150K starts never pass. These are
conditional model results, not calibrated live-account probabilities or evidence that losing streaks end.

## What the four losses establish

|Account/date|Recorded remaining cushion|Planned ONB stop risk before costs|Implication|
|---|---:|---:|---|
|150K #3, Oct 30|$1,822.60|$2,456.00 at 8 MNQ|Floor can liquidate before the planned stop|
|50K #2, Nov 4|$931.34|$1,062.00 at 3 MNQ|Same|
|150K #4, Nov 4|$1,939.60|$2,478.00 at 7 MNQ|Same|

Account #1 failed October 26; its exact final fill/floor is not independently reconstructed. The final two
failures share the same NQ signal, so they are correlated exposures. They are not independent strategy trials.
On November 4 both account equity logs were below their floors by 09:50 CT. Later VB chart trades are not
demonstrated broker fills. The earlier chart-signal “15/15 execution OK” comparison also included known rejected
or post-lock/death trades. Exact broker attribution still needs the original statements; committed chart logs
alone cannot reconcile it. See the [source-linked forensic report](../inputs/eval_audit_20261104/loss_forensics.md).

A final read-only fetch found Claude advanced to `75df521` during this audit. Its `0b5ac65` follow-up now
excludes the later account#2/#4 chart trades from dashboard/journal generation. The tested evaluation roster
and source inputs did not change. See [source follow-up](../inputs/eval_audit_20261104/source_followup_75df521.md).

## Search and evidence boundaries

- Reviewed the 368-row registry as 36 economic/source families; 18 compatible source strategies entered this study.
  Failed families, multiday/early-close violations and missing material signal inputs remain excluded with reasons
  in the [inventory](../inputs/eval_audit_20261104/strategy_inventory.md). VB partitions were not independent alpha.
- Original 2,485 configurations: uniform scaling, current-book reweights/removals, ONBML substitution, standalone
  strategies, two/three-leg equal-risk books, replacements, diversification and account risk controls.
- A separately committed 460-case fixed-quantity arm followed input-admission findings. It includes 1/2/4/8/12/20
  native micros per standalone and equal 2/4 per eligible pair. Its 16 canonical aliases reuse earlier results.
  It avoids needing ATR to calculate quantity; it does not reconstruct missing ATR or relax held-price/fill gates.
- An independently sourced DT correction moved all 401 time exits uniformly to their known OPEN clock.
  The 390 legacy CLOSE mismatches remain in original results. All 401 corrected open prices matched; no favorable
  touch search or source price change occurred. See [diagnosis](../inputs/eval_audit_20261104/postexecution_source_diagnosis.md).
- The joint design selected four parents; 20 reserved governor/target-guard definitions were committed before
  their outcomes. Final nominations were committed before 2023+ account computation. Total 2,965 registered
  definitions, 35 slots unspent under 3,000. Conservative counts and aliases preserve multiplicity; configurations
  and overlapping account starts are not independent predictive discoveries.
- Primary source window: 2018-04-02–2026-07-07, with 2017 raw warmup. Design uses 244 Monday starts with whole
  expiry before 2023:723,460 account records. Historical validation uses 896 weekday starts 2023-01-02–2026-06-08,
  each with complete 30-calendar-day access: 8 candidate/control books × 12 cost/cushion views=86,016 more records.
  Previously seen 2023+ is historical validation, not fresh OOS. Recent October/November losses were not fitted.

## Fresh-account historical validation

All rows use 896 identical starts. Pass time is calendar days **conditional on passing**. All four nominated
books have 20 MNQ(two NQ minis); source signals/exits stay fixed. Three add the prospective target guard.

|Home / frozen nominee|Pass|Fail|Expire|Unknown|Median pass days|Fee units per pass|
|---|---:|---:|---:|---:|---:|---:|
|50K FC2B 20 MNQ + target guard|38.8%|61.0%|0.1%|0.0%|3.76|2.57 × |
|50K ONBML 20 MNQ + target guard|45.1%|45.6%|9.3%|0.0%|9.72|2.22 × |
|150K FC2B 20 MNQ + target guard|28.3%|65.2%|6.5%|0.0%|10.26|3.53 × |
|150K LDF 20 MNQ|6.7%|39.3%|54.0%|0.0%|21.92|14.93 × |

Fee units are descriptive fee/P(pass), not an independent-retry forecast. The actual 50K purchase price
is unverified. Conditional on a $249 150K purchase, FC2B implies $878.36 per pass and LDF $3,718.40,
excluding activation/other charges. EMPTY has 0 passes/0 failures/896 expirations in each home.

### Current baseline is not identified

|Home|Confirmed pass/fail/expire/unknown counts|Identified pass-rate range|
|---|---|---:|
|150K|6 / 128 / 0 / 762|0.7%–85.7%|
|50K|23 / 80 / 0 / 793|2.6%–91.1%|

Missing expected-open ATR lookback observations prevent certifying the current dollar-risk quantities.
UNKNOWN is neither a failure nor a no-trade day. Confirmed-pass differences against this baseline cannot
be treated as improvements. All paired 90%4/8-week, 5,000-resample identified pass and failure contrasts
span zero widely. Neither the efficiency nor safety recommendation gate is established.

### Recent 2026 source cohort

These 113 starts end June 8, with paths through July 7; this is not all 2026 or the November failure period.

|Frozen nominee|2023–25 pass/fail|2026 pass/fail/expire|
|---|---|---|
|50K FC2B 20 MNQ + target guard|41.8% / 58.1%|18.6% / 81.4% / 0.0%|
|50K ONBML 20 MNQ + target guard|45.1% / 46.2%|45.1% / 41.6% / 13.3%|
|150K FC2B 20 MNQ + target guard|28.0% / 64.6%|31.0% / 69.0% / 0.0%|
|150K LDF 20 MNQ|5.9% / 35.8%|12.4% / 63.7% / 23.9%|

FC2B 50K deteriorates to 18.6% pass/81.4% fail in the 2026 cohort. No new date filter, rescue size
or nominee substitution was made from this observation.

## Costs and depleted-cushion sensitivity

Main commission is $1.24 RT per micro plus one adverse native tick per market/stop fill. A two-sided MNQ
market roundtrip therefore costs $2.24 per micro, before additional impact. Low cost is $1.04 RT/one tick;
stress is $2.48 RT/two ticks($4.48 per two-sided MNQ market roundtrip). Limits require frozen trade-through
qualification. MES/MCL fees in unselected designs remain assumptions, not broker invoices.

|Frozen nominee|Main fresh pass/fail|Stress fresh pass/fail|Half cushion pass/fail|Quarter cushion pass/fail|
|---|---|---|---|---|
|50K FC2B 20 MNQ + target guard|38.8% / 61.0%|37.8% / 62.1%|25.6% / 74.4%|15.5% / 84.5%|
|50K ONBML 20 MNQ + target guard|45.1% / 45.6%|43.0% / 47.9%|33.6% / 63.6%|16.0% / 81.6%|
|150K FC2B 20 MNQ + target guard|28.3% / 65.2%|27.6% / 65.3%|16.5% / 81.9%|8.6% / 90.8%|
|150K LDF 20 MNQ|6.7% / 39.3%|6.1% / 44.0%|6.1% / 56.4%|5.0% / 75.1%|

Thin-cushion starts have zero initial net profit and 25/50/75% of the original trail left. They are synthetic
states, not replays of the actual four accounts. Faster conditional pass times among surviving thin-cushion
accounts do not offset the increased failures. All 12 scenario/cohort counts are retained in the
[metrics CSV](eval_audit_20261104_metrics.csv) and exact case archive.

### Why smaller risk controls did not solve the target/expiry tradeoff

On the known 100-point-stop FC2B design, the full cushion/DLL cap has 50K 22 passes/222 expirations/0 failures
(9.0% pass), and 150K 11 passes/233 expirations/0 failures(4.5% pass), each of 244 starts. Tighter caps mostly
expire. These controls were retained and did not win the frozen selection.
For LDF/ONBML, missing historical risk inputs can cause the defined cap model to reject orders. Their
zero-trade/zero-failure expirations are data-rejection outcomes, **not evidence that native ATR risk caps
are safe or ineffective**. All final validation nominees have risk_fraction=0; this limitation does not
create their positive pass rates. A remaining-cushion check is a necessary implementation safeguard for
a proposal, but a profitable evaluation schedule still has to earn its target before expiration.

## Engineering checks and material limits

- Corrected model rules include EOD floor ratchet with inclusive intraday enforcement, evaluation versus
  PA floor-lock distinction, market DLL liquidation/pause, 30 calendar-day access, net integer contract caps,
  closing costs before target recognition and suppression of later orders after account termination.
- Dates/closures and compressed-chart clocks are explicit; the index 15-minute pause endsJune 28,2021.
  Source lookback gaps remain unknown. Missing returns are not interpolated. Original and amended
  code, source hashes, ledgers, trial history and outcome fingerprints are preserved.
- Engineering checks include 35 synthetic cases/100 raw-versus-fast tapes, 157 actual-fill design checks
  and 220 checks across four frozen validation cases, including a 150K pass. These validate the specified
  accounting model; they are not independent native-platform economic verification.
- Shared OHLC phases and cross-asset ordering remain models. Intraminute first observed liquidation prices
  can differ materially from actual tick-level DLL/floor liquidation. Continuous NQ/ES/CL prices do not
  verify MNQ/MES/MCL native spreads, contract rolls, latency, queue priority or size-dependent market impact.
- The target guard is prospective, uninstalled/unverified. It requires account-equity monitoring, market
  flattening/cancellation and suppression of further entries after reaching the realized target. Its modeled
  benefit cannot be assumed from an uncompiled/native-unmatched controller or a chart-only signal log.
- Fast minimum equity is a visited-node minimum plus a conservative bound, not exact joint drawdown.
  No alternate tick chronology, exact native source matching, funded payouts or personal-account return
  improvement is claimed. All 36-family/old strategy selection histories remain relevant.

## Reproduction and Claude handoff

|Stage|Committed before dependent outcomes|
|---|---|
|Original evidence/config/exact code/2,485 definitions|`a087708b13697df4c3dd0b0814f98cb53a2b254a`|
|Fixed-size arm/source-clock overlay/460 definitions|`e8e249b4e7c8946d517e8e4c9a4a3b4e62063e24`|
|Joint initial selection/20 governor definitions|`67bab2a2daa808ffc7c50ebde150ed857df51b69`|
|Frozen final nominees before 2023+|`588e6b692e83154d056a3ecefca8eb1411f78d19`|

Use `/workspace/venvs/thebeginning/bin/python` from repository root. Original stage commands are in
[runner usage](../inputs/eval_audit_20261104/runner_usage.md). For the amended stages, use
`analysis/codex_eval_amended_run_20261104.py` with `--commit e8e249b4e7c8946d517e8e4c9a4a3b4e62063e24`;
derived design uses `--selection-commit 67bab2a2daa808ffc7c50ebde150ed857df51b69`, validation uses
`--selection-commit 588e6b692e83154d056a3ecefca8eb1411f78d19`. Saved completed cases are reused by hash.

The [exact case archive](eval_audit_20261104_cases.zip) and
[SHA 256 manifest](eval_audit_20261104_cases.manifest.json) retain account CSVs, ledgers, quality/source
receipts, design/validation summaries and all 12 uncertainty views. Large reconstructible tape arrays are
excluded. To render this report/CSV from the retained runtime tree, run
`python analysis/codex_eval_report_20261104.py`; it computes no new market outcome or selection.

Review [Claude handoff](../inputs/eval_audit_20261104/CLAUDE_REVIEW.md),
[account/source review](../inputs/eval_audit_20261104/final_results_review.md) and
[raw/account engineering review](../inputs/eval_audit_20261104/validation_engineering_review.md).
The remaining current-baseline requirement is source-matched per-entry stop/risk values or native sizing
evidence for its ONB/EOS history. Existing free/owned minute gaps cannot certify those values. This does
not authorize a recurring data chase, proxy replacement or a new outcome-selected strategy. The completed
research and exact code are ready for the user to forward to Claude; no external message was sent.
