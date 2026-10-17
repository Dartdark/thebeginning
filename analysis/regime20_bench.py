"""Funded bench for the 20-day regime filter (analysis/regime20_filter_test.py): CL fade skipped in CL bear states, VB sized by NQ bear state.
  python3 analysis/regime20_bench.py   (needs scratch_data: lab, single_print_sessions, s_rank_gap2)
"""
import sys, io, contextlib, runpy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
sys.argv = ["x", "scratch_data/"]
with contextlib.redirect_stdout(io.StringIO()):
    lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
import regime20_filter_test as R
from cl_forced_flows_test import load
g = lab.g; dates = pd.DatetimeIndex(g.ts[lab.tr])
S = pd.read_pickle("scratch_data/single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
nq_st, _ = R.state_series(R.daily_close(pickle.load(open("scratch_data/g24.pkl", "rb"))))
cl_st, _ = R.state_series(R.daily_close(load("CL"), 1600))
nqb = (nq_st.shift(1).reindex(dates, method="ffill") == "bear").to_numpy()
clb = (cl_st.shift(1).reindex(dates, method="ffill") == "bear").to_numpy()
def put(nm, k, mask):
    lab.W[nm] = lab.W[k] * mask[:, None]; lab.C[nm] = lab.C[k] * mask
put("VB_F", "VB", flag); put("VB_N", "VB", ~flag)
put("VB_NB", "VB", ~flag & nqb); put("VB_NO", "VB", ~flag & ~nqb)
put("CLS_O", "CLS", ~clb)
base = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
def pl(**kw):
    p = dict(base); [p.pop(k) for k in kw.pop("drop", [])]; p.update(kw); return p
plans = {"plan (bench)": base,
         "CL fade skipped in CL bear state": pl(drop=["CLS"], CLS_O=2),
         "VB 4 MNQ in NQ bear state (else 3 / 1)": pl(drop=["VB_N"], VB_NO=3, VB_NB=4),
         "VB 2 MNQ outside bear (bear 3)": pl(drop=["VB_N"], VB_NO=2, VB_NB=3)}
for nm, p in plans.items():
    a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
    print(f"   {nm:<42} 1y ${a['expected']:,.0f} blown {a['blown']:.0%} | 2y ${c['expected']:,.0f} blown {c['blown']:.0%}")
