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

## Health checks (automatic, 2026-10-21)

- **Logger:** the updated `Apex_Trade_Logger.txt` also writes `POS` rows (strategy position vs the broker's position for
  that strategy) on every change and every 30 minutes. One-time step: paste the new code into the existing "Apex Trade
  Logger" signal and compile, outside market hours (all charts that use it pick it up; inputs unchanged, new input
  `HeartbeatMins` 30).
- **VPS:** `push_trade_logs.ps1` now adds a health line (`live/health/YYYYMMDD.csv`: MultiCharts running, free disk, last
  boot, time zone, log rows, push errors) and, on its first run, installs the morning task `VpsHealthOpen` (08:15 CT) by
  itself. Nothing to set up.
- **Check:** the 16:40 CT journal job (`analysis/journal_trades.py` -> `analysis/vps_health.py`) writes a 'Health (auto)'
  section into the day's journal note: MISMATCH (position differs from the broker), STALE (no heartbeat > 70 min in
  RTH), VPS problems. 'All clear' when nothing is wrong.

## Live alarm to your phone (2026-10-21)

`watchdog.ps1` runs every 5 minutes, weekdays 08:15-15:10 CT (task `VpsWatchdog`, installed automatically by the 16:10
push script). It sends a phone alert through the free **ntfy** app the moment: MultiCharts isn't running, it has no live
internet connections (Rithmic / feed down), a chart's heartbeat is > 45 min old, a chart's position differs from the
broker's, or a NEW rejected order appears in MultiCharts' logs (Symbol Mapping hint included). Max one alert an hour per
problem (every new rejection alerts). One-time: install **ntfy** on the phone and subscribe to topic
`apex-alarm-6e531eb6db8e` (keep the name private: anyone with it can read the alerts). Alerts also land in
`C:\TradingLogs\alerts.txt`, in `live/health/` and in the journal's Health section.
