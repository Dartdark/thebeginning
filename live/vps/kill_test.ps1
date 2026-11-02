# Disconnected test of the two-latch kill switch (Codex review 2026-11-01 #3). Uses a scratch folder (never
# C:\TradingLogs), sends no phone alerts, touches no chart or order. Run on the VPS:
#   powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\kill_test.ps1
# Every line must say PASS.
$K = "C:\TradingRepo\live\vps\kill.ps1"; $D = Join-Path $env:TEMP ("killtest_" + [guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory -Force $D | Out-Null
function K([string[]]$a) { & powershell -NoProfile -ExecutionPolicy Bypass -File $K -Dir $D -NoAlert @a | Out-Null; $LASTEXITCODE }
function Reset { Get-ChildItem $D | Remove-Item -Recurse -Force }
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
Reset; K @("-Remote") | Out-Null; Set-Content "$D\KILL" ""; K @("-Remote", "-Resume") | Out-Null
                                                  Check "remote kill, empty KILL by hand, remote resume -> stays ON" $true
Reset; K @("-Remote") | Out-Null; Set-Content "$D\KILL" "mine"; K @("-Check") | Out-Null; K @("-Remote", "-Resume") | Out-Null
                                                  Check "remote kill, KILL by hand, check, remote resume -> stays ON" $true
Reset; K @() | Out-Null; Remove-Item "$D\KILL"; K @("-Check") | Out-Null
                                                  Check "local kill, KILL deleted by hand, check -> restored" $true
Reset; K @("-Check") | Out-Null;                  Check "check with nothing set -> stays off" $false
# failure injection: the effective KILL path is a folder, so rebuilding the KILL file must fail -> exit 1, never "trade again"
Reset; Set-Content "$D\KILL_LOCAL" "x"; Set-Content "$D\KILL_REMOTE" "y"; New-Item -ItemType Directory "$D\KILL" | Out-Null
$code = K @("-Remote", "-Resume")
if ($code -ne 0) { "PASS  a resume that can't rebuild KILL returns an error (exit $code), not 'trade again'" } else { "FAIL  failed rebuild returned 0"; $fail++ }
Get-ChildItem $D | Remove-Item -Recurse -Force
Reset; $code = K @(); if ($code -eq 0) { "PASS  kill exit code 0" } else { "FAIL  kill exit code $code"; $fail++ }
Remove-Item $D -Recurse -Force
if ($fail -eq 0) { "ALL PASS" } else { "$fail FAILED: do not install, send Claude this output" }
