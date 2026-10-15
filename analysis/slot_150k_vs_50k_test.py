"""One account slot over 3 years: 50K vs 150K (2026-10-15). With Apex's 20-account limit the question is what one slot is
worth. A slot cycles challenge -> funded PA -> next challenge (analysis/account_pipeline_test.py mechanics).
  50K : combine set (pass 50.1%), current funded plan, full size from a $1,500 cushion, payouts up to $13,000
  150K: combine set x 2.5 (150K evaluation pass 41.6%, analysis/plan_150k_test.py), funded plan x 1.5 with full size from
        a $3,000 cushion (blown 0% / 0%, $15.9k / $19.7k at 1 / 2 years), payouts up to $20,500 (ladder assumed)
Every 10th start day 2018-01 .. 2023-09, 3 years, real day order. Reported BEFORE fees with the counts of challenges and
activations, so any fee schedule can be applied: net = payouts - challenges x eval price - funded x activation.
  python3 analysis/slot_150k_vs_50k_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import account_pipeline_test as A50, account_pipeline150 as A150
from plan_150k_test import evaluation, R150, R50, ONB30

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
H = 756
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; atr = g.daily_atr(15); tr = lab.tr; D = len(tr); dates = pd.DatetimeIndex(g.ts[tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    PLAN = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
        w, r_ = paths(g, t); P[nm] = (w[tr] / 10, r_[tr] / 10)
    rk = lambda dl_, m: np.floor(dl_ / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": rk(1100, 0.25), "MON_BR": 2.0, "EOS": rk(500, REPORTS["EOS"][1])}
    Wc = sum(P[k][0] * q[k] for k in P); Rc = sum(P[k][1] * q[k] for k in P)
    s_lo, s_hi = int(np.argmax(dates >= "2018-01-01")), int(np.argmax(dates >= "2023-09-01")); starts = list(range(s_lo, min(s_hi, D - H - 30), 10))
    for nm, mod, rules, ck, plan, ref in (("50K", A50, R50, 1.0, PLAN, 1500.0),
                                          ("150K", A150, R150, 2.5, {n: (("risk", v[1] * 1.5) if isinstance(v, tuple) else v * 1.5) for n, v in PLAN.items()}, 3000.0)):
        chal = [evaluation(Wc * ck, Rc * ck, s, D, rules) for s in range(D)]
        names, b = lab._base(plan)
        Wf = np.stack([lab.W[k] for k in names]); Cf = np.stack([lab.C[k] for k in names]); b = np.ascontiguousarray(b)
        cache = {}
        def PA(s, h):
            if (s, h) not in cache: cache[(s, h)] = mod.pa_timeline(Wf, Cf, b, s, h, 0.5, 1.0, ref)
            return cache[(s, h)]
        rows = []
        for s0 in starts:
            fl, c = mod.slot(s0, s0 + H, chal, PA, 0.0)
            pay = sum(v for v in fl.values() if v > 0)
            p12 = sum(v for d, v in fl.items() if v > 0 and d - s0 <= 252)
            rows.append(dict(pay36=pay, pay12=p12, **c))
        df = pd.DataFrame(rows)
        ok = [x for x in chal if x is not None]
        print(f"\n{nm}: evaluation pass {np.mean([x[0] == 'pass' for x in ok]):.1%}; per slot over 3 years (medians / means):")
        print(f"   payouts 12 months ${df.pay12.median():,.0f} (mean ${df.pay12.mean():,.0f}); 36 months ${df.pay36.median():,.0f} (mean ${df.pay36.mean():,.0f})")
        print(f"   challenges bought {df.challenges.mean():.1f}, funded accounts {df.funded.mean():.1f}, completed (all 6) {df.full.mean():.1f}, blown {df.blown.mean():.2f}")
