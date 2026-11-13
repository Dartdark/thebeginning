"""Is swapping ONB ADX30 for ONB ML (funded v2) in the evaluation worth it? (user 2026-11-08). Corrected evaluation engines
(floor keeps trailing): 50K combine_levers_test.challenge, 150K plan_150k_test.evaluation. Every start day 2018+.
150K plan: VB 20, ONB ADX30 $2,750, Bridge Monday 5, EOS $1,250; swap ONB ML at $2,000 / $2,750 / $3,500 risk (0.30 ATR stop).
Uncertainty: paired difference in pass rate, start days resampled in blocks of 60 (2,000 runs; overlapping 21-day windows).
  tools/run_stamped.sh analysis/onb_ml_swap_150k.py > analysis/outputs/onb_ml_swap_150k_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import challenge, MAXD, ONB30
from plan_150k_test import evaluation, R150

FEE = 249.0

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year
    P = {}
    for k, t in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, ONB30)),
                 "ONB_ML": with_slippage(load_mc(g, REPORTS["ONB_ML2_MC"][0])), "MON_BR": load_bridge_mc(g),
                 "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, r = paths(g, t); P[k] = (w[trr] / 10, r[trr] / 10)
    risk = lambda d, m: np.floor(d / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    ok = yr >= 2018
    def res(q, acct):
        W = sum(P[k][0] * v for k, v in q.items()); R = sum(P[k][1] * v for k, v in q.items())
        if acct == 50: out = [challenge(W, R, np.arange(s, min(s + MAXD, D)), lambda p, c, n: 1.0) for s in range(D)]
        else: out = [evaluation(W, R, s, D, R150) for s in range(D)]
        o = np.array([x[0] if x is not None else "" for x in out]); n = np.array([x[1] if x is not None else 0 for x in out])
        valid = ok & np.array([x is not None for x in out]); return o, n, valid
    def line(nm, o, n, v):
        ps = o == "pass"
        return (f"   {nm:<40} pass {ps[v].mean():5.1%} (18-22 {ps[v & (yr < 2023)].mean():5.1%}, 23+ {ps[v & (yr >= 2023)].mean():5.1%}) "
                f"fail {(o[v] == 'fail').mean():5.1%} time {(o[v] == 'time').mean():5.1%} median days {np.median(n[v & ps]):.0f} fee/funded ${FEE / ps[v].mean():,.0f}")
    def boot(a, b, v, B=2000, blk=60, seed=1):
        d = ((a == "pass").astype(float) - (b == "pass").astype(float))[v]; rng = np.random.default_rng(seed); nb = int(np.ceil(len(d) / blk))
        st = rng.integers(0, len(d), (B, nb)); idx = ((st[:, :, None] + np.arange(blk)) % len(d)).reshape(B, -1)[:, :len(d)]
        m = d[idx].mean(axis=1); return d.mean(), np.percentile(m, 5), np.percentile(m, 95), np.mean(m <= 0)
    for acct, base, onb, sizes in ((50, {"VB": 8.0, "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}, 1100, (800, 1100, 1400)),
                                   (150, {"VB": 20.0, "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])}, 2750, (2000, 2750, 3500))):
        print(f"\n{acct}K evaluation (corrected engine), every start day 2018+:")
        o0, n0, v0 = res({**base, "ONB30": risk(onb, 0.25)}, acct); print(line(f"plan: ONB ADX30 ${onb:,}", o0, n0, v0))
        for d in sizes:
            o1, n1, v1 = res({**base, "ONB_ML": risk(d, 0.30)}, acct); v = v0 & v1
            print(line(f"ONB ML ${d:,} instead", o1, n1, v1))
            m, lo, hi, p = boot(o1, o0, v)
            print(f"      paired pass difference {m:+.1%} (90% band {lo:+.1%} to {hi:+.1%}; share of resamples <= 0: {p:.0%})")
