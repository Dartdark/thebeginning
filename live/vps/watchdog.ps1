# VPS watchdog (2026-10-21): checks every 5 minutes on weekdays 08:15-15:10 CT and pushes an alert to the user's phone
# (ntfy app, topic below) the moment something can affect trading. Installed by push_trade_logs.ps1 as the task
# 'VpsWatchdog'. Read-only: it never touches MultiCharts, Rithmic or orders.
# Checks: MultiCharts running; MultiCharts has live network connections (broker / data); every chart's logger heartbeat
# is < 45 min old (frozen chart / feed); a chart's position differs from the broker's (MISMATCH); NEW rejected-order lines
# in MultiCharts' logs (Symbol Mapping, wrong account, Apex lock). Each problem alerts at most once an hour.
$ErrorActionPreference = "SilentlyContinue"
$Topic = "apex-alarm-6e531eb6db8e"            # subscribe to this topic in the ntfy app (iPhone / Android)
$Logs = "C:\TradingLogs"
$StateFile = "$Logs\watchdog_state.json"
$now = Get-Date; $day = $now.ToString("yyyyMMdd"); $hhmm = [int]$now.ToString("HHmm")
$state = @{}; if (Test-Path $StateFile) { (Get-Content $StateFile -Raw | ConvertFrom-Json).PSObject.Properties | ForEach-Object { $state[$_.Name] = $_.Value } }
$problems = @()

# 1. MultiCharts running and connected
$mc = @(Get-Process | Where-Object { $_.ProcessName -like "MultiCharts*" -or $_.ProcessName -like "TradingServer*" -or $_.ProcessName -like "*Rithmic*" })
if ($mc.Count -eq 0) { $problems += "MC_DOWN|MultiCharts is not running on the VPS" }
else {
    $ids = $mc.Id
    $conn = @(Get-NetTCPConnection -State Established | Where-Object { $ids -contains $_.OwningProcess -and $_.RemoteAddress -notmatch '^(127\.|::1)' })
    if ($conn.Count -eq 0) { $problems += "NO_NET|MultiCharts has no live internet connections (Rithmic / data feed down?)" }
}

# 2. logger rows: heartbeats and position vs broker
$f = "$Logs\$day.csv"
$tags = @{}
Get-ChildItem "$Logs\2*.csv" | Sort-Object Name -Descending | Select-Object -First 6 | ForEach-Object {
    Get-Content $_.FullName | Where-Object { $_ -like "POS,*" } | ForEach-Object { $tags[$_.Split(",")[1]] = $true } }
$last = @{}
if (Test-Path $f) { Get-Content $f | Where-Object { $_ -like "POS,*" } | ForEach-Object { $c = $_.Split(","); $last[$c[1]] = $c } }
if ($hhmm -ge 845 -and $hhmm -le 1500) {
    foreach ($t in $tags.Keys) {
        if (-not $last.ContainsKey($t)) { $problems += "STALE_$t|Chart $t has written no heartbeat today"; continue }
        $c = $last[$t]; $bt = [int]$c[13]; $age = ([int]($hhmm / 100) * 60 + $hhmm % 100) - ([int]($bt / 100) * 60 + $bt % 100)
        if ($age -gt 45) { $problems += "STALE_$t|Chart $t: no heartbeat for $age min (frozen chart or feed?)" }
        if ($c[4] -ne $c[11] -and $age -ge 3) { $problems += "MISMATCH_$t|Chart $t thinks $($c[4]) contracts, broker has $($c[11]). Check the account now." }
    }
}

# 3. new rejected-order lines in MultiCharts' own logs
$rej = 0; $msg = ""
foreach ($r in @("$env:LOCALAPPDATA\TS Support", "$env:APPDATA\TS Support", "C:\ProgramData\TS Support") | Where-Object { Test-Path $_ }) {
    Get-ChildItem $r -Recurse -File -Include *.log, *.txt | Where-Object { $_.LastWriteTime.Date -eq $now.Date -and $_.Length -lt 200MB } | ForEach-Object {
        $h = Select-String -Path $_.FullName -Pattern "Rejected|Invalid .* order|done for day"
        if ($h) { $rej += @($h).Count; $msg = $h[-1].Line } }
}
$prev = 0; if ($state["rej_day"] -eq $day) { $prev = [int]$state["rej_count"] }
if ($rej -gt $prev) {
    $hint = ""; if ($msg -match "@MNQ|@MES|Invalid") { $hint = " Likely Symbol Mapping: File > Broker Profiles > Symbol Mapping." }
    $problems += "REJECT_$rej|$($rej - $prev) new rejected order(s). Last: $($msg.Substring(0, [math]::Min(140, $msg.Length))).$hint"
}
$state["rej_day"] = $day; $state["rej_count"] = $rej

# 4. alert (once an hour per problem), log, save state
foreach ($p in $problems) {
    $key, $text = $p.Split("|", 2); $k = "sent_" + ($key -replace '_\d+$', '')
    $lastSent = if ($state[$k]) { [datetime]$state[$k] } else { [datetime]::MinValue }
    if (($now - $lastSent).TotalMinutes -ge 60 -or $key -like "REJECT_*") {
        try { Invoke-RestMethod -Method Post -Uri "https://ntfy.sh/$Topic" -Body "VPS: $text" -Headers @{ Title = "Trading alarm"; Priority = "high" } | Out-Null } catch {}
        "$($now.ToString('yyyy-MM-dd HH:mm')) ALERT $text" | Add-Content "$Logs\alerts.txt"
        $state[$k] = $now.ToString("o")
    }
}
$state | ConvertTo-Json | Set-Content $StateFile
