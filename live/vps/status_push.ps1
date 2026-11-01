# VPS status snapshot for Claude (2026-11-01, user: "i want u to have access to the vps"). Every 5 minutes (task
# 'VpsStatusPush'): a screenshot of the desktop, MultiCharts processes / window titles / open broker connections, the KILL
# flag, today's trade-log tail, scheduled-task results, disk and boot time -> pushed to branch 'vps-status' as ONE commit
# that replaces the last (force push: the repo never grows). Read-only: never touches MultiCharts, Rithmic or orders.
# Claude reads it with: python3 analysis/vps_status.py
#   Install once:  schtasks /Create /TN "VpsStatusPush" /SC MINUTE /MO 5 /TR "C:\TradingRepo\live\vps\run_status.cmd" /F
#   (no /RU: runs in your logged-on session, which the screenshot needs)
param([switch]$Diag)
$ErrorActionPreference = "SilentlyContinue"
$Out = "C:\TradingStatus"; $Logs = "C:\TradingLogs"; $Log = "$Logs\status_push_log.txt"
function Say($m) { $l = "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) $m"; Add-Content $Log $l; if ($Diag) { $l } }
if ((Get-Date).DayOfWeek -eq 'Saturday' -and -not $Diag) { exit 0 }   # market closed all Saturday
New-Item -ItemType Directory -Force $Out | Out-Null
Get-ChildItem $Out -Force | Where-Object { $_.Name -ne ".git" } | Remove-Item -Recurse -Force

# 1. screenshot (all monitors). Black/blank if the RDP window was minimized or disconnected: see VPS_STATUS.md
try {
    Add-Type -AssemblyName System.Windows.Forms, System.Drawing
    $b = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
    $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
    $codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
    $ep = New-Object System.Drawing.Imaging.EncoderParameters 1
    $ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), 70L
    $bmp.Save("$Out\screen.jpg", $codec, $ep); $g.Dispose(); $bmp.Dispose(); $shot = "ok"
} catch { $shot = "FAILED: $($_.Exception.Message)" }

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
    screenshot = $shot; kill_flag = (Test-Path "$Logs\KILL")
    session = (query user 2>$null | Out-String).Trim()
    boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToString("yyyy-MM-dd HH:mm")
    disk_free_gb = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
    processes = @($p); tasks = @($tasks)
}
$status | ConvertTo-Json -Depth 5 | Set-Content "$Out\status.json" -Encoding UTF8

# 5. one-commit branch, force-pushed (history never grows)
Set-Location $Out
$url = (git -C "C:\TradingRepo" remote get-url origin)
if (Test-Path ".git") { Remove-Item ".git" -Recurse -Force }
git init -q; git checkout -q -b vps-status
git -c user.name="VPS status" -c user.email="vps@localhost" add -A
git -c user.name="VPS status" -c user.email="vps@localhost" commit -q -m "VPS status $((Get-Date).ToString('yyyy-MM-dd HH:mm'))"
git push -q -f $url vps-status:vps-status 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Say "pushed (screenshot $shot, $($procs.Count) MC processes)" } else { Say "push FAILED" }
exit 0
