# VPS status for Claude (2026-11-01)

Every 5 minutes the VPS pushes a snapshot to branch **vps-status** (one commit, replaced each time): `status.json` (MultiCharts processes, window titles, broker connections, KILL flag, task results, disk, boot),
the last 200 trade-log lines and the last 30 alerts. Read-only: nothing on the VPS is changed by it. Claude reads it with
`python3 analysis/vps_status.py`.

## Install (once, ~5 min, on the VPS)
1. `cd C:\TradingRepo` then `git pull`
2. Test it: `powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\status_push.ps1 -Diag` -> last line `pushed (N MC processes)`
3. Schedule it: `schtasks /Create /TN "VpsStatusPush" /SC MINUTE /MO 5 /TR "C:\TradingRepo\live\vps\run_status.cmd" /F`
4. Tell Claude "status installed": Claude reads the snapshot and confirms what it sees.

## Screenshot (optional, 2026-11-01)
`screen_push.ps1` captures the desktop every 5 min; the status push carries it. Windows Defender flagged the first version
(screen capture + upload looks like spyware). Allowing it is your call on your own VPS; the script is short and readable,
check it first. In an **administrator** PowerShell:
1. `Add-MpPreference -ExclusionPath "C:\TradingRepo\live\vps\screen_push.ps1"` (only this one file, not the folder)
2. Test: `powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\screen_push.ps1; Get-Content C:\TradingStatus\screen_status.txt` -> `... ok`
3. Schedule: `schtasks /Create /TN "VpsScreenshot" /SC MINUTE /MO 5 /TR "C:\TradingRepo\live\vps\run_screen.cmd" /F`
If Defender still blocks it after the exclusion, stop there (screenshots by hand); don't widen the exclusion.
Undo: `Remove-MpPreference -ExclusionPath "C:\TradingRepo\live\vps\screen_push.ps1"` and `schtasks /Delete /TN VpsScreenshot /F`.
Black image = Remote Desktop minimized or disconnected; keep it open, or disconnect with `tscon %sessionname% /dest:console`.
