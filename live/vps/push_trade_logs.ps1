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
schtasks /Query /TN "VpsWatchdog" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    schtasks /Create /TN "VpsWatchdog" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 08:15 /RI 5 /DU 07:00 /TR "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\TradingRepo\live\vps\watchdog.ps1" /F | Out-Null
}
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
            if ($hits) { $rej += @($hits).Count; $rejmsg = ($hits[-1].Line -replace ',', ';' -replace '\s+', ' ').Substring(0, [math]::Min(160, $hits[-1].Line.Length)) }
        }
}
New-Item -ItemType Directory -Force "live\health" | Out-Null
$line = "$Mode,$(Get-Date -Format 'yyyy-MM-dd HH:mm'),mc_processes=$mc,disk_free_gb=$disk,last_boot=$boot,tz=$tz,log_rows_today=$rows,push_errors=$errs,rejected_today=$rej,last_reject=$rejmsg"
Add-Content "live\health\$day.csv" $line

New-Item -ItemType Directory -Force "live\trades" | Out-Null
Copy-Item "$Logs\*.csv" "live\trades\" -Force -ErrorAction SilentlyContinue
git add live/trades live/health
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "live trades + health $(Get-Date -Format yyyy-MM-dd) ($Mode)"
    git push origin "HEAD:$branch"
    if ($LASTEXITCODE -ne 0) { "$(Get-Date) push failed" | Out-File -Append "$Logs\push_errors.txt" }
}
