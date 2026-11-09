# Cushion peak files (2026-11-09; user: 'make whatever you have to automated'). The funded cushion guard needs each account's
# highest END-OF-DAY balance (Apex trails its threshold on it). The strategies track it themselves while running, but lose it
# on a MultiCharts restart / recompile; this script keeps it on disk so nobody retypes PeakSeed.
# From the Apex Chart Guard's ACCT rows (C:\TradingLogs\YYYYMMDD.csv: ACCT,tag,symbol,account,auto,networth,equity,...,date,time)
# it takes, per account and day, the last equity read between 15:00 and 16:00 CT (the day's close), keeps the highest (at least
# the start balance: 150,000 for a 150K account, 50,000 for a 50K), rounds it UP to $100, caps it at start + trailing drawdown +
# $100 (the threshold is locked from there on), and writes the empty file C:\TradingLogs\peak\<account>_<value> (older files of
# that account are removed). The strategies look for it once a day (input UseCushion true). Run by push_trade_logs.ps1 on every
# push (08:15, every 30 min in RTH, 16:10). Reads logs only; never touches MultiCharts.
$ErrorActionPreference = "Continue"
$Logs = "C:\TradingLogs"; $Dir = "$Logs\peak"
New-Item -ItemType Directory -Force -Path $Dir | Out-Null
$eod = @{}     # "account|date" -> @(time, equity)
$any = @{}     # account -> highest equity seen (to tell 50K from 150K)
foreach ($f in Get-ChildItem "$Logs\2*.csv" -ErrorAction SilentlyContinue) {
    foreach ($ln in Get-Content $f.FullName) {
        if (-not $ln.StartsWith("ACCT,")) { continue }
        $c = $ln.Split(",")
        if ($c.Count -lt 14 -or $c[3] -eq "") { continue }
        $acct = $c[3]; $eq = 0.0
        if (-not [double]::TryParse($c[6], [ref]$eq) -or $eq -le 0) { continue }
        $t = [int]$c[13]
        if (-not $any.ContainsKey($acct) -or $eq -gt $any[$acct]) { $any[$acct] = $eq }
        if ($t -lt 1500 -or $t -gt 1600) { continue }
        $k = "$acct|$($c[12])"
        if (-not $eod.ContainsKey($k) -or $t -ge $eod[$k][0]) { $eod[$k] = @($t, $eq) }
    }
}
foreach ($acct in $any.Keys) {
    if ($any[$acct] -gt 100000) { $start = 150000; $dd = 4000 } else { $start = 50000; $dd = 2000 }
    $peak = $start
    foreach ($k in $eod.Keys) { if ($k.StartsWith("$acct|") -and $eod[$k][1] -gt $peak) { $peak = $eod[$k][1] } }
    $v = [math]::Min([math]::Ceiling($peak / 100) * 100, $start + $dd + 100)
    $name = "$($acct)_$([int]$v)"
    Get-ChildItem "$Dir\$($acct)_*" -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne $name } | Remove-Item -Force
    if (-not (Test-Path "$Dir\$name")) { New-Item -ItemType File -Force -Path "$Dir\$name" | Out-Null }
}
