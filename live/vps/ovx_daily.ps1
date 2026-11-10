# Oil-volatility flag for the personal CL Sunday fade (user 2026-11-10: in the personal plan while watched, WATCHLIST #37).
# Each weekday evening: download CBOE's OVX history, and if the latest close is above the median of the past 252 closes
# (the closes before it), write the empty file C:\TradingLogs\ovx\OVX_HIGH; otherwise delete it. The CL fade chart
# (funded_strategies/CL_Sunday_Gap_Fade.txt, UseOVX true, OVXQty 2) checks the file at its Sunday entry, so Friday's run decides
# the weekend. Log: C:\TradingLogs\ovx\ovx_log.csv (copied to live/health/ by the push). No phone alerts. Installed by
# push_trade_logs.ps1 as the task 'OvxDaily' (weekdays 18:00-21:00 CT, hourly; idempotent). Never touches MultiCharts.
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$Dir = "C:\TradingLogs\ovx"; New-Item -ItemType Directory -Force -Path $Dir | Out-Null
try {
    $csv = (Invoke-WebRequest -UseBasicParsing -Uri "https://cdn.cboe.com/api/global/us_indices/daily_prices/OVX_History.csv" -TimeoutSec 60).Content
} catch { "$(Get-Date -Format 'yyyy-MM-dd HH:mm'),,,DOWNLOAD_FAILED" | Add-Content "$Dir\ovx_log.csv"; exit }
$rows = @($csv -split "`n" | Select-Object -Skip 1 | Where-Object { $_ -match '^\d' } | ForEach-Object {
    $c = $_.Trim().Split(","); [pscustomobject]@{ d = [datetime]::Parse($c[0], [Globalization.CultureInfo]::InvariantCulture); v = [double]$c[$c.Count - 1] } } | Sort-Object d)
if ($rows.Count -lt 253) { exit }
$last = $rows[-1]; $past = @($rows[($rows.Count - 253)..($rows.Count - 2)] | ForEach-Object { $_.v } | Sort-Object)
$med = ($past[125] + $past[126]) / 2
$high = $last.v -gt $med
if ($high) { New-Item -ItemType File -Force -Path "$Dir\OVX_HIGH" | Out-Null } else { Remove-Item "$Dir\OVX_HIGH" -Force -ErrorAction SilentlyContinue }
"$(Get-Date -Format 'yyyy-MM-dd HH:mm'),$($last.d.ToString('yyyy-MM-dd')),$($last.v),$([math]::Round($med, 2)),$([int]$high)" | Add-Content "$Dir\ovx_log.csv"
