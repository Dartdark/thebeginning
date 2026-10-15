"""Should the CL Sunday fade be sized down after finding that 85% of its P&L comes from oil-event weekends
(analysis/oil_supply_windows_test.py, watchlist #18)? Funded bench (plan with single-print VB, cushion $1,500, 1 / 2 years),
CL fade at 0 / 1 / 2 / 3 MCL, (a) as tested, (b) with every in-window weekend removed = a future with no oil events.
  python3 analysis/cl_fade_size_check.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from oil_supply_windows_test import window

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    # Monday rows of in-window weekends (Sunday entry is booked on Monday); include the Saturday/Sunday before
    inw = np.array([window(d)[0] != "outside" or window(d - pd.Timedelta(days=1))[0] != "outside" for d in dates])
    lab.W["CLS_OUT"] = lab.W["CLS"] * ~inw[:, None]; lab.C["CLS_OUT"] = lab.C["CLS"] * ~inw
    print(f"CL fade P&L per MCL: all ${lab.C['CLS'].sum():,.0f}, outside windows ${lab.C['CLS_OUT'].sum():,.0f}")
    base = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}
    for key, lbl in (("CLS", "as tested"), ("CLS_OUT", "no oil-event weekends")):
        for q in (0, 1, 2, 3):
            p = {**base, key: q} if q else base
            a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
            print(f"   {lbl:<22} {q} MCL: 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%} paid {a['any_payout']:.0%}", flush=True)
