# Friday weekly reconciliation runbook: 2026-10-19 through 2026-10-23

Status: **waiting for Friday exports**. Review snapshot **59de62a** contains no `live/*_live.xlsx` exports and no
ADX30 evaluation backtest export. Existing reports ending October 9 do not cover this week. No weekly result is claimed.
No job was installed or scheduled here. This runbook records the next conditional task; it is not an unattended monitor.

## Inputs and gates

After Friday's export is pushed, pull `codex/work`, fetch Claude's branch and pin the source commit. Stay on `codex/work`;
do not merge the Claude branch or modify live paths. Read its report blobs or copy needed exports into a new
`analysis/outputs/codex_week_20261019/inputs/` directory. Preserve originals and hashes. Never overwrite the earlier audit.

Required for meaningful comparisons:

- Evaluation ONB key **ONB_ADX30**, not the funded **ONB_ML2_MC** and not ambiguous chart tag ONB.
  Preferred backtest export name: `mc_reports/Backtesting Strategy Performance Report ONB ADX30.xlsx`.
  Explicit `--expected-report` allows any reviewed export path; the filename alone does not establish its settings.
  Read actual Settings: ADXMin 30, 15 Minutes, NQ Overnight Bias evaluation family, dates covering the week.
  Review all other inputs/code against the deployed chart, particularly stops, entry buffer, RiskPerTrade and holidays.
- Rerun/export the matching VB, EOS and Bridge Monday backtests on the user's machine, with their deployed versions
  and dates covering the week. Codex does not rerun strategies during this paused-research task.
- Chart-model live reports and POS logs are useful for model/monitoring differences but **are not broker executions**.
  For actual slippage and missed fills, obtain account-attributed broker executions/order history, commissions and
  rejections, converted into reviewed closed round trips. Retain order IDs, original contract and actual timestamps.
- Confirm account activation dates, actual account identifiers, clock/timezone and contract mapping. Convert actual
  execution timestamps to naive Central time deliberately. Preserve UTC/offset/source times in additional columns.
  Do not assume a 30-minute chart label is the exchange execution time; do not apply a time offset to improve matching.
- Both account chart sets need separate expected scopes and actual records. A dashboard daily P&L confirms the day,
  not trade-by-trade attribution. Do not split the order-tracker screenshot's rows between accounts without evidence.
- Include Sunday evening 2026-10-18 context for Monday's Bridge trade. Canonical comparison assigns entries at/after
  16:00 CT to the next session, consistent with the existing reader. Verify any other session/calendar exceptions.

The review's dashboard table refines 10/21 to **−$575.82 each**, compared with the earlier rounded −$575 confirmation.
The prototype reads this dated table when present in the pinned source; the old e097c0f audit remains a historical
snapshot. This does not identify per-fill fees or allocate the chart/actual residual.

## Canonical records and commands

Canonical CSV required fields:
`account,strategy,symbol,entry_time,exit_time,side,qty,entry,exit`.
`side` is +1/−1; qty is positive whole contracts; entry/exit are actual prices for broker records. Symbols are verified
roots (e.g. MNQ); keep `actual_contract` separately so the normalization does not conceal a wrong-month order.
For other instruments supply explicit `point_value,tick_size`. Do not use chart fills as the broker CSV.
Aggregate partial executions into round trips using account/order identities, not only coincident timestamps.

First, a chart/log coverage audit after exports arrive, with `SOURCE_COMMIT` replaced by the pinned actual commit:

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/thebeginning/bin/python analysis/codex_live_reconcile.py \
  --source SOURCE_COMMIT --start 2026-10-19 --end 2026-10-23 \
  --output analysis/outputs/codex_week_20261019
```

This includes previous-day context. It keeps the original reports' version/coverage caveats; its historical
`daily_account_strategy_coverage.csv` uses the original evaluation activation schedule, which must be rechecked
if deployment changed. An absent file does not establish no trade. Review `backtest_coverage.csv` before comparing.

For an ONB backtest exported on the **same contract root and actual evaluation sizing**, use `--expected-qty report`
to retain per-trade quantities. Example for the first account, after `VERIFIED_ACCOUNT_ID`, input paths and source
settings have been checked:

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/thebeginning/bin/python analysis/codex_live_reconcile.py \
  --compare-only --expected-report analysis/outputs/codex_week_20261019/inputs/ONB_ADX30_backtest.xlsx \
  --report-key ONB_ADX30 --account VERIFIED_ACCOUNT_ID --symbol MNQ --expected-qty report \
  --broker analysis/outputs/codex_week_20261019/inputs/broker_roundtrips.csv \
  --start 2026-10-19 --end 2026-10-23 \
  --output analysis/outputs/codex_week_20261019_onb_account1
```

Repeat separately for the other verified account. Report mode filters both inputs to the declared account/key/root;
its JSON summary records pre-filter row counts. Do not interpret ignored other-account records as a completed audit
of those accounts. An NQ report's quantity cannot be preserved as MNQ quantity. A numeric override is only for a
confirmed fixed-size deployment; it must not replace the evaluation's variable dollar-risk sizing. When report sizing
differs, supply reviewed per-trade expected quantities in canonical CSV rather than inventing a constant size.

For the complete multi-strategy week, assemble a reviewed expected CSV from matching reports, with actual evaluation
account/sizing for each trade. Then compare against the actual broker round trips:

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/thebeginning/bin/python analysis/codex_live_reconcile.py \
  --compare-only --expected analysis/outputs/codex_week_20261019/inputs/expected_roundtrips.csv \
  --broker analysis/outputs/codex_week_20261019/inputs/broker_roundtrips.csv \
  --start 2026-10-19 --end 2026-10-23 \
  --output analysis/outputs/codex_week_20261019_verified
```

These initial runs intentionally omit `--coverage-complete`: unmatched rows remain unresolved. Add it only after
review establishes that **both files cover every declared session/account/strategy**, including entirely silent days
and first/last dates, and all expected settings/versions and actual attribution are verified. Then absent expected
matches become missed/extra. The flag is a declaration, not a completeness detector. Never use it simply because the
command ran or to turn unknown evidence into zeros.

## Deliverable after the actual weekly dry run

Write `agents/codex/results/live_reconcile_week_20261019.md` with a Summary of at most five lines. Pin input commits,
hashes, report Settings, accounts, sizing/normalizations and all exclusions; preserve chart, broker and dashboard layers.
Report matched/missed/extra/unresolved counts by account and key, wrong sizes, entry/exit slippage and timing offsets,
plus gross and net reconciliations where fees are supplied. Explain every discrepancy and any remaining unknowns.
If broker data is absent, report a chart-model comparison only and leave actual slippage/performance unknown.

Do not issue a scale/edge-retention decision from a handful of trades, a near-zero/negative baseline, incomplete
coverage or a model ledger substituted for fills. No automated position changes or recommendations to reset charts
from stale flags. Research, funded bench and VPS integration remain paused. Commit/push only permitted Codex paths
and send the report path back to the user for Claude's review. Wiring into 16:40 remains a separate reviewed action.
