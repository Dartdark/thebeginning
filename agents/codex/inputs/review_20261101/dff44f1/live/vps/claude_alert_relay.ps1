# Claude -> phone relay (2026-10-29, user approved). Claude's own push notifications didn't reach the phone; ntfy from this
# VPS does. Every minute (task 'ClaudeAlertRelay'): fetch the work branch (only new changes), read live/claude_alerts.txt
# from it WITHOUT touching the working copy, and send each line not sent before to ntfy. Lines come from
# analysis/send_alert.py. Never touches MultiCharts, Rithmic or orders.
#   Install once:  schtasks /Create /TN "ClaudeAlertRelay" /SC MINUTE /MO 1 /TR "C:\TradingRepo\live\vps\run_relay.cmd" /F
#   (via run_relay.cmd: the direct powershell task failed with Last Result 1 and no log, 2026-10-29; verified working)
param([switch]$Diag, [int]$Resend = 0)   # -Diag: print every step; -Resend N: send the last N lines again
$ErrorActionPreference = "SilentlyContinue"
$Topic = "apex-alarm-6e531eb6db8e"
$branch = "claude/nq-trading-strategy-params-5h9d20"
$State = "C:\TradingLogs\claude_alerts_sent.txt"
Set-Location "C:\TradingRepo"
$Log = "C:\TradingLogs\relay_log.txt"
function Say($m) { $line = "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) $m"; Add-Content $Log $line; if ($Diag) { $line } }
git fetch -q origin $branch 2>$null
# remote kill switch (2026-11-01, live/vps/KILL_SWITCH.md): live/KILL on the branch = kill; removed = resume. Only a kill made
# remotely is resumed remotely; a kill made on the VPS (kill.ps1) stays until kill.ps1 -Resume.
$remote = [bool](git ls-tree --name-only "origin/${branch}" live/KILL 2>$null)
$flag = "C:\TradingLogs\KILL"; $mark = "C:\TradingLogs\KILL_REMOTE"
if ($remote -and -not (Test-Path $flag)) {
    $why = (git show "origin/${branch}:live/KILL" 2>$null | Select-Object -First 1)
    & powershell -ExecutionPolicy Bypass -File "C:\TradingRepo\live\vps\kill.ps1" -Why "remote: $why" | Out-Null
    Set-Content $mark "1"; Say "remote KILL applied: $why"
} elseif (-not $remote -and (Test-Path $mark)) {
    & powershell -ExecutionPolicy Bypass -File "C:\TradingRepo\live\vps\kill.ps1" -Resume -Why "remote resume" | Out-Null
    Remove-Item $mark -Force; Say "remote RESUME applied"
}
$lines = @(git show "origin/${branch}:live/claude_alerts.txt" 2>$null)
if ($Diag) { Say "fetched; alert lines in repo: $($lines.Count)" }
if ($lines.Count -eq 0) { Say "no alert file on the branch"; exit 0 }
if (-not (Test-Path $State)) { Set-Content $State $lines.Count; Say "first run: recorded $($lines.Count) existing lines"; exit 0 }
$sent = [int]((Get-Content $State -Raw).Trim())
if ($Resend -gt 0) { $sent = [math]::Max(0, $lines.Count - $Resend) }
if ($sent -gt $lines.Count) { $sent = 0 }
if ($Diag) { Say "already sent: $sent; to send now: $($lines.Count - $sent)" }
for ($i = $sent; $i -lt $lines.Count; $i++) {
    try {
        Invoke-RestMethod -Method Post -Uri "https://ntfy.sh/$Topic" -Body "Claude: $($lines[$i])" -Headers @{ Title = "Claude alert"; Priority = "high" } -ErrorAction Stop | Out-Null
        Say "sent: $($lines[$i])"
    } catch { Say "ntfy FAILED: $($_.Exception.Message)" }
    Start-Sleep -Seconds 1
}
Set-Content $State $lines.Count
exit 0
