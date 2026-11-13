# Jump Fade and Overnight Bias on other markets (user 2026-11-13: "run jump fade then overnight bias"). Written before any result.
Second and third engine ports after the noise port (F everywhere, checks/candidates/noise_other_markets). Rules = the NQ rules,
no tuning; each generic engine must first reproduce the NQ engine's trades before any other market is run.
Markets: ES YM GC CL ZN 6E NG. Costs: $5 commission ($7.25 NQ) + 1 tick per market / stop fill (target = limit, none). 1 contract,
2018-2026. Point values / ticks as in the noise prereg. Data: unadjusted continuous front month (rolls happen at the 17:00 reopen:
the jump score drops the first bar after a gap; the ATR on roll days is slightly inflated: noted, not corrected).

## A. Jump Fade (analysis/jump_generic.py; NQ rule = analysis/jump_morning_fade.py, MinVolRatio 0, the live version)
5-min bar closing 07:00-09:59 CT with |J| > 3 (J = r / (sig x f), K 276, slot factor 60 sessions) -> fade at the next minute's open;
stop 1.5 x the bar's range (skip if < 8 ticks), target 0.3 x stop, out after 240 min or 15:55 CT; one position at a time.
The SAME clock window on every market (the US morning: 07:30 / 08:30 / 09:00 releases and the cash open), because the NQ window
itself was found post hoc: this port is also the out-of-sample check of that lead (ES / YM are not independent of NQ; GC CL ZN 6E NG are).
Info only (exploratory, 7 x 24 = 168 cells, not a pass route): the same fade by hour of the day per market.

## B. Overnight Bias ADX30 (analysis/onb_generic.py; NQ rule = candidates24.overnight_bias24(adx_min=30, stop_atr=0.25), live on #5)
Overnight range = 15-min bars closing after 23:00 CT through the market's session open t0; bias from the open's position in it (top third
long, bottom third short); stop-order break of the first 15-min bar after t0 (its high for longs / low for shorts), armed at each 15-min
close while ADX(14) > 30; stop 0.25 x ATR15, target 3R; one trade a day; flat at 'flat' (early-close days: last entry 11:00, flat 11:30).
  market  t0     last entry  flat        (t0 / flat as in the noise prereg)
  ES, YM  08:30  14:00       14:30
  GC      07:30  12:00       12:30
  CL, NG  08:00  13:00       13:30
  ZN, 6E  07:30  13:30       14:00
Target fills need 1 tick through (NQ engine: 1 point; the NQ validation run uses 1 point).

## Pass (each engine, per market and side: both / longs / shorts = 21 trials per engine)
avg > 0 after costs, t >= 2.5, positive in BOTH 2018-22 and 2023-26, and a random-side placebo (same entries / days, side by coin,
100 runs) p < 0.05. A pass goes to the eval bench (bench150 LIVE_EVAL) at micro size, then needs a MultiCharts report. Report: by year,
halves, longs / shorts, win rate, PF; the full metric battery only for passes (first-gate rule).

## Result (2026-11-13, `analysis/outputs/jump_onb_other_markets_test_output.txt`): FAIL, both engines, all 7 markets
Engine checks on NQ: Jump Fade 694 / 694 trades identical; Overnight Bias 684 / 684 identical.
A. Jump Fade, per contract after costs (both sides): ES +$22 (t 0.9; 2018-22 -$4, 2023-26 +$59), YM -$3, GC -$78 (t -2.1), CL -$36,
   ZN -$21 (t -3.0), 6E -$18 (t -2.2), NG -$26. Nothing reaches t 2. The NQ morning fade has NO support in the five independent markets
   and only the same weak sign in ES: as an out-of-sample check of the (post-hoc) NQ lead this is negative.
   Exploratory hour table: one cell above its bar (t 3.4 for 168 cells): GC fade, bars closing 10:00-10:59 CT, $139, t 3.8, placebo
   p 0.000. Follow-up (`gc_h10_jump_fade_check_output.txt`): 2026 alone is $24.5k of $36.8k (gold's stops grew ~4x: $930 -> $3,874);
   in risk units t 2.57 (below the bar), 2018-22 t 0.75, ex-2026 t 1.56; hours 9 and 11 are negative. NOT a lead.
B. Overnight Bias ADX30 (both sides): ES +$63 (t 1.6; 2018-22 +$114, 2023-26 -$1), YM +$2, GC -$40, CL -$18, ZN -$44 (t -6.9),
   6E -$36 (t -3.7), NG +$33 (t 1.3; shorts +$65, t 1.75, positive in 9 of 9 years but below every bar; 1 of 21 trials).
