# FINRA short volume (Nasdaq DIX) -> NQ next day (2026-11-08)
 (header committed before the first run;
1 variant). Data: FINRA Reg SHO daily consolidated short-sale volume (cdn.finra.org CNMSshvol, from 2018-08; published the same evening),
filtered to QQQ + 10 Nasdaq-100 mega-caps (AAPL MSFT NVDA AMZN META GOOGL AVGO TSLA COST NFLX) -> data/finra/short_volume.csv.
Mechanism (DIX logic, SqueezeMetrics; tested before on S&P names as 'DIX-high long', C, t 2.1): most off-exchange 'short volume' is
market makers selling short to fill customer BUY orders, so a high short-volume ratio = heavy customer buying absorbed by dealers,
who then buy back -> upward pressure the next day; a low ratio = customer selling. New here: the Nasdaq version, traded on NQ.
Rule: ratio_s = ShortVolume / TotalVolume per symbol and day; R = equal-weight mean over the 11 symbols; Z = (R - mean of the previous
60 days) / sd of the previous 60; Z >= 1 -> long NQ the next trading day, Z <= -1 -> short; enter at the 08:31 open, stop 0.5 x ATR15,
out at the 14:55 close; CME early-close days skipped. NQ, $7.25 + 1 tick per market / stop fill.

