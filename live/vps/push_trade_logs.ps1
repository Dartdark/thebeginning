# Copies the day's trade logs from C:\TradingLogs into the repo clone on the VPS and pushes them (live/trades/).
# Runs from Task Scheduler on weekdays at 16:10 CT (see live/vps/README.md). Light: a few KB, one git push.
$ErrorActionPreference = "Continue"
$Repo = "C:\TradingRepo"
$Logs = "C:\TradingLogs"
$branch = "claude/nq-trading-strategy-params-5h9d20"
Set-Location $Repo
git pull --no-rebase --no-edit origin $branch
New-Item -ItemType Directory -Force "live\trades" | Out-Null
Copy-Item "$Logs\*.csv" "live\trades\" -Force -ErrorAction SilentlyContinue
git add live/trades
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "live trades $(Get-Date -Format yyyy-MM-dd)"
    git push origin "HEAD:$branch"
    if ($LASTEXITCODE -ne 0) { "$(Get-Date) push failed" | Out-File -Append "$Logs\push_errors.txt" }
}
