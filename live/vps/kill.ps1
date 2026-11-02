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
param([switch]$Resume, [switch]$Remote, [switch]$Check, [string]$Why = "manual on the VPS", [string]$Dir = "C:\TradingLogs", [switch]$NoAlert)
# -Dir / -NoAlert: only for kill_test.ps1 (a scratch folder, no phone alert)
$L = $Dir; $Flag = "$L\KILL"; $Latch = if ($Remote) { "$L\KILL_REMOTE" } else { "$L\KILL_LOCAL" }
$Topic = "apex-alarm-6e531eb6db8e"
$now = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss"); $who = if ($Remote) { "remote" } else { "local" }
# A KILL file that no latch accounts for was made by hand (or by the old one-latch version): adopt it as a LOCAL kill, so a
# remote resume can never clear it (Codex follow-up 2026-11-02 #1). "Accounted for" = its text equals a latch's text.
function T($f) { if (Test-Path $f) { $c = Get-Content $f -Raw -ErrorAction Stop; if ($null -eq $c) { "" } else { $c.Trim() } } else { $null } }
# -Check (the relay, every minute): no latch change; only repair the invariant (adopt a hand-made KILL, restore a deleted
# KILL while a latch is set). Silent unless it repaired something or failed.
$before = "$(Test-Path $Flag)|$(Test-Path "$L\KILL_LOCAL")|$(Test-Path "$L\KILL_REMOTE")"
$err = $null
try {
    $k = T $Flag; $lo = T "$L\KILL_LOCAL"; $re = T "$L\KILL_REMOTE"
    if ($null -ne $k -and $null -eq $lo -and $k -ne $re) { Set-Content "$L\KILL_LOCAL" $(if ($k) { $k } else { "$now by hand" }) -ErrorAction Stop }
    if ($Check) { } elseif ($Resume) { if (Test-Path $Latch) { Remove-Item $Latch -Force -ErrorAction Stop } } else { Set-Content $Latch "$now $Why" -ErrorAction Stop }
    # effective flag = local OR remote
    $active = @(@("$L\KILL_LOCAL", "$L\KILL_REMOTE") | Where-Object { Test-Path $_ })   # @(): one match must stay a list
    if ($active.Count -gt 0) { Set-Content $Flag (T $active[0]) -ErrorAction Stop } elseif (Test-Path $Flag) { Remove-Item $Flag -Force -ErrorAction Stop }
} catch { $err = $_.Exception.Message }
# verify the whole invariant, not just the requested latch (Codex follow-up #2): KILL exists exactly when a latch exists,
# and the requested latch is in the requested state. Any error or mismatch = ERROR (exit 1), never "trade again".
$anyLatch = (Test-Path "$L\KILL_LOCAL") -or (Test-Path "$L\KILL_REMOTE"); $on = Test-Path $Flag
$ok = (-not $err) -and ($on -eq $anyLatch) -and ($(if ($Check) { $true } elseif ($Resume) { -not (Test-Path $Latch) } else { Test-Path $Latch }))
$after = "$(Test-Path $Flag)|$(Test-Path "$L\KILL_LOCAL")|$(Test-Path "$L\KILL_REMOTE")"
if ($Check -and $ok -and $before -eq $after) { exit 0 }
$left = (@(@("$L\KILL_LOCAL", "$L\KILL_REMOTE") | Where-Object { Test-Path $_ }) | ForEach-Object { Split-Path $_ -Leaf }) -join " + "
if ($Check -and $ok) { $msg = "KILL switch repaired: KILL file was out of step with its latches (made or deleted by hand?). Now: KILL $(if ($on) {'ON'} else {'off'}) ($left). Resume only with kill.ps1 -Resume." }
elseif (-not $ok) { $msg = "KILL SWITCH ERROR: $who $(if ($Resume) {'resume'} else {'kill'}) ($Why): state not consistent (KILL file $(if ($on) {'present'} else {'MISSING'}), latches: $(if ($left) {$left} else {'none'})$(if ($err) {"; $err"})). Flatten by hand if needed (KILL_SWITCH.md) and tell Claude." }
elseif ($Resume -and $on) { $msg = "$who resume done, but KILL STAYS ON: $left still set. Strategies still blocked." }
elseif ($Resume) { $msg = "RESUME ($who, $Why): no kill latch left. Strategies trade again from their next bar." }
else { $msg = "KILL ACTIVE ($who, $Why): no new entries; open positions exit at market on their next bar. For an instant exit, flatten by hand (KILL_SWITCH.md)." }
Add-Content "$L\kill_log.txt" "$now $msg"
if (-not $NoAlert) { try { Invoke-RestMethod -Method Post -Uri "https://ntfy.sh/$Topic" -Body $msg -Headers @{ Title = "KILL SWITCH"; Priority = "urgent" } | Out-Null } catch {} }
$msg
if (-not $ok) { exit 1 }
exit 0
