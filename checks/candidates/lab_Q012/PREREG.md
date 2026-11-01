# Lab Q012: 6E after the ECB policy decision and press conference (pre-registered 2026-11-01, before any return)

**Mechanism.** FX order flow after scheduled macro news keeps moving the price for hours as real-money accounts
reposition (Evans & Lyons 2008). The ECB headline (decision) is mostly priced at once; the press conference carries the
guidance. If repositioning is slow, the decision -> press-conference-end move continues into the late morning (V1, V3); if
the first reaction overshoots, it reverses (V2).

**ECB days (volume only).** Thursdays. Candidate decision minutes T0 = 13:45 and 14:15 Europe/Berlin (converted to CT per
date). ratio = volume of the bar covering T0 .. T0+1 / median volume of the 15 bars before T0. ECB day if the larger ratio
is >= 5; T0 = that candidate.

**Rule (1 6E, $125,000 a point, tick 0.00005 = $6.25).** move = close(bar ending T0+90) - close(bar ending T0).
Entry at the open of the bar covering T0+91 .. T0+92. Stop 0.3 x `daily_atr(14)` from the entry, checked on each bar to
10:30 CT, filled at the stop (or the bar open if it gaps) 1 tick worse; else exit at the close of the 10:30 CT bar.
- V1 follow: side = sign(move). V2 fade: side = -sign(move).
- V3 follow the press-conference part only: side = sign(close(T0+90) - close(T0+30)).
Skip if the side is 0.

**Costs.** $5 + 1 tick per fill = $17.50 a round trip.

**Gates.** Stage 1 (2018-22): best t >= 2.0, PF >= 1.15, >= 40 trades (event study). Stage 2: the same variant at the same
CT clock on random non-ECB Thursdays (same count, 500 draws), p < 0.05; >= 4 of 5 years positive. Stage 3 one look on
2023-onward: same sign, t >= 1.5, PF >= 1.1. t bar `lab_tools.bar()` 3.64 (N 371); pre-registered mechanism with 3 variants
-> full-sample t >= 2.0 + clean placebo. Apex: yes (6E / M6E).
