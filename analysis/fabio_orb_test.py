"""Fabio Valentini ORB (The Institutional Protocol, M. Conti 2026, 'Fabio Valentini Opening Range Breakout' validation PDF
+ the user's FabioValentini_ORB.txt with The Bridge delta toggle, 2026-10-15). Rules: opening range = 5-min bars 8:30-9:00
(chart time); first 5-min CLOSE above the range high, if that bar's delta >= 200, buy at that close; stop = range low,
target = entry + 1 x range width (both from the next bar); flat at the bar crossing Trade_End; long only, one a day.
Paper: NQ 2021-01 .. 2026-04, 823 trades, 58.3% win, PF 1.31 gross / 1.28 net, $201 a trade gross, max DD $25.3k.
The paper's input panel says ORB 8:30 'NY' and Trade_End 14:00 'NY', the code's defaults are 9:30 / 15:00 NY: the same
session if the chart was in exchange (Chicago) time, so here: range 8:30-9:00 CT, flat 14:00 CT (and a 15:00 CT variant).
Python replica on NQ 1-min (CT), 5-min bars closing at :05/:10..; path inside a trade at 1-min resolution (stop first when
a minute touches both). Costs: $7.25 + 1 tick on the entry and on stop / time exits (target = limit, no slip). 1 NQ.
Delta: The Bridge MBO buy - sell volume of the breakout bar (OF_1min_*.csv, RTH 2018-01 .. 2026-07).
  A  no delta filter, delta >= 200 (the paper's number, volume units), delta > 0; by year; longs = all
  B  delta-filter split: trades the filter removes vs keeps (does the filter add anything?)
  C  placebo: same days and times, entry long but exits on a random breakout-free day? -> instead: random-entry control,
     buy at the same bar time on the same day count without the breakout condition (5 runs)
  D  overlap with the plan: same-day correlation with VB / ONB ML P&L
  python3 analysis/fabio_orb_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from orderflow_test import load_of
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25


def run(g, A, end=1400, thr=None, rr=1.0, rand=None, years=(2018, 2027)):
    rng = np.random.default_rng(rand) if rand is not None else None
    ts = pd.DatetimeIndex(g.ts); out = []
    J0, J1, JE = jof(830), jof(900), jof(end)
    for d in g.trading:
        if not (years[0] <= ts[d].year < years[1]): continue
        h, l, c = g.h[d], g.l[d], g.c[d]
        if np.isnan(h[J0 + 1:J1 + 1]).all(): continue
        orh, orl = np.nanmax(h[J0 + 1:J1 + 1]), np.nanmin(l[J0 + 1:J1 + 1])
        cf = pd.Series(c).ffill().to_numpy()
        ends = np.arange(J1 + 5, JE, 5)                                   # 5-min bar closes 9:05 .. before end
        brk = [e for e in ends if cf[e] > orh]
        if rng is not None:                                               # control: same count of days, random bar time
            if not brk: continue
            e = int(rng.choice(ends))
        else:
            if not brk: continue
            e = brk[0]
        delta = np.nansum(A["delta"][d, e - 4:e + 1]) if A["has"][d, e - 4:e + 1].any() else np.nan
        if thr is not None and rng is None and not (delta >= thr): continue
        ep = cf[e]; sl = orl; tp = ep + rr * (ep - sl)
        if sl >= ep: continue
        entry = ep + TICK; x = None; kind = None
        for j in range(e + 1, JE + 1):
            if np.isnan(h[j]): continue
            if l[j] <= sl: x = min(sl, g.o[d, j]) - TICK; kind = "stop"; break
            if h[j] >= tp: x = max(tp, g.o[d, j]) if g.o[d, j] > tp else tp; kind = "target"; break
        if x is None: x = cf[JE] - TICK; kind = "time"
        out.append(dict(day=d, date=ts[d], j0=e, entry=entry, exit=x, kind=kind, delta=delta, width=orh - orl,
                        net=(x - entry) * PV - COMM))
    return pd.DataFrame(out)


def line(t, nm, w=46):
    x = t.set_index("date").net; y = x.index.year; by = x.groupby(y).sum()
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum()); tt = x.mean() / x.std() * np.sqrt(len(x))
    return (f"   {nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf:.2f} t {tt:+.1f} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${x[y < 2023].mean():5.0f} 23-26 ${x[y >= 2023].mean():5.0f} | 21-26.04 (paper) ${x[(x.index >= '2021') & (x.index < '2026-04-17')].mean():5.0f}")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); A = load_of(g)
    print("\nA. Rules as tested (range 8:30-9:00 CT, 1R target, stop = range low):")
    base = run(g, A)
    T = {"no delta filter, flat 14:00": base, "delta >= 200, flat 14:00": run(g, A, thr=200), "delta > 0, flat 14:00": run(g, A, thr=0.001),
         "no delta filter, flat 15:00": run(g, A, end=1500), "delta >= 200, flat 15:00": run(g, A, end=1500, thr=200)}
    for nm, t in T.items(): print(line(t, nm))
    print("   net $ by year (no filter, 14:00):", base.groupby(base.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print(f"   exits: {base.kind.value_counts(normalize=True).round(2).to_dict()}; median range {base.width.median():.0f} pts "
          f"(2018 {base[base.date.dt.year == 2018].width.median():.0f}, 2025 {base[base.date.dt.year == 2025].width.median():.0f}); "
          f"avg loss on stops ${base[base.kind == 'stop'].net.mean():,.0f}")
    print("\nB. What the delta filter does (no-filter trades with delta data, breakout bar delta in contracts):")
    b = base.dropna(subset=["delta"])
    print(f"   breakout-bar delta: median {b.delta.median():.0f}, share >= 200 {np.mean(b.delta >= 200):.0%}, share > 0 {np.mean(b.delta > 0):.0%}")
    for nm, m in (("delta >= 200 (kept)", b.delta >= 200), ("delta < 200 (removed)", b.delta < 200), ("delta <= 0", b.delta <= 0)):
        if m.sum() > 2: print(line(b[m], nm))
    q = pd.qcut(b.delta, 5, labels=False)
    print("   avg $ by delta quintile:", b.net.groupby(q).mean().round(0).astype(int).tolist())
    print("\nC. Control: same days (those with a breakout), long at a random 5-min bar after 9:00, same stop / target rules (10 runs):")
    pl = [run(g, A, rand=r).net.mean() for r in range(10)]
    print(f"   random-time longs avg ${np.mean(pl):.0f} (range {min(pl):.0f}..{max(pl):.0f}) vs breakout ${base.net.mean():.0f}")
    print("\nStandard metrics (no filter, flat 14:00, 1 NQ; long only):")
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = base.groupby("date").net.sum().reindex(days, fill_value=0.0)
    print(M.table({"all (= longs)": (dl, base.net)}))
    bt, pm = R.report({"2023+": dl[dl.index >= "2023-01-01"]}, n=3000); print(bt); print(pm)
    print("\nD. Same-day P&L correlation with the plan (days where both trade):")
    for nm in ("VB", "ONB_ML2_MC"):
        t = with_slippage(load_mc(g, REPORTS[nm][0])); t["net"] = (t.exit - t.entry) * t.side * PV - COMM
        s = t.groupby(pd.DatetimeIndex(g.ts[t.day.to_numpy()])).net.sum()
        j = pd.concat([dl, s], axis=1, join="inner").dropna(); j = j[(j.iloc[:, 0] != 0) & (j.iloc[:, 1] != 0)]
        print(f"   {nm}: {len(j)} shared days, corr {j.corr().iloc[0, 1]:+.2f}")
    base.to_pickle(SP + "fabio_orb_trades.pkl")
    print("\nC2. Fair control without look-ahead (C picks days that later broke out): every day, long at the 9:05 close,")
    print("    stop = range low, target = 1 x range width, flat 14:00:")
    g2 = g; ts = pd.DatetimeIndex(g.ts); out = []
    for d in g.trading:
        if ts[d].year < 2018: continue
        h, l, c = g.h[d], g.l[d], g.c[d]; J0, J1, JE = jof(830), jof(900), jof(1400)
        if np.isnan(h[J0 + 1:J1 + 1]).all(): continue
        cf = pd.Series(c).ffill().to_numpy(); orh, orl = np.nanmax(h[J0 + 1:J1 + 1]), np.nanmin(l[J0 + 1:J1 + 1])
        e = J1 + 5; ep = cf[e]
        if not (orl < ep): continue
        tp = ep + (orh - orl); entry = ep + TICK; x = None
        for j in range(e + 1, JE + 1):
            if np.isnan(h[j]): continue
            if l[j] <= orl: x = min(orl, g.o[d, j]) - TICK; break
            if h[j] >= tp: x = max(tp, g.o[d, j]); break
        if x is None: x = cf[JE] - TICK
        out.append(dict(date=ts[d], net=(x - entry) * PV - COMM))
    print(line(pd.DataFrame(out), "long every day at 9:05 (same exits)"))
