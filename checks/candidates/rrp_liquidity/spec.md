# RRP liquidity -> NQ next day (2026-11-08)
 d5 = RRP today - RRP 5 operation days earlier ($bn); Z = d5 / sd of d5 over the previous 60 days; only days with RRP > $50bn
(otherwise there is no facility to drain); month-end windows excluded (last 2 and first 2 business days of each month: bank window
dressing, mechanical); Z <= -1 (cash leaving) -> long NQ the next trading day 08:31 -> 14:55, Z >= 1 -> short; stop 0.5 x ATR15;
early-close days skipped; $7.25 + 1 tick per fill.

