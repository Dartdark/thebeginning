"""Is ES more mean-reverting than NQ? (user's premise, 2026-10-14). Day session 8:30-15:00 CT, 2018-2026.
Variance ratio VR(k) = var(k-min returns) / (k x var(1-min returns)) (< 1 = mean reversion), and the autocorrelation of
consecutive k-minute returns, per day pooled; also the daily session-to-next-session autocorrelation.
  python3 analysis/es_mean_reversion_premise.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

def grid(f):
    g = pickle.load(open(SP + f, "rb")); tr = g.trading; idx = pd.DatetimeIndex(g.ts[tr])
    a = pd.DataFrame(g.c[tr, jof(830):jof(1500) + 1]).ffill(axis=1).bfill(axis=1).to_numpy()
    ok = ~np.isnan(a).any(1) & (idx >= "2018-01-01"); return np.log(a[ok]), idx[ok]

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for nm, f in (("ES", "ge.pkl"), ("NQ", "g24.pkl")):
        L, idx = grid(f); r1 = np.diff(L, axis=1); v1 = np.nanvar(r1)
        for per, m in (("2018-26", np.ones(len(idx), bool)), ("2023-26", idx >= "2023-01-01")):
            out = []
            for k in (5, 15, 30, 60):
                rk = L[m][:, k::k] - L[m][:, :-k:k][:, :L[m][:, k::k].shape[1]]
                vr = np.nanvar(rk) / (k * np.nanvar(r1[m]))
                a, b = rk[:, :-1].ravel(), rk[:, 1:].ravel(); ok = ~np.isnan(a) & ~np.isnan(b)
                out.append(f"{k:>2}m VR {vr:.3f} ac {np.corrcoef(a[ok], b[ok])[0, 1]:+.3f}")
            day = L[m][:, -1] - L[m][:, 0]
            print(f"{nm} {per}: " + " | ".join(out) + f" | session-to-next-session ac {np.corrcoef(day[:-1], day[1:])[0, 1]:+.3f}")
