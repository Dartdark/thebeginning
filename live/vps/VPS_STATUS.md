# VPS status for Claude (2026-11-01)

Every 5 minutes the VPS pushes a snapshot to branch **vps-status** (one commit, replaced each time): `screen.jpg` (the
desktop), `status.json` (MultiCharts processes, window titles, broker connections, KILL flag, task results, disk, boot),
the last 200 trade-log lines and the last 30 alerts. Read-only: nothing on the VPS is changed by it. Claude reads it with
`python3 analysis/vps_status.py`.

## Install (once, ~5 min, on the VPS)
1. `cd C:\TradingRepo` then `git pull`
2. Test it: `powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\status_push.ps1 -Diag` -> last line `pushed (screenshot ok, ...)`
3. Schedule it: `schtasks /Create /TN "VpsStatusPush" /SC MINUTE /MO 5 /TR "C:\TradingRepo\live\vps\run_status.cmd" /F`
4. Tell Claude "status installed": Claude reads the snapshot and confirms what it sees.

## Screenshot black or blank?
Windows draws nothing while the Remote Desktop window is **minimized**, or after you **disconnect** (closing the RDP
window). The rest of the snapshot still works. Fixes: leave RDP open (not minimized) or, instead of closing RDP, run
`tscon %sessionname% /dest:console` as administrator (moves your session to the console; it stays drawn).
