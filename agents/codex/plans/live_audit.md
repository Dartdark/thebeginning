# Read-only live execution audit

Source snapshot: Claude `e097c0f`; working branch `codex/work`.
Task: `agents/codex/TASK_live_audit.md` at that snapshot. This is an execution-record audit, not a strategy trial.

Read only the git snapshots of logs, journals, setup history, deployed-source descriptions and existing reports.
No VPS connections, broker/API access, live commands, notifications, live-file edits or strategy backtests.
Write only the Codex audit report, an offline reconciliation prototype and outputs under permitted paths.

Preserve three evidence layers: chart-model trades, actual broker executions and user confirmations.
Never turn a chart CLOSE into a broker fill. The user's 10/20 no-fill and 10/21 filled/-$575 per-account
confirmation override any inference that the chart ledger alone proves actual execution.
Do not allocate the 10/21 daily account total to individual executions or assume the residual is fees.

Audit every available live session from the stated 10/12 start to the latest available 10/21 journal;
account 2 begins 10/20. Missing logs/reports mean unknown, not no trade. Include the 10/18 manual test separately.
Inventory report Settings end dates and input versions before claiming same-day backtest matching.
Use existing report reader/matcher where eligible; do not rebuild rules on unavailable post-10/09 raw prices.

Identify each unique chart OPEN/CLOSE episode without treating repeated OPEN events as new fills.
Retain raw append order for POS rows: same-bar states can resolve and exact-row deduplication can erase
the final flat state. Flag unresolved conflicts, scale/identity ambiguity and unsupported precision explicitly.
Evaluate every saved mismatch and rejection summary; distinguish line counts from rejected order IDs and
same-day order errors from stale/non-order strings. Do not automatically suppress all mismatch warnings.

Prototype `analysis/codex_live_reconcile.py`: offline reads only; writes to its Codex output directory.
Accept optional canonical expected-trade and broker round-trip CSVs for future journal integration; absent
verified coverage/fills yields null slippage and P&L comparisons, not zeros or a fictional edge ratio.
Generate per-trade audit, per-day/account/strategy coverage, position transitions, issue classifications,
report coverage/settings and source hashes. Surface duplicate keys rather than silently collapsing different trades.

Report with <=5 summary lines, all known trade/attempt rows, source limits and numbered proposed fixes.
Commit and push the audit FIRST, announce "live audit pushed", then begin TASK_evidence_free_data.md.
