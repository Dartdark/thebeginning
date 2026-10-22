# Task 1 (do first): live-trading audit, read-only

Branch `codex/work`. Read-only on everything live: never touch the VPS, MultiCharts, broker or account settings, and
don't edit `apex_strategies/`, `funded_strategies/`, `live/` or `analysis/vps_health.py` (propose changes instead).

## Why
The plan needs live results before anything else (mid-December gate: ~40-70 live trades at >= 75% of backtest, no
ALARM; `funded_strategies/FUNDED_PLAN.md`). Execution problems, not strategy research, are the current risk.

## What we know (user's own reports, in `journal/daily/`)
- 2026-10-20: Vault Break's logged trades (8 MNQ, both accounts) **did not fill** on the account ("tech difficulties").
- 2026-10-21: Vault Break traded twice per account (8 MNQ: +~40 pts at 12:30, then −75 pts 13:00→14:00). The log's
  health block flagged "MISMATCH VB / VB-2 at 1400: strategy +8, broker +0" and ~60 "rejection" lines, **yet the user
  reports the trades went through: −$575 on both accounts**. So some health flags may be false alarms.
- Trade log format: `apex_strategies/Apex_Trade_Logger.txt` → `live/trades/YYYYMMDD.csv` (OPEN / CLOSE / POS rows;
  the 10/21 file repeats OPEN rows many times). Health: `live/health/`, `analysis/vps_health.py`,
  `analysis/journal_trades.py`, `live/vps/watchdog.ps1`. Known failure modes: `MULTICHARTS_PITFALLS.md`.

## Do
1. For every live day so far, reconcile per strategy and account: what the backtest rule would have done (repo
   rebuilds / MultiCharts trade lists, same day) vs what the log shows vs what the user reported (journal). Classify
   each difference: missed, extra, duplicate, wrong size, late fill, stop rejected, or logger / health artefact.
2. Check the health signals: for each MISMATCH / REJECTED flag, is it a real problem or a logger artefact (e.g. the
   broker position field lagging, rejection lines from old sessions or other symbols)? Propose precise fixes to the
   logger / health check so a real problem is flagged and noise isn't.
3. Check the 10/20 no-fill against the setup history in `TODO.md` / `NEW_CHAT_BRIEF.md` (symbol mapping, account
   selected behind the gear icon, chart broker set to Rithmic vs SIM, auto-trading state) and list the most likely
   causes with the evidence for each.
4. Propose a **daily reconciliation script** (`analysis/codex_live_reconcile.py`, writes under
   `analysis/outputs/codex_live_reconcile/`) that the 16:40 CT journal job could call later: expected vs logged trades
   per strategy and account, slippage in ticks, P&L vs the backtest's P&L for the same trade.

## Output
`agents/codex/results/live_audit.md` (5-line Summary first): a table of every live trade / expected trade, the
issues found with likely cause and evidence, and a numbered fix list for the user (what to check or click on the VPS),
most important first. Note what can't be determined from the files and what the user should export to settle it
(e.g. the Apex / Rithmic order history for 10/20 and 10/21). Commit, push, say "live audit pushed".
