# VPS status for Claude (2026-11-01)

Every 5 minutes the VPS pushes a snapshot to branch **vps-status** (one commit, replaced each time): `status.json` (MultiCharts processes, window titles, broker connections, KILL flag, task results, disk, boot),
the last 200 trade-log lines and the last 30 alerts. Read-only: nothing on the VPS is changed by it. Claude reads it with
`python3 analysis/vps_status.py`.

## Install (once, ~5 min, on the VPS)
1. `cd C:\TradingRepo` then `git pull`
2. Test it: `powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\status_push.ps1 -Diag` -> last line `pushed (N MC processes)`
3. Schedule it: `schtasks /Create /TN "VpsStatusPush" /SC MINUTE /MO 5 /TR "C:\TradingRepo\live\vps\run_status.cmd" /F`
4. Tell Claude "status installed": Claude reads the snapshot and confirms what it sees.

## No screenshot (2026-11-01)
The first version also captured the screen; Windows Defender blocked it as spyware-like (screen capture + upload). That
is the right call and is not bypassed. When Claude needs to see the screen (chart settings, connection lights), send a
screenshot by hand.
