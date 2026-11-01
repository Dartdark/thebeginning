# Lab Q007: NG EIA storage-report first-5-minute fade / follow (pre-registered 2026-10-31, before any return)

**Mechanism.** EIA Weekly Natural Gas Storage Report, Thursday 10:30 ET = 09:30 CT (moves to Wed/Fri in holiday weeks).
Headline-reading algos move NG on injection/withdrawal vs consensus in the first minutes; weather-driven hedgers and
utilities trade after. If the first move overshoots, fading it pays (V1); if the details confirm, following pays (V2).

**Data.** `data/NG_1min_2017..2026.csv` (CT, bar-end stamps: bar 0931 covers 09:30-09:31). NG $10,000 a point,
tick 0.001 = $10. Grid24(night_pattern="").

**Release days (volume only, never returns).** Per week: Thursday if it is a session and its 09:31 bar volume is >= 3x the
median volume of its 09:16-09:30 bars. Otherwise the Wednesday or Friday of that week whose 09:31 ratio is >= 3x
(highest if both). Otherwise the week has no event (e.g. an 11:00 CT holiday release is skipped).

**Rule.** move = close(0935) - close(0930). ATR = `Grid24.daily_atr(14)` known on the day. Trade if |move| >= 0.15 ATR.
Entry at the open of the 09:36-09:37 bar (stamp 0937). Stop 0.3 ATR from the entry, checked on bars 0937..1030; fill at
the stop (or the bar open if it gaps through) - 1 tick against us. Otherwise exit at the 10:30 close (bar 1030).
- V1 fade: side = -sign(move).
- V2 follow: side = +sign(move).
- V3: V1 only in Nov-Mar (heating season).

**Costs.** $5 commission + 1 tick ($10) per fill = $25 a round trip per NG (stop fills: the 1 tick is that fill's tick).

**Gates (lab/README.md).** Stage 1 (2018-22): best variant t >= 2.0, PF >= 1.15, >= 40 trades (event study).
Stage 2: placebo = the same variant at 09:30 on random non-release weekdays (same count as release days, 500 draws),
p < 0.05; >= 4 of 5 years positive. Stage 3 (one look, 2023-onward): same sign, t >= 1.5, PF >= 1.1.
t bar: `lab_tools.bar()` = 3.63 (N 357); this is pre-registered from a stated mechanism with 3 variants, so the full-sample
bar is t >= 2.0 with a clean placebo. Best variant = highest stage-1 t; only it goes on.
Apex: yes (QG / NG; micro MNG listing to confirm). Results reported per 1 NG.
