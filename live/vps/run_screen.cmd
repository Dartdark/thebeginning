@echo off
REM Launcher for the VpsScreenshot task (2026-11-01).
powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\TradingRepo\live\vps\screen_push.ps1 >> C:\TradingLogs\screen_task_out.txt 2>&1
