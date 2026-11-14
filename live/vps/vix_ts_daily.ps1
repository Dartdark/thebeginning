# VIX term-structure flag for the personal ES Dip Buy (personal_strategies/ES_Dip_Buy.txt; WATCHLIST #45). Written 2026-11-14,
# NOT YET RUN on the VPS: run it once by hand and check the log + files before relying on it.
# Downloads CBOE's VIX and VIX3M daily history; ratio = VIX / VIX3M on dates both have. Rising = the latest ratio close is higher
# than the close 20 trading days earlier (analysis/new_data_screen.py RULES 'rising'). The flag applies to every CME session whose
# date is after that close and up to 4 calendar days later (covers weekends and a Monday holiday); a later close overwrites them.
# Writes empty files C:\TradingLogs\vix\VIXTS_<yyyymmdd>_1 (rising) or _0 (not rising), one per session date, and deletes the
# opposite file. No file for a session = the strategy takes no new real entry (it logs the shadow entry). Files older than 10
# days are removed. Log: C:\TradingLogs\vix\vix_ts_log.csv. No phone alerts. Never touches MultiCharts.
# Install once (as OvxDaily in push_trade_logs.ps1), weekdays every 15 minutes from 15:30 to 23:30 CT:
#   schtasks /Create /TN "VixTsDaily" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 15:30 /RI 15 /DU 08:00 /TR "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\TradingRepo\live\vps\vix_ts_daily.ps1" /F
# Timing risk (GUESS): if CBOE posts the day's close after 17:00 CT, evening entries (17:00 until the file appears) find no file
# for the next session and are skipped; the shadow log shows how often (Rising = -1).
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$Dir = "C:\TradingLogs\vix"; New-Item -ItemType Directory -Force -Path $Dir | Out-Null
$Log = Join-Path $Dir "vix_ts_log.csv"
function Get-Cboe($name) {
    $u = "https://cdn.cboe.com/api/global/us_indices/daily_prices/" + $name + "_History.csv"
    $csv = (Invoke-WebRequest -UseBasicParsing -Uri $u -TimeoutSec 60).Content
    $h = @{}
    foreach ($line in ($csv -split "`n" | Select-Object -Skip 1)) {
        $c = $line.Trim().Split(",")
        if ($c.Count -lt 2 -or $c[0] -notmatch '^\d') { continue }
        $d = [datetime]::Parse($c[0], [Globalization.CultureInfo]::InvariantCulture).Date
        $h[$d] = [double]::Parse($c[$c.Count - 1], [Globalization.CultureInfo]::InvariantCulture)
    }
    return $h
}
try { $vix = Get-Cboe "VIX"; $v3m = Get-Cboe "VIX3M" }
catch { "$(Get-Date -Format 'yyyy-MM-dd HH:mm'),,,,DOWNLOAD_FAILED" | Add-Content $Log; exit }
$dates = @($vix.Keys | Where-Object { $v3m.ContainsKey($_) -and $v3m[$_] -gt 0 } | Sort-Object)
if ($dates.Count -lt 21) { "$(Get-Date -Format 'yyyy-MM-dd HH:mm'),,,,TOO_SHORT" | Add-Content $Log; exit }
$last = $dates[-1]; $back = $dates[-21]
$rLast = $vix[$last] / $v3m[$last]; $rBack = $vix[$back] / $v3m[$back]
$flag = 0; if ($rLast -gt $rBack) { $flag = 1 }
for ($i = 1; $i -le 4; $i++) {
    $s = $last.AddDays($i).ToString("yyyyMMdd")
    New-Item -ItemType File -Force -Path (Join-Path $Dir ("VIXTS_" + $s + "_" + $flag)) | Out-Null
    Remove-Item (Join-Path $Dir ("VIXTS_" + $s + "_" + (1 - $flag))) -Force -ErrorAction SilentlyContinue
}
Get-ChildItem $Dir -Filter "VIXTS_*" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-10) } | Remove-Item -Force -ErrorAction SilentlyContinue
"$(Get-Date -Format 'yyyy-MM-dd HH:mm'),$($last.ToString('yyyy-MM-dd')),$([math]::Round($rLast, 4)),$([math]::Round($rBack, 4)),$flag" | Add-Content $Log
