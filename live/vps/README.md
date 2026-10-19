# VPS: trade logs -> repo (daily, automatic)

1. **Folder:** create `C:\TradingLogs` on the VPS.
2. **Logger:** add `apex_strategies/Apex_Trade_Logger.txt` (compile it as a Signal named "Apex Trade Logger") to every live
   chart, `Tag` = VB / ONB / EOS / MON_BR. It only writes files; it places no orders.
3. **Git on the VPS (once):** install Git for Windows (git-scm.com), then in PowerShell:
   `git clone https://github.com/Dartdark/thebeginning.git C:\TradingRepo` and
   `cd C:\TradingRepo; git checkout claude/nq-trading-strategy-params-5h9d20`. Sign in to GitHub when asked (the repo is
   private); the login is remembered.
4. **Schedule the push (once):** in PowerShell as the VPS user:
   `schtasks /Create /TN "PushTradeLogs" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 16:10 /TR "powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\push_trade_logs.ps1"`
   (16:10 in the VPS's own clock: set the VPS to Central time, or change the time.)
5. **Test:** run `powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\push_trade_logs.ps1` once by hand; tell
   Claude, who checks the file arrived in `live/trades/`.

Claude's weekday task (16:40 CT) runs `python3 analysis/journal_trades.py` and writes the trades into that day's journal
note (`journal/daily/YYYY-MM-DD.md`, between the `auto-trades` markers). Errors from the push go to
`C:\TradingLogs\push_errors.txt`.
