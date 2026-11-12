"""Size COMBINATION search on the live #5 evaluation book (user 2026-11-12 'search combinations').
Grid: ONB30 {2000, 2750, 3500} x EOS {0, 750, 1250, 1750} x MON_BR {3, 5, 7} x TWIN {0, 2, 4} x DT {0, 2, 3} x JF {0, 2, 3} = 972.
Anti-overfit: the search ranks on FRESH 150K evaluations starting 2018-2022 only; the top 10 and the live sizes are then judged on
starts 2023 -> 2026-09 (holdout, one look) and from #5's state now. Same engine as plan_150k_test.evaluation (numba port, checked
against it on the live book below). Paired diffs with 60-day block bands.
  tools/run_stamped.sh analysis/eval_size_combo.py > analysis/outputs/eval_size_combo_output.txt
"""
import sys, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd, numba as nb
import bench150 as BN
from plan_150k_test import evaluation, R150
from build_lab import REPORTS
print(__doc__.split("\n")[0])


@nb.njit(cache=True)
def ev_all(W, R, H, bal0, fl0, tgt, dd, dll, trail_fresh):
    D = W.shape[0]; out = np.full(D, -1.0)
    for s in range(D - H + 1):
        bal = bal0; floor = fl0; res = 0.0
        for d in range(s, s + H):
            lim = max(floor, bal - dll); jb = 1440; jp = 1440
            for j in range(1440):
                if bal + W[d, j] <= lim: jb = j; break
            for j in range(1440):
                if bal + R[d, j] - (bal0 if trail_fresh else 0.0) >= tgt: jp = j; break
            if jp < jb: res = 1.0; break
            if jb < 1440:
                if lim == floor: break
                bal = lim
            else: bal += R[d, 1439]
            floor = max(floor, bal - dd)
        out[s] = res
    return out


ctx = BN.setup(); g, trr, D, dts, P = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"], ctx["P"]
atr = g.daily_atr(15); RM = {"ONB30": 0.25, "EOS": REPORTS["EOS"][1]}
def mult(k, v): return np.floor(v / (np.nan_to_num(RM[k] * atr[trr], nan=1e12) * 2))[:, None] if k in RM else float(v)
def book(spec):
    W = np.zeros((D, 1440)); R = np.zeros((D, 1440))
    for k, v in spec.items():
        if v: m = mult(k, v); W += P[k][0] * m; R += P[k][1] * m
    return W, R
LIVE = {k: (v[1] if isinstance(v, tuple) else v) for k, v in BN.LIVE_EVAL.items()}
yr = dts.year
valid = np.zeros(D, bool); valid[:D - 21 + 1] = True
DES = valid & (yr >= 2018) & (yr <= 2022); HOL = valid & (yr >= 2023) & (dts <= "2026-09-01"); NOWV = valid & (yr >= 2018) & (dts <= "2026-09-01")
fresh = lambda W, R: ev_all(W, R, 21, 150000.0, 146000.0, 9000.0, 4000.0, 2000.0, True)
now = lambda W, R: ev_all(W, R, 20, 147998.08, 146000.0, 159000.0, 4000.0, 2000.0, False)

W0, R0 = book(LIVE); f0 = fresh(W0, R0); n0 = now(W0, R0)
chk = np.array([1.0 if (x := evaluation(W0, R0, s, D, R150)) and x[0] == "pass" else 0.0 for s in range(0, D - 21, 7)])
print(f"engine check (every 7th start): numba {f0[0:D - 21:7].mean():.4f} vs plan_150k_test {chk.mean():.4f}")
print(f"LIVE {LIVE}: fresh 2018-22 {f0[DES].mean():.1%}, 2023+ {f0[HOL].mean():.1%}, all {f0[NOWV].mean():.1%} | from #5 now {n0[NOWV].mean():.1%}")
G = dict(ONB30=[2000, 2750, 3500], EOS=[0, 750, 1250, 1750], MON_BR=[3, 5, 7], TWIN=[0, 2, 4], DT=[0, 2, 3], JF=[0, 2, 3])
rows = []
for combo in itertools.product(*G.values()):
    sp = dict(zip(G, combo)); W, R = book(sp); f = fresh(W, R); rows.append((sp, f[DES].mean(), f))
rows.sort(key=lambda x: -x[1]); print(f"\n{len(rows)} combinations; 2018-22 pass: best {rows[0][1]:.1%}, live {f0[DES].mean():.1%}, median {np.median([r[1] for r in rows]):.1%}")
live_rank = 1 + sum(r[1] > f0[DES].mean() for r in rows); print(f"live sizes rank {live_rank} of {len(rows)} on 2018-22")
def band(d):
    rng = np.random.default_rng(1); n = len(d); nb_ = int(np.ceil(n / 60)); st = rng.integers(0, n, (1000, nb_))
    mm = d[((st[:, :, None] + np.arange(60)) % n).reshape(1000, -1)[:, :n]].mean(1); return np.percentile(mm, 5), np.percentile(mm, 95)
print("\n== top 10 on 2018-22 -> holdout 2023-26 and from #5 now (diff vs live, band)")
for sp, s1, f in rows[:10]:
    W, R = book(sp); n = now(W, R); dh = f[HOL] - f0[HOL]; dn = n[NOWV] - n0[NOWV]; bh = band(dh); bn = band(dn)
    print(f"   {', '.join(f'{k} {v}' for k, v in sp.items())}: 18-22 {s1:.1%} | 23-26 {f[HOL].mean():.1%} ({dh.mean():+.1%}, {bh[0]:+.1%}/{bh[1]:+.1%}) | #5 now {n[NOWV].mean():.1%} ({dn.mean():+.1%}, {bn[0]:+.1%}/{bn[1]:+.1%})", flush=True)
print("\n== per-piece size among the top 50 on 2018-22 (how often each size appears)")
for k in G: print(f"   {k}: " + ", ".join(f"{v} {sum(r[0][k] == v for r in rows[:50])}" for v in G[k]))
best_h = max(rows, key=lambda r: r[2][HOL].mean()); print(f"\n(info) best on the HOLDOUT itself (selection on the holdout, not usable): {best_h[0]} 23-26 {best_h[2][HOL].mean():.1%}")

print("\n== targeted follow-up (added after the search, disclosed): ONB 3500 alone, with / without JF; pass AND fail (from #5 now)")
def now_full(W, R):
    p = now(W, R); return p
def fail_now(W, R):
    # fail = touched the floor within 20 days (1 - pass - still open); recompute with an open flag
    return None
cands = {"live": LIVE, "ONB 3500": {**LIVE, "ONB30": 3500}, "ONB 3500, JF 0": {**LIVE, "ONB30": 3500, "JF": 0},
         "JF 0 (ONB 2750)": {**LIVE, "JF": 0}, "ONB 3500, EOS 750, JF 0": {**LIVE, "ONB30": 3500, "EOS": 750, "JF": 0}}
@nb.njit(cache=True)
def ev_fail(W, R, H, bal0, fl0, tgt, dd, dll):
    D = W.shape[0]; out = np.full(D, -1.0)
    for s in range(D - H + 1):
        bal = bal0; floor = fl0; res = 0.0
        for d in range(s, s + H):
            lim = max(floor, bal - dll); jb = 1440; jp = 1440
            for j in range(1440):
                if bal + W[d, j] <= lim: jb = j; break
            for j in range(1440):
                if bal + R[d, j] >= tgt: jp = j; break
            if jp < jb: break
            if jb < 1440:
                if lim == floor: res = 1.0; break
                bal = lim
            else: bal += R[d, 1439]
            floor = max(floor, bal - dd)
        out[s] = res
    return out
for nm, sp in cands.items():
    W, R = book(sp); f = fresh(W, R); n = now(W, R); fl = ev_fail(W, R, 20, 147998.08, 146000.0, 159000.0, 4000.0, 2000.0)
    dh = f[HOL] - f0[HOL]; dn = n[NOWV] - n0[NOWV]; bh = band(dh); bn = band(dn)
    print(f"   {nm:<26} fresh 18-22 {f[DES].mean():.1%} 23-26 {f[HOL].mean():.1%} ({dh.mean():+.1%}, {bh[0]:+.1%}/{bh[1]:+.1%}) | #5 now pass {n[NOWV].mean():.1%} ({dn.mean():+.1%}, {bn[0]:+.1%}/{bn[1]:+.1%}) fail {fl[NOWV].mean():.1%} still open {1 - n[NOWV].mean() - fl[NOWV].mean():.1%}")
