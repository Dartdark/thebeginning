# H10 VB covariance: independent source rejection confirmed

**Review integrity PASS; hypothesis/source gate FAIL.** The missing required book date closes H10
before covariance windows, quantity masks, raw prices or economic tests. The machine-readable
[decision](hunt_v2_vb_covariance_source_result.json) deliberately has `passed:false` and
`raw_outcome_authorized:false`; integrity verification is not permission to continue.

Budget verified in current progress: **5/60 economic evaluations,10/10 registered hypotheses,4gross
screens**, plus archived65t6. This independent review adds0hypotheses,0gross screens,0economic
evaluations. The final-hypothesis budget boundary requires root's complete summary and authorized
continuation pause; this review changes no automation, progress, book, settings or other branch.

## Bound run and scope

- Preregistration: `f7d70c64b5a55da9afeb216996081711102ae623`.
- Implementation: `98d5fd54bb4bd38511dbbe113a26040e4e1d97dc`.
- Actual FEATURE entrypoint: `2026-10-27T04:41:51.924394+00:00` through `2026-10-27T04:41:52.449520+00:00`.
- [Saved marker](../../../analysis/outputs/codex_hunt_v2_vb_covariance/feature_verified_execution.json), SHA256`a2dfc238c3cbac421e17df18320edb8fb2657ee78d0dbc077ccd09a6c8f75556`.
- [Saved gate](../../../analysis/outputs/codex_hunt_v2_vb_covariance/feature_gate.json), SHA256`e18c0820437b2a1085b4c428be79523d6c32de2e7b5353517dc042c716c0f5a2`.

The reviewer verified all **6** listed artifact hashes and all **10** code/dependency/plan/evidence
hashes against current files and the implementation commit. The frozen plan and mechanism also match
the preregistration commit. Both baseline copies match the frozen `d724c7d02b6db71e63ba705079dbea7fefaa42c6b4f436308a28993ca1908803`
SHA256 and267640bytes each. No favorable alternate source was selected.

Actual reviewed inputs were saved audit JSON, source code and a **focused original baseline DATE
COLUMN ONLY** read (`pandas.read_csv(...,usecols=['date'],dtype={'date':'string'})`). This reviewer
selected no P&L column, converted no P&L value, calculated no covariance, and opened no raw NQ/ES
file, market/MC ledger or account path. The full source or earlier ES audit was not rerun. Full-file
hashing verifies byte identity and does not interpret financial cells.

## Independent reconciliation

|Check|Result|
|---|---:|
|Original baseline date rows|2,262, strictly ordered/unique|
|2018–22 stored design rows|1,289|
|Runner's finite, exact19-column design rows|1,289;0unknown rows/0format issues|
|First / last design date|2018-01-02 /2022-12-30|
|Full saved calendar records|1,826, every2018-01-01..2022-12-31 date|
|Expected normal/early cash dates|1,259|
|Expected dates actually present|1,258|
|Extra actual non-normal rows retained|31|
|Missing required normal date|**2020-11-30**|
|Excluded future date-metadata rows|973|
|Runner's2023+ financial cells numerically converted|**0**|
|Covariance / activation mask / activation counts|**NOT COMPUTED**|
|Raw/gross/protected/account returns|**NOT RUN**|

The count identity is `1,259 expected -1missing +31extra observed =1,289 stored design rows`.
The31 holiday/other rows remain in the admitted row collection; they were not dropped to create a
more favorable rolling window. No actual252-row covariance window was formed after the failed gate.

The973 out-of-design date keys split into2023:257,2024:259,2025:257,2026:200. The date-only review
reconciles these counts. Source inspection confirms `read_design_rows` continues on an out-of-design
date **before** width/financial conversion. The saved zero-future-financial-conversion claim is
consistent with that guard. This is not a read of validation P&L or a validation result.

## Decisive missing date

The original baseline's date column goes from2020-11-27 to2020-12-01;2020-11-30 is absent.
Focused neighboring keys are2020-11-25,11-26,11-27,12-01,12-02. The bound calendar record identifies
2020-11-30 as Monday, `kind:'normal',cash_close_j:900` (15:00CT), not a holiday or early closure.
This is a fact under the committed source-calendar contract, not a new claim that all native-futures
coverage has been independently certified.

The preregistration explicitly requires every normal/early cash date across the full design range.
A missing expected row therefore fails globally. It is not an observed zero/no-trade day and cannot
be removed, zero-filled, relabeled as a closure or bypassed by compressing the252-row history. The
numeric/header audit's PASS does not cure the missing-date coverage failure.

## Proof that the failed run stopped before feature and outcome selection

The hash-bound `run_features` branch saves source and calendar audits, then assigns
`SOURCE_REJECTED_BEFORE_FEATURES` when either fails. Only its separate `else` branch calls
`compute_features`, summarizes activation counts and writes `feature_rows.json`/`feature_counts.csv`.
The saved calendar fails on the date above. The gate says `feature_mask_computed:false` and
`feature_counts_computed:false`; both output files are absent at the declared output path. No
`gross_*` or `design_*` output is present there. The marker likewise records no raw execution,
new candidate profit/t/account calculation or authorization to continue.

Thus the activation count is **unknown, not zero**. The review establishes neither that negative
covariance opportunities exist nor that they fail economically. All five protected definitions,
matched allocation paths, first-proposal gross, source-native parent replay, five metrics, dailyNW5,
placebos, book/EMPTY benches and2023+ historical validation remain unrun. The preserved algebraic
identity and predata software fixtures are not substitutes for those measurements.

## Limits and disposition

Published fee/reentry, mark/version, OTcoverage, counterfactual roster and source-completion-clock
limits remain unchanged. Minimum cash-calendar coverage is not proof of native MNQ fills, complete
futures data or actual account receipts. No variance-reduction, alpha, promotion, funded/evaluation
pass or payout claim follows from this audit.

**Close H10 unchanged.** Keep all failure/selection history, save the complete bounded-program
summary and pause the exact authorized continuation at10hypotheses. Do not calculate masks after
repairing/deleting this date, start an eleventh hypothesis, price an overlapping diagnostic as an
executable strategy, or resume t6/the paused watcher.

## Focused date-only reproduction

Historical review recipe only; do not rerun the failed FEATURE entrypoint or a full price audit:

```python
import pandas as pd
from datetime import date
p = 'analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.24/baseline_daily19.csv'
keys = pd.read_csv(p,usecols=['date'],dtype={'date':'string'},keep_default_na=False)['date']
days = [date.fromisoformat(x) for x in keys]
assert days == sorted(set(days))
assert len(days) == 2262
assert len([d for d in days if date(2018,1,1) <= d < date(2023,1,1)]) == 1289
assert date(2020,11,30) not in days
# No P&L column is selected or converted.
```
