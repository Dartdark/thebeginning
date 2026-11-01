# Lab Q013: 6E after US payrolls (pre-registered 2026-11-01, before any return)

**Mechanism.** NFP (07:30 CT) reprices the dollar; FX order flow after macro news keeps moving the price as real-money
accounts reposition (Evans & Lyons 2008), and European hedgers act after their lunch, before the 10:00 CT London fix. If
slow repositioning dominates, the first 15 minutes' move continues (V1, V3); if the first reaction overshoots, it reverses (V2).

**NFP days (volume only, as the repo's GC / NQ tests).** Fridays with day of month <= 10 whose 6E 07:30-07:31 bar (stamp
0731) has volume >= 5x the median of stamps 0716-0730.

**Rule (1 6E, $125,000 a point, tick 0.00005 = $6.25).** move = close(0745) - close(0730). Entry at the open of stamp 0747
(07:46). Stop 0.3 x `daily_atr(14)` from the entry, checked each bar to stamp 0955, filled at the stop (or the bar open if it
gaps) 1 tick worse; else exit at the close of stamp 0955.
- V1 follow: side = sign(move). V2 fade: side = -sign(move). V3: V1 only when |move| >= 0.3 ATR.

**Costs.** $5 + 1 tick per fill = $17.50 a round trip.

**Gates.** Stage 1 (2018-22): best t >= 2.0, PF >= 1.15, >= 40 trades. Stage 2: the same variant at the same clock on
random non-NFP Fridays (same count, 500 draws) p < 0.05; >= 4 of 5 years positive. Stage 3 one look on 2023-onward: same
sign, t >= 1.5, PF >= 1.1. t bar `lab_tools.bar()` 3.65 (N 376); pre-registered mechanism, 3 variants -> full-sample
t >= 2.0 + clean placebo. Power: ~12 a year, ~60 in 2018-22 (V3 fewer). Apex: yes (6E / M6E).
