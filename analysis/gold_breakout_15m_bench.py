"""Funded bench for Gold Breakout 15M (NY+7 clock, 1% stop, out broker 20:00 = 12:00 CT) in MGC next to the current plan
(+ CL fade 2 MCL), cushion $1,500. Booked on the Apex day of the exit (entries from 23:00 CT belong to the next Apex day).
  python3 analysis/gold_breakout_15m_bench.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0]); sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")
        gs = runpy.run_path("analysis/gold_breakout_15m_test.py", run_name="gb")
    lab = ns["lab"]; t = gs["run"](gs["load"]("GC"), "A", "pct")
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); pos = pd.Series(np.arange(len(dates)), index=dates)
    Wd = np.zeros(len(dates)); Cd = np.zeros(len(dates))
    for d, r in t.iterrows():
        if d in pos.index: i = pos[d]; Wd[i] += min(r.adv, r.net); Cd[i] += r.net
    lab.W["GLD"] = Wd[:, None] / 10 * np.ones((1, lab.W["VB"].shape[1])); lab.C["GLD"] = Cd / 10
    print("daily corr with plan:", {k: round(float(np.corrcoef(lab.C["GLD"], lab.C[k])[0, 1]), 2) for k in ("VB", "ONB_ML2_MC", "LDF_MC", "CLS")})
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    for q in (0, 1, 2):
        p = {**plan, "GLD": q} if q else plan
        a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
        print(f"   plan{' + ' + str(q) + ' MGC' if q else '':<10} ${a['expected']:,.0f} / ${c['expected']:,.0f}  blown {a['blown']:.0%} / {c['blown']:.0%}"
              f" | 1y 2018-22 ${a['s2018_22']:,.0f} 2023+ ${a['s2023_on']:,.0f}")
