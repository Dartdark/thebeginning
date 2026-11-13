"""Jump Fade and Overnight Bias ADX30 ported to ES YM GC CL ZN 6E NG (pre-registered: checks/candidates/jump_onb_other_markets/PREREG.md,
user 2026-11-13). Engines analysis/jump_generic.py and analysis/onb_generic.py; each is first checked against the NQ engine below.
  tools/run_stamped.sh analysis/jump_onb_other_markets_test.py > analysis/outputs/jump_onb_other_markets_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.argv = ["x", "scratch_data"]
import numpy as np, pandas as pd
import jump_generic as JG, jump_study as S, onb_generic as OG, candidates24 as C24
from funded_lab import with_slippage
from cl_forced_flows_test import load
print(__doc__.split("\n")[0])
SYMS = ["ES", "YM", "GC", "CL", "ZN", "6E", "NG"]
def tt(x): x = pd.Series(x); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan
def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
def table(T, dcol, passes, sym, eng):
    y = T[dcol].dt.year
    for nm, m in (("both", np.ones(len(T), bool)), ("longs", (T.side > 0).values), ("shorts", (T.side < 0).values)):
        x = T.net[m]; yy = y[m]
        if len(x) < 5: print(f"   {nm:<6} n {len(x)}"); continue
        a, b_ = x[yy <= 2022], x[yy >= 2023]
        by = " ".join(f"{k % 100:02d}:{x[yy == k].sum() / 1000:+.1f}k" for k in sorted(yy.unique()))
        print(f"   {nm:<6} n {len(x):4d} avg ${x.mean():6.1f} t {tt(x):5.2f} PF {pf(x):.2f} win {np.mean(x > 0):.0%} | 18-22 ${a.mean():6.1f} (t {tt(a):4.1f}) 23-26 ${b_.mean():6.1f} (t {tt(b_):4.1f})\n          {by}", flush=True)
        if tt(x) >= 2.0 and a.mean() > 0 and b_.mean() > 0: passes.append((eng, sym, nm, x.mean(), tt(x)))

# ---------- engine checks on NQ
b, M = JG.use("NQ"); yr = b.ts.dt.year.to_numpy(); sgn = np.sign(b.r).fillna(0).to_numpy()
mask = (yr >= 2018) & (b.J.abs().to_numpy() > 3) & np.isin(b.ts.dt.hour.to_numpy(), [7, 8, 9])
ref = S.trades(b, M, mask, -sgn, "rng", 1.5, tp=0.3, hold=240); T = JG.trades(b, M, mask, -sgn, JG.MK["NQ"]); m = ref.merge(T, on="ts", suffixes=("", "_g"))
print(f"engine check JUMP on NQ: reference {len(ref)} trades ${ref.net.mean():.1f}, generic {len(T)} ${T.net.mean():.1f}, same minute {len(m)}, same net {np.mean(np.isclose(m.net, m.net_g)):.3f}")
g = pickle.load(open("scratch_data/g24.pkl", "rb")); r = C24.overnight_bias24(g, adx_min=30, stop_atr=0.25); r = r[pd.to_datetime(r.date) >= "2018-01-01"]
rs = with_slippage(r); r = r.assign(rnet=((rs.exit - rs.entry) * rs.side * 20 - 7.25).values)
t = OG.run(g, JG.MK["NQ"], through=1.0); t = t[t.date >= "2018-01-01"]; m = r.merge(t, on=["day", "j0", "side"], suffixes=("", "_g"))
print(f"engine check ONB on NQ: reference {len(r)} trades ${r.rnet.mean():.1f}, generic {len(t)} ${t.net.mean():.1f}, same day+minute+side {len(m)}, same net {np.mean(np.isclose(m.rnet, m.net_g)):.3f}")

passes = []
print("\n################ A. JUMP FADE (07:00-09:59 CT, |J| > 3, stop 1.5 x range, target 0.3 x stop)")
hourly = {}
for sym in SYMS:
    b, M = JG.use(sym); mk = JG.MK[sym]; yr = b.ts.dt.year.to_numpy(); sgn = np.sign(b.r).fillna(0).to_numpy(); hr = b.ts.dt.hour.to_numpy(); aJ = b.J.abs().to_numpy()
    mask = (yr >= 2018) & (aJ > 3) & np.isin(hr, [7, 8, 9]); T = JG.trades(b, M, mask, -sgn, mk)
    print(f"\n== {sym}: {len(T)} trades, avg stop ${T.R.mean() * mk['pv']:,.0f}, target exits {np.mean(T.why == 'tgt'):.0%}")
    n0 = len(passes); table(T, "ts", passes, sym, "JUMP")
    if len(passes) > n0:
        rng = np.random.default_rng(1); pl = np.array([JG.trades(b, M, mask, -sgn, mk, rng=rng).net.mean() for _ in range(100)])
        for p in passes[n0:]: print(f"   placebo (random side, 100 runs): mean ${pl.mean():.1f}, p95 ${np.percentile(pl, 95):.1f} -> {p[2]} avg ${p[3]:.1f}: p {np.mean(pl >= p[3]):.3f} (both-sides placebo)")
    hh = []
    for h in range(24):
        x = JG.trades(b, M, (yr >= 2018) & (aJ > 3) & (hr == h), -sgn, mk).net
        if len(x) >= 30: hh.append((h, len(x), x.mean(), tt(x)))
    hourly[sym] = hh
print("\n== info only (exploratory, 168 cells; |t| >= 3.4 would be needed): fade by hour of the bar's close, cells with |t| >= 2")
for sym, hh in hourly.items():
    print(f"   {sym}: " + (", ".join(f"h{h:02d} n {n} ${a:.0f} t {t_:.1f}" for h, n, a, t_ in hh if abs(t_) >= 2) or "none"))

print("\n################ B. OVERNIGHT BIAS ADX30 (23:00 -> t0 range, break of the first 15-min bar, stop 0.25 ATR, target 3R)")
SESS = {"ES": (830, 1400, 1430), "YM": (830, 1400, 1430), "GC": (730, 1200, 1230), "CL": (800, 1300, 1330), "NG": (800, 1300, 1330), "ZN": (730, 1330, 1400), "6E": (730, 1330, 1400)}
for sym in SYMS:
    g = load(sym); mk = JG.MK[sym]; t0, le, fl = SESS[sym]
    T = OG.run(g, mk, t0=t0, last_entry=le, flat=fl); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
    print(f"\n== {sym} (open {t0}, flat {fl}): {len(T)} trades, avg stop ${T.stop_pts.mean() * mk['pv']:,.0f}, exits stop/target/time {np.mean(T.kind == 0):.0%}/{np.mean(T.kind == 1):.0%}/{np.mean(T.kind == 2):.0%}")
    n0 = len(passes); table(T, "date", passes, sym, "ONB")
    if len(passes) > n0:
        rng = np.random.default_rng(1); pl = []
        for _ in range(100):
            P = OG.run(g, mk, t0=t0, last_entry=le, flat=fl, rng=rng); pl.append(P[P.date >= "2018-01-01"].net.mean())
        pl = np.array(pl)
        for p in passes[n0:]: print(f"   placebo (random bias side, 100 runs): mean ${pl.mean():.1f}, p95 ${np.percentile(pl, 95):.1f} -> {p[2]} avg ${p[3]:.1f}: p {np.mean(pl >= p[3]):.3f} (both-sides placebo)")
    T.to_csv(f"checks/candidates/jump_onb_other_markets/onb_{sym}.csv", index=False)
print("\n################ candidates with t >= 2.0 and both halves positive (pass needs t >= 2.5 and placebo p < 0.05):")
for p in passes: print(f"   {p[0]} {p[1]} {p[2]}: avg ${p[3]:.1f}, t {p[4]:.2f}{'  <- clears t 2.5' if p[4] >= 2.5 else ''}")
if not passes: print("   none")
