"""Funded bench for one pre-specified tilt from the user's Session Efficiency Forecast (2026-10-14): on the forecast band
(analysis/session_efficiency_model.py, exact port, 2019+ out of sample) Vault Break 2 / 3 / 4 MNQ and Overnight Bias ML
risk $300 / $400 / $500 on low / mid / high days; days without a forecast (2018) at the normal size. Rest of the plan unchanged,
CL fade 2 MCL, cushion $1,500.
  python3 analysis/session_efficiency_bench.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0]); sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")
    lab = ns["lab"]; g = lab.g; atr = g.daily_atr(15)
    band = pd.read_pickle(SP + "sess_eff_forecast.pkl").band
    full = pd.read_pickle(SP + "sess_eff_forecast.pkl")
    for nm, f, sa in (("VB", "mc_reports/Backtesting Strategy Performance Report VB v1.xlsx", 0.30),
                      ("ONB", "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx", 0.30)):
        t = load_mc(g, f); d = pd.DatetimeIndex(g.ts[t.day.values]); b = d.map(band).to_numpy()
        for k, m in (("L", b == 1), ("M", (b == 2) | pd.isna(b)), ("H", b == 3)):
            lab.add(f"{nm}_{k}", t[m].reset_index(drop=True), stop_pts=sa * atr)
        print(f"{nm}: low {int((b == 1).sum())}, mid / none {int(((b == 2) | pd.isna(b)).sum())}, high {int((b == 3).sum())}")
    base = {"MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    for nm, p in (("plan", {**base, "VB": 3, "ONB_ML2_MC": ("risk", 400)}),
                  ("tilt VB 2/3/4, ONB 300/400/500", {**base, "VB_L": 2, "VB_M": 3, "VB_H": 4,
                                                       "ONB_L": ("risk", 300), "ONB_M": ("risk", 400), "ONB_H": ("risk", 500)})):
        a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
        print(f"   {nm:<32} ${a['expected']:,.0f} / ${c['expected']:,.0f}  paid {a['any_payout']:.0%}  blown {a['blown']:.0%} / {c['blown']:.0%}"
              f" | 1y 2018-22 ${a['s2018_22']:,.0f} 2023+ ${a['s2023_on']:,.0f}")
