"""Order-flow-entropy gate on Dual Thrust v4. Pre-registered: checks/candidates/dt_entropy/PREREG.md (2026-11-11).
  python analysis/dt_entropy_test.py [holdout]  -> analysis/outputs/dt_entropy_output.txt
Without 'holdout' only 2018-2022 is reported (gate 1); with it, the single 2023+ look is added.
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
HOLD = "holdout" in sys.argv
import statistics
if not hasattr(statistics, "NormalDist"):   # Python 3.7 on this PC: stand-in for metrics.py's import (cdf / inv_cdf only)
    from scipy.stats import norm as _n
    class _ND:
        def __init__(self, mu=0.0, sigma=1.0): self.mu, self.sigma = mu, sigma
        def cdf(self, x): return float(_n.cdf(x, self.mu, self.sigma))
        def inv_cdf(self, p): return float(_n.ppf(p, self.mu, self.sigma))
    statistics.NormalDist = _ND
import dual_thrust_test as DT, jump_lib as JL

days = DT.load(); t = DT.run(days, DT.setups(days))
m = JL.minute(); ts = m.ts.to_numpy(); cl = m.close.to_numpy()

def ent(x):
    s = np.sign(np.diff(x)).astype(int) + 1
    p = np.bincount(s[:-1] * 3 + s[1:], minlength=9) / max(1, len(s) - 1); p = p[p > 0]
    return -(p * np.log(p)).sum()

E = []
for r in t.itertuples():
    end = np.datetime64(pd.Timestamp(r.date).normalize() + pd.Timedelta(minutes=int(r.sig_time) // 100 * 60 + int(r.sig_time) % 100))
    j = np.searchsorted(ts, end, side="right"); lo = np.searchsorted(ts, end - np.timedelta64(30, "m"))
    x = cl[lo:j]; E.append(ent(x) if len(x) >= 20 else np.nan)
t["E"] = E; t["yr"] = pd.DatetimeIndex(t.date).year
D = t[t.yr <= 2022]; q30 = D.E.quantile(0.30)
print(f"DT v4 trades {len(t)} (design {len(D)}); entropy missing {t.E.isna().sum()}; design cut q30 = {q30:.4f}")

def welch(a, b):
    return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))

def line(x, lab):
    n = x.net; pf = n[n > 0].sum() / max(1, -n[n < 0].sum())
    print(f"   {lab:<30} n {len(n):4d} win {np.mean(n > 0):5.1%} ${n.mean():7.1f} PF {pf:4.2f} t {n.mean() / n.std() * np.sqrt(len(n)):5.2f}  stop/target/flat {dict(n.groupby(x.kind).size())}")

def split(X, cut, lab):
    on = X[X.E <= cut]; rest = X[~(X.E <= cut)]
    print(f"{lab}: diff ${on.net.mean() - rest.net.mean():.1f} per NQ, Welch t {welch(on.net, rest.net):.2f}")
    line(on, "gate on (low entropy)"); line(rest, "rest"); return on, rest

print("=== Gate 1: design 2018-2022")
on, rest = split(D, q30, "primary q30")
rng = np.random.default_rng(1); pm = np.array([rng.choice(D.net.to_numpy(), len(on), replace=False).mean() for _ in range(2000)])
print(f"   placebo random subsets of {len(on)}: mean ${pm.mean():.1f}, p = {np.mean(pm >= on.net.mean()):.3f}")
print("--- information only (design)")
for qq in (0.2, 0.5): split(D, D.E.quantile(qq), f"cut q{int(qq * 100)}")
for s, nm in ((1, "longs"), (-1, "shorts")): split(D[D.side == s], q30, nm)
print("   by year (gate on - rest):", "  ".join(f"{y} ${g[g.E <= q30].net.mean() - g[~(g.E <= q30)].net.mean():.0f}" for y, g in D.groupby("yr")))
if HOLD:
    print("=== Gate 2: ONE LOOK at 2023+ (cut unchanged)")
    split(t[t.yr >= 2023], q30, "holdout q30")
