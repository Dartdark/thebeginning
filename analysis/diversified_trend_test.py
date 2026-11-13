"""Diversified trend (time-series momentum) across NQ ES YM GC CL NG ZN 6E BTC, personal account only (pre-registered:
checks/candidates/diversified_trend/PREREG.md, user 2026-11-13).
  tools/run_stamped.sh analysis/diversified_trend_test.py > analysis/outputs/diversified_trend_test_output.txt
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.argv = ["x", "scratch_data"]
import numpy as np, pandas as pd
from grid24 import Grid24, jof
import roll_adjust as RA, metrics as Mx
from cl_forced_flows_test import load
print(__doc__.split("\n")[0])
SPEC = {"NQ": (20, 0.25, 7.25), "ES": (50, 0.25, 5), "YM": (5, 1, 5), "GC": (100, 0.1, 5), "CL": (1000, 0.01, 5), "NG": (10000, 0.001, 5),
        "ZN": (1000, 1 / 64, 5), "6E": (125000, 0.00005, 5), "BTC": (5, 5, 5)}
LARGE, SMALL = ["GC", "CL", "NG", "ZN"], ["NQ", "ES", "YM", "6E"]
RA.WINDOWS.setdefault("NG", (tuple(range(1, 13)), 15, 31)); RA.WINDOWS.setdefault("BTC", (tuple(range(1, 13)), 15, 31))
CACHE = "scratch_data/trend_prices.pkl"
if os.path.exists(CACHE): PX = pickle.load(open(CACHE, "rb"))
else:
    PX = {}
    for s in SPEC:
        g = Grid24() if s == "NQ" else load(s)
        rows = np.array([r for r in range(g.D) if pd.Timestamp(g.ts[r]).dayofweek < 5 and not np.isnan(g.c[r, :jof(1500) + 1]).all()])
        px, J = RA.adjusted_close(g, s, rows * 1440 + jof(1500))
        PX[s] = pd.Series(px, index=pd.DatetimeIndex(g.ts[rows])); print(f"   {s}: {len(rows)} days, {len(J)} rolls removed", flush=True)
    pickle.dump(PX, open(CACHE, "wb"))
P = pd.DataFrame(PX).sort_index(); P = P[P.index >= "2017-06-01"]
dP = P.diff() * pd.Series({s: v[0] for s, v in SPEC.items()})                     # $ change per contract
tcost = pd.Series({s: v[2] / 2 + v[1] * v[0] for s, v in SPEC.items()})           # per contract per side
vol = np.sqrt((dP ** 2).ewm(com=60, min_periods=40).mean()).shift(1)


def book(sig, risk=1000.0):
    pos = (sig * risk / vol).where(vol > 0)
    pnl = pos.shift(1) * dP; cost = pos.diff().abs() * tcost
    return (pnl - cost.fillna(0)).fillna(0), pos


def tsmom(lbs=(21, 63, 252)):
    return sum(np.sign(P.diff(n)) for n in lbs) / len(lbs)


def stats(x, nm, start="2019-01-01"):
    x = x[x.index >= start]; tot = x.sum(axis=1) if isinstance(x, pd.DataFrame) else x
    def sh(y): return y.mean() / y.std() * np.sqrt(252) if y.std() > 0 else np.nan
    a, b = tot[tot.index < "2023-01-01"], tot[tot.index >= "2023-01-01"]
    pf = Mx.perf(tot, capital=100_000)
    by = " ".join(f"{k % 100:02d}:{v / 1000:+.0f}k" for k, v in tot.groupby(tot.index.year).sum().items())
    print(f"   {nm:<34} ${pf['annual']:>8,.0f}/yr Sharpe {pf['sharpe']:5.2f} Sortino {pf['sortino']:5.2f} maxDD ${pf['max_dd']:>7,.0f} Calmar {pf['calmar']:5.2f} "
          f"| 2019-22 Sharpe {sh(a):5.2f} 2023-26 {sh(b):5.2f}\n        {by}")
    return sh(a), sh(b), tot


print("\n== TSMOM book (1/3/12-month sign blend, $1,000 daily risk per market, costs in), from 2019 (12-month lookback warm-up)")
pnl, pos = book(tsmom()); a1, b1, tot = stats(pnl, "TSMOM, 9 markets")
pnlL, _ = book(pd.DataFrame(1.0, index=P.index, columns=P.columns)); aL, bL, totL = stats(pnlL, "C1 long-only vol-scaled")
for n in (21, 63, 252): stats(book(tsmom((n,)))[0], f"C2 lookback {n} days alone")
stats(pnl[LARGE], "large-tick group (GC CL NG ZN)"); stats(pnl[SMALL], "small-tick group (NQ ES YM 6E)")
print("\n== per market (TSMOM): Sharpe 2019-26 / 2019-22 / 2023-26, annual $, avg contracts held, turnover cost $/yr")
y0 = pnl[pnl.index >= "2019-01-01"]
for s in SPEC:
    x = y0[s]; sh = lambda z: z.mean() / z.std() * np.sqrt(252)
    print(f"   {s:<4} {sh(x):5.2f} / {sh(x[x.index < '2023-01-01']):5.2f} / {sh(x[x.index >= '2023-01-01']):5.2f}   ${x.mean() * 252:>7,.0f}/yr   "
          f"{pos[s][pos.index >= '2019-01-01'].abs().mean():6.2f} contracts   ${(pos[s].diff().abs() * tcost[s])[pos.index >= '2019-01-01'].sum() / 7.85:,.0f}/yr cost")
print("\n== C3 placebo: random sign per market per month (100 runs), Sharpe 2019-26")
rng = np.random.default_rng(1); mon = P.index.to_period("M"); ps = []
tot19 = tot[tot.index >= "2019-01-01"]; sh0 = tot19.mean() / tot19.std() * np.sqrt(252)
for _ in range(100):
    R = pd.DataFrame({s: pd.Series(rng.choice([-1.0, 1.0], len(mon.unique())), index=mon.unique()).reindex(mon).values for s in P.columns}, index=P.index)
    x = book(R)[0].sum(axis=1); x = x[x.index >= "2019-01-01"]; ps.append(x.mean() / x.std() * np.sqrt(252))
ps = np.array(ps); print(f"   placebo Sharpe mean {ps.mean():.2f}, p95 {np.percentile(ps, 95):.2f}; TSMOM {sh0:.2f} -> p {np.mean(ps >= sh0):.3f}")
try:
    Pp = pd.read_pickle("scratch_data/personal_P.pkl"); pb = Pp.sum(axis=1)
    j = pd.concat([tot, pb], axis=1, join="inner").dropna(); j = j[j.index >= "2019-01-01"]
    print(f"\n== correlation with the personal book (daily, {len(j)} days): {np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1]:+.2f}")
except Exception as e: print("personal book not available:", e)
ok = a1 >= 0.5 and b1 >= 0.5 and b1 > bL and np.mean(ps >= sh0) < 0.05
print(f"\n== PASS RULE: Sharpe 2019-22 {a1:.2f} and 2023-26 {b1:.2f} >= 0.5; holdout beats long-only ({b1:.2f} vs {bL:.2f}); placebo p {np.mean(ps >= sh0):.3f} -> {'PASS' if ok else 'FAIL'}")
