@echo off
REM Launcher for the VpsStatusPush task (2026-11-01), same pattern as run_relay.cmd (no profile, errors kept).
cd /d C:\TradingRepo
powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\TradingRepo\live\vps\status_push.ps1 >> C:\TradingLogs\status_task_out.txt 2>&1
