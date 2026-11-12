@echo off
REM Launcher for the VpsStatusPush task (2026-11-01), same pattern as run_relay.cmd (no profile, errors kept).
cd /d C:\TradingRepo
REM 2026-11-12: self-update once an hour (minutes 00-04, when push_trade_logs at :15 / :45 is not using git). A .ps1 with a
REM parse error can't run its own 'git pull' (11/11: logs down all day until the user pulled by hand); this .cmd can.
REM Fast-forward only: never merges, never touches local changes; a failure is just logged.
set MM=%time:~3,2%
if "%MM%" LSS "05" git pull -q --ff-only origin claude/nq-trading-strategy-params-5h9d20 >> C:\TradingLogs\self_update.txt 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\TradingRepo\live\vps\status_push.ps1 >> C:\TradingLogs\status_task_out.txt 2>&1
