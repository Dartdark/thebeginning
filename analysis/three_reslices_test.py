"""Three targeted re-slices (user 2026-11-10: 'start on all 3 re-slices'). PRE-REGISTERED (header committed before the first run).
1 Funded payout drag: the funded 150K plan (plan x 1.5 + Twin 2) with each piece removed in turn (600 paired 2-year histories):
  a piece whose removal does not lower 2-year payouts and does not raise blown accounts is dead weight. Rule: removal must be
  >= +$100 with blown no higher, else keep.
2 Evaluation start weekday: base outcomes of the current 150K evaluation set (VB 15, ONB $2,750, Bridge Monday 5, EOS $1,250, Twin 2,
  DT 2; corrected engine) split by the start day's weekday; Monday-Friday pass rates with a 60-day block bootstrap band of each day vs
  the rest; a rule only if one weekday is >= 3 points apart with the band excluding 0 and the same sign in 2018-22 and 2023+.
3 Recovery mode: the day after an evaluation day that hit the $2,000 daily pause, (a) half size, (b) skip the day, (c) half size until
  the account makes a new closing high; vs the base, paired band, both periods.
  tools/run_stamped.sh analysis/three_reslices_test.py > analysis/outputs/three_reslices_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
import dual_thrust_bench as DTB, bench150 as BB
from eval_levers150 import band

START, TARGET, MLL, DLL, MAXD = 150_000.0, 9_000.0, 4_000.0, 2_000.0, 21


def challenge(W, R, s, D, mode=None):
    bal = START; floor = START - MLL; hit_prev = False; peak = START; recover = False
    for n, d in enumerate(range(s, min(s + MAXD, D)), 1):
        k = 1.0
        if mode == "half_next" and hit_prev: k = 0.5
        if mode == "skip_next" and hit_prev: k = 0.0
        if mode == "half_until_high" and recover: k = 0.5
        w, r = W[d] * k, R[d] * k; lim = max(floor, bal - DLL)
        hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
        win = np.nonzero(bal + r - START >= TARGET)[0]; jp = win[0] if len(win) else len(w)
        if jp < jb: return "pass"
        hit_prev = False
        if jb < len(w):
            if lim == floor: return "fail"
            bal = lim; hit_prev = True; recover = True
        else: bal += r[-1]
        if bal > peak: peak = bal; recover = False
        floor = max(floor, bal - MLL)
    return "time" if s + MAXD <= D else None


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(); g, trr, D, dts = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"]
    # ---------------- 1
    print("\n1. Funded 150K, each piece removed:")
    var = {f"without {k}": {q: v for q, v in BB.BASE_FUNDED.items() if q != k} for k in BB.BASE_FUNDED if k != "VB_F"}
    var["without VB (both)"] = {q: v for q, v in BB.BASE_FUNDED.items() if q not in ("VB_N", "VB_F")}
    BB.funded_bench(ctx, var)
    # ---------------- evaluation base
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("DT", DTB.dt_trades(g))): w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    Wb = ctx["Wb"] - 5 * P["VB"][0] + 2 * P["DT"][0]; Rb = ctx["Rb"] - 5 * P["VB"][1] + 2 * P["DT"][1]
    St = np.array([s for s in range(D) if pd.Timestamp("2018-01-02") <= dts[s] <= pd.Timestamp("2026-09-01")]); sd = dts[St]; e = sd < "2023-01-01"
    o0 = np.array([challenge(Wb, Rb, s, D) for s in St]); p0 = (o0 == "pass").astype(float)
    print(f"\n   150K evaluation base: pass {p0.mean():.1%} fail {(o0 == 'fail').mean():.1%} time-out {(o0 == 'time').mean():.1%}")
    # ---------------- 2
    print("\n2. Pass rate by start weekday:")
    wd = sd.dayofweek.values; rng = np.random.default_rng(2)
    for k, nm in enumerate(("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")):
        m = wd == k; diffs = []
        for _ in range(2000):
            st = rng.integers(0, len(St), int(np.ceil(len(St) / 60))); ii = ((st[:, None] + np.arange(60)) % len(St)).ravel()[:len(St)]
            mm, pp = m[ii], p0[ii]; diffs.append(pp[mm].mean() - pp[~mm].mean())
        lo, hi = np.percentile(diffs, [5, 95])
        print(f"   {nm:<10} n {m.sum():4d} pass {p0[m].mean():5.1%} vs rest {p0[~m].mean():5.1%}: {p0[m].mean() - p0[~m].mean():+.1%} (band {lo:+.1%} / {hi:+.1%}) | 18-22 {p0[m & e].mean() - p0[~m & e].mean():+.1%}, 23+ {p0[m & ~e].mean() - p0[~m & ~e].mean():+.1%}", flush=True)
    # ---------------- 3
    print("\n3. Recovery mode after a daily-pause day:")
    for mode, nm in (("half_next", "half size the next day"), ("skip_next", "skip the next day"), ("half_until_high", "half size until a new closing high")):
        o = np.array([challenge(Wb, Rb, s, D, mode) for s in St]); p = (o == "pass").astype(float); lo, hi = band(p - p0)
        print(f"   {nm:<36} pass {p.mean():5.1%} ({p.mean() - p0.mean():+.1%}, band {lo:+.1%} / {hi:+.1%}; 18-22 {p[e].mean() - p0[e].mean():+.1%}, 23+ {p[~e].mean() - p0[~e].mean():+.1%}) fail {(o == 'fail').mean():.1%} time-out {(o == 'time').mean():.1%}", flush=True)
