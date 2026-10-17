# Sends your journal notes and weekly MultiCharts reports to GitHub, and brings down Claude's latest files.
# Run it from PowerShell in the vault folder:
#   powershell -ExecutionPolicy Bypass -File journal\sync.ps1
# It only commits journal\ and live\. Never edit Claude's files (TODO.md, the plans, the strategy code) in this folder.
$ErrorActionPreference = "Continue"   # git writes progress to stderr; exit codes are checked below
Set-Location (Split-Path $PSScriptRoot -Parent)
$branch = "claude/nq-trading-strategy-params-5h9d20"
$cur = git rev-parse --abbrev-ref HEAD
if ($cur -ne $branch) { Write-Host "This folder is on '$cur', not $branch. Stopping (nothing changed)."; exit 1 }
git add journal live
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) { git commit -m "journal: notes $(Get-Date -Format yyyy-MM-dd)" }
git pull --no-rebase --no-edit origin $branch
if ($LASTEXITCODE -ne 0) { Write-Host "Pull failed (a file was edited on both sides?). Send Claude a screenshot."; exit 1 }
git push origin "HEAD:$branch"
if ($LASTEXITCODE -ne 0) { Write-Host "Push failed. Send Claude a screenshot."; exit 1 }
Write-Host "Synced. Tell Claude: 'read my journal'."
