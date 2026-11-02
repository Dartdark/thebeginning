# Disconnected test of the two-latch kill switch (Codex review 2026-11-01 #3). Uses a scratch folder (never
# C:\TradingLogs), sends no phone alerts, touches no chart or order. Run on the VPS:
#   powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\kill_test.ps1
# Every line must say PASS.
$K = "C:\TradingRepo\live\vps\kill.ps1"; $D = Join-Path $env:TEMP ("killtest_" + [guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory -Force $D | Out-Null
function K([string[]]$a) { & powershell -NoProfile -ExecutionPolicy Bypass -File $K -Dir $D -NoAlert @a | Out-Null; $LASTEXITCODE }
function Reset { Get-ChildItem $D | Remove-Item -Force }
$fail = 0
function Check($name, $want) { $on = Test-Path "$D\KILL"; if ($on -eq $want) { "PASS  $name (KILL $(if ($on) {'on'} else {'off'}))" } else { "FAIL  $name (KILL $(if ($on) {'on'} else {'off'}), wanted $(if ($want) {'on'} else {'off'}))"; $script:fail++ } }

Reset; K @() | Out-Null;                         Check "local kill" $true
K @("-Resume") | Out-Null;                        Check "local resume" $false
Reset; K @("-Remote") | Out-Null;                 Check "remote kill" $true
K @("-Remote", "-Resume") | Out-Null;             Check "remote resume" $false
Reset; K @("-Remote") | Out-Null; K @() | Out-Null; K @("-Remote", "-Resume") | Out-Null
                                                  Check "remote kill, local kill, remote resume -> stays ON" $true
K @("-Resume") | Out-Null;                        Check "  ...then local resume -> off" $false
Reset; K @() | Out-Null; K @("-Remote") | Out-Null; K @("-Resume") | Out-Null
                                                  Check "local kill, remote kill, local resume -> stays ON" $true
K @("-Remote", "-Resume") | Out-Null;             Check "  ...then remote resume -> off" $false
Reset; Set-Content "$D\KILL" "old-style kill"; K @("-Remote", "-Resume") | Out-Null
                                                  Check "old one-file kill survives a remote resume" $true
Reset; K @("-Resume") | Out-Null;                 Check "resume with nothing set" $false
$code = K @(); if ($code -eq 0) { "PASS  kill exit code 0" } else { "FAIL  kill exit code $code"; $fail++ }
Remove-Item $D -Recurse -Force
if ($fail -eq 0) { "ALL PASS" } else { "$fail FAILED: do not install, send Claude this output" }
