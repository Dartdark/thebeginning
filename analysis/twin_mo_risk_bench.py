"""Apex-shaped Morning Momentum (2026-10-15): Twin's MO leg alone on NQ, stop = 0.292 x 15-day ATR (= 75 pts at NQ's median
ATR), sized by a fixed dollar risk per trade like Overnight Bias (MNQ = floor(risk / (stop pts x $2))), so every loss is a
known amount. Funded bench (cushion $1,500, 1 / 2 years): added to the plan at $150 / $250 / $350 risk, and alone in its
own PA at $300 / $500 / $700.
  python3 analysis/twin_mo_risk_bench.py [SCRATCH_DIR]   (after twin_family_test.py)
"""
import sys, io, contextlib, runpy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc
from twin_continuation_bench import grids

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
K = 0.292
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; B = tc.flatten(g); T = pd.read_pickle(SP + "twin_family_NQ.pkl"); T = T[T.setup == "MO"]
    W, Rr = grids(g, B, T); lab.W["MO_R"] = W[lab.tr] / 10; lab.C["MO_R"] = Rr[lab.tr][:, -1] / 10
    lab.stop["MO_R"] = np.nan_to_num(K * g.daily_atr(15)[lab.tr], nan=1e12)
    q = lambda r: np.floor(r / (lab.stop["MO_R"] * 2.0))
    print(f"MO trades {len(T)}; MNQ at $250 risk: median {np.median(q(250)[q(250) > 0]):.0f} (2018 {np.median(q(250)[lab.yr == 2018]):.0f}, 2026 {np.median(q(250)[lab.yr == 2026]):.0f})")
    dates = pd.DatetimeIndex(g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    base = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
            "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    def show(nm, p):
        r = (lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0))
        print(f"   {nm:<30} ${r[0]['expected']:,.0f} / ${r[1]['expected']:,.0f}  blown {r[0]['blown']:.0%} / {r[1]['blown']:.0%}  paid {r[0]['any_payout']:.0%}"
              f"  days to 1st {r[0]['days_to_1st']:.0f} | 1y 2018-22 ${r[0]['s2018_22']:,.0f} 2023+ ${r[0]['s2023_on']:,.0f}", flush=True)
    show("plan", base)
    for r_ in (150, 250, 350): show(f"plan + MO risk ${r_}", {**base, "MO_R": ("risk", r_)})
    for r_ in (300, 500, 700): show(f"MO alone risk ${r_}", {"MO_R": ("risk", r_)})
