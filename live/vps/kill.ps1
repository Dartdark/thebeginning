# Kill switch (2026-11-01, user approved; live/vps/KILL_SWITCH.md). Run on the VPS:
#   powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\kill.ps1            -> local KILL
#   powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\kill.ps1 -Resume    -> clear the LOCAL kill only
# Two latches (Codex review 2026-11-01 #3): KILL_LOCAL (this script) and KILL_REMOTE (the relay, from Claude). The file the
# strategies read, C:\TradingLogs\KILL, exists while EITHER latch is set: a remote resume can never clear your local kill,
# and a local resume never clears a remote one. While KILL exists, every live strategy (built 2026-11-01 or later) places
# no new entries and exits its own open position at market on its next bar (up to one bar: 30 min on Vault Break). It does
# NOT cancel working orders or flatten the broker account: for that, the manual FLATTEN steps in KILL_SWITCH.md (seconds).
# Sends an ntfy alert. Never places or cancels orders itself.
#   -Remote / -Remote -Resume: used only by claude_alert_relay.ps1 (the remote latch).
param([switch]$Resume, [switch]$Remote, [string]$Why = "manual on the VPS", [string]$Dir = "C:\TradingLogs", [switch]$NoAlert)
# -Dir / -NoAlert: only for kill_test.ps1 (a scratch folder, no phone alert)
$L = $Dir; $Flag = "$L\KILL"; $Latch = if ($Remote) { "$L\KILL_REMOTE" } else { "$L\KILL_LOCAL" }
$Topic = "apex-alarm-6e531eb6db8e"
$now = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss"); $who = if ($Remote) { "remote" } else { "local" }
# migration: a KILL file from the old one-latch version with no latch at all counts as a local kill (keeps the stop)
if ((Test-Path $Flag) -and -not (Test-Path "$L\KILL_LOCAL") -and -not (Test-Path "$L\KILL_REMOTE")) { Copy-Item $Flag "$L\KILL_LOCAL" -Force }
if ($Resume) { if (Test-Path $Latch) { Remove-Item $Latch -Force } } else { Set-Content $Latch "$now $Why" }
# effective flag = local OR remote
$active = @(@("$L\KILL_LOCAL", "$L\KILL_REMOTE") | Where-Object { Test-Path $_ })   # @(): one match must stay a list
if ($active) { Set-Content $Flag ((Get-Content $active[0] -Raw).Trim()) } elseif (Test-Path $Flag) { Remove-Item $Flag -Force }
# verify the write actually happened
$on = Test-Path $Flag; $ok = if ($Resume) { -not (Test-Path $Latch) } else { (Test-Path $Latch) -and $on }
$left = ($active | ForEach-Object { Split-Path $_ -Leaf }) -join " + "
if (-not $ok) { $msg = "KILL SWITCH ERROR: $who $(if ($Resume) {'resume'} else {'kill'}) did NOT take effect ($Why). Flatten by hand (KILL_SWITCH.md)." }
elseif ($Resume -and $on) { $msg = "$who resume done, but KILL STAYS ON: $left still set. Strategies still blocked." }
elseif ($Resume) { $msg = "RESUME ($who, $Why): no kill latch left. Strategies trade again from their next bar." }
else { $msg = "KILL ACTIVE ($who, $Why): no new entries; open positions exit at market on their next bar. For an instant exit, flatten by hand (KILL_SWITCH.md)." }
Add-Content "$L\kill_log.txt" "$now $msg"
if (-not $NoAlert) { try { Invoke-RestMethod -Method Post -Uri "https://ntfy.sh/$Topic" -Body $msg -Headers @{ Title = "KILL SWITCH"; Priority = "urgent" } | Out-Null } catch {} }
$msg
if (-not $ok) { exit 1 }
exit 0
