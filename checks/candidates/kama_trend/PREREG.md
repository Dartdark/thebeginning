# KAMA_TrendFollowing (user's paste 2026-11-14, Jesse crypto strategy). Written before any result.
Rule as coded: LONG when close > KAMA (base tf) AND ADX14 > 50 AND close > KAMA(4h) AND Choppiness14 < 50 AND Bollinger width (20, 2:
(upper - lower) / middle) x 100 < 7 AND >= 10 base bars since the last position closed; SHORT mirrored (close < KAMA, < KAMA(4h)). Stop and
target both 2.5 x ATR14 (base) from the fill; no time exit; one position at a time. KAMA = Jesse default (10-bar efficiency ratio, fast 2,
slow 30). (3% risk x3 qty = sizing only.)
Base tf not in the code: PRIMARY 1h (the code's 4h higher tf implies a base below 4h), SECONDARY 15 min (disclosed). Higher tf = last
COMPLETED 4h bar. Signal at a bar's close, fill at the next minute's open, stop / target on the 1-min path.
Markets / costs as EMBIA_V3 (checks/candidates/embia_v3/PREREG.md): BTC spot (0.06% a side), NQ as coded (holds overnight) and NQ Apex
(no entries 15:00-17:00 CT, flat 15:55). Report: by year, halves, sides, random-side placebo, ingredient breakdown (each of the 6 conditions
removed in turn), data sweep on the NQ trades. Pass: avg > 0 and t >= 2.0 in both 2018-22 and 2023+, placebo p < 0.05.

## Result (2026-11-14, `analysis/outputs/kama_trend_test_output.txt`, `analysis/outputs/kama_trend_sweep_output.txt`): FAIL everywhere
1h primary, after costs: BTC spot -$31 a trade (t -0.4; 2023+ -$125; random side p 0.38); NQ as coded -$91 (t -0.4; 2018-22 -$381);
NQ Apex -$314 (t -1.7; 2018-22 t -3.0; random side p 0.98). 15 min: BTC +$2, NQ +$44 / Apex -$34. Ingredients: ADX > 50 is the only
condition that matters (without it 10x the trades and worse); dropping the cooldown / BB width / chop filters helps BTC slightly (t <= 1).
Data sweep (NQ): best version p 0.77 vs the fair placebo: luck. No lead.
