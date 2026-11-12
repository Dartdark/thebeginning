"""Is the live #5 evaluation book (bench150.LIVE_EVAL: ONB30 $2,750, EOS $1,250, MON_BR 5, Twin 2, DT 2, JF 2) at the best sizes?
(user 2026-11-12). One piece at a time from the live base, then the best one-at-a-time changes together. Two measures:
  fresh  150K evaluation pass rate (bench150 engine, 21 trading days, starts 2018 -> 2026-09-01)
  #5     from #5's state now: balance $147,998, floor $146,000 (trail $4,000), target $159,000, DLL $2,000, 20 trading days
Paired diff vs the live base with a 60-day block bootstrap 5-95% band; a change counts only if its band excludes 0 in BOTH.
  tools/run_stamped.sh analysis/eval_size_live.py > analysis/outputs/eval_size_live_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import bench150 as BN
from plan_150k_test import evaluation, R150
from build_lab import REPORTS
print(__doc__.split("\n")[0])
ctx = BN.setup(); g, trr, D, dts, P = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"], ctx["P"]
atr = g.daily_atr(15); RM = {"ONB30": 0.25, "EOS": REPORTS["EOS"][1]}
def mult(k, v): return np.floor(v / (np.nan_to_num(RM[k] * atr[trr], nan=1e12) * 2))[:, None] if k in RM else float(v)
def book(spec):
    return sum(P[k][0] * mult(k, v) for k, v in spec.items()), sum(P[k][1] * mult(k, v) for k, v in spec.items())
LIVE = {k: (v[1] if isinstance(v, tuple) else v) for k, v in BN.LIVE_EVAL.items()}
ok = (ctx["yr"] >= 2018) & (dts <= "2026-09-01")

def fresh(W, R):
    res = [evaluation(W, R, s, D, R150) for s in range(D)]; return np.array([1.0 if x and x[0] == "pass" else 0.0 for x in res]), ok & np.array([x is not None for x in res])
def now(W, R, H=20, bal0=147998.08, fl0=146000.0, tgt=159000.0):
    out = np.zeros(D); val = np.zeros(D, bool)
    for s in range(D - H):
        bal, floor = bal0, fl0; r = 0.0
        for d in range(s, s + H):
            w, rr = W[d], R[d]; lim = max(floor, bal - 2000.0)
            hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
            win = np.nonzero(bal + rr >= tgt)[0]; jp = win[0] if len(win) else len(w)
            if jp < jb: r = 1.0; break
            if jb < len(w):
                if lim == floor: break
                bal = lim
            else: bal += rr[-1]
            floor = max(floor, bal - 4000.0)
        out[s] = r; val[s] = True
    return out, val & ok
def band(d):
    rng = np.random.default_rng(1); n = len(d); nb = int(np.ceil(n / 60)); st = rng.integers(0, n, (1000, nb))
    mm = d[((st[:, :, None] + np.arange(60)) % n).reshape(1000, -1)[:, :n]].mean(1); return np.percentile(mm, 5), np.percentile(mm, 95)

W0, R0 = book(LIVE); f0, fv0 = fresh(W0, R0); n0, nv0 = now(W0, R0)
print(f"LIVE {LIVE}: fresh pass {f0[fv0].mean():.1%}, from #5 now {n0[nv0].mean():.1%}")
GRID = {"ONB30": [0, 1500, 2000, 2750, 3500], "EOS": [0, 750, 1250, 1750], "MON_BR": [0, 3, 5, 7], "TWIN": [0, 2, 3, 4], "DT": [0, 2, 3, 4], "JF": [0, 2, 3, 4]}
best = {}
for k, vals in GRID.items():
    print(f"\n== {k} (live {LIVE[k]})")
    sc = {}
    for v in vals:
        if v == LIVE[k]: continue
        sp = {**LIVE, k: v}; sp = {a: b for a, b in sp.items() if b}
        W, R = book(sp); f, fv = fresh(W, R); n, nv = now(W, R); m1 = fv & fv0; m2 = nv & nv0
        d1 = f[m1] - f0[m1]; d2 = n[m2] - n0[m2]; b1 = band(d1); b2 = band(d2)
        sig = b1[0] > 0 and b2[0] > 0; sc[v] = (d1.mean() + d2.mean(), sig)
        print(f"   {k} {v:>5}: fresh {f[fv].mean():5.1%} ({d1.mean():+.1%}, band {b1[0]:+.1%}/{b1[1]:+.1%}) | #5 now {n[nv].mean():5.1%} ({d2.mean():+.1%}, band {b2[0]:+.1%}/{b2[1]:+.1%}){'  <- both bands > 0' if sig else ''}", flush=True)
    sig = {v: x for v, x in sc.items() if x[1]}
    if sig: best[k] = max(sig, key=lambda v: sig[v][0])
print(f"\n== changes whose bands exclude 0 in both measures: {best if best else 'none'}")
if best:
    sp = {a: b for a, b in {**LIVE, **best}.items() if b}; W, R = book(sp); f, fv = fresh(W, R); n, nv = now(W, R)
    d1 = f[fv & fv0] - f0[fv & fv0]; d2 = n[nv & nv0] - n0[nv & nv0]
    print(f"   combined {sp}: fresh {f[fv].mean():.1%} ({d1.mean():+.1%}, band {band(d1)[0]:+.1%}/{band(d1)[1]:+.1%}) | #5 now {n[nv].mean():.1%} ({d2.mean():+.1%}, band {band(d2)[0]:+.1%}/{band(d2)[1]:+.1%})")
