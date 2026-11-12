"""Jump Fade size with ONB at $3,500 (user switched ONB to 3500 on #5, 2026-11-12; 'upping jump fades wont help?').
Reuses eval_size_combo's engine (fresh 2018-22 / 2023-26 and from #5 now: pass, fail, open).
  tools/run_stamped.sh analysis/jf_size_onb3500.py > analysis/outputs/jf_size_onb3500_output.txt
"""
import sys, runpy, io, contextlib; sys.path.insert(0, "analysis")
sys.argv = ["x"]
import numpy as np
src = open("analysis/eval_size_combo.py").read().split("rows = []")[0]       # setup + engine only, no search
src = src.replace("cache=True", "cache=False"); ns = {}; exec(compile(src, "eval_size_combo_head", "exec"), ns)
book, fresh, now, LIVE, f0, n0, DES, HOL, NOWV = (ns[k] for k in ("book", "fresh", "now", "LIVE", "f0", "n0", "DES", "HOL", "NOWV"))
def band(d):
    rng = np.random.default_rng(1); n = len(d); nb_ = int(np.ceil(n / 60)); st = rng.integers(0, n, (1000, nb_))
    mm = d[((st[:, :, None] + np.arange(60)) % n).reshape(1000, -1)[:, :n]].mean(1); return np.percentile(mm, 5), np.percentile(mm, 95)
import numba as nb
@nb.njit
def fail(W, R, H, bal0, fl0, tgt, dd, dll):
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
base = {**LIVE, "ONB30": 3500}; Wb, Rb = book(base); fb = fresh(Wb, Rb); nbb = now(Wb, Rb)
print("vs ONB 3500 + JF 2 (the new live book):")
for j in (0, 1, 2, 3, 4, 6):
    W, R = book({**base, "JF": j}); f = fresh(W, R); n = now(W, R); fl = fail(W, R, 20, 147998.08, 146000.0, 159000.0, 4000.0, 2000.0)
    dh = f[HOL] - fb[HOL]; dn = n[NOWV] - nbb[NOWV]; bh = band(dh); bn = band(dn)
    print(f"   JF {j}: fresh 18-22 {f[DES].mean():.1%} 23-26 {f[HOL].mean():.1%} ({dh.mean():+.1%}, {bh[0]:+.1%}/{bh[1]:+.1%}) | #5 now pass {n[NOWV].mean():.1%} ({dn.mean():+.1%}, {bn[0]:+.1%}/{bn[1]:+.1%}) fail {fl[NOWV].mean():.1%}", flush=True)
