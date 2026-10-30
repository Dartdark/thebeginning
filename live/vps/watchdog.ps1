# VPS watchdog (2026-10-21): checks every 5 minutes on weekdays 08:15-15:10 CT and pushes an alert to the user's phone
# (ntfy app, topic below) the moment something can affect trading. Installed by push_trade_logs.ps1 as the task
# 'VpsWatchdog'. Read-only: it never touches MultiCharts, Rithmic or orders.
# Checks: MultiCharts running; MultiCharts has live network connections (broker / data); every chart's logger heartbeat
# is < 45 min old (frozen chart / feed); a chart's position differs from the broker's (MISMATCH); NEW rejected-order lines
# in MultiCharts' logs (Symbol Mapping, wrong account, Apex lock). Each problem alerts at most once an hour.
param([switch]$Test)
$ErrorActionPreference = "SilentlyContinue"
$Topic = "apex-alarm-6e531eb6db8e"            # subscribe to this topic in the ntfy app (iPhone / Android)
$Logs = "C:\TradingLogs"
$StateFile = "$Logs\watchdog_state.json"
# -Test (2026-10-29): send one sample of every alert type to the phone, then stop (checks the ntfy path end to end)
if ($Test) {
    $samples = @("MultiCharts is not running on the VPS", "MultiCharts has no live internet connections (Rithmic / data feed down?)",
        "Chart VB-2: no heartbeat for 50 min (frozen chart or feed?)", "Chart VB-2 thinks 8 contracts, broker has 0. Check the account now.",
        "Chart ONB-2: auto-trading is OFF (account APEX-681524-02). Turn it on if this chart should trade.",
        "Chart EOS150: last bar is 12 min old. Data feed / Rithmic quiet? Check the connection status.",
        "Strategy on chart ONB150 wrote no heartbeat today: not compiled / removed? It cannot trade.",
        "1 new rejected order(s). Last: Invalid Market order parameters @MNQ. Likely Symbol Mapping.")
    $i = 0
    foreach ($m in $samples) { $i++; try { Invoke-RestMethod -Method Post -Uri "https://ntfy.sh/$Topic" -Body "TEST $i/8 VPS: $m" -Headers @{ Title = "Trading alarm (TEST)"; Priority = "high" } | Out-Null } catch { "ntfy failed: $_" }; Start-Sleep -Seconds 2 }
    "Sent $i test alerts to ntfy topic $Topic"
    exit
}
$now = Get-Date; $day = $now.ToString("yyyyMMdd"); $hhmm = [int]$now.ToString("HHmm")
$state = @{}; if (Test-Path $StateFile) { (Get-Content $StateFile -Raw | ConvertFrom-Json).PSObject.Properties | ForEach-Object { $state[$_.Name] = $_.Value } }
$problems = @()

# 1. MultiCharts running and connected
$mc = @(Get-Process | Where-Object { $_.ProcessName -like "MultiCharts*" -or $_.ProcessName -like "TradingServer*" -or $_.ProcessName -like "*Rithmic*" })
if ($mc.Count -eq 0) { $problems += "MC_DOWN|MultiCharts is not running on the VPS" }
else {
    $ids = $mc.Id
    $conn = @(Get-NetTCPConnection -State Established | Where-Object { $ids -contains $_.OwningProcess -and $_.RemoteAddress -notmatch '^(127\.|::1)' })
    # 2026-10-29: the Rithmic / dxFeed sockets belong to a MultiCharts helper process this name filter misses, so the
    # check fired all morning while every chart had 0-1 s old bars. Alarm only if no chart wrote a fresh bar (ACCT row,
    # bar age < 10 min) in the last 10 minutes; a really dead feed is also caught by the FEED_ check below.
    $fresh = $false
    if (Test-Path "$Logs\$day.csv") {
        $m = [math]::Floor($hhmm / 100) * 60 + $hhmm % 100
        Get-Content "$Logs\$day.csv" -Tail 400 | Where-Object { $_ -like "ACCT,*" } | ForEach-Object {
            $c = $_.Split(","); $bt = [int]$c[13]
            if ([double]$c[7] -lt 600 -and ($m - ([math]::Floor($bt / 100) * 60 + $bt % 100)) -le 10) { $fresh = $true } }
    }
    if ($conn.Count -eq 0 -and -not $fresh) { $problems += "NO_NET|MultiCharts has no live internet connections and no chart has a fresh bar (Rithmic / data feed down?)" }
}

# 2. logger rows: heartbeats and position vs broker
$f = "$Logs\$day.csv"
$tags = @{}
Get-ChildItem "$Logs\2*.csv" | Sort-Object Name -Descending | Select-Object -First 6 | ForEach-Object {
    Get-Content $_.FullName | Where-Object { $_ -like "POS,*" } | ForEach-Object { $tags[$_.Split(",")[1]] = $true } }
# only the charts that should be live (live/expected_setup.json): a closed account's tags (VB, ONB, EOS, MON_BR = #1)
# stay in the last days' files and gave false 'no heartbeat today' alarms on 2026-10-29
$cfg = Get-Content "C:\TradingRepo\live\expected_setup.json" -Raw | ConvertFrom-Json
if ($cfg) { $live = @($cfg.charts.PSObject.Properties.Name); foreach ($t in @($tags.Keys)) { if ($live -notcontains $t) { $tags.Remove($t) } } }
$last = @{}
if (Test-Path $f) { Get-Content $f | Where-Object { $_ -like "POS,*" } | ForEach-Object { $c = $_.Split(","); $last[$c[1]] = $c } }
if ($hhmm -ge 845 -and $hhmm -le 1500) {
    foreach ($t in $tags.Keys) {
        if (-not $last.ContainsKey($t)) { $problems += "STALE_$t|Chart $t has written no heartbeat today"; continue }
        $c = $last[$t]; $bt = [int]$c[13]; $age = ([math]::Floor($hhmm / 100) * 60 + $hhmm % 100) - ([math]::Floor($bt / 100) * 60 + $bt % 100)
        if ($age -gt 45) { $problems += "STALE_$t|Chart ${t}: no heartbeat for $age min (frozen chart or feed?)" }
        if ($c[4] -ne $c[11] -and $age -ge 3) { $problems += "MISMATCH_$t|Chart $t thinks $($c[4]) contracts, broker has $($c[11]). Check the account now." }
    }
}

# 2b. Apex Chart Monitor rows (2026-10-29): auto-trading off, or the chart's last bar > 10 min old (feed quiet)
$acct = @{}
if (Test-Path $f) { Get-Content $f | Where-Object { $_ -like "ACCT,*" } | ForEach-Object { $c = $_.Split(","); $acct[$c[1]] = $c } }
if ($hhmm -ge 830 -and $hhmm -le 1500) {
    foreach ($t in $acct.Keys) {
        $c = $acct[$t]
        if ($c[4] -eq "0") { $problems += "AUTOOFF_$t|Chart ${t}: auto-trading is OFF (account $($c[3])). Turn it on if this chart should trade." }
        if ([double]$c[7] -gt 600) { $problems += "FEED_$t|Chart ${t}: last bar is $([int]([double]$c[7] / 60)) min old. Data feed / Rithmic quiet? Check the connection status." }
    }
}

# 2c. strategy heartbeat (SIG rows, 2026-10-29): a strategy that stopped writing for > 45 min in RTH is not running
#     (failed compile, removed, error) even if the chart and its AA button look normal
$sigTags = @{}
Get-ChildItem "$Logs\2*.csv" | Sort-Object Name -Descending | Select-Object -First 6 | ForEach-Object {
    Get-Content $_.FullName | Where-Object { $_ -like "SIG,*" } | ForEach-Object { $sigTags[$_.Split(",")[1]] = $true } }
$sigLast = @{}
if (Test-Path $f) { Get-Content $f | Where-Object { $_ -like "SIG,*" } | ForEach-Object { $c = $_.Split(","); $sigLast[$c[1]] = [int]$c[13] } }
if ($hhmm -ge 900 -and $hhmm -le 1500) {
    foreach ($t in $sigTags.Keys) {
        if (-not $sigLast.ContainsKey($t)) { $problems += "NOSTRAT_$t|Strategy on chart $t wrote no heartbeat today: not compiled / removed? It cannot trade."; continue }
        $bt = $sigLast[$t]; $age = ([math]::Floor($hhmm / 100) * 60 + $hhmm % 100) - ([math]::Floor($bt / 100) * 60 + $bt % 100)
        if ($age -gt 45) { $problems += "NOSTRAT_$t|Strategy on chart ${t}: no heartbeat for $age min. Check the strategy is running." }
    }
}

# 3. new rejected-order lines in MultiCharts' own logs
$rej = 0; $msg = ""
foreach ($r in @("$env:LOCALAPPDATA\TS Support", "$env:APPDATA\TS Support", "C:\ProgramData\TS Support") | Where-Object { Test-Path $_ }) {
    Get-ChildItem $r -Recurse -File -Include *.log, *.txt | Where-Object { $_.LastWriteTime.Date -eq $now.Date -and $_.Length -lt 200MB } | ForEach-Object {
        $h = Select-String -Path $_.FullName -Pattern "Rejected|Invalid .* order|done for day"
        $h = @($h | Where-Object { $_.Line -like ("*" + $now.ToString("dd.MM.yyyy") + "/*") })   # today's lines only (2026-10-29)
        # count ORDERS, not log lines: one rejected order writes many lines; keep lines that name an order (2026-10-30:
        # '2,301 rejected' was ~100 orders, MultiCharts' own 'stop after N rejected orders' had already stopped it)
        $o = @($h | Where-Object { $_.Line -match "OrderName=" }); if ($o.Count -eq 0) { $o = $h }
        if ($h) { $rej += $o.Count; $msg = $h[-1].Line } }
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
