"""Why is Vault Break losing now? (user 2026-11-12: the Bridge's lorenzobruno says VB passed its 9-10 year max drawdown, 17.345 vs
16.415, and is pulling it; a second group member sees the same). Our rebuild (vault_break_v8_test.run, MC-validated) v1 and v8,
24h NQ data to the latest file, per 1 NQ after $7.25 + 1 tick a fill.
 (1) equity, historical max DD and the current one (peak date, depth, trades since)
 (2) the drawdown stretch vs history: win rate, exits, avg win / loss, trades a day
 (3) regime: NQ's 15-day ATR in points vs the FIXED 40 / 75-point bracket (price 6,000 -> 27,000): performance by stop / ATR
 (4) signal vs bracket: entry -> 14:30 drift and excursions, and random-time entries on the same days with the same bracket
 (5) bad luck or broken: block-bootstrap probability of a drawdown this deep in 9 years, and of a stretch this bad
  tools/run_stamped.sh analysis/vb_drawdown_diag.py > analysis/outputs/vb_drawdown_diag_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24
import vault_break_v8_test as V
print(__doc__.split("\n")[0])
g = Grid24(); print(f"data {pd.Timestamp(g.ts[0]).date()} .. {pd.Timestamp(g.ts[g.trading[-1]]).date()}")
B = V.boundary(g, "tr"); ts = pd.DatetimeIndex(g.ts)
c_close = {}


def dd_info(t, nm):
    eq = t.net.cumsum().values; pk = np.maximum.accumulate(eq); dd = eq - pk
    k = int(np.argmin(dd)); kp = int(np.argmax(eq[:k + 1])) if k else 0
    cur = dd[-1]; cp = int(np.argmax(eq))
    # top 5 historical drawdown episodes (non-overlapping)
    eps = []; i = 0
    while i < len(eq):
        if dd[i] < 0:
            j = i
            while j < len(eq) and dd[j] < 0: j += 1
            m = i + int(np.argmin(dd[i:j])); eps.append((dd[m], t.date.iloc[i - 1] if i else t.date.iloc[0], t.date.iloc[m], j - i, j >= len(eq))); i = j
        else: i += 1
    eps.sort(key=lambda x: x[0])
    print(f"\n== {nm}: {len(t)} trades, net ${t.net.sum():,.0f}, avg ${t.net.mean():.0f}, PF {t.net[t.net > 0].sum() / -t.net[t.net < 0].sum():.2f}")
    print(f"   current drawdown ${cur:,.0f} from the peak on {t.date.iloc[cp].date()} ({len(t) - 1 - cp} trades since); worst 5 episodes:")
    for d_, a, b_, n, op in eps[:5]: print(f"      ${d_:9,.0f}  peak {a.date()} -> low {b_.date()}  ({n} trades{', STILL OPEN' if op else ''})")
    return cp


T = {v: V.run(g, v) for v in ("v1", "v8")}
for v, t in T.items(): t["atr"] = B[t.day.values]; t["px"] = t.entry
cp = {v: dd_info(t, f"VB {v}") for v, t in T.items()}

t = T["v1"]; t["yr"] = t.date.dt.year; t["sa"] = 75.0 / t.atr; t["dd_stretch"] = np.arange(len(t)) > cp["v1"]
print("\n== (2) v1 by year and the current stretch (per NQ): n, win, target / stop / time exits, avg win, avg loss, avg")
def row(x, nm):
    w = x.net > 0; k = x.kind
    return (f"   {nm:<22} n {len(x):4d} win {w.mean():5.1%} tgt {np.mean(k == 1):5.1%} stop {np.mean(k == 0):5.1%} time {np.mean(k == 2):5.1%} | "
            f"avg win ${x.net[w].mean():4.0f} loss ${x.net[~w].mean():6.0f} | avg ${x.net.mean():5.0f} | ATR {x.atr.mean():4.0f} pts, stop/ATR {x.sa.mean():.3f}")
for y in sorted(t.yr.unique()): print(row(t[t.yr == y], str(y)))
for lab, m in (("2026 H1", (t.date >= "2026-01-01") & (t.date < "2026-07-01")), ("2026 Jul-Sep", (t.date >= "2026-07-01") & (t.date < "2026-10-01")),
               ("2026 Oct-", t.date >= "2026-10-01"), ("since the peak", t.dd_stretch)):
    print(row(t[m], lab))
print("   breakeven win rate for the bracket (40 win / 75 loss, after costs): ~"
      f"{(75 * 20 + 7.25 + 5) / (40 * 20 - 7.25 + 75 * 20 + 7.25 + 5 + 0):.1%} (ignoring time exits)")

print("\n== (3) the fixed bracket vs volatility: all 2018-26 trades by stop / ATR (75 points / 15-day ATR)")
q = pd.qcut(t.sa, 5)
for k_, x in t.groupby(q): print(row(x, f"stop/ATR {k_.left:.2f}-{k_.right:.2f}") + f" | years {x.yr.min()}-{x.yr.max()}")
print("   same, 2018-2024 only (before the recent stretch):")
o = t[t.yr <= 2024]; q2 = pd.cut(o.sa, [0, 0.15, 0.2, 0.25, 0.35, 10])
for k_, x in o.groupby(q2):
    if len(x): print(row(x, f"stop/ATR {k_}"))

# (4) entry -> 14:30 close drift and excursions; random-time placebo on the same days
print("\n== (4) signal vs bracket: points from entry to the 14:30 close, max up / down before 14:30 (per trade)")
fl = g.jof(1430)
def path(d, j0):
    h = g.h[d, j0:fl + 1]; l_ = g.l[d, j0:fl + 1]; c = g.c[d, fl] if not np.isnan(g.c[d, fl]) else np.nan
    return np.nanmax(h), np.nanmin(l_), c
P = np.array([path(r.day, r.j0) for r in t.itertuples()]); t["mfe"] = P[:, 0] - t.entry; t["mae"] = t.entry - P[:, 1]; t["drift"] = P[:, 2] - t.entry
t["mfe_a"] = t.mfe / t.atr; t["mae_a"] = t.mae / t.atr; t["drift_a"] = t.drift / t.atr
rng = np.random.default_rng(1)
def placebo(x):
    """same day, random minute AFTER VB's entry (to 14:29), same bracket (40 / 75 points), out at 14:30 close (fair: no look-ahead
    into the move that triggered VB; first run drew from 10:00, which rode the trigger move: disclosed, replaced)"""
    out = []
    for r in x.itertuples():
        d = r.day
        if r.j0 >= g.jof(1429): continue
        m = int(rng.integers(r.j0, g.jof(1429)))
        if np.isnan(g.o[d, m]): continue
        e = g.o[d, m] + V.TICK; res = None
        for mm in range(m, fl + 1):
            if np.isnan(g.h[d, mm]): continue
            if g.l[d, mm] <= e - V.TICK - 75: res = (-75 - 1 * V.TICK) * V.PV - V.COST - V.TICK * V.PV; break
            if g.h[d, mm] >= e - V.TICK + 40: res = 40 * V.PV - V.COST - V.TICK * V.PV; break
        if res is None:
            c = g.c[d, fl]
            if np.isnan(c): continue
            res = (c - V.TICK - e) * V.PV - V.COST
        out.append(res)
    return np.mean(out)
for lab, m in (("2018-2024", t.yr <= 2024), ("2025", t.yr == 2025), ("2026", t.yr == 2026), ("since the peak", t.dd_stretch)):
    x = t[m]; pl = np.mean([placebo(x) for _ in range(20)])
    print(f"   {lab:<15} n {len(x):4d} | drift to 14:30 {x.drift.mean():+6.1f} pts ({x.drift_a.mean():+.3f} ATR) | MFE {x.mfe_a.mean():.3f} ATR, MAE {x.mae_a.mean():.3f} ATR "
          f"| VB ${x.net.mean():5.0f} vs random time same days ${pl:5.0f} (signal edge ${x.net.mean() - pl:+5.0f})")

print("\n== (5) bad luck or broken? block bootstrap (20-trade blocks) of 2018-2024 trades over 9 years of trades")
base = t.net[t.yr <= 2024].values; N = len(t); L = len(t) - 1 - cp["v1"]; cur = t.net.values[cp["v1"] + 1:].sum()
mdd = []; worst_run = []
for _ in range(4000):
    st = rng.integers(0, len(base) - 20, int(np.ceil(N / 20))); x = np.concatenate([base[s:s + 20] for s in st])[:N]
    eq = np.cumsum(x); mdd.append((eq - np.maximum.accumulate(eq)).min())
    worst_run.append(min(np.convolve(x, np.ones(L), "valid")) if L > 0 else 0)
mdd = np.array(mdd); worst_run = np.array(worst_run); hist_mdd = (np.cumsum(t.net.values[:cp['v1'] + 1]) - np.maximum.accumulate(np.cumsum(t.net.values[:cp['v1'] + 1]))).min()
print(f"   current stretch: {L} trades, ${cur:,.0f}; max DD before it ${hist_mdd:,.0f}")
print(f"   P(max DD over {N} trades <= current ${t.net.values[cp['v1'] + 1:].cumsum().min():,.0f}) = {np.mean(mdd <= t.net.values[cp['v1'] + 1:].cumsum().min()):.1%}; median max DD ${np.median(mdd):,.0f}, p95 ${np.percentile(mdd, 5):,.0f}")
print(f"   P(some {L}-trade stretch in {N} trades loses >= ${-cur:,.0f}) = {np.mean(worst_run <= cur):.1%}")
t.to_csv("analysis/outputs/vb_drawdown_diag_trades.csv", index=False)

print("\n== (6) market-wide intraday momentum on NQ (all weekdays): does the 08:30 -> 10:00 move continue 10:00 -> 14:30?")
rows = []
for d in g.trading:
    o, a, b_ = g.o[d, g.jof(831)], g.c[d, g.jof(1000)], g.c[d, g.jof(1430)]
    if np.isnan(o) or np.isnan(a) or np.isnan(b_) or np.isnan(B[d]): continue
    rows.append((ts[d], (a - o) / B[d], (b_ - a) / B[d]))
M = pd.DataFrame(rows, columns=["date", "am", "pm"]); M["yr"] = M.date.dt.year
M["half"] = np.where(M.date >= "2026-08-01", "2026 Aug-", np.where(M.date >= "2026-01-01", "2026 Jan-Jul", M.yr.astype(str)))
for k, x in M.groupby("half"):
    up = x.am > 0.3
    print(f"   {k:<13} days {len(x):3d} | corr(am, pm) {np.corrcoef(x.am, x.pm)[0, 1]:+.3f} | after am > +0.3 ATR (n {up.sum():3d}) pm {x.pm[up].mean():+.3f} ATR vs all days {x.pm.mean():+.3f}")
