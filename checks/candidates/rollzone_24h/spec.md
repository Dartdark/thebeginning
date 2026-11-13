# RollZone 24h NQ Long v1 (RZL1): spec as tested

Source: user upload 2026-10-31, PowerLanguage signal `RollZone 24h NQ Long v1` plus an 11-page research note ("RollZone 24h,
research note v1.0", based on Zarattini, Aziz and Barbon 2024, SSRN 4824172, "noise area"). The code was reviewed in
`agents/cross_review/CODE_REVIEW_LOG.md` (2026-10-31, entry 4). Python port: `analysis/rollzone_24h_test.py`. Benches:
`analysis/rollzone_bench.py`.

## Rule
- **Chart:** NQ, 5-minute bars stamped at their close, 24h Globex session from 17:00 CT (the first bar reads 17:05).
  Long only, one position.
- **DailyATR:** the average high-low of the last 30 completed Globex sessions.
- **Noise width per 15-minute slot:** the average |slot close - session open| over the last 14 sessions in which that
  slot existed.
- **Zone:** centre = the session open; half-width = 0.75 x the slot's noise width x WFac (WFac starts each session at 1).
  A 5-minute close beyond a line by more than 0.05 x DailyATR moves the centre to that close and sets
  WFac = 1 + break / DailyATR, clamped to 0.5-3.0.
- **Entry:** a buy stop at the next bar's upper line, placed only after a bar whose high stayed below that line.
  - The fill bar must end between 17:00 and 15:30 CT.
  - No entries from 01:00 to 07:00 or from 08:30 to 09:00.
  - Half days: no entries from 11:30.
  - No entry if the fill bar would end within one bar of the 15:58 flat.
  - Good Friday: no entries in the Good Friday session (the review's fix; the uploaded code has no guard).
- **Exits:**
  - Target 1.40 x DailyATR; stop 0.80 x DailyATR, cut to what is left of the session's loss budget (DailyLossCap plus
    the session's closed P&L). No entries once the budget is used up.
  - Time exits at the next bar's open, at market: night 08:25 CT, day 15:55, half days 11:55, carry at the next
    session's first bar.
- **Two budget versions:**
  - **NQCAP:** the note's tested run, $1,500 on 1 NQ = 75 points per contract (on MNQ that is $150 per micro). The
    budget sets most stops.
  - **ATR:** the default $1,500 on 1 MNQ = 750 points, never binding, so the stop is the plain 0.8 x DailyATR. Above
    2 MNQ the cap would bind again, so this version scales only at 1 MNQ.

## Test conventions
- **Data:** Grid24 (`data/NQ_1min_*.csv` + `NQ_1min_ON_*.csv`). The overnight files start 2017-12, so results are
  reported from 2018-01-01.
- **Bar magnifier:** 1-minute fills.
  - The entry stop fills at max(minute open, line).
  - The stop fills at min(minute open, stop). It is checked first in a minute, and also on the entry minute.
  - The target needs 1 tick through.
- **Costs:** $7.25 per NQ plus 1 tick per stop or market fill (the entry stop, the protective stop and time exits).
- **Rolls:** trades whose entry-to-exit window contains a roll bar are dropped (rolls as
  `s_rank_gap_round2_test.rolls_index`; 7 trades).
- **Apex trading date:** a fill after 17:00 belongs to the next weekday session.
- **Placebo:** market entries at random allowed bars, with the same windows, budget and exits (20 seeds).

## Parity with the note
Trades per year match the note within ±2% (2018 399 vs 392, 2019 341 vs 344, 2023 326 vs 327, 2025 282 vs 282), and the
median hold is 521 vs 520 minutes. Gross P&L per year differs:

| Year | Ours (NQCAP gross) | Note |
|---|---:|---:|
| 2018 | -$10.2k | -$6.2k |
| 2020 | +$32.0k | +$58.3k |
| 2022 | -$36.3k | +$12.9k |
| 2024 | +$116.7k | +$103.3k |
| 2026 | -$15.5k | +$11.1k |

The likely causes are the data feed (the note: `@NQ#C`, the Bridge's bars; ours: dxFeed front month) and fill details.
The author's MultiCharts trade list is needed for a trade-for-trade check.
