"""Vault Break with an ATR-scaled bracket (pre-registered: checks/candidates/vb_atr_bracket/PREREG.md, user 2026-11-12).
  tools/run_stamped.sh analysis/vb_atr_bracket_test.py > analysis/outputs/vb_atr_bracket_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24
import vault_break_v8_test as V, metrics as M
print(__doc__.split("\n")[0])
g = Grid24(); B = V.boundary(g, "tr"); print(f"data to {pd.Timestamp(g.ts[g.trading[-1]]).date()}")
F = V.run(g, "v1"); F["atr"] = B[F.day.values]; d = F[F.date.dt.year <= 2024]
TP, SL = float(np.median(40 / d.atr)), float(np.median(75 / d.atr))
print(f"PRIMARY from 2018-24 medians: tp {TP:.3f} x ATR, sl {SL:.3f} x ATR (fixed 40 / 75 at the median ATR {d.atr.median():.0f} pts)")


def mk(tp=None, sl=None):
    t = F if tp is None else V.run(g, "v1", tp_atr=tp, sl_atr=sl)
    t = t.copy(); t["atr"] = B[t.day.values]
    stop_pts = 75.0 if sl is None else np.round(sl * t.atr * 4) / 4
    t["R"] = t.net / (stop_pts * 20); t["yr"] = t.date.dt.year; return t


def tt(x): x = pd.Series(x); return x.mean() / x.std() * np.sqrt(len(x))


def line(t, nm):
    p = lambda m: t.R[m]
    a, b, c = p(t.yr <= 2024), p(t.yr >= 2025), p(t.yr >= 2023)
    k = t.kind
    return (f"   {nm:<26} n {len(t):4d} win {np.mean(t.net > 0):5.1%} tgt/stop/time {np.mean(k == 1):4.0%}/{np.mean(k == 0):4.0%}/{np.mean(k == 2):4.0%} | "
            f"avg R 18-24 {a.mean():+.3f} (t {tt(a):4.1f}) 25-26 {b.mean():+.3f} (t {tt(b):4.1f}) 23+ {c.mean():+.3f} | all {t.R.mean():+.3f} t {tt(t.R):4.1f} | $/NQ {t.net.mean():5.0f}")


V_ = {"F fixed 40/75 (control)": mk(), f"P primary {TP:.3f}/{SL:.3f}": mk(TP, SL)}
G = {}
for tp in (0.10, 0.15, 0.20):
    for sl in (0.20, 0.30, 0.40): G[f"G {tp:.2f}/{sl:.2f}"] = mk(tp, sl)
print("\n== Variants (R = net / stop $; 1 NQ, costs in)")
for nm, t in {**V_, **G}.items(): print(line(t, nm))
best = max(G, key=lambda k: G[k].R[G[k].yr <= 2024].mean()); print(f"   best grid on 2018-24 avg R: {best} (secondary, selected)")

for nm in ("F fixed 40/75 (control)", f"P primary {TP:.3f}/{SL:.3f}", best):
    t = {**V_, **G}[nm]
    print(f"\n== {nm} by year: avg R / win / $ per NQ / exits")
    for y, x in t.groupby("yr"):
        print(f"   {y}: n {len(x):3d} avg R {x.R.mean():+.3f} win {np.mean(x.net > 0):5.1%} ${x.net.mean():6.0f} tgt/stop/time {np.mean(x.kind == 1):4.0%}/{np.mean(x.kind == 0):4.0%}/{np.mean(x.kind == 2):4.0%}")
    dR = t.groupby(t.date).R.sum(); dR = dR.reindex(pd.bdate_range(t.date.min(), t.date.max()), fill_value=0)
    pf = M.perf(dR * 1000, trades=t.R * 1000, capital=100000)
    print(f"   daily R (x $1,000 risk): Sharpe {pf['sharpe']:.2f} Sortino {pf['sortino']:.2f} PF {pf['profit_factor']:.2f} Calmar {pf['calmar']:.2f} Ulcer {pf['ulcer']:.2f} maxDD ${pf['max_dd']:,.0f} annual ${pf['annual']:,.0f}")
    h = t.R[t.yr >= 2025].values; rng = np.random.default_rng(1); bs = [rng.choice(h, len(h)).mean() for _ in range(4000)]
    print(f"   2025-26 avg R bootstrap 95%: {np.percentile(bs, 2.5):+.3f} .. {np.percentile(bs, 97.5):+.3f}")

P_ = V_[f"P primary {TP:.3f}/{SL:.3f}"]; Fc = V_["F fixed 40/75 (control)"]
ok1 = P_.R[P_.yr <= 2024].mean() >= Fc.R[Fc.yr <= 2024].mean(); h1, h0 = P_.R[P_.yr >= 2025].mean(), Fc.R[Fc.yr >= 2025].mean(); c23 = P_.R[P_.yr >= 2023].mean()
print(f"\n== PASS RULE (P vs F): 2018-24 P >= F: {ok1}; 2025-26 P > 0: {h1 > 0} and > F ({h1:+.3f} vs {h0:+.3f}): {h1 > h0}; 2023+ positive: {c23 > 0} -> {'PASS' if ok1 and h1 > 0 and h1 > h0 and c23 > 0 else 'FAIL'}")
print(f"   since 2026-08-01: F avg R {Fc.R[Fc.date >= '2026-08-01'].mean():+.3f} (n {np.sum(Fc.date >= '2026-08-01')}), P {P_.R[P_.date >= '2026-08-01'].mean():+.3f} (n {np.sum(P_.date >= '2026-08-01')})")
print(f"   bar: t_threshold(N_items) see analysis/trials.py; P is a pre-registered single variant of an existing strategy's exit")
P_.to_csv("checks/candidates/vb_atr_bracket/trades_P.csv", index=False)
