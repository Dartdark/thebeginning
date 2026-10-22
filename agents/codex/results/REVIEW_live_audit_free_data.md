# Claude's review: Codex `live_audit.md` (67eec3e) and free-data evidence sheets (28d7307), 2026-10-22

## Live audit: accepted, useful
- Right separation of three records: chart-model trades (the logger), broker executions, the user's account figures.
  **The logger records MultiCharts' position, not fills** (10/20: logged losses, nothing filled).
- 10/20 root cause confirmed since: the user's order-tracker screenshot (`live/orders_20261020_21.md`, after Codex's
  snapshot) shows both entries sent as `@MNQ`, broker ID 0, rejected. Mapping now `MNQZ6` (10/21 filled). Codex's fix
  item 1 (order history) is done for 10/20-21; items 2-3 (mapping, gear account) are verified by the 10/21 fills and the
  Apex dashboard (accounts -01 / -02 each −$575.82).
- **Health false alarms: fixed in `analysis/vps_health.py`** (Claude, this commit): MISMATCH now only when the LAST row
  for a chart is still mismatched (10/21: both were resolved within the bar → informational line); rejection counts
  from an earlier day or without 'reject / invalid' in the last line are shown as probable noise, not REJECTED ORDERS.
  Not yet changed: `live/vps/watchdog.ps1` (bar time used as heartbeat age; same stale-mismatch logic). It runs on the
  VPS, so a change there needs the user to pull on the VPS: proposed for the weekend.
- Backtest coverage gap is real: reports / NQ data end 10/09, so no live-vs-backtest edge ratio yet. Friday's report
  export (TODO) fixes it; the evaluation ONB is ADX30 (`live_vs_backtest.py` maps the funded ONB ML: add an ADX30 key).
- `analysis/codex_live_reconcile.py`: keep as an offline prototype; wire into the 16:40 job only after a dry run with the
  Friday exports.

## Free-data evidence: accepted, both DON'T TEST
Treasury dealer awards (no evidence of a 40-minute effect worth $70-102 gross per ZN) and ETF fails (data published weeks
late) are correctly stopped at the sheet. No third sheet invented to fill the quota: right call.

## Overall
Seven research rounds without a new strategy, each stopped cheaply. That is the filter working, not Codex failing: with
free data, the obvious forced flows are already tested or already in the plan. Codex's time is now better spent on live
execution and reconciliation until new data or a strong outside idea arrives.
