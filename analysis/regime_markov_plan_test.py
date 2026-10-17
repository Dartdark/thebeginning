"""Plan strategies' trades split by the non-overlapping states of analysis/regime_markov2_test.py (previous day's 1-day
move state and volatility state, NQ for NQ strategies, CL for the CL fade), 2026-10-17. Net per contract, MC trade lists.
  python3 analysis/regime_markov_plan_test.py
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.path.insert(0, "analysis/jesse")
import numpy as np, pandas as pd
sys.argv = sys.argv[:1]
import compare as C
from regime_markov_test import series, tstat
from regime_markov2_test import make, LAB
from regime20_filter_test import STRATS, tdiff

if __name__ == "__main__":
    print(__doc__.split("\n")[0]); res = []
    st = {nm: {k: make(series(nm)[0].r, k) for k in ("1d", "vol")} for nm in ("NQ", "CL")}
    for s in STRATS:
        path, pv, tick, cost = C.REPORTS[s]; m = C.mc_trades(path); m["net"] = C.net(m, pv, tick, cost)
        d = m.entry_time.dt.normalize() + (pd.Timedelta(days=1) if s == "CLSundayFade" else pd.Timedelta(0))
        sym = "CL" if s == "CLSundayFade" else "NQ"
        for k in ("1d", "vol"):
            lab = st[sym][k].shift(1).reindex(d, method="ffill").to_numpy()       # yesterday's state, known before entry
            x = m.assign(state=lab).dropna(subset=["state"]); x = x[x.entry_time >= "2018-01-01"]
            parts = []
            for v in LAB[k]:
                y = x[x.state == v].net; parts.append(f"{v} n {len(y):4d} ${y.mean() if len(y) else np.nan:6.0f}")
                t = tdiff(y, x[x.state != v].net); e, h = x[x.entry_time < "2023"], x[x.entry_time >= "2023"]
                res.append(dict(strategy=s, kind=k, state=v, n=len(y), t=t, t1822=tdiff(e[e.state == v].net, e[e.state != v].net),
                                t23=tdiff(h[h.state == v].net, h[h.state != v].net)))
            print(f"{s:<13} [{k:>3}] " + " | ".join(parts))
    df = pd.DataFrame(res)
    ok = df[(df.t.abs() >= 2) & (np.sign(df.t1822) == np.sign(df.t23))]
    print(f"\n{len(df)} tests; |t| >= 2 with the same sign in both periods: {len(ok)}"); print(ok.round(2).to_string(index=False))
