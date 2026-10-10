# NQ VWAP Momentum — Final Version v3

Saved 2026-10-10. MultiCharts name: **NQ VWAP Fuck Em v3**.

## Files

| File | What it is | MultiCharts type |
|---|---|---|
| `NQ_VWAP_Momentum_v3_FINAL.txt` | The strategy, with the final settings as defaults | Signal |
| `NQ_VWAP_15m_Anchored.txt` | VWAP line the strategy trades on (8:30 CT anchor, 15-min) | Indicator |
| `NQ_Filter_Status.txt` | 10-day average range; green = OK to start a challenge | Indicator |

## Strategy rules

**Long setup:** close above VWAP, VWAP rising over the last 15 minutes, price up at least 0.1% over the last hour, and the close at least 0.35% above VWAP.
**Short setup:** the mirror image.
**Trigger:** first red candle of a pullback (longs) / first green candle of a bounce (shorts). Enter at the open of the next 5-minute bar.
**Exits:** 80-point stop; 40-point target on longs, 50-point target on shorts.
**Guardrails:** one position at a time, max 4 trades and max 2 losses a day, no entries before 9:00 CT or from 14:30 CT, flat at 14:55 CT. On CME holiday half-days, no entries from 11:00 CT and flat at 11:45 CT.
In backtests MultiCharts never entered before 9:50 CT even though entries are allowed from 9:00; the cause is unknown, and the results below include it.

## Final settings

| Setting | Value |
|---|---|
| AnchorTime / VwapBarMins | 830 / 15 |
| MomentumMins / MinChangePct | 60 / 0.1 |
| StopPts / LongTargetPts / ShortTargetPts | 80 / 40 / 50 |
| UsePctExits | false |
| BreakevenPts / BreakevenPct | 0 / 0 |
| NoTradeUntil / LastEntryTime / FlattenTime | 900 / 1430 / 1455 |
| UseHolidayTimes / EarlyLastEntry / EarlyFlattenTime | true / 1100 / 1145 |
| TradeLongs / TradeShorts | true / true |
| MaxTradeMins | 0 |
| **MinVwapDistPct** | **0.35** |
| **MinAvgRangePct** | **0** |
| RangeDays / SessionEnd | 10 / 1515 |
| MaxTradesPerDay / MaxLossesPerDay | 4 / 2 |
| NumContracts | 1 for NQ backtests; **10 live on MNQ** |

Chart: 5-minute NQ/MNQ, Exchange time zone (Central).
Backtest properties: no commission or slippage in MultiCharts (costs of $7.25 per NQ round trip are added in the analysis), limit fills only when price exceeds the target by 1 point, Bar Magnifier on at 1 minute.

## Prop challenge plan (Apex 50K, 21 trading days, $2,000 trailing drawdown, $1,000 daily limit)

1. Trade **10 MNQ**. One stop-out is about $800.
2. **Only start a challenge when the Filter Status line has been green for at least 2–3 days in a row.** Starting on the first green day passed only about 25% of the time; about 30% of green stretches last 3 days or less.
3. Follow every signal, same size every trade.
4. If 3 attempts fail in a row, stop and compare live trades with the backtest before buying more.

## Backtest results (2 Jan 2018 – 9 Oct 2026, 1 NQ, after costs)

| | 2018–2023 | 2024–2026 | All |
|---|---|---|---|
| Trades | 2,360 | 1,137 | 3,497 (2.2 per day) |
| Win rate | 62.4% | 63.2% | 62.7% |
| Average trade | $73 | $36 | $61 |
| Profit factor | 1.17 | 1.07 | 1.14 |

Average trade per year: 2018 $110, 2019 −$22, 2020 $70, 2021 $119, 2022 $85, 2023 $35, 2024 $19, 2025 $26, 2026 $66.

**Apex 50K pass rate**, with challenges started on real days and run on the real days that followed:

| Start rule | 10 MNQ | Median days to pass |
|---|---|---|
| Start any day | 33% | 4 |
| Start while the filter line is green | 40% | 4 |
| Green for 6+ days | 41% | 4 |
| Starts in 2024–2026, line green | 45% | 3 |

Expected: about 2.5 accounts per pass (about $125 at $50 an account). Plan for about 35% live, i.e. 3–5 accounts per pass.

## Caveats

- The edge is thin: the pass rate is only a few points above a version with no edge, and timing the start drives most of the gain.
- Neighbouring start days share most of the same days, so pass rates are estimates, not precise figures.
- Live results are usually a bit worse than backtests (stop slippage, news days).
- Once funded, the goal changes to steady payouts; size down and re-run the funded-phase analysis.
