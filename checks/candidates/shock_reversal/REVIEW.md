# ORB + Shock Reversal (L. Franceschetti research note, 22.09.2026; uploaded 2026-10-24)

`ORB_Shock_Reversal_note.pdf`. An afternoon contrarian module added to their ORB (= the OB v2 / Block A family:
close-confirmed 08:30 ORB in the overnight direction with a volatility regime filter).

## What the note says
- Shock = a 30-min move that is unusually large against the same time slot over the 60 prior sessions. Down shock and
  price above the RTH VWAP → long; up shock below VWAP → short. Entries 13:00-14:00 CT, next-bar open, one a day, after any
  ORB trade; 8-bar cap, so out at the 15:00 CT close. ADX + ATR filters, a module stop and target: **thresholds withheld**.
- Mechanism cited: Zawadowski, Andor & Kertész (2006), partial reversal after extreme intraday moves in liquid stocks.
- Selection: 100,000 configurations on 2017-24 (ORB frozen); the IS bootstrap gate **failed**; one OOS look at 2025-26
  was then allowed, on years the author had already seen.
- Added module: IS 290 trades, $106, PF 1.29; OOS 83 trades, $115, PF 1.21 (2026: $70). 95% bootstrap interval of its
  average includes zero in both IS (-$21 / $228) and OOS (-$119 / $358). Combined OOS max DD +47%.
- Their ORB alone: IS PF 1.46 ($209), OOS 2025-26 PF 1.12 ($88): it decayed.
- Costs: $4 a round trip, zero slippage in the tables (two ticks only in a stress line).

## Our proxy test (`analysis/shock_reversal_test.py`, pre-registered, 3 variants, per NQ, $7.25 + 1 tick per fill)
| shock threshold | trades | avg | PF | t | 2018-22 | 2023-26 | random side beaten by |
|---|---|---|---|---|---|---|---|
| z 2.0 | 113 | $312 | 1.45 | 1.3 | $194 | $460 | 10% |
| z 2.5 | 55 | $686 | 2.15 | 1.7 | $507 | $918 | 3.6% |
| z 3.0 | 22 | $410 | 1.58 | 0.7 | $644 | -$214 | 25% |

- The sign is right: following the shock loses (z 2.5 -$721). Without the VWAP condition the reversal is ~$0 (z 2.5 $54,
  t 0.3): the VWAP side does the work, not the shock.
- Daily Sharpe 0.43 / 0.58 / 0.23; DSR at 288 items 0.04 / 0.08 / 0.01. Longs and shorts each t ≤ 1.4.
- Post-hoc: at their trade frequency (z 1.5, 25 a year) $137, t 0.9, 2018-22 -$39. Every day 'VWAP side at 12:45 → 15:00'
  $82, t 2.3, but 2023+ -$6 (an afternoon trend effect that faded).

## Verdict: D
Proxy only, since the thresholds are withheld; nothing reaches t 2, and at the author's frequency there is no edge. The
author's own evidence agrees (bootstrap intervals include zero, IS gate failed, 100,000 configurations). Retest only if
the PowerLanguage code arrives (exact rule, MultiCharts report): then parity first, one pre-registered run.
