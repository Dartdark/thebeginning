"""Mega-cap earnings, intraday shape on NQ (follow-up to analysis/megacap_earnings_nq_test.py), 2018-2026, 1 NQ, $17.25.

Pre-specified (2026-10-14, before looking):
  a  run-up into after-close reports: report day D (post-market, six largest names: weight >= 4), long 13:00 -> 15:00 and
     8:30 -> 15:00 (placebo: the same windows on non-event days)
  b  event session T: the first 30 minutes (8:30 -> 9:00) followed / faded 9:00 -> 15:00 (placebo: other days)
  c  dealer gamma (GEX_1min_<year>.csv, 2022-26, 8:31 CT row: close vs flip): on T, fade the 15:00 -> 8:30 earnings-night
     move R when NQ is above the gamma flip (positive gamma = dampening), follow it when below (negative gamma)
  python3 analysis/megacap_earnings_intraday_test.py [SCRATCH_DIR]
"""
import sys, glob, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import line

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, COST = 20.0, 7.25 + 2 * 0.25 * 20
WT = {"NVDA": 9, "MSFT": 8, "AAPL": 8, "AMZN": 6, "GOOGL": 5, "AVGO": 5, "META": 4, "TSLA": 3, "AMD": 1, "PLTR": 1}

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); tr = g.trading; days = pd.DatetimeIndex(g.ts[tr])
    px = lambda hh: cf[tr * 1440 + jof(hh)]
    P = pd.DataFrame({h: px(h) for h in (830, 900, 1300, 1500)}, index=days)
    P["prev1500"] = P[1500].shift(1); P = P[P.index >= "2018-01-01"]
    P["R"] = np.log(P[830] / P.prev1500)
    E = pd.read_csv("data/ndx_megacap_earnings.csv"); E["d"] = pd.to_datetime(E.reportedDate)
    E = E[(E.d >= "2017-12-15") & E.ticker.isin(WT)]; E["w"] = E.ticker.map(WT)
    idx = P.index
    D_post = pd.DatetimeIndex(E[(E.reportTime == "post-market") & (E.w >= 4)].d.unique()).intersection(idx)
    def sess(r):
        k = idx.searchsorted(r.d) if r.reportTime == "pre-market" else idx.searchsorted(r.d, side="right")
        return idx[k] if k < len(idx) else pd.NaT
    E["sess"] = E.apply(sess, axis=1); T = pd.DatetimeIndex(E.dropna(subset=["sess"])["sess"].unique())
    isD = pd.Series(idx.isin(D_post), index=idx); isT = pd.Series(idx.isin(T), index=idx)
    print(f"report days (post-market, six largest) {isD.sum()}; event sessions {isT.sum()}")
    print("\na. run-up into after-close reports (long)")
    for a, b_ in ((1300, 1500), (830, 1500)):
        x = (P[b_] - P[a]) * PV - COST
        print(line(x[isD], f"report day {a}-{b_}", 34)); print(line(x[~isD & ~isT], f"other days {a}-{b_} (placebo)", 34))
    print("\nb. event session: first 30 min (8:30-9:00) followed 9:00-15:00")
    s = np.sign(P[900] - P[830]); y = s * (P[1500] - P[900]) * PV - COST; yf = -s * (P[1500] - P[900]) * PV - COST
    print(line(y[isT], "follow, event sessions", 34)); print(line(y[~isT], "follow, other days", 34))
    print(line(yf[isT], "fade, event sessions", 34)); print(line(yf[~isT], "fade, other days", 34))
    print("\nc. gamma rule on event sessions (2022-26): fade R above the flip, follow R below")
    G = []
    for f in sorted(glob.glob("GEX_1min_20*.csv")):
        d = pd.read_csv(f, usecols=["date", "time", "close", "flip"]); d = d[(d.time == 931) & (d.flip > 0)]; G.append(d)
    G = pd.concat(G); G.index = pd.to_datetime(G.date.astype(str)); G = G[~G.index.duplicated()]
    pos = (G.close > G.flip).reindex(idx)
    sig = np.where(pos == True, -np.sign(P.R), np.where(pos == False, np.sign(P.R), np.nan))
    z = pd.Series(sig, index=idx) * (P[1500] - P[830]) * PV - COST
    for nm, m in (("gamma rule, event sessions", isT), ("gamma rule, other days (placebo)", ~isT)):
        print(line(z[m & pos.notna()], nm, 34))
    for nm, m in (("  positive gamma, fade R", pos == True), ("  negative gamma, follow R", pos == False)):
        print(line(z[isT & m], nm, 34))
    print(f"   event sessions with GEX: {int((isT & pos.notna()).sum())}, of which positive gamma {int((isT & (pos == True)).sum())}")
