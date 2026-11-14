# EMBIA_V3 (user's paste 2026-11-14: a Jesse crypto strategy, 'Embi/b48 @ Discord'). Written before any result.
Rule as coded: LONG when VWMA5 > VWMA8 > VWMA13 (base tf) AND ADX14 > 28 AND close > VWMA51(1h) AND StochRSI-K(1h) < 90 AND StochRSI-K(base)
< 20 AND VWMA5 > VWMA8 > VWMA13 on 1h; SHORT mirrored (ADX > 28, close < VWMA51(1h), StochRSI-K(1h) > 10, base StochRSI-K > 80).
Stop 2.85 x ATR14 (base), target 3.4 x ATR14, set from the fill; no time exit; one position at a time. (The 5x qty / 6% risk is sizing only.)
Base timeframe is not in the code (Jesse's route sets it): PRIMARY 15 min, SECONDARY 5 min (disclosed). Higher tf = the last COMPLETED
1h bar (a forming-1h version would be no-look-ahead too; the completed one is the conservative choice). StochRSI = RSI14 -> 14-bar
stochastic -> K = SMA3 (Jesse defaults). Signal at a bar's close, market fill at the next minute's open; stop / target on the 1-min path.
Markets: (A) BTC spot (data/BTCUSD_spot_1min, its home market; 24/7; cost 0.05% a side fee + 0.01% slippage), per 1 BTC;
(B) NQ 24h (ours; $7.25 + 1 tick a side), as coded (holds overnight: personal only) and APEX version (no entries 15:00-17:00 CT, flat 15:55).
Report: by year, 2018-22 vs 2023+, longs / shorts, PF, win, t; random-side placebo (same entries); ingredient breakdown (each of the 6
filters removed one at a time, exits fixed); data sweep (analysis/strategy_data_sweep.py) on the NQ trades. Pass: avg > 0, t >= 2.0 in both
2018-22 and 2023+ ... then the eval / personal bench. Expectation: multi-filter indicator stacks like this rarely beat random entries.

## Result (2026-11-14, `analysis/outputs/embia_v3_test_output.txt`, `analysis/outputs/embia_v3_sweep_output.txt`): FAIL
15-min primary, per unit after costs: BTC spot -$24 a trade (t -0.8; 2018-22 +$38, 2023+ -$105; random side p 0.38); NQ as coded +$127 (t 1.3;
2018-22 -$34, 2023+ +$334; random side p 0.075; all from shorts); NQ Apex +$17 (t 0.2). 5-min: BTC -$8, NQ +$38 / Apex +$55 (t <= 1.3).
Ingredients: the two small-timeframe filters (VWMA stack, StochRSI < 20 / > 80) are the only ones that matter; dropping the 1h StochRSI
lifts NQ as coded to +$164 (t 2.66) but 2018-22 is t 0.7 (post hoc, not a pass). Data sweep (NQ as coded): VIX3M z-high regime keeps 66
trade days at $1,279 (fair placebo p 0.02 -> LEAD by the tool's rule) but 2018-22 $158 vs 2023+ $2,158 and ~7 a year: too rare and too
recent to matter for any book; personal-book bench not run here (personal_P.pkl is not in this session).
