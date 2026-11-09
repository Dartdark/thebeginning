# Copies the day's trade logs from C:\TradingLogs into the repo clone on the VPS and pushes them (live/trades/), plus a VPS
# health line (live/health/YYYYMMDD.csv). Task Scheduler: 'PushTradeLogs' weekdays 16:10 CT (see live/vps/README.md).
# Since 2026-10-21 it also installs, once, a second task 'VpsHealthOpen' (weekdays 08:15 CT, -Mode open) so the
# morning check runs with no setup by the user. Light: a few KB, one git push. Never touches MultiCharts or Rithmic.
param([string]$Mode = "close")
$ErrorActionPreference = "Continue"
$Repo = "C:\TradingRepo"
$Logs = "C:\TradingLogs"
$branch = "claude/nq-trading-strategy-params-5h9d20"
Set-Location $Repo
git pull --no-rebase --no-edit origin $branch

# one-time: the morning health task
schtasks /Query /TN "VpsHealthOpen" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    schtasks /Create /TN "VpsHealthOpen" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 08:15 /TR "powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\push_trade_logs.ps1 -Mode open" /F | Out-Null
}

New-Item -ItemType Directory -Force "live\health" | Out-Null
# one-time (2026-10-29): intraday push every 30 min in RTH (-Mode intraday: logs + alerts only, no health line), so
# Claude's master session can see a problem during the day, not only at 16:10
schtasks /Query /TN "VpsIntradayPush" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    schtasks /Create /TN "VpsIntradayPush" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 08:45 /RI 30 /DU 06:30 /TR "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\TradingRepo\live\vps\push_trade_logs.ps1 -Mode intraday" /F | Out-Null
}
schtasks /Query /TN "VpsWatchdog" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    schtasks /Create /TN "VpsWatchdog" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 08:15 /RI 5 /DU 07:00 /TR "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\TradingRepo\live\vps\watchdog.ps1" /F | Out-Null
}
# user 2026-11-09: no weekly VPS restart any more -> remove the 'WeeklyRestart' task if it exists (created by hand from
# VPS_MAINTENANCE.md section 3). If Windows refuses (the task runs as SYSTEM), the failure goes to push_errors.txt.
schtasks /Query /TN "WeeklyRestart" 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    schtasks /Delete /TN "WeeklyRestart" /F 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { "$(Get-Date) could not delete task WeeklyRestart (needs admin): run as admin: schtasks /Delete /TN WeeklyRestart /F" | Out-File -Append "$Logs\push_errors.txt" }
}
# one-time (2026-11-09): FINRA short-volume signal, weekdays 18:00-21:00 CT hourly (live/vps/finra_daily.ps1; idempotent)
schtasks /Query /TN "FinraDaily" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    schtasks /Create /TN "FinraDaily" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 18:00 /RI 60 /DU 03:30 /TR "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\TradingRepo\live\vps\finra_daily.ps1" /F | Out-Null
}
# cushion peak files for the funded cushion guard (2026-11-09; every push, so a new account's file appears within 30 min)
& powershell -ExecutionPolicy Bypass -File "$Repo\live\vps\cushion_peak.ps1"
# alerts the watchdog sent today go to the repo too (live/health/YYYYMMDD_alerts.txt)
if (Test-Path "$Logs\alerts.txt") { Get-Content "$Logs\alerts.txt" | Where-Object { $_ -like "$((Get-Date).ToString('yyyy-MM-dd'))*" } | Set-Content "live\health\$(Get-Date -Format yyyyMMdd)_alerts.txt" }

# health line
$day = Get-Date -Format yyyyMMdd
$mc = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like "MultiCharts*" }).Count
$disk = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
$boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToString("yyyy-MM-dd HH:mm")
$tz = (Get-TimeZone).Id
$today = Join-Path $Logs "$day.csv"
$rows = 0; if (Test-Path $today) { $rows = @(Get-Content $today).Count }
$errs = 0; if (Test-Path "$Logs\push_errors.txt") { $errs = @(Get-Content "$Logs\push_errors.txt").Count }
# rejected orders today: scan MultiCharts' own log files (TS Support folders) for 'Rejected' lines written today
# (catches Symbol Mapping errors like 'Invalid Market order parameters ... @MNQ.CME', Apex locks, wrong accounts).
$rej = 0; $rejmsg = ""
$roots = @("$env:LOCALAPPDATA\TS Support", "$env:APPDATA\TS Support", "C:\ProgramData\TS Support") | Where-Object { Test-Path $_ }
foreach ($r in $roots) {
    Get-ChildItem $r -Recurse -File -Include *.log, *.txt -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime.Date -eq (Get-Date).Date -and $_.Length -lt 200MB } | ForEach-Object {
            $hits = Select-String -Path $_.FullName -Pattern "Rejected|Invalid .* order|not found|done for day" -SimpleMatch:$false -ErrorAction SilentlyContinue
            # count only lines stamped today (MultiCharts writes dd.MM.yyyy/HH:mm:ss): a log file touched today still
            # holds older days' lines (10/28 counted 3,228, the last from 10/26) (2026-10-29)
            $hits = @($hits | Where-Object { $_.Line -like ("*" + (Get-Date).ToString("dd.MM.yyyy") + "/*") })
            if ($hits) { $rej += @($hits).Count; $rejmsg = ($hits[-1].Line -replace ',', ';' -replace '\s+', ' ').Substring(0, [math]::Min(160, $hits[-1].Line.Length)) }
        }
}
New-Item -ItemType Directory -Force "live\health" | Out-Null
$line = "$Mode,$(Get-Date -Format 'yyyy-MM-dd HH:mm'),mc_processes=$mc,disk_free_gb=$disk,last_boot=$boot,tz=$tz,log_rows_today=$rows,push_errors=$errs,rejected_today=$rej,last_reject=$rejmsg"
if ($Mode -ne "intraday") { Add-Content "live\health\$day.csv" $line }

New-Item -ItemType Directory -Force "live\trades" | Out-Null
Copy-Item "$Logs\*.csv" "live\trades\" -Force -ErrorAction SilentlyContinue
# daily 1-minute bars from the NQ Daily Bar Feed indicator (2026-10-29) -> data/live_bars/
New-Item -ItemType Directory -Force "$Logs\bars" | Out-Null
New-Item -ItemType Directory -Force "data\live_bars" | Out-Null
Copy-Item "$Logs\bars\*.csv" "data\live_bars\" -Force -ErrorAction SilentlyContinue
# FINRA signal log (2026-11-09) -> live/finra/ (Claude follows WATCHLIST #32's forward log from it)
New-Item -ItemType Directory -Force "live\finra" | Out-Null
if (Test-Path "$Logs\finra\signals.csv") { Copy-Item "$Logs\finra\signals.csv" "live\finra\signals.csv" -Force }
# copier group state log (2026-11-09) -> live/health/group_log.csv
if (Test-Path "$Logs\group\group_log.csv") { Copy-Item "$Logs\group\group_log.csv" "live\health\group_log.csv" -Force }
git add live/trades live/health data/live_bars live/finra
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "live trades + health $(Get-Date -Format yyyy-MM-dd) ($Mode)"
    git push origin "HEAD:$branch"
    if ($LASTEXITCODE -ne 0) { "$(Get-Date) push failed" | Out-File -Append "$Logs\push_errors.txt" }
}
