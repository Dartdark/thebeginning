# Breakout regime: follow when hot, fade when cold (user 2026-11-12: "use the current market conditions ... see what market IS doing
# instead and build something around that"). Written before any result of this test.
Motivation (vb_drawdown_diag): after VB's breakout entries the move to 14:30 averaged +0.037 ATR (2018-24) but -0.060 since Aug 2026.
Building on Aug-Nov 2026 alone = fitting ~60 trades; so the testable question is a REGIME rule over all of 2018-26:
does the recent post-breakout drift predict the next one?

Signals: VB v1 entries (vault_break_v8_test.run(g, "v1"), unchanged). drift = (14:30 close - entry fill) / ATR15.
State S = mean drift of the previous 60 VB signals on EARLIER dates (known before today's open). Warm-up: first 60 signals dropped.
D0 (descriptive): path after entry at +30 / +60 / +120 min and 14:30 (ATR units), 2018-24 vs since 2026-08; share that trade back
   to the noise level and to VWAP before 14:30.
H1 (persistence): corr(S, next drift) (Spearman), and mean drift when S < 0 vs S >= 0, 2018-22 and 2023-26 separately.
Variants (4), per NQ, $7.25 + 1 tick a market / stop fill:
  A  FADE WHEN COLD: S < 0 -> short at VB's entry minute (open - 1 tick), mirrored bracket target 40 / stop 75 points, out 14:30.
  B  VB WHEN HOT (= the watch rule as a filter): VB's own trade only when S >= 0.
  C  SWITCH: B + A.
  D  MARKET-WIDE: every weekday, morning move m = (10:00 close - 08:31 open) / ATR15; |m| >= 0.3 -> trade 10:01 open -> 14:30 close
     in m's direction if the trailing 60-day corr(morning, 10:00->14:30) >= 0, against it if < 0; stop 0.3 ATR.
Pass for A and D: avg > 0 with t >= 2.0 over 2018-26 AND positive in both 2018-22 and 2023-26, AND beats a random-side placebo
(same entries, side by coin, 200 runs) at p < 0.05. B passes if it beats VB-always in avg R in both periods.
Not Apex-tested yet: a pass goes to a book bench (bench150 LIVE_EVAL) before anything else.
