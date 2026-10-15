"""Twin Continuation as a REPLACEMENT in the funded plan (user's idea, 2026-10-15): swap out one or more plan strategies
(the weakest by deflated Sharpe first: NFP Fade 0.16, EOS 0.42, Monday Long 0.73, Late-Day Flow 0.79; also ONB ML) for Twin
with the breakout stop capped at 1 ATR (cap1), plain or with a 150-pt Morning Momentum target (cap1_mo150), at 1 / 2 MNQ.
Plan = single-print VB 3 / 1 + ONB ML $400 + Monday 1 + EOS $700 + LDF 2 + NFP $500 + Bridge Monday 1 + CL fade 2 MCL;
cushion $1,500; 1 and 2 years.
  python3 analysis/twin_replace_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc
from twin_continuation_bench import grids

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; B = tc.flatten(g)
    for nm, kw in (("cap1", dict(max_stop_mult=1.0)), ("cap1_mo150", dict(max_stop_mult=1.0, mo_target=150.0))):
        T = tc.simulate(B, **kw); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
        W, Rr = grids(g, B, T); lab.W[nm] = W[lab.tr] / 10; lab.C[nm] = Rr[lab.tr][:, -1] / 10
    dates = pd.DatetimeIndex(g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    base = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
            "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    def show(nm, p):
        r = (lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0))
        print(f"   {nm:<44} ${r[0]['expected']:,.0f} / ${r[1]['expected']:,.0f}  blown {r[0]['blown']:.0%} / {r[1]['blown']:.0%}  paid {r[0]['any_payout']:.0%}"
              f"  days to 1st {r[0]['days_to_1st']:.0f} | 1y 2018-22 ${r[0]['s2018_22']:,.0f} 2023+ ${r[0]['s2023_on']:,.0f}", flush=True)
    show("plan", base)
    drops = [("NFP",), ("EOS",), ("NFP", "EOS"), ("MON",), ("LDF",), ("NFP", "EOS", "MON"), ("ONB",)]
    key = {"NFP": "NFP_MC", "EOS": "EOS", "MON": "MON_MC", "LDF": "LDF_MC", "ONB": "ONB_ML2_MC"}
    for d in drops:
        rest = {k: v for k, v in base.items() if k not in [key[x] for x in d]}
        show(f"without {'+'.join(d)}", rest)
        for tw in ("cap1", "cap1_mo150"):
            for q in (1, 2):
                show(f"without {'+'.join(d)} + {tw} {q} MNQ", {**rest, tw: q})
