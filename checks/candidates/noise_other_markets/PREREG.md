# Noise-area momentum on other markets (user 2026-11-13: "search for edges in other markets"). Written before any result.
Why this engine: it is the best-verified NQ intraday edge we have (MC-confirmed, t 5.4 longs), and the published source
(Zarattini, Aziz & Barbon) is a general intraday-momentum mechanism, so it is the fair first port. Other markets already have
100+ tier-list rows, mostly C/D: this round only ports what works on NQ, rules fixed here, no tuning.

Engine: analysis/noise_generic.py = the bridge_noise_15m_test.run logic with the session as inputs (bar-for-bar the same on NQ:
checked against the NQ engine before any other market is run). Per market, 15-min bars on the 24h grid, RTH-anchored:
  market  open bar (anchor = its open)  first decision  last entry  flat     PV      tick      commission
  ES      08:30                         09:00           14:00       14:30    50      0.25      $5
  YM      08:30                         09:00           14:00       14:30    5       1         $5
  GC      07:30 (pit 07:20)             08:00           12:00       12:30    100     0.10      $5
  CL      08:00                         08:30           13:00       13:30    1000    0.01      $5
  ZN      07:30 (pit 07:20)             08:00           13:30       14:00    1000    1/64      $5
  6E      07:30 (pit 07:20)             08:00           13:30       14:00    125000  0.00005   $5
  NG      08:00                         08:30           13:00       13:30    10000   0.001     $5
Rules as NQ: look 20, band x 1.0, EMA 20, target = 0.5 x stop, max 10 entries / 3 stops a day, reversals, flat at 'flat'.
Stop: NQ's 50 points was 0.20 of NQ's median 15-day ATR in 2018-24, so stop = 0.20 x the market's 15-day ATR (known at the open).
Costs: commission + 1 tick per market / stop fill (target = limit, no slip). 1 contract, 2018-2026.
Report per market: both sides, longs, shorts; by year; 2018-22 vs 2023+; random-side placebo (200 runs, same entries).
Pass (per market and side): avg > 0, t >= 2.5 (7 markets x 3 sides = 21 trials), positive in BOTH halves, placebo p < 0.05.
A pass goes to the eval bench (bench150 LIVE_EVAL) as an addition at micro size, then needs a MultiCharts report.
