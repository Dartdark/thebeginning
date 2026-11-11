# 5-minute jump follow (user upload 2026-11-11: pino1 screenshot + Joulin 2008, Marcaccioli 2022, Bouchaud 2004)

Written 2026-11-11 after the design-period (2018-22) exploration and BEFORE any 2023+ result was seen. Not a clean
pre-registration: about 250 design configurations were looked at first (follow / fade, two jump scores, thresholds 3-8,
two stop definitions, sessions, 0.3R / 1R / no target, 30 / 60 / 240 min), so the design t-values are selected. The
holdout look below is the evidence. Independent prior: Headline Shock Follow (TIER_LIST, 2026-10-12) found the same
continuation with a different score.

- **Mechanism (who pays):** information. A 5-minute move several times its normal size for that time of day is mostly a
  reaction to news / a liquidity gap (Joulin 2008); slow traders and stopped-out positions keep trading the same way for
  the next half hour, so the move continues. Marcaccioli 2022 gives the score; Bouchaud 2004 says the impact part decays,
  which is why fades were also tested (they lose).
- **Score:** J = r / (sigma x f), r = 5-min close-to-close move, sigma = bipower volatility of the previous 276 bars,
  f = trailing 60-session mean of |r|/sigma for the same 5-minute slot. All from earlier bars only.
- **Rule:** when a bar closes with |J| > 3 during 08:30-15:00 CT, enter in the bar's direction at the next minute's open
  (market). R = the jump bar's high - low. Stop R against. Out at the exit below or 15:55 CT. One trade at a time.
- **Variants (4, fixed):**
  - P1 target 1.0R, time exit 30 min (design: 746 trades, net $107, PF 1.41, t 3.39)
  - P2 no target, time exit 30 min (design: 681, $115, PF 1.44, t 3.07)
  - P3 the screenshot's shape: target 0.3R, time exit 240 min (design: 828, win 80.4%, $18, PF 1.09, t 0.74)
  - P4 overnight (not 08:30-15:00), Joulin score s > 6 (|r| > 6 x mean |r| of the last 24 bars), no target, 30 min
    (design: 1130, $47, PF 1.35, t 2.82)
- **Costs:** $7.25 a contract + 1 tick ($5) on every market / stop fill; fills walked on 1-minute bars, stop before
  target inside a minute.
- **Pass bars (holdout 2023-01 .. 2026-11, one look):** same sign, t >= 1.5, PF >= 1.1; then full-sample t against
  `metrics.t_threshold(N)`. Placebo on design: random minute of the same session window, direction = the last 5-min move,
  same exits; candidate must beat it (p < 0.05).
