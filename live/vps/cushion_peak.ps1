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

# ---------- Rithmic copier groups (2026-11-09) ----------
# The copier sends the leader's orders to every follower, so the strategies size for the GROUP (user: one leader for the
# evaluations, one for the funded accounts; followers 1x). From the latest day's close balances (the Apex Chart Guard's SCAN
# rows cover every account, not only the leader):
#   evaluations (APEX-..., 150K): alive = above its trailing floor (highest close - 4,000) and below the 159,000 target;
#     the group's MEAN profit >= 6,000 -> file group\EVAL_FINISH (every evaluation trades half size), else group\EVAL_FULL
#     (analysis/copier_finish_bench.py: the best rule a copier allows, +0.8 points vs no finish mode);
#   funded (PA-APEX-...): cushion = close - min(start + 100, highest close - trailing drawdown); the smallest cushion of the
#     accounts still above their threshold, rounded DOWN to $100 (0-10,000) -> file group\FUNDED_C<value>.
# The strategies read these once a day (input CopierGroup true). No alive account of a type = its files are removed.
$G = "$Logs\group"; New-Item -ItemType Directory -Force -Path $G | Out-Null
$last = ($eod.Keys | ForEach-Object { $_.Split("|")[1] } | Sort-Object | Select-Object -Last 1)
$evalProf = @(); $fundCush = @()
if ($last) {
    foreach ($acct in $any.Keys) {
        $k = "$acct|$last"; if (-not $eod.ContainsKey($k)) { continue }
        $close = $eod[$k][1]
        if ($any[$acct] -gt 100000) { $start = 150000; $dd = 4000; $tgt = 159000 } else { $start = 50000; $dd = 2000; $tgt = 53000 }
        $hi = $start
        foreach ($kk in $eod.Keys) { if ($kk.StartsWith("$acct|") -and $eod[$kk][1] -gt $hi) { $hi = $eod[$kk][1] } }
        if ($acct.StartsWith("PA-")) {
            $thr = [math]::Min($start + 100, $hi - $dd); $c = $close - $thr
            if ($c -gt 0) { $fundCush += $c }
        } elseif ($acct.StartsWith("APEX-") -and $start -eq 150000) {
            if ($close -gt ($hi - $dd) -and $close -lt $tgt) { $evalProf += ($close - $start) }
        }
    }
}
Get-ChildItem "$G\EVAL_*" -ErrorAction SilentlyContinue | Remove-Item -Force
if ($evalProf.Count -gt 0) {
    $m = ($evalProf | Measure-Object -Average).Average
    $f = if ($m -ge 6000) { "EVAL_FINISH" } else { "EVAL_FULL" }
    New-Item -ItemType File -Force -Path "$G\$f" | Out-Null
}
Get-ChildItem "$G\FUNDED_C*" -ErrorAction SilentlyContinue | Remove-Item -Force
if ($fundCush.Count -gt 0) {
    $mc = [math]::Max(0, [math]::Min(10000, [math]::Floor((($fundCush | Measure-Object -Minimum).Minimum) / 100) * 100))
    New-Item -ItemType File -Force -Path "$G\FUNDED_C$([int]$mc)" | Out-Null
}
"$(Get-Date -Format 'yyyy-MM-dd HH:mm'),$last,evals=$($evalProf.Count),eval_mean=$(if ($evalProf.Count) { [math]::Round(($evalProf | Measure-Object -Average).Average, 0) }),funded=$($fundCush.Count),min_cushion=$(if ($fundCush.Count) { [math]::Round(($fundCush | Measure-Object -Minimum).Minimum, 0) })" | Add-Content "$G\group_log.csv"
