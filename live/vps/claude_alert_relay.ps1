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
git fetch -q origin $branch 2>$null; $fetchOk = ($LASTEXITCODE -eq 0)
# remote kill switch (2026-11-01, live/vps/KILL_SWITCH.md): live/KILL on the branch = kill; removed = resume (remote latch
# only: kill.ps1 keeps a local kill on). Unknown state never resumes (Codex review 2026-11-01 #3): a RESUME needs a successful
# fetch AND a successful tree read that positively lists the branch without live/KILL; a KILL is applied from any readable
# state (cached or fresh). Read errors change nothing and are logged.
$tree = @(git ls-tree --name-only "origin/${branch}" live/ 2>$null); $treeOk = ($LASTEXITCODE -eq 0) -and ($tree.Count -gt 0)
$remoteKill = $treeOk -and ($tree -contains "live/KILL")
$latch = "C:\TradingLogs\KILL_REMOTE"
if ($remoteKill -and -not (Test-Path $latch)) {
    $why = (git show "origin/${branch}:live/KILL" 2>$null | Select-Object -First 1)
    $r = & powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TradingRepo\live\vps\kill.ps1" -Remote -Why "remote: $why"
    Say "remote KILL applied (exit $LASTEXITCODE): $r"
} elseif ($fetchOk -and $treeOk -and -not $remoteKill -and (Test-Path $latch)) {
    $r = & powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TradingRepo\live\vps\kill.ps1" -Remote -Resume -Why "remote resume"
    Say "remote RESUME applied (exit $LASTEXITCODE): $r"
} elseif (-not ($fetchOk -and $treeOk)) { Say "kill state UNKNOWN (fetch ok=$fetchOk, tree ok=$treeOk): nothing changed" }
# every minute: keep KILL in step with its latches (Codex follow-up 2026-11-02 #1: a hand-made or hand-deleted KILL file)
$r = & powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TradingRepo\live\vps\kill.ps1" -Check
if ($r) { Say "kill check: $r" }
if (-not $fetchOk) { Say "alert fetch FAILED; cursor unchanged"; exit 1 }
$lines = @(git show "origin/${branch}:live/claude_alerts.txt" 2>$null)
if ($LASTEXITCODE -ne 0) { Say "alert read FAILED; cursor unchanged"; exit 1 }
if ($Diag) { Say "fetched; alert lines in repo: $($lines.Count)" }
if ($lines.Count -eq 0) { Say "no alert file on the branch"; exit 0 }
if (-not (Test-Path $State)) { Set-Content $State 0 -ErrorAction Stop; Say "first run: replay from first unacknowledged line" }
$sent = [int]((Get-Content $State -Raw).Trim())
if ($Resend -gt 0) { $sent = [math]::Max(0, $lines.Count - $Resend) }
if ($sent -gt $lines.Count) { $sent = 0 }
if ($Diag) { Say "already sent: $sent; to send now: $($lines.Count - $sent)" }
for ($i = $sent; $i -lt $lines.Count; $i++) {
    try {
        Invoke-RestMethod -Method Post -Uri "https://ntfy.sh/$Topic" -Body "Claude: $($lines[$i])" -Headers @{ Title = "Claude alert"; Priority = "high" } -TimeoutSec 15 -ErrorAction Stop | Out-Null
        Set-Content $State ($i + 1) -ErrorAction Stop
        Say "accepted by ntfy: $($lines[$i])"
    } catch { Say "delivery/checkpoint FAILED; pending line $i retained: $($_.Exception.Message)"; exit 1 }
    Start-Sleep -Seconds 1
}
exit 0
