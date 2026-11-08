# Lab Q009: NG drift before the EIA storage report (pre-registered 2026-11-01, before any return; parent Q007)

**Mechanism.** Pre-announcement drift / event-risk premium (cf. Lucca & Moench 2015 pre-FOMC drift): traders who must be
hedged or flat into the Thursday 09:30 CT storage number (utilities, weather funds cutting risk) trade before it, so NG
drifts in a consistent direction 08:00 -> 09:29 CT on release days. Q007 traded the reaction; this trades the run-up.

**Release days.** As Q007 (`analysis/lab_Q007.release_rows`: the 09:31 bar volume >= 3x the 09:16-09:30 median, Thursday
first, else Wed / Fri of that week). Volume only, never returns.

**Rule (1 NG, $10,000 a point, tick 0.001 = $10).** Entry at the open of bar 0801 (08:00 CT). Stop 0.3 x `daily_atr(14)`
from the entry, checked on bars 0801..0929, filled at the stop (or the bar open if it gaps through) 1 tick worse. Else exit
at the close of bar 0929.
- V1 long. V2 short.
- V3 follow the overnight: side = sign(close(0759) - open of the 17:01 bar of the previous evening session); skip if 0.

**Costs.** $5 + 1 tick per fill = $25 a round trip.

**Gates.** Stage 1 (2018-22): best t >= 2.0, PF >= 1.15, >= 40 trades. Stage 2: same variant on random non-release
weekdays (same count, 500 draws) p < 0.05, >= 4 of 5 years positive. Stage 3 one look 2023-onward: same sign, t >= 1.5,
PF >= 1.1. t bar `lab_tools.bar()` 3.64; pre-registered mechanism, 3 variants -> full-sample t >= 2.0 + clean placebo.
Apex: yes (QG / NG).
