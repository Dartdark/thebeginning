"""Independent check of Antigravity's 'Vault Break Combined' (HYP-025, antigravity/jesse 2026-10-21,
tasks/CLAUDE_COMPREHENSIVE_REVIEW_DOSSIER.md): Vault Break with (1) no entries on decision bars closing after 12:30 CT
and (2) no entry when the decision close is more than 0.50 x daily ATR(15) above the midnight VWAP.

Rebuild = analysis/candidates24.vault_break24 (matches the MultiCharts VB v1 trade list), our costs ($7.25 + 1 tick per
market / stop fill, target needs a 1-point trade-through). Prints:
  A  base / window / stretch / combined, 2018-26, 2018-22 (design), 2023+ (holdout), longs only (VB has no shorts)
  B  grid of last decision time x stretch cap (t and max DD per period) to look for a plateau or a cliff
  C  the trades each filter removes (same entries as base: are they significantly worse?)
  D  random-removal placebo: drop the same number of base trades at random, how often is max DD as low?
  E  paired block bootstrap of the max-DD and annual-P&L difference, combined - base
  F  Monte Carlo (montecarlo.report) at 3 MNQ (funded) and 8 MNQ (challenge)

  python3 analysis/anti_vb_combined_test.py SCRATCH_DIR   (SCRATCH_DIR/g24.pkl from build_lab.py)
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from candidates24 import vault_break24
from grid import execute
from grid24 import jof
import param_clusters as PC, metrics as M, montecarlo as MC

SP = sys.argv[1] if len(sys.argv) > 1 else "scratch_data"
g = pickle.load(open(f"{SP}/g24.pkl", "rb"))
days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
b = g.bars(30); vw = g.vwap_rows(b); atr = g.daily_atr(15)
PERIODS = (("2018-26", "2018-01-01", "2027-01-01"), ("2018-22", "2018-01-01", "2023-01-01"), ("2023+", "2023-01-01", "2027-01-01"))


def signals(last=1430, cap=np.inf):
    s, kw = vault_break24(g, last=last)
    k = s["dj"].to_numpy() // 30
    stretch = (b["c"][s["day"], k] - vw[s["day"], k]) / atr[s["day"].to_numpy()]
    s = s.assign(stretch=stretch)
    return s[s.stretch <= cap], kw


def run(last=1430, cap=np.inf):
    s, kw = signals(last, cap)
    t = execute(g, s, **kw)
    t = t[pd.DatetimeIndex(t.date).year >= 2018].reset_index(drop=True)
    t["x"] = PC.trade_net(t).to_numpy()
    return t


def daily(t, lo="2018-01-01", hi="2027-01-01"):
    d = pd.DatetimeIndex(t.date); m = (d >= lo) & (d < hi)
    return t.x[m].groupby(d[m]).sum().reindex(days[(days >= lo) & (days < hi)], fill_value=0.0)


def row(t, lo, hi):
    d = pd.DatetimeIndex(t.date); x = t.x[(d >= lo) & (d < hi)]
    r = M.perf(daily(t, lo, hi), trades=x)
    r["t"] = x.mean() / x.std() * np.sqrt(len(x))
    return r


def show(name, t):
    for p, lo, hi in PERIODS:
        r = row(t, lo, hi)
        print(f"  {name:<22} {p:<8} n {r['trades']:>5}  win {r['win']:.0%}  avg ${r['avg']:>4.0f}  t {r['t']:.2f}  "
              f"Sharpe {r['sharpe']:.2f}  Sortino {r['sortino']:.2f}  PF {r['profit_factor']:.2f}  "
              f"Calmar {r['calmar']:.2f}  Ulcer {r['ulcer']:.2f}  maxDD ${r['max_dd']:,.0f}  ${r['annual']:,.0f}/yr")


V = {"base": run(), "window (<=12:30)": run(last=1300), "stretch (<=0.50)": run(cap=0.5),
     "combined": run(last=1300, cap=0.5)}
print("A. Vault Break variants, per NQ, after our costs ($7.25 + 1 tick per market/stop fill)")
for k, t in V.items():
    show(k, t)
print("\n   Antigravity's costs ($17.25 + 1 tick a fill), 2018-26:")
for k, t in V.items():
    x = t.x - 10.0; d = pd.DatetimeIndex(t.date)
    dd = (x.groupby(d).sum().cumsum()); dd = (dd.cummax() - dd).max()
    print(f"  {k:<22} n {len(x)}  net ${x.sum():,.0f}  avg ${x.mean():.2f}  t {x.mean()/x.std()*np.sqrt(len(x)):.2f}  maxDD ${dd:,.0f}")

print("\nB. Grid: last decision bar (rows, entry at the next bar) x stretch cap in ATR (columns); t-stat | max DD $k")
LASTS = (1130, 1200, 1230, 1300, 1330, 1400, 1430)
CAPS = (0.25, 0.35, 0.5, 0.65, 0.8, 1.0, np.inf)
G = {(l, c): run(l, c) for l in LASTS for c in CAPS}
for p, lo, hi in PERIODS:
    print(f"\n  {p}")
    print("  last\\cap " + "".join(f"{c:>13}" for c in CAPS))
    for l in LASTS:
        cells = []
        for c in CAPS:
            r = row(G[(l, c)], lo, hi); cells.append(f"{r['t']:5.2f}|{r['max_dd']/1000:5.1f}k")
        lj = jof(l) - 30
        print(f"  {(lj // 60) * 100 + lj % 60:>8} " + "".join(f"{x:>13}" for x in cells))

print("\nC. Base trades by decision half-hour and by stretch bucket (per NQ, our costs)")
base = V["base"]
s_all, _ = signals()
key = s_all.set_index(["day", "dj"]).stretch
base["dj"] = base.j0 - 1
base["stretch"] = [key.get((d, j), np.nan) for d, j in zip(base.day, base.dj)]
base["dec"] = (base.dj // 30) * 30
base["dec_hhmm"] = (base.dec // 60) * 100 + base.dec % 60
yr = pd.DatetimeIndex(base.date).year
for name, grp in (("decision", base.dec_hhmm), ("stretch", pd.cut(base.stretch, [-9, 0.25, 0.5, 0.75, 1.0, 9]))):
    out = []
    for k, x in base.groupby(grp).x:
        des = x[yr[x.index] <= 2022]; hol = x[yr[x.index] >= 2023]
        out.append(f"    {str(k):<14} n {len(x):>4}  avg ${x.mean():>5.0f}  t {x.mean()/x.std()*np.sqrt(len(x)):5.2f}   "
                   f"2018-22 ${des.mean():>5.0f}  2023+ ${hol.mean():>5.0f}")
    print(f"  by {name}:"); print("\n".join(out))
late = base.dj > jof(1230); hi_s = base.stretch > 0.5
for nm, m in (("decision after 12:30", late), ("stretch > 0.50", hi_s), ("either", late | hi_s)):
    x = base.x[m]
    print(f"  removed by '{nm}': n {len(x)}  avg ${x.mean():.0f}  t {x.mean()/x.std()*np.sqrt(len(x)):.2f}  sum ${x.sum():,.0f}")

print("\nD. Random-removal placebo (2,000 draws): drop as many base trades as the combined filter drops "
      "(same-day re-entries ignored)")
rng = np.random.default_rng(1)
n_drop = int((late | hi_s).sum())
d_all = pd.DatetimeIndex(base.date)
def mdd(x, d):
    c = x.groupby(d).sum().reindex(days, fill_value=0.0).cumsum(); return (c.cummax() - c).max()
act_dd = mdd(base.x[~(late | hi_s)], d_all[~(late | hi_s)]); act_t = base.x[~(late | hi_s)]
act_t = act_t.mean() / act_t.std() * np.sqrt(len(act_t))
dds, ts = [], []
for _ in range(2000):
    keep = np.ones(len(base), bool); keep[rng.choice(len(base), n_drop, replace=False)] = False
    x = base.x[keep]; dds.append(mdd(x, d_all[keep])); ts.append(x.mean() / x.std() * np.sqrt(len(x)))
dds, ts = np.array(dds), np.array(ts)
print(f"  filtered: max DD ${act_dd:,.0f}, t {act_t:.2f};  random: DD median ${np.median(dds):,.0f} "
      f"(5-95% ${np.percentile(dds,5):,.0f}-{np.percentile(dds,95):,.0f}), P(DD <= filtered) {np.mean(dds <= act_dd):.3f}; "
      f"t median {np.median(ts):.2f}, P(t >= filtered) {np.mean(ts >= act_t):.3f}")

print("\nE. Paired block bootstrap (10-day blocks, 5,000), combined - base")
for p, lo, hi in PERIODS:
    A = daily(V["base"], lo, hi).to_numpy(); B = daily(V["combined"], lo, hi).to_numpy(); n = len(A)
    nb = int(np.ceil(n / 10)); dd_d, an_d = [], []
    for _ in range(5000):
        st = rng.integers(0, n - 10, nb); idx = (st[:, None] + np.arange(10)).ravel()[:n]
        a, bb = A[idx], B[idx]
        ca, cb = a.cumsum(), bb.cumsum()
        dd_d.append((np.maximum.accumulate(cb) - cb).max() - (np.maximum.accumulate(ca) - ca).max())
        an_d.append((bb.sum() - a.sum()) / (n / 252))
    dd_d, an_d = np.array(dd_d), np.array(an_d)
    print(f"  {p:<8} max DD diff median ${np.median(dd_d):,.0f} (90% ${np.percentile(dd_d,5):,.0f} to {np.percentile(dd_d,95):,.0f}), "
          f"P(lower DD) {np.mean(dd_d < 0):.2f};  annual diff median ${np.median(an_d):,.0f} "
          f"(90% ${np.percentile(an_d,5):,.0f} to {np.percentile(an_d,95):,.0f})")

print("\nF. Monte Carlo (Apex $2,000 EOD trailing), 2023+ daily P&L")
for k in ("base", "combined"):
    t = V[k]; m = pd.DatetimeIndex(t.date) >= "2023-01-01"
    for size, lab in ((0.3, "3 MNQ"), (0.8, "8 MNQ")):
        print(MC.report(t.x[m].to_numpy(), daily(t, "2023-01-01").to_numpy(), size=size, label=f"{k} {lab}"))
