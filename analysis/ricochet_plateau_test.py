"""Ricochet 1144 plateau check in the current personal book (user 2026-11-09). PRE-REGISTERED (header committed before the run; 7 versions:
the current settings and one step either side of each of its three real settings; a plateau check, NOT a search - no version is adopted
from this run). Ricochet: long after a red regular session at the 17:05 reopen, re-entries at S1 + margin x ATR14, stop 50 / target 100
points, out at the 15:00 close, max 4 a session (ricochet_1144_test.run; g24_ext.pkl linked to g24.pkl).
  re-entry margin 0.10 / 0.15 (now) / 0.20      stop 40 / 50 (now) / 60      target 80 / 100 (now) / 120
Book: the current personal book (OT 2 MNQ) + Ricochet 1 MNQ (per NQ net / 10 - $0.55 a trade); 1-year block-bootstrap MC return / DD p95 by
period. Reading: if the neighbours look like the current setting, the setting sits on a plateau; a neighbour that fixes 2018-22 without
losing 2023+ would be a forward-log lead (post hoc), never a direct change.
  tools/run_stamped.sh analysis/ricochet_plateau_test.py > analysis/outputs/ricochet_plateau_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
from ingredient_ablation3 import line
import ricochet_1144_test as RC

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    Pp = pd.read_pickle("scratch_data/personal_P.pkl"); Pp = Pp[[c for c in Pp.columns if c not in ("FC2B", "Kusho", "S47", "S30")]]
    book = Pp.sum(axis=1) + Pp.OvernightTick; idx = Pp.index
    mc = lambda x: (lambda d: d["pnl_p50"] / d["dd_p95"])(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
    per = {"2018-26": np.ones(len(idx), bool), "2018-22": idx.year <= 2022, "2023+": idx.year >= 2023}
    b = {p: mc(book[m]) for p, m in per.items()}; print("   book " + " | ".join(f"{p} {v:.2f}" for p, v in b.items()))
    V = {"current (0.15 / 50 / 100)": {}, "margin 0.10": dict(marg=0.10), "margin 0.20": dict(marg=0.20), "stop 40": dict(stop=40.0), "stop 60": dict(stop=60.0),
         "target 80": dict(target=80.0), "target 120": dict(target=120.0)}
    for nm, kw in V.items():
        t = RC.run(**kw); t["date"] = pd.to_datetime(t.date); t = t[t.date >= "2018-01-01"]
        s = (t.net / 10 - 0.55).groupby(t.date).sum().reindex(idx, fill_value=0.0)
        r = {p: mc((book + s)[m]) for p, m in per.items()}
        print(line(t.net, t.date, nm)); print("      book + 1 MNQ: " + " | ".join(f"{p} {r[p]:.2f} ({r[p] - b[p]:+.2f})" for p in per), flush=True)
