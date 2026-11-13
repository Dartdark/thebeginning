"""Follow-ups of analysis/three_reslices_test.py (user 2026-11-10: 'do both'). PRE-REGISTERED (header committed before the first run).
1 Funded 150K: VB normal-day size (VB_N; plan x 1.5 = 3 MNQ now; single-print-flagged VB_F unchanged) 3 / 2 / 1 / 0, 600 paired
  2-year histories. Rule: a smaller size is adopted only if 2-year payouts are not lower AND blown is lower, in the bench and in
  both halves of the start window (2018-22 / 2023-26 starts reported by the paired diff sign).
2 150K evaluation (current set): finish mode (half size once up $6,000) and recovery mode (half size the day after a daily-pause
  day), alone and together (half size when either applies, never a quarter); paired band vs the base and vs finish alone, both
  periods. Adoption of the pair: band vs finish alone above zero.
  tools/run_stamped.sh analysis/vbn_and_modes_test.py > analysis/outputs/vbn_and_modes_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
import dual_thrust_bench as DTB, bench150 as BB
from eval_levers150 import band

START, TARGET, MLL, DLL, MAXD = 150_000.0, 9_000.0, 4_000.0, 2_000.0, 21


def challenge(W, R, s, D, finish=False, recover=False):
    bal = START; floor = START - MLL; hit_prev = False
    for n, d in enumerate(range(s, min(s + MAXD, D)), 1):
        half = (finish and bal - START >= 6000) or (recover and hit_prev); k = 0.5 if half else 1.0
        w, r = W[d] * k, R[d] * k; lim = max(floor, bal - DLL)
        hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
        win = np.nonzero(bal + r - START >= TARGET)[0]; jp = win[0] if len(win) else len(w)
        if jp < jb: return "pass"
        hit_prev = False
        if jb < len(w):
            if lim == floor: return "fail"
            bal = lim; hit_prev = True
        else: bal += r[-1]
        floor = max(floor, bal - MLL)
    return "time" if s + MAXD <= D else None


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(base="legacy"); g, trr, D, dts = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"]
    print("\n1. Funded 150K, VB normal-day size (now 3 MNQ):")
    var = {f"VB_N {q}": {**BB.BASE_FUNDED, "VB_N": q} for q in (2, 1)}; var["VB_N 0"] = {k: v for k, v in BB.BASE_FUNDED.items() if k != "VB_N"}
    BB.funded_bench(ctx, var); BB.funded_bench(ctx, var, end="2022-12-31", label="   same, histories drawn from 2018-22 only")
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("DT", DTB.dt_trades(g))): w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    Wb = ctx["Wb"] - 5 * P["VB"][0] + 2 * P["DT"][0]; Rb = ctx["Rb"] - 5 * P["VB"][1] + 2 * P["DT"][1]
    St = np.array([s for s in range(D) if pd.Timestamp("2018-01-02") <= dts[s] <= pd.Timestamp("2026-09-01")]); e = dts[St] < "2023-01-01"
    res = {nm: np.array([challenge(Wb, Rb, s, D, **kw) for s in St]) for nm, kw in
           (("base", {}), ("finish", dict(finish=True)), ("recovery", dict(recover=True)), ("finish + recovery", dict(finish=True, recover=True)))}
    print("\n2. 150K evaluation (current set):")
    p0, pf = (res["base"] == "pass").astype(float), (res["finish"] == "pass").astype(float)
    for nm, o in res.items():
        p = (o == "pass").astype(float); a = band(p - p0); b = band(p - pf)
        print(f"   {nm:<18} pass {p.mean():5.1%} fail {(o == 'fail').mean():5.1%} time-out {(o == 'time').mean():4.1%} | vs base {p.mean() - p0.mean():+.1%} ({a[0]:+.1%} / {a[1]:+.1%}; 18-22 {p[e].mean() - p0[e].mean():+.1%}, 23+ {p[~e].mean() - p0[~e].mean():+.1%}) | vs finish {p.mean() - pf.mean():+.1%} ({b[0]:+.1%} / {b[1]:+.1%})", flush=True)
