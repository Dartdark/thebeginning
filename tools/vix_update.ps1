# Daily VIX file for the Overnight Tick / VIX strategy (2026-10-24). dxFeed has no VIX index, so MultiCharts reads
# C:\TradingData\VIX\VIX_daily.csv through Map ASCII (symbol VIX_CBOE, daily). This script rewrites that file from Cboe's
# official history (https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv); if Cboe has not added
# today's close yet, it appends today's daily bar from Yahoo Finance (^VIX). Format kept as the repo's data/VIX_daily.csv:
#   DATE,OPEN,HIGH,LOW,CLOSE  with DATE = yyyy-MM-dd.
# Run on the machine that trades (the VPS, Central clock), weekdays after the VIX close (15:15 CT), before 17:05 CT:
#   powershell -ExecutionPolicy Bypass -File C:\TradingData\VIX\vix_update.ps1
# Register it once (PowerShell as Administrator) - runs 15:30 and again 16:30 CT, Monday-Friday:
#   $a = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\TradingData\VIX\vix_update.ps1"
#   $t1 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 3:30PM
#   $t2 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 4:30PM
#   Register-ScheduledTask -TaskName "VIXUpdate" -Action $a -Trigger $t1,$t2 -Description "VIX daily file for MultiCharts"
# The log (vix_update.log next to the CSV) shows the last date written each run. If both sources fail, the old file stays
# and the strategy uses the previous day's VIX (backtest $309 vs $374 per NQ): nothing breaks.

$ErrorActionPreference = "Stop"
$dir = "C:\TradingData\VIX"
$out = Join-Path $dir "VIX_daily.csv"
$tmp = Join-Path $dir "VIX_daily.tmp"
$log = Join-Path $dir "vix_update.log"
New-Item -ItemType Directory -Force $dir | Out-Null
function Log($m) { Add-Content $log ("{0}  {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m) }
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

try {
    $raw = (Invoke-WebRequest -UseBasicParsing -Uri "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv" -TimeoutSec 60).Content
    $rows = New-Object System.Collections.Generic.List[string]
    $rows.Add("DATE,OPEN,HIGH,LOW,CLOSE")
    $last = $null
    foreach ($line in ($raw -split "`r?`n")) {
        if ($line -notmatch '^\d{2}/\d{2}/\d{4},') { continue }          # skips the header and blank lines
        $f = $line.Split(",")
        $d = [datetime]::ParseExact($f[0], "MM/dd/yyyy", [Globalization.CultureInfo]::InvariantCulture)
        $vals = $f[1..4] | ForEach-Object { "{0:0.00}" -f [double]::Parse($_, [Globalization.CultureInfo]::InvariantCulture) }
        $rows.Add(($d.ToString("yyyy-MM-dd") + "," + ($vals -join ",")))
        $last = $d
    }
    if ($rows.Count -lt 1000) { throw "Cboe file too short ($($rows.Count) rows)" }
    $today = (Get-Date).Date
    if ($last -lt $today -and $today.DayOfWeek -ne "Saturday" -and $today.DayOfWeek -ne "Sunday") {
        try {
            $y = Invoke-RestMethod -Uri "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?interval=1d&range=5d" -Headers @{ "User-Agent" = "Mozilla/5.0" } -TimeoutSec 60
            $r = $y.chart.result[0]; $q = $r.indicators.quote[0]
            $ct = [TimeZoneInfo]::FindSystemTimeZoneById("Central Standard Time")
            for ($i = 0; $i -lt $r.timestamp.Count; $i++) {
                $bar = [TimeZoneInfo]::ConvertTimeFromUtc([DateTimeOffset]::FromUnixTimeSeconds($r.timestamp[$i]).UtcDateTime, $ct).Date
                if ($bar -eq $today -and $q.close[$i] -ne $null) {
                    $rows.Add(("{0},{1:0.00},{2:0.00},{3:0.00},{4:0.00}" -f $today.ToString("yyyy-MM-dd"), $q.open[$i], $q.high[$i], $q.low[$i], $q.close[$i]))
                    $last = $today; Log "Cboe ended $($rows[$rows.Count - 2].Split(',')[0]); appended today's close from Yahoo"
                }
            }
        } catch { Log "Yahoo failed: $($_.Exception.Message)" }
    }
    Set-Content -Path $tmp -Value $rows -Encoding ASCII
    Move-Item -Force $tmp $out
    Log ("OK, last date " + $last.ToString("yyyy-MM-dd") + ", " + ($rows.Count - 1) + " days")
} catch {
    Log ("FAILED, file unchanged: " + $_.Exception.Message)
    exit 1
}
