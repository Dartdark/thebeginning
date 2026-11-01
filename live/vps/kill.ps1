# Kill switch (2026-11-01, user approved; live/vps/KILL_SWITCH.md). Run on the VPS:
#   powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\kill.ps1            -> KILL: create C:\TradingLogs\KILL
#   powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\kill.ps1 -Resume    -> RESUME: delete it
# While the file exists, every live strategy (built 2026-11-01 or later) places no new entries and exits any open position at
# market on its next bar (up to one bar: 30 min on Vault Break). It does NOT flatten instantly: for that, use the manual
# FLATTEN steps in KILL_SWITCH.md (seconds). Sends an ntfy alert either way. Never places or cancels orders itself.
param([switch]$Resume, [string]$Why = "manual on the VPS")
$Flag = "C:\TradingLogs\KILL"
$Topic = "apex-alarm-6e531eb6db8e"
$now = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
if ($Resume) {
    if (Test-Path $Flag) { Remove-Item $Flag -Force }
    $msg = "RESUME: kill flag removed ($Why). Strategies trade again from their next bar."
} else {
    Set-Content $Flag "$now $Why"
    $msg = "KILL ACTIVE ($Why): no new entries; open positions exit at market on their next bar. For an instant exit, flatten by hand (KILL_SWITCH.md)."
}
Add-Content "C:\TradingLogs\kill_log.txt" "$now $msg"
try { Invoke-RestMethod -Method Post -Uri "https://ntfy.sh/$Topic" -Body $msg -Headers @{ Title = "KILL SWITCH"; Priority = "urgent" } | Out-Null } catch {}
$msg
