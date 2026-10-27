# PrimeSync placement: no current plan earns a material improvement
Summary: Four frozen full-exit contexts tested at1micro as additions/replacements.
No50K/150K evaluation or funded configuration clears the registered placement gates.
Closest personal addition ES30 adds about$454/year, but improves mean-profit/p95-DD only1.8%, below5%.
Keep the current plans; preserve v2 research code and the MC verification queue.
Native MC parity and independent signal validation remain outstanding.

Plan: agents/codex/plans/primesync_accounts.md, commit2ecbaa2da48a3445ef5b71587b63d6444904df70 before account returns.
Script: analysis/codex_primesync_accounts.py. Output: analysis/outputs/codex_primesync_accounts/.
Four candidate variants (NQ15,NQ30,ES15,ES30); no new exit/entry/side tuning.
Code: [PrimeSync_v2.txt](../code/PrimeSync_v2.txt), [setup](../code/PrimeSync_v2_SETUP.md).

## Rule and account size

Exit0 from the earlier selection stays frozen: full exit4.5R; stop to entry at1.5R and to originalTP1 at2.5R.
This bench uses **one micro per frozen eligible entry**, not the earlier variable-quantity$500 profit table.
The original three-micro/$500 eligibility and cooldown remain, so reducing account size does not manufacture new trades.
Test BASE, ADD, EMPTY_VB and REPLACE_VB. VB was specified in advance as the closest directional-breakout overlap.
No size search or choosing the best market after results provides a fresh validation claim.

Common coverage2018-01-02 through2026-07-07 because reviewed Overnight Tick history stops there.
Current adopted funded baselines are the archived current-payout stacks; personal source is Claude6416de2 (19 pieces).
Funded/evaluation fees$1.04/micro RT, one adverse tick at market/stop/time fills and unchanged target assumptions.
Personal comparison retains the published19-piece accounting/cost assumptions, charging PrimeSync$1.275/unit RT
so it does not gain from a cheaper candidate commission assumption. Those inherited booking approximations remain a limitation.

## Funded results

1,000 paired two-year histories,20-day blocks,seeds1-4x250; canonical cushion sizing.
All contexts are shown at one micro; amounts are payout totals, not raw trading profits.
The two-year column is cumulative over both years; it is not second-year income alone.

|Context|Account|Config|Year1 paid|Two years paid|Blown|Days to6|Year1 change90% interval|
|---|---|---|---:|---:|---:|---:|---|
|NQ15|50K|BASE|$9,932|$12,188|6.2%|238|[$0, $0]|
|NQ15|50K|ADD|$10,024|$12,068|7.2%|237|[$-10, $196]|
|NQ15|50K|EMPTY_VB|$9,812|$12,422|4.4%|249|[$-242, $6]|
|NQ15|50K|REPLACE_VB|$9,761|$12,205|6.1%|247|[$-310, $-42]|
|NQ15|150K|BASE|$18,228|$20,118|1.8%|203|[$0, $0]|
|NQ15|150K|ADD|$18,204|$20,062|2.1%|202|[$-118, $77]|
|NQ15|150K|EMPTY_VB|$17,485|$20,257|1.1%|221|[$-908, $-579]|
|NQ15|150K|REPLACE_VB|$17,534|$20,306|0.8%|220|[$-852, $-530]|
|NQ30|50K|BASE|$9,932|$12,188|6.2%|238|[$0, $0]|
|NQ30|50K|ADD|$9,911|$12,020|7.5%|235|[$-108, $73]|
|NQ30|50K|EMPTY_VB|$9,812|$12,422|4.4%|249|[$-242, $6]|
|NQ30|50K|REPLACE_VB|$9,818|$12,330|5.1%|247|[$-248, $28]|
|NQ30|150K|BASE|$18,228|$20,118|1.8%|203|[$0, $0]|
|NQ30|150K|ADD|$18,233|$20,040|2.3%|201|[$-78, $84]|
|NQ30|150K|EMPTY_VB|$17,485|$20,257|1.1%|221|[$-908, $-579]|
|NQ30|150K|REPLACE_VB|$17,432|$20,226|1.2%|220|[$-965, $-635]|
|ES15|50K|BASE|$9,932|$12,188|6.2%|238|[$0, $0]|
|ES15|50K|ADD|$9,844|$12,073|7.3%|238|[$-184, $10]|
|ES15|50K|EMPTY_VB|$9,812|$12,422|4.4%|249|[$-242, $6]|
|ES15|50K|REPLACE_VB|$9,710|$12,353|4.8%|251|[$-352, $-96]|
|ES15|150K|BASE|$18,228|$20,118|1.8%|203|[$0, $0]|
|ES15|150K|ADD|$18,164|$20,138|1.7%|203|[$-162, $32]|
|ES15|150K|EMPTY_VB|$17,485|$20,257|1.1%|221|[$-908, $-579]|
|ES15|150K|REPLACE_VB|$17,416|$20,286|0.9%|221|[$-978, $-638]|
|ES30|50K|BASE|$9,932|$12,188|6.2%|238|[$0, $0]|
|ES30|50K|ADD|$10,052|$12,134|6.6%|237|[$22, $219]|
|ES30|50K|EMPTY_VB|$9,812|$12,422|4.4%|249|[$-242, $6]|
|ES30|50K|REPLACE_VB|$9,840|$12,346|5.0%|247|[$-220, $38]|
|ES30|150K|BASE|$18,228|$20,118|1.8%|203|[$0, $0]|
|ES30|150K|ADD|$18,296|$20,206|1.4%|202|[$-31, $170]|
|ES30|150K|EMPTY_VB|$17,485|$20,257|1.1%|221|[$-908, $-579]|
|ES30|150K|REPLACE_VB|$17,462|$20,220|1.3%|220|[$-936, $-610]|

Best50K ADD (ES30) earns+$121 in year1, but cumulative two-year payouts fall$54 and blown rises6.2%→6.6%.
Best150K ADD (ES30) earns+$68 in year1,90% interval[−$31,+$170]; insufficient.
Every VB replacement loses year1 payout value and slows completion versus BASE.
Some replacements lower blowups, but do not meet the frozen speed/payout requirements.
The $250 year1 materiality gate fails for every addition, so none qualifies even before MC uncertainty.

## Evaluation results

2,174 complete21-day starts,885 since2023; actual same-minute priority conventions retained.
A candidate needs at least+2 percentage points in both cohorts plus a positive paired lower interval.
No candidate even improves the overall pass-rate point estimate; the first gate fails, so no further confidence gate can qualify it.

|Context|Account|Config|Overall pass|2023+ pass|
|---|---|---|---:|---:|
|NQ15|50K|BASE|50.37%|56.16%|
|NQ15|50K|ADD|49.40%|53.11%|
|NQ15|50K|EMPTY_VB|44.25%|50.51%|
|NQ15|50K|REPLACE_VB|45.08%|51.07%|
|NQ15|150K|BASE|41.54%|45.65%|
|NQ15|150K|ADD|41.21%|44.41%|
|NQ15|150K|EMPTY_VB|31.14%|35.25%|
|NQ15|150K|REPLACE_VB|31.65%|35.48%|
|NQ30|50K|BASE|50.37%|56.16%|
|NQ30|50K|ADD|50.37%|55.14%|
|NQ30|50K|EMPTY_VB|44.25%|50.51%|
|NQ30|50K|REPLACE_VB|44.30%|49.49%|
|NQ30|150K|BASE|41.54%|45.65%|
|NQ30|150K|ADD|41.54%|45.54%|
|NQ30|150K|EMPTY_VB|31.14%|35.25%|
|NQ30|150K|REPLACE_VB|31.74%|35.93%|
|ES15|50K|BASE|50.37%|56.16%|
|ES15|50K|ADD|50.18%|55.93%|
|ES15|50K|EMPTY_VB|44.25%|50.51%|
|ES15|50K|REPLACE_VB|44.80%|50.40%|
|ES15|150K|BASE|41.54%|45.65%|
|ES15|150K|ADD|41.35%|44.75%|
|ES15|150K|EMPTY_VB|31.14%|35.25%|
|ES15|150K|REPLACE_VB|31.37%|35.93%|
|ES30|50K|BASE|50.37%|56.16%|
|ES30|50K|ADD|50.28%|56.27%|
|ES30|50K|EMPTY_VB|44.25%|50.51%|
|ES30|50K|REPLACE_VB|44.89%|50.85%|
|ES30|150K|BASE|41.54%|45.65%|
|ES30|150K|ADD|41.54%|45.31%|
|ES30|150K|EMPTY_VB|31.14%|35.25%|
|ES30|150K|REPLACE_VB|31.46%|35.25%|

Replacing VB reduces pass rates substantially. No evaluation placement is supported.

## Personal results

Published19-piece reference, common dates,1000 paired252-day/20-day-block histories.
Annual$ is mean simulated one-year profit; capital=p95 drawdown/20%.
Return/DD here specifically means mean annual profit divided by p95 annual drawdown, not another report's historical-DD ratio.

|Context|Config|Annual$|p95 DD|Capital|Return/p95DD|Sharpe|
|---|---|---:|---:|---:|---:|---:|
|NQ15|BASE|$40,771|$7,178|$35,888|5.680|3.180|
|NQ15|ADD|$41,689|$7,249|$36,247|5.751|3.176|
|NQ15|EMPTY_VB|$39,063|$7,021|$35,105|5.564|3.181|
|NQ15|REPLACE_VB|$39,982|$7,083|$35,416|5.645|3.175|
|NQ30|BASE|$40,771|$7,178|$35,888|5.680|3.180|
|NQ30|ADD|$41,373|$7,255|$36,277|5.702|3.186|
|NQ30|EMPTY_VB|$39,063|$7,021|$35,105|5.564|3.181|
|NQ30|REPLACE_VB|$39,666|$7,033|$35,163|5.640|3.187|
|ES15|BASE|$40,771|$7,178|$35,888|5.680|3.180|
|ES15|ADD|$41,110|$7,241|$36,205|5.677|3.168|
|ES15|EMPTY_VB|$39,063|$7,021|$35,105|5.564|3.181|
|ES15|REPLACE_VB|$39,403|$6,976|$34,882|5.648|3.169|
|ES30|BASE|$40,771|$7,178|$35,888|5.680|3.180|
|ES30|ADD|$41,225|$7,128|$35,640|5.784|3.178|
|ES30|EMPTY_VB|$39,063|$7,021|$35,105|5.564|3.181|
|ES30|REPLACE_VB|$39,517|$7,095|$35,477|5.569|3.179|

ES30 is the closest personal ADD: annual+$454, p95DD about$50 lower, capital about$249 lower;
mean-profit/p95DD5.680→5.784 (+1.8%). The predeclared5% materiality bar fails.
All other additions/replacements also fail that bar; no personal plan change is recommended.
A below-threshold gain is not proof the strategy has no value at every conceivable size; no other size was tested.

## Verification, uncertainty and code

Candidate terminal paths reconcile to each frozen trade's per-unit cash. Replayed exit times are checked against
original ledgers; later minute ranges are excluded after a modeled stop/target exit.32 exact direct-simulator
checks validate funded lookup outputs across all context/account/config combinations.
This checks accounting/implementation, not the trading edge or statistical validity of the historical bootstrap.

Funded history uncertainty is conditional on the sampled2018–July2026 market days. Existing CL/OT daily-adverse
and MOC close-path approximations remain. Personal baseline retains the current published ledger's mixed marking/
fee approximations; do not treat it as independently rebuilt19-piece live equity. Shared signal/factor dependence,
longer regimes, real micro quote differences and slippage are incompletely modeled.

PowerLanguage v2 exposes FixedSizeContracts1 for this sizing projection;0 restores the earlier variable-risk
comparison. Partial ExitMode1 requires variable-size mode. EnableEntries controls new entries. The original entry
eligibility, milestone logic and full final target stay unchanged. Structural checks pass; MC compilation, partial
entry/rejection behavior, timing and native micro signals remain unverified. See the setup unit-conversion notes.
No code is installed or traded, and no existing plan/live file was edited.

## Decision by destination

|Plan|Decision|
|---|---|
|50K evaluation|Do not add/replace; no pass-rate gain|
|150K evaluation|Do not add/replace; no pass-rate gain|
|50K funded|Do not add/replace; minor payout changes, no risk/payout gate pass|
|150K funded|Do not add/replace; gains too small/uncertain; replacements slower|
|Personal19-piece plan|Do not add now; closest ES30 risk-adjusted gain1.8% is below5% gate|

Keep PrimeSync on the unverified-review queue; compile/parity evidence may settle implementation uncertainty,
but these results do not justify a trading allocation. Report for Claude: agents/codex/results/primesync_accounts.md.
