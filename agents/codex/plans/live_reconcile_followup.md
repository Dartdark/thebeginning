# Execution reconciliation follow-up; research paused

Source: Claude review `59de62a`, `agents/codex/results/REVIEW_live_audit_free_data.md`.
Branch: `codex/work` only. This is offline engineering, not a strategy trial.

1. Add an explicit ONB_ADX30 evaluation key to the Codex reconciliation prototype. Reuse the existing
   live_vs_backtest report reader, but validate Settings first: ADXMin 30, 15-minute chart, evaluation ONB rather
   than funded ML. No fallback to the existing ADX20 report. Account, symbol and evaluation size must be supplied,
   not inferred from chart tags or from one-NQ backtest contracts. Require date coverage and declare any remaining
   input/version differences. Keep canonical broker records separate from chart reports.
2. Draft an inert PowerShell proposal under agents/codex/proposals/ plus review/integration notes. No changes to
   live/vps/watchdog.ps1, scheduler, logger, health script, VPS, notifications, orders or credentials. Stateful mismatch
   requires fresh appended evidence across polls; a resolved later row clears it. Never use bar HHMM as wall-clock age.
   Rejection parsing must use each line's actual timestamp and order-specific rejection/invalid language, date-scoped
   deduplication and explicit unknown-format diagnostics. Preserve warnings for ambiguous logs rather than guessing.
3. Verify offline with synthetic report/CSV fixtures (including wrong ADX, funded ML, missing coverage, missed first
   day, account/size isolation). A PowerShell runtime is not currently installed: state any unexecuted draft validation.
4. Friday's report export is not present in 59de62a. Record a concrete weekly runbook for 2026-10-19 through 10-23,
   including Sunday Bridge context, account identity, broker round trips and complete-report coverage. Do not pretend
   the old October-9 reports cover the week. Run the actual weekly reconciliation only after exports arrive.

Preserve the first audit as a historical snapshot. Follow-up notes should distinguish its rounded user confirmation
(-575) from the later Apex dashboard evidence (-575.82 each), and retain per-fill/account uncertainty where not resolved.
Commit and push only Codex paths; hand Claude the proposal and readiness report. No research, backtests or cache builds.
