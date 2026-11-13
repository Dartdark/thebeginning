# FINRA short-volume signal, fully automatic (user 2026-11-09: 'I don't want to do anything manually every day').
# Personal-plan piece 'FINRA short-volume longs' (WATCHLIST #32, analysis/finra_longs_test.py). Each weekday evening:
#   1. downloads FINRA's consolidated daily short-volume file (cdn.finra.org, published ~17:00 CT the same day);
#   2. R = the equal-weight mean of ShortVolume / TotalVolume over QQQ + AAPL MSFT NVDA AMZN META GOOGL AVGO TSLA COST NFLX;
#   3. Z = (R - mean of the previous 60 days' R) / their sample sd (as the Python rule);
#   4. Z >= 1 -> writes the flag file C:\TradingLogs\finra\SIG_<FINRA date yyyymmdd>. The MultiCharts strategy
#      (checks/candidates/finra_longs/NQ_FINRA_Short_Volume_Longs.txt, UseFlagFiles true) looks for the flag of the previous
#      weekday at each new day and buys NQ / MNQ at the 08:31 open: the 'next trading day' of the backtest.
# History: C:\TradingLogs\finra\history.csv (date,R), seeded the first time from the repo's data/finra/short_volume.csv.
# Every new date is logged to C:\TradingLogs\finra\signals.csv (date,R,Z,signal); a download still missing after 20:00 CT is
# logged as date,,,MISSING (a holiday or a FINRA delay). No phone alerts (user 2026-11-09: fewer alerts): the 16:10 push copies
# the log to the repo (live/finra/signals.csv) and Claude checks it in the Friday review. Safe to run many times a day.
# Installed by push_trade_logs.ps1 as the task 'FinraDaily' (weekdays 18:00-21:00 CT, hourly). Never touches MultiCharts.
param([string]$Day = "")
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12   # Windows PowerShell 5.1 defaults can fail on cdn.finra.org
$Repo = "C:\TradingRepo"; $Dir = "C:\TradingLogs\finra"
$Syms = @("QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "AVGO", "TSLA", "COST", "NFLX")
New-Item -ItemType Directory -Force -Path $Dir | Out-Null
$Hist = "$Dir\history.csv"; $Log = "$Dir\signals.csv"

function Get-R($lines) {
    $r = @()
    foreach ($ln in $lines) {
        $c = $ln.Split("|")
        if ($c.Count -ge 5 -and $Syms -contains $c[1]) {
            $tot = [double]$c[4]
            if ($tot -gt 0) { $r += [double]$c[2] / $tot }
        }
    }
    if ($r.Count -eq 0) { return $null }
    return ($r | Measure-Object -Average).Average
}

# 1. history (seed from the repo the first time)
$H = [ordered]@{}
if (Test-Path $Hist) {
    foreach ($ln in Get-Content $Hist) { $c = $ln.Split(","); if ($c.Count -eq 2 -and $c[0] -match '^\d{8}$') { $H[$c[0]] = [double]$c[1] } }
}
if ($H.Count -lt 61 -and (Test-Path "$Repo\data\finra\short_volume.csv")) {
    $rows = Get-Content "$Repo\data\finra\short_volume.csv" | Select-Object -Skip 1
    foreach ($g in ($rows | Group-Object { $_.Split("|")[0] })) { $v = Get-R $g.Group; if ($v -ne $null) { $H[$g.Name] = $v } }
}

# 2. today's file (or -Day yyyyMMdd), plus any missed weekdays in the last 10 days
$now = Get-Date
$want = @()
if ($Day) { $want += $Day } else {
    for ($i = 10; $i -ge 0; $i--) {
        $d = $now.Date.AddDays(-$i)
        if ($d.DayOfWeek -ne "Saturday" -and $d.DayOfWeek -ne "Sunday") { $want += $d.ToString("yyyyMMdd") }
    }
}
$new = @()
foreach ($d in $want) {
    if ($H.Contains($d)) { continue }
    try {
        $txt = (Invoke-WebRequest -UseBasicParsing -Uri "https://cdn.finra.org/equity/regsho/daily/CNMSshvol$d.txt" -TimeoutSec 60).Content
        $v = Get-R ($txt -split "`n")
        if ($v -ne $null) { $H[$d] = $v; $new += $d }
    } catch {
        # missing = not published yet or a market holiday; logged once, late in the evening
        if ($d -eq $now.ToString("yyyyMMdd") -and $now.Hour -ge 20 -and -not (Select-String -Path $Log -Pattern "^$d," -Quiet -ErrorAction SilentlyContinue)) {
            "$d,,,MISSING" | Add-Content $Log
        }
    }
}
$keys = @($H.Keys | Sort-Object)
($keys | ForEach-Object { "$_,$($H[$_])" }) | Set-Content $Hist

# 3. Z and the flag for every newly added date
foreach ($d in ($new | Sort-Object)) {
    $i = [array]::IndexOf($keys, $d)
    if ($i -lt 60) { continue }
    $prev = @($keys[($i - 60)..($i - 1)] | ForEach-Object { $H[$_] })
    $m = ($prev | Measure-Object -Average).Average
    $sd = [math]::Sqrt((($prev | ForEach-Object { ($_ - $m) * ($_ - $m) }) | Measure-Object -Sum).Sum / ($prev.Count - 1))
    $z = if ($sd -gt 0) { ($H[$d] - $m) / $sd } else { 0 }
    $sig = [int]($z -ge 1.0)
    "$d,$([math]::Round($H[$d], 6)),$([math]::Round($z, 3)),$sig" | Add-Content $Log
    if ($sig -eq 1) {
        New-Item -ItemType File -Force -Path "$Dir\SIG_$d" | Out-Null
    }
}
