@echo off
REM Launcher for the ClaudeAlertRelay task (2026-10-29): runs the relay without the PowerShell profile and keeps its errors.
cd /d C:\TradingRepo
powershell -NoProfile -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\claude_alert_relay.ps1 >> C:\TradingLogs\relay_task_out.txt 2>&1
