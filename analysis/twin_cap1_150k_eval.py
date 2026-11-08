"""Twin Continuation, breakout stop capped at 1 ATR ('cap1'), on the 150K EVALUATION (user 2026-11-08), as an ADDITION to the
150K evaluation set and as a REPLACEMENT of the piece it overlaps most (corrected engine: floor keeps trailing).
150K set: VB 20, ONB ADX30 $2,750, Bridge Monday 5, EOS $1,250 (MC trade lists + 1 tick). Twin cap1: Python port (MC-confirmed
v2.1 rules + max_stop_mult 1.0), per MNQ. Every start day 2018+; paired pass-rate difference with 60-day block resampling.
  tools/run_stamped.sh analysis/twin_cap1_150k_eval.py > analysis/outputs/twin_cap1_150k_eval_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30
from plan_150k_test import evaluation, R150
import twin_continuation_test as tc
from twin_continuation_bench import grids

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year
    P = {}
    for k, t in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, ONB30)), "MON_BR": load_bridge_mc(g),
                 "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, r = paths(g, t); P[k] = (w[trr] / 10, r[trr] / 10)
    B = tc.flatten(g); T = tc.simulate(B, max_stop_mult=1.0); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
    W, Rr = grids(g, B, T); P["TWIN"] = (W[trr] / 10, Rr[trr] / 10)
    print(f"   Twin cap1: {len(T)} trades, ${T.net.mean():.0f} a trade per NQ")
    C = pd.DataFrame({k: P[k][1][:, -1] for k in P}, index=pd.DatetimeIndex(g.ts[trr]))[yr >= 2018]
    print("   daily corr of Twin with the set:", C.corr().loc["TWIN"].drop("TWIN").round(2).to_dict())
    risk = lambda d, m: np.floor(d / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    base = {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])}
    ok = yr >= 2018
    def run(q):
        Wc = sum(P[k][0] * v for k, v in q.items()); Rc = sum(P[k][1] * v for k, v in q.items())
        res = [evaluation(Wc, Rc, s, D, R150) for s in range(D)]
        o = np.array([x[0] if x else "" for x in res]); n = np.array([x[1] if x else 0 for x in res]); v = ok & np.array([x is not None for x in res])
        return o, n, v
    def boot(a, b, v, B=2000, blk=60):
        d = ((a == "pass").astype(float) - (b == "pass").astype(float))[v]; rng = np.random.default_rng(1); nb = int(np.ceil(len(d) / blk))
        st = rng.integers(0, len(d), (B, nb)); m = d[((st[:, :, None] + np.arange(blk)) % len(d)).reshape(B, -1)[:, :len(d)]].mean(axis=1)
        return d.mean(), np.percentile(m, 5), np.percentile(m, 95)
    o0, n0, v0 = run(base)
    def show(nm, o, n, v):
        ps = o == "pass"; m, lo, hi = boot(o, o0, v & v0)
        print(f"   {nm:<36} pass {ps[v].mean():5.1%} (18-22 {ps[v & (yr < 2023)].mean():5.1%}, 23+ {ps[v & (yr >= 2023)].mean():5.1%}) fail {(o[v] == 'fail').mean():5.1%}"
              f" time {(o[v] == 'time').mean():5.1%} median days {np.median(n[v & ps]):.0f} fee/funded ${249 / ps[v].mean():,.0f} | vs plan {m:+.1%} ({lo:+.1%} / {hi:+.1%})", flush=True)
    print("\n150K evaluation (corrected engine), every start day 2018+:")
    show("plan", o0, n0, v0)
    for q in (2, 4, 6, 8): show(f"plan + Twin cap1 {q} MNQ", *run({**base, "TWIN": float(q)}))
    for q in (4, 8): show(f"Twin cap1 {q} instead of Bridge Mon", *run({**{k: v for k, v in base.items() if k != "MON_BR"}, "TWIN": float(q)}))
    for q in (8, 12): show(f"Twin cap1 {q} instead of VB", *run({**{k: v for k, v in base.items() if k != "VB"}, "TWIN": float(q)}))
    for q in (8, 12): show(f"Twin cap1 {q} instead of ONB ADX30", *run({**{k: v for k, v in base.items() if k != "ONB30"}, "TWIN": float(q)}))
