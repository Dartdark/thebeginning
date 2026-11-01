# VPS status snapshot for Claude (2026-11-01, user: "i want u to have access to the vps"). Every 5 minutes (task
# 'VpsStatusPush'): MultiCharts processes / window titles / open broker connections, the KILL
# flag, today's trade-log tail, scheduled-task results, disk and boot time -> pushed to branch 'vps-status' as ONE commit
# that replaces the last (force push: the repo never grows). Read-only: never touches MultiCharts, Rithmic or orders.
# Claude reads it with: python3 analysis/vps_status.py
#   Install once:  schtasks /Create /TN "VpsStatusPush" /SC MINUTE /MO 5 /TR "C:\TradingRepo\live\vps\run_status.cmd" /F
# Screenshot: separate script screen_push.ps1 (Defender may block it; this one keeps working).
param([switch]$Diag)
$ErrorActionPreference = "SilentlyContinue"
$Out = "C:\TradingStatus"; $Logs = "C:\TradingLogs"; $Log = "$Logs\status_push_log.txt"
function Say($m) { $l = "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) $m"; Add-Content $Log $l; if ($Diag) { $l } }
if ((Get-Date).DayOfWeek -eq 'Saturday' -and -not $Diag) { exit 0 }   # market closed all Saturday
New-Item -ItemType Directory -Force $Out | Out-Null
Get-ChildItem $Out -Force | Where-Object { $_.Name -notin ".git", "screen_new.jpg", "screen_status.txt" } | Remove-Item -Recurse -Force
if (Test-Path "$Out\screen_new.jpg") { Move-Item "$Out\screen_new.jpg" "$Out\screen.jpg" -Force }   # from screen_push.ps1

# 2. MultiCharts processes, window titles, established TCP connections (broker / data feed proxy)
$procs = @(Get-Process | Where-Object { $_.ProcessName -like "MultiCharts*" -or $_.ProcessName -like "*QuoteManager*" -or $_.ProcessName -like "*Rithmic*" -or $_.ProcessName -like "tsServer*" })
$p = foreach ($x in $procs) {
    $conn = @(Get-NetTCPConnection -OwningProcess $x.Id -State Established -ErrorAction SilentlyContinue).Count
    [ordered]@{ name = $x.ProcessName; id = $x.Id; title = $x.MainWindowTitle; started = $x.StartTime.ToString("yyyy-MM-dd HH:mm"); tcp_established = $conn; responding = $x.Responding }
}
# 3. scheduled tasks we rely on
$tasks = foreach ($t in "ClaudeAlertRelay", "PushTradeLogs", "VpsHealthOpen", "VpsIntradayPush", "VpsWatchdog", "VIXUpdate", "VpsStatusPush") {
    $i = Get-ScheduledTaskInfo -TaskName $t -ErrorAction SilentlyContinue
    if ($i) { [ordered]@{ task = $t; last_run = $i.LastRunTime.ToString("yyyy-MM-dd HH:mm"); last_result = $i.LastTaskResult } } else { [ordered]@{ task = $t; last_run = "MISSING" } }
}
# 4. today's trade log tail (entries, exits, heartbeats per chart)
$day = Get-Date -Format yyyyMMdd
if (Test-Path "$Logs\$day.csv") { Get-Content "$Logs\$day.csv" -Tail 200 | Set-Content "$Out\trades_tail.csv" }
if (Test-Path "$Logs\alerts.txt") { Get-Content "$Logs\alerts.txt" -Tail 30 | Set-Content "$Out\alerts_tail.txt" }

$status = [ordered]@{
    time_local = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss"); tz = (Get-TimeZone).Id
    kill_flag = (Test-Path "$Logs\KILL")
    session = (query user 2>$null | Out-String).Trim()
    boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToString("yyyy-MM-dd HH:mm")
    disk_free_gb = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
    processes = @($p); tasks = @($tasks)
}
$status | ConvertTo-Json -Depth 5 | Set-Content "$Out\status.json" -Encoding UTF8

# one-commit branch (amended each run), force-pushed (history never grows). Fail closed (Codex review 2026-11-01 #4): every
# git call names the status repo explicitly (-C $Out), and nothing runs unless that repo's top level IS $Out and its branch
# is vps-status, so a failed directory change can never stage or amend C:\TradingRepo.
$url = (git -C "C:\TradingRepo" remote get-url origin)
if (-not (Test-Path "$Out\.git")) { git -C $Out init -q; git -C $Out checkout -q -b vps-status; $first = $true }
$top = (git -C $Out rev-parse --show-toplevel 2>$null); $br = (git -C $Out rev-parse --abbrev-ref HEAD 2>$null)
if (-not $top -or ((Resolve-Path $top).Path.TrimEnd("\") -ne (Resolve-Path $Out).Path.TrimEnd("\")) -or ($br -ne "vps-status" -and -not $first)) {
    Say "ABORT: status repo check failed (top '$top', branch '$br'); nothing staged"; exit 1 }
git -C $Out -c user.name="VPS status" -c user.email="vps@localhost" add -A
$amend = @(); if (-not $first) { $amend = @("--amend") }
git -C $Out -c user.name="VPS status" -c user.email="vps@localhost" commit -q @amend -m "VPS status $((Get-Date).ToString('yyyy-MM-dd HH:mm'))"
git -C $Out push -q -f $url vps-status:vps-status 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Say "pushed ($($procs.Count) MC processes)" } else { Say "push FAILED" }
exit 0
