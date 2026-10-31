# Live guard: catching MultiCharts / Rithmic problems before they cost trades (2026-10-29)

The user asked (2026-10-29) for Claude to notice when something is wrong in MultiCharts (a chart or strategy setting, the
Rithmic connection) and fix it by itself. This file states what runs now, what comes next, and the limit on 'fix it by itself'.

## Running now

| Layer | When | What it catches | Where you see it |
|---|---|---|---|
| `watchdog.ps1` on the VPS | every 5 min, 08:15-15:10 CT | MultiCharts not running; MultiCharts with no internet connections (Rithmic / data feed down); a chart's heartbeat > 45 min old (frozen chart / feed); a chart's position differs from the broker's; new rejected orders | ntfy alert on the phone within ~5 min |
| `analysis/vps_health.py` + `live/expected_setup.json` (new) | 16:40 CT job | everything above for the whole day, plus: an expected chart that never heartbeat (closed, logger missing, auto-trading off), an unknown chart tag, a closed account's charts still running, an entry with the wrong size | journal 'Health (auto)', phone push, 'Live guard' panel on the dashboard |

Fixed 2026-10-29: both VPS scripts counted every 'Rejected' line in any MultiCharts log file touched today, including older
days' lines (10/28 reported 3,228; the last one was from 10/26). They now count only lines stamped with today's date. The VPS
picks this up at its next `git pull` (the 16:10 push script pulls first).

First finding of the new check: **account #1's four charts (tags VB / ONB / EOS / MON_BR) were still running on 10/26-10/28**
after the account was blown. VB kept sending orders on 10/27, and they were rejected; the 10/26 log has 3,350 rejection lines.
Turn auto-trading off on those charts or close them.

## Next (needs one step from the user each)

1. **Apex Chart Monitor indicator** (replaces the one-off Apex Account Check). One per live chart, inputs `Tag` and
   `AccountName`. Every 5 minutes it writes a `CFG` row to C:\TradingLogs with the account's NetWorth / Equity
   (`GetRTAccountNetWorth`), whether auto-trading is on, and how old the last tick is. This gives:
   - real Apex balances on the dashboard and for cushion sizing, with no typing;
   - an alarm when auto-trading is off on a chart that should trade;
   - an alarm when the data feed is stale even though MultiCharts is connected.

   Blocked on the Account Check test in TODO.md (does NetWorth come through for each account?). The auto-trading flag
   (`GetAppInfo(aiStrategyAuto)`) must be confirmed when the indicator compiles.
2. **Intraday push**: the watchdog also pushes `alerts.txt` and the day's log to the repo every 30 minutes in RTH. The master
   session can then read a problem during the day, not only at 16:40 (it needs the user to ask, or a check-in).
3. **Missed-trade check**: compare each live entry with the strategy's own backtest signal for that day. This needs fresh
   1-minute data. It runs weekly in the Friday review (`analysis/live_vs_backtest.py`, matched / missed / extra) once the
   weekly MultiCharts reports are in `live/`.

## The limit on fixing things by itself

Claude runs in Anthropic's cloud and cannot click in MultiCharts on the VPS. Remote control of a computer only works for
Mac / Linux folders, and the VPS runs Windows. A VPS script *could* restart MultiCharts or toggle auto-trading. On a live
account that is the wrong trade-off: a restart with auto-trading on can double a position or send stale orders, and
MultiCharts asks for confirmations that should stay human. So the design is:

- **Detect automatically:** the layers above.
- **Diagnose automatically:** the alert names the chart and the likely cause.
- **Give the exact fix:** steps from `MULTICHARTS_PITFALLS.md`.
- **The user clicks.**

Problems that can be fixed safely without touching orders (the push failing, the rejection count, a script bug) Claude
fixes in the repo, and the VPS picks the fix up at its next pull.
