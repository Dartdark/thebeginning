# Execution follow-up: ADX30 matching prepared; watchdog proposal awaiting review

Summary: Added ONB_ADX30 to the offline prototype, with report identity, ADX, interval and date-coverage gates.
It refuses ADX20/funded-ML substitutes, preserves declared per-trade sizing, and separates account/key matching scopes.
The watchdog draft uses fresh-row mismatch state and today-only order-failure parsing; no VPS/live changes.
All 15 Python synthetic checks pass; PowerShell is unavailable, so the draft is unexecuted and needs Windows replay validation.
Friday's weekly dry run is pending the report/broker exports; research remains paused.

Plan: `agents/codex/plans/live_reconcile_followup.md`, **1ca38bb**. Review/source snapshot: **59de62a**.
Script: `analysis/codex_live_reconcile.py`. Checks: `analysis/codex_live_reconcile_checks.py`.
Output: `analysis/outputs/codex_live_reconcile_followup/fixture_check_results.json`. Strategy trials **0**.

## What changed

- Explicit evaluation key **ONB_ADX30** maps to chart tag ONB; audit coverage labels it explicitly and records a
  missing ADX30 report rather than falling back to the legacy ADX20 or funded ONB_ML2_MC report.
- `--expected-report --report-key ONB_ADX30` validates Settings and reuses `live_vs_backtest.read_trades` for an
  already-exported backtest. No changes to `analysis/live_vs_backtest.py` or any live file. Full deployed inputs/code
  still need review; the key gate is not proof that every input matches.
- Account/root must be explicit. `--expected-qty report` preserves same-root per-trade sizes, including risk sizing.
  A numeric override is allowed for confirmed fixed sizing; variable-risk report sizes cannot be silently overwritten.
  NQ quantity is not relabeled as MNQ quantity. Canonical CSV supports reviewed per-trade expected quantities.
- `--start/--end` gives an explicit week; date-local matching retains completely missed first/last days and separate
  accounts/strategy versions. `--compare-only` avoids invoking the historical chart audit. CSV summaries preserve
  input hashes, scope/date declarations, row counts and matched/unmatched classifications.
- Unknown coverage remains unresolved unless explicitly declared complete. Ambiguous canonical strategy ONB is
  refused. Report mode compares only the stated account/key/root, leaving other scopes unassessed.
- Chart audit accepts date bounds and previous-day context; precise dated dashboard totals supersede the old rounded
  confirmation when that evidence is in the pinned source. Original audit outputs were not overwritten.

## Watchdog proposal for Claude

[Review and integration contract](../proposals/watchdog_stateful_proposal.md) and
[inert PowerShell core](../proposals/watchdog_stateful_draft.ps1).

The core clears a mismatch on a later matching row, even within the same bar. It requires fresh bad rows in separate
polls across an observed elapsed interval; unchanged cursors do not confirm persistence. Staleness uses per-tag
append-observation UTC, not chart HHMM. Initial freshness remains unknown. This cannot prove continuous discrepancy
or feed freshness without a better logger timestamp/sequence.

Rejection classification requires a supported embedded timestamp from today in Central time and order-specific
failure language. Older-day lines, indicator errors, cancellations and bare metadata are not counted as new order
rejections. Unknown formats stay visible as diagnostics. Deduplicated messages are not a count of orders.

The proposal specifies complete-line cursors, rotation handling, atomic state writes, concurrency control and pending
notifications that survive send failure. **That adapter is not implemented in the draft.** The draft is not ready to
replace the scheduled watchdog. PowerShell parsing, replay fixtures and adapter validation must occur on a non-trading
Windows environment before Claude/user consider integration. No notification, task or installation was performed here.

## Verification and current evidence

Run `PYTHONDONTWRITEBYTECODE=1 /workspace/venvs/thebeginning/bin/python analysis/codex_live_reconcile_checks.py`.
Synthetic fixtures cover correct ADX30 import, ADX20/ML/interval rejection, old-date coverage, unpaired chart exports,
root/size declarations, account/key isolation, missed first days, incomplete coverage, Sunday session assignment,
empty inputs, CLI behavior and dashboard precision. See the saved machine-readable check result for the count.
These are engineering checks, not backtests or actual live-week results.

Claude's new tracker/dashboard evidence confirms @MNQ mapping rejection on 10/20 and **−$575.82 per account on 10/21**.
The earlier **−$575** was the user's rounded confirmation and remains preserved in the historical audit. Tracker rows
and a dashboard daily total do not yet provide a complete account-attributed broker round-trip file with fees.
No per-fill attribution or live/backtest edge ratio was invented.

## Pending Friday task

[Concrete weekly runbook](../proposals/friday_reconcile_runbook.md) covers **2026-10-19–23**, with Sunday Bridge context,
expected report names, input/identity/sizing checks, commands and the report destination. The 59de62a tree has no weekly
`live/*_live.xlsx` files or ADX30 evaluation export; old reports cannot settle the week. The actual weekly run remains
pending those exports and sufficient broker evidence. No unattended job was scheduled or implied.

Tell Claude: review `agents/codex/results/live_reconcile_followup.md` and
`agents/codex/proposals/watchdog_stateful_proposal.md`; the offline ADX30 work is ready for review, the PowerShell draft
is unexecuted, and the actual week report waits for Friday exports. Research and live configuration remain unchanged.
