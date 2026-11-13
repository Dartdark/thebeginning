"""POST HOC follow-up of the one exploratory cell that cleared its bar in jump_onb_other_markets_test.py: fading GC 5-min jumps (|J| > 3)
whose bar closes in the 10:00 CT hour (t 3.8 vs 3.4 for 168 cells). Same rule (stop 1.5 x range, target 0.3 x stop, 240 min, 15:55).
Checks: halves / years / sides, random-side placebo, target needing 1 and 2 ticks through, neighbours (hours 9-11 halves, |J| 2.5 / 4,
30-minute sub-windows), which days (weekday, the 10:00 ET / 09:00 CT... releases are an hour earlier: what is at 10:00 CT?).
  tools/run_stamped.sh analysis/gc_h10_jump_fade_check.py > analysis/outputs/gc_h10_jump_fade_check_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import jump_generic as JG, jump_lib as L
print(__doc__.split("\n")[0])
b, M = JG.use("GC"); mk = JG.MK["GC"]; yr = b.ts.dt.year.to_numpy(); sgn = np.sign(b.r).fillna(0).to_numpy(); hr = b.ts.dt.hour.to_numpy(); mn = b.ts.dt.minute.to_numpy(); aJ = b.J.abs().to_numpy()
def tt(x): x = pd.Series(x); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan
def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
def line(T, nm):
    x = T.net; y = T.ts.dt.year
    if len(x) < 5: return f"   {nm:<34} n {len(x)}"
    by = " ".join(f"{k % 100:02d}:{x[y == k].sum() / 1000:+.1f}k" for k in sorted(y.unique()))
    return (f"   {nm:<34} n {len(x):4d} avg ${x.mean():6.1f} t {tt(x):5.2f} PF {pf(x):.2f} win {np.mean(x > 0):.0%} | 18-22 ${x[y <= 2022].mean():6.1f} (t {tt(x[y <= 2022]):4.1f}) "
            f"23-26 ${x[y >= 2023].mean():6.1f} (t {tt(x[y >= 2023]):4.1f})\n        {by}")
base = (yr >= 2018) & (aJ > 3) & (hr == 10); T = JG.trades(b, M, base, -sgn, mk)
print(line(T, "GC fade, bar closes 10:00-10:59 CT")); print(line(T[T.side > 0], "  longs (fade drops)")); print(line(T[T.side < 0], "  shorts (fade spikes)"))
print(f"   avg stop ${T.R.mean() * 100:,.0f}, worst trade ${T.net.min():,.0f}, exits " + ", ".join(f"{k} {v}" for k, v in T.why.value_counts().items()) + f"; trades a year {len(T) / 8.85:.0f}")
rng = np.random.default_rng(1); pl = np.array([JG.trades(b, M, base, -sgn, mk, rng=rng).net.mean() for _ in range(300)])
print(f"   random-side placebo (300 runs): mean ${pl.mean():.1f}, p95 ${np.percentile(pl, 95):.1f}, max ${pl.max():.1f} -> p {np.mean(pl >= T.net.mean()):.4f}")
# adverse fill: target needs k ticks through (re-walk with a farther target, credit only the original target)
def through(k):
    out = []
    o = M.arr[0]; R = (b.rng * 1.5).to_numpy(); i1 = b.i1.to_numpy(); busy = -1; tick = mk["tick"]
    for q in np.flatnonzero(base):
        e = i1[q] + 1
        if e >= len(o) - 1 or e <= busy or M.late[e] or M.ts[e] - M.ts[e - 1] > np.timedelta64(2, "m"): continue
        r = R[q]; s = int(-sgn[q])
        if not np.isfinite(r) or r < 8 * tick - 1e-12 or s == 0: continue
        r = round(r / tick) * tick; px = o[e]; iend = min(M.end[e], e + 240)
        if iend <= e: continue
        tg = round(0.3 * r / tick) * tick
        ex, why, ix = L.walk(M.arr, e, s, px - s * r, px + s * (tg + k * tick), iend)
        if why == "tgt": ex = px + s * tg
        g_ = s * (ex - px) * mk["pv"]; out.append(g_ - (mk["comm"] + tick * mk["pv"] + (0 if why == "tgt" else tick * mk["pv"]))); busy = ix
    return np.array(out)
for k in (1, 2): x = through(k); print(f"   target needs {k} tick(s) through: n {len(x)} avg ${x.mean():.1f} t {tt(x):.2f} PF {pf(pd.Series(x)):.2f}")
print("\n== neighbours (each its own run)")
for nm, m in (("hour 9 (09:00-09:59)", hr == 9), ("hour 11", hr == 11), ("10:00-10:25", (hr == 10) & (mn < 30)), ("10:30-10:55", (hr == 10) & (mn >= 30)),
              ("10:00 bar only", (hr == 10) & (mn == 0)), ("10:05-10:55", (hr == 10) & (mn > 0))):
    print(line(JG.trades(b, M, (yr >= 2018) & (aJ > 3) & m, -sgn, mk), nm))
for th in (2.5, 3.5, 4.0): print(line(JG.trades(b, M, (yr >= 2018) & (aJ > th) & (hr == 10), -sgn, mk), f"hour 10, |J| > {th}"))
for k_, tp_ in ((1.0, 0.3), (2.0, 0.3), (1.5, 0.5), (1.5, 1.0)): print(line(JG.trades(b, M, base, -sgn, mk, k=k_, tp=tp_), f"hour 10, stop {k_} x range, target {tp_} x stop"))
print("\n== by weekday (Mon..Fri)"); T["dow"] = T.ts.dt.dayofweek
print("   " + " | ".join(f"{d}: n {len(x)} ${x.mean():.0f}" for d, x in T.groupby("dow").net))
print("== by minute of the signal bar's close"); q = pd.Series((T.ts - pd.Timedelta(minutes=1)).dt.minute.values // 5 * 5)
print("   " + " | ".join(f":{int(k):02d} n {len(x)} ${x.mean():.0f}" for k, x in T.net.groupby(q.values)))
T.to_csv("checks/candidates/jump_onb_other_markets/gc_h10_trades.csv", index=False)
