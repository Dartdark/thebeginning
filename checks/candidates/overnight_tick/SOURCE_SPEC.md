# User's specification (pasted 2026-10-24, with three screenshots: MC equity curve, Monte Carlo paths, performance summary)

NQ Overnight Anomaly Strategy Optimized. IS 2017-05-21 .. 2024-02-12, OOS 2024-02-13 .. 2026-07-09.
Long-only NQ overnight; Data1 NQ 5-min 24h Globex, chart Eastern time, UpTicks / DownTicks, IOG off; Data2 VIX daily.
Entry decision 18:00 ET (normally the 18:05 bar), exit 04:00 ET, 1 NQ, no stop / target.
Prior RTH 09:30-16:00 ET close < open (mandatory). Early close: last RTH bar before 15:00 ET -> no trade.
TickRSV = (UpTicks - DownTicks) / (UpTicks + DownTicks) over 15:15-16:15 ET; threshold 0; no observations -> no entry.
VIX regime: latest completed daily VIX close vs SMA of the last L closes (code default 20; 25 tested best).
Entry: (TickRSV < 0 AND VIX > MA) OR (TickRSV >= 0 AND VIX <= MA).
Optional disaster stop (off): entry - 3 x average range of the last 20 overnight sessions.
Reported (screenshots): 547 trades, all long, net $211,405, PF 2.01, 59.96% win, max strategy drawdown -$16,515,
period 9/12/2017 - 7/7/2026. Author's notes: 2017-2019 Q2 stagnant; volatility targeting and stop losses did not help.
