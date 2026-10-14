"""Funded bench for the one filter that passed analysis/bridge_filter_scan.py (2026-10-14): Overnight Bias ML sized by whether
The Bridge's cumulative delta (RTH, before the entry minute) agrees with the trade's side. The scan's null says one pass in 63
tests happens by chance 20% of the time, so this is a check, not a discovery.
Plan = current funded plan + CL fade 2 MCL, cushion $1,500 (1 year / 2 years, blown); ONB ML at risk $400 now.
  python3 analysis/onb_delta_bench.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")
    lab = ns["lab"]; g = lab.g
    F = pd.read_pickle(SP + "bridge_features.pkl"); F = F[F.strat == "ONB_ML"]
    agree = {(int(r.day), int(r.j0)): (r.cd > 0) for r in F.itertuples() if not np.isnan(r.cd)}
    t = load_mc(g, "Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx")
    a = np.array([agree.get((int(d), int(j)), None) for d, j in zip(t.day, t.j0)], dtype=object)
    print(f"ONB ML trades {len(t)}: delta agrees {int((a == True).sum())}, disagrees {int((a == False).sum())}, no data {int((a == None).sum())}")
    atr = g.daily_atr(15)
    lab.add("ONB_A", t[(a == True)].reset_index(drop=True), stop_pts=0.30 * atr)
    lab.add("ONB_D", t[(a != True)].reset_index(drop=True), stop_pts=0.30 * atr)   # disagree or no data
    base = {"VB": 3, "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    for nm, p in (("plan (ONB ML $400)", {**base, "ONB_ML2_MC": ("risk", 400)}),
                  ("agree $400 / disagree $200", {**base, "ONB_A": ("risk", 400), "ONB_D": ("risk", 200)}),
                  ("agree $500 / disagree $300", {**base, "ONB_A": ("risk", 500), "ONB_D": ("risk", 300)}),
                  ("agree $600 / disagree $200", {**base, "ONB_A": ("risk", 600), "ONB_D": ("risk", 200)}),
                  ("agree $400 only (skip disagree)", {**base, "ONB_A": ("risk", 400)})):
        r1, r2 = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
        print(f"   {nm:<34} ${r1['expected']:,.0f} / ${r2['expected']:,.0f}  blown {r1['blown']:.0%} / {r2['blown']:.0%}"
              f" | 1y 2018-22 ${r1['s2018_22']:,.0f} 2023+ ${r1['s2023_on']:,.0f}")
