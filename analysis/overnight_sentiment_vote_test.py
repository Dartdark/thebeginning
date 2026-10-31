"""Overnight Sentiment Strategy v1 (user's MultiCharts paste, 2026-10-23; Vojtko & Hanicova 2021). Long the 15:00 CT close
(16:00 ET), out at the next 8:30 CT open, when >= 2 of 3 signals are bullish: daily close > 20-day MA, VIX < its 20-day MA,
CNN Fear & Greed > its 20-day MA. We have no Fear & Greed history, so with trend + VIX only '2 of 3' cannot be checked;
shown: each signal alone, both, either. Signals from the PREVIOUS day's daily closes (what a daily data series shows at
15:00 CT in a backtest; VIX closes 15:15 CT) and, as a check, from today's 15:00 price + yesterday's VIX.
Costs per contract round trip as in analysis/overnight_round.py (ES $35, NQ $24.50); roll-week nights left out.
  python3 analysis/overnight_sentiment_vote_test.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import overnight_round as O
from grid24 import jof

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE
    vix_ok = (vix < vix.rolling(20).mean())
    for sym in ("ES", "NQ"):
        g = O.load(sym); _, pv, cost = O.MK[sym]; tr = g.trading
        cf = pd.Series(g.c.ravel()).ffill().to_numpy(); dts = pd.DatetimeIndex(g.ts[tr]).normalize()
        c15 = pd.Series(cf[tr * 1440 + jof(1500)], index=dts); o830 = g.o[tr, jof(831)]
        night = pd.Series(np.r_[(o830[1:] - c15.values[:-1]) * pv - cost, np.nan], index=dts)
        trend_today = c15 > c15.rolling(20).mean()
        trend_prev = trend_today.shift(1).fillna(False).astype(bool)
        v_prev = vix_ok.shift(1).reindex(dts, method="ffill").fillna(False).astype(bool)
        rollwk = np.isin(dts.month, (3, 6, 9, 12)) & (dts.day >= 8) & (dts.day <= 17)
        ok = (~rollwk) & night.notna().values & (dts >= "2018-01-01")
        print(f"\n {sym}: per contract after costs, 15:00 CT -> next 8:30 CT")
        O.stats(night[ok], dts[ok], "every night")
        for nm, m in (("trend up (prev day)", trend_prev), ("VIX < MA (prev day)", v_prev), ("both (= 2 of 3 w/o F&G)", trend_prev & v_prev),
                      ("either", trend_prev | v_prev), ("neither (fear)", ~trend_prev & ~v_prev), ("trend up (today 15:00)", trend_today),
                      ("both, trend today", trend_today & v_prev)):
            mm = ok & m.values; O.stats(night[mm], dts[mm], nm)
