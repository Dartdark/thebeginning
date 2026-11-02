# Codex review request: everything Claude did 2026-10-31 .. 11-01 (user, 2026-11-01)

Scope: `git log 98530aa..HEAD` on `claude/nq-trading-strategy-params-5h9d20` (~55 commits). Same rules as
TASK_weekly_cross_review.md: at most 5-8 material findings, most important first; each with the claim, evidence
(file / line / number), consequence and the smallest settling check. Write `agents/codex/results/REVIEW_2026-11-01.md` on
codex/work. Live-money items first; a confirmed execution defect goes to the user at once.

## Priority 1: live trading code and config (money on the line)
| Item | Files | What to check |
|---|---|---|
| Kill switch in 6 live strategies (not yet installed on the VPS) | `funded_strategies/NQ_Vault_Break*.txt`, `NQ_Overnight_Bias*.txt`, `NQ_Expiration_Open_Short.txt`, `Bridge_Monday_Long_L644NQ.txt`; `live/vps/kill.ps1`; `live/vps/KILL_SWITCH.md`; `analysis/kill_switch.py` | `ELC.PathExists` real-time only; `KILL LX/SX` market exits flatten every case (open position, pending stop/limit entries); entries all gated by `KillOn = false`; no behaviour change when the flag is absent; MULTICHARTS_PITFALLS compliance |
| Remote kill via the relay | `live/vps/claude_alert_relay.ps1` | only a remote kill is remotely resumed; failure modes if git fetch fails (fail-safe?) |
| Account #4 added | `live/expected_setup.json`, `analysis/dashboard_data.py`, `analysis/live_panels.py`, `analysis/account_tools.py` | 150K rules (trail 4,000, lock 150,100, target 159,000); VB150/ONB150/EOS150/MON_BR150 un-retired and mapped to #4; max_loss values (VB 20 MNQ x 75 pts = $3,000; ONB $2,750) |
| Not-started account guard | `analysis/live_panels.py` (`n < 1` -> NOT STARTED) | correct for a fresh account; no other panel divides by days |
| Buy gate | `analysis/buy_gate.py` | failure-date parsing, cool-off window, live-edge maths |
| VPS status feed (new, read-only) | `live/vps/status_push.ps1`, `screen_push.ps1`, `run_*.cmd`, `analysis/vps_status.py`, `live/vps/VPS_STATUS.md` | force-push only to `vps-status`; can it ever touch the work branch or C:\TradingRepo's working copy? Defender exclusion scoped to one file |
| Pre-market check / live guard | `analysis/premarket_check.py`, `analysis/live_guard.py` (`pending_install` mute) | the mute can't hide a real version mismatch after the install |
| Known false alarm (Claude's error) | LESSONS.md, MULTICHARTS_PITFALLS.md | ACCT rows' `account` is the Chart Monitor's typed input, not routing. Next step proposed: log `GetAccountID` in the Chart Monitor. Is `GetAccountID` the right keyword (returns the strategy's auto-trading account)? |
| Kill switch file read switched to GetFileAttributesA (EL Collections absent on the VPS); invvol table fix (#7) | `apex_strategies/*`, `funded_strategies/NQ_Expiration_Open_Short.txt`, `analysis/personal_invvol_ladder.py`, `personal_strategies/PORTFOLIO.md` | DLL call semantics (-1 missing, 16 folder verified on the VPS); causal vs deploy vectors |
| Routing check (built after this packet) | `apex_strategies/Apex_Chart_Monitor.txt` (GetAccountID -> ACCT col 9), `live/vps/watchdog.ps1` 2e, `analysis/vps_health.py`, `analysis/vps_status.py`, `live_guard.py` / `account_tools.py` (ACCT match on column 4 only) | GetAccountID semantics; empty when AA off; alarm text; no reader broken by the new column |

## Priority 2: plan and statistics decisions
| Item | Files | What to check |
|---|---|---|
| Firm-risk test (accounts are one bet, corr 0.73 one-a-day vs 0.29 one-a-week) | `analysis/firm_risk_test.py`, `analysis/outputs/firm_risk_test_output.txt` | overlapping starts inflate the correlation estimate? Batch starts every day are not independent samples |
| Inverse-vol personal weights (adopted) | `analysis/personal_invvol_test.py`, `personal_invvol_confirm.py`, `personal_strategies/PORTFOLIO.md` | weights from 2018-25 used in a 2023+ score = leak? (design 2018-22 weights version exists: confirm which one was adopted) |
| Swing Target revert, 150K integer sizes, opposing-overlap v2 | `funded_strategies/FUNDED_PLAN.md`, `analysis/plan150_integer_test.py`, `analysis/opposing_overlap_check.py` | numbers reproduce |
| Provenance stamp | `analysis/provenance.py`, `tools/run_stamped.sh` | fingerprint = names + sizes only (an in-place edit with the same size is missed) |

## Priority 3: lab and process
- Lab rules in code: `analysis/lab_tools.py` (dupcheck, error classes, receipts, STOP, 5/day cap); studies Q003, Q009,
  Q010, Q012, Q016 (all F), Q011 blocked (NG roll), GC Asia continuation (D). Check one F verdict end to end.
- Morning brief `analysis/morning_brief.py` (scout count vs IDEAS.md before the window; CHAIN BROKEN), `tools/prepush_check.py`.
- `DATA_NEEDS.md`: costs are from memory, unverified.

## Also for comment: Claude's notes on the Jane Street interview
`agents/codex/JANE_STREET_NOTES.md`: does Codex agree with the takeaways, and does anything there argue for a change to our
process that Claude missed?
