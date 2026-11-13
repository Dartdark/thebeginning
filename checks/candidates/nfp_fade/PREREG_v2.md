# NFP Fade: can the 5-minute fade (samuel.nys, 2026-11-13) improve ours? Written before any result. User 2026-11-13.
Base = our live NFP Fade (fade the 07:30->07:45 CT reaction, 07:46 -> 09:00, stop 0.5 x ATR15). His rule = fade 07:30->07:35, 07:36 -> 08:30,
no stop ($306 a trade, t 2.34 on our data). Same NFP days (spike proxy), per NQ, our costs. Already known (ingredient_ablation4): our rule
with his 07:35 reaction $236, with his 08:30 exit $155 (both worse): not retested.
Variants (2, fixed here):
  V1 AGREE: our trade only when the 07:30->07:35 and 07:30->07:45 moves have the same sign (both say 'fade the same way'); else no trade.
  V2 TWO LEGS: half size in his leg (07:36 -> 08:30, no stop) + half size in ours (07:46 -> 09:00, stop 0.5 ATR), each leg on its own day signal.
Judge: 2023-26 avg AND t vs the base on the same days (design 2018-22 shown too); a variant replaces the base only if it beats it in BOTH
periods and on Sharpe / max DD. 78 days total: any difference under ~$150 a trade is noise.
