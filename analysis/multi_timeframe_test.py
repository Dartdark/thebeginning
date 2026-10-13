"""Multiple timeframes (2026-10-13, user idea), on the funded plan's own strategies.

A. Higher-timeframe trend filter: keep a trade only if it agrees with a slower trend known before
   entry. Measures: previous 15:00 close vs its 20 / 50 / 200-day SMA (daily), and the last
   completed 60-minute close vs its 60-minute EMA(20) at entry (intraday). Applied to the
   MultiCharts trade lists of all 7 plan strategies; kept vs skipped, by year, funded bench.
B. Timeframe ensemble: Vault Break run on 15-, 30- and 60-minute bars at 1 MNQ each, instead of
   30-minute bars at 3 MNQ (same total size). Python version (candidates24.vault_break24 logic).
Per NQ after $7.25 + 1 tick per market/stop fill.
  python3 analysis/multi_timeframe_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from grid import execute
from portfolio import load_mc
from candidates24 import _hhmm, _early
from build_lab import REPORTS
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PLAN = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
        "NFP_MC": ("risk", 500), "VCS_MC": 1}
CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)


def vault_break_bars(g, k, mult=0.30, first=1000, last=1430, flat=1430, tp=40.0, sl=75.0, max_trades=3):
    b = g.bars(k); t = _hhmm(b["j"]); atr = g.daily_atr(15)
    has = ~np.isnan(b["c"]); first_i = np.argmax(has, axis=1)
    noise = b["o"][np.arange(g.D), first_i] + mult * atr
    vw = g.vwap_rows(b); early = _early(g)
    last_e = np.where(early, 1100, last)[:, None]; flat_j = np.where(early, jof(1130), jof(flat))
    m = (t[None, :] >= first) & (t[None, :] < last_e) & (b["c"] > noise[:, None]) & (b["c"] > vw) & has
    d, kk = np.nonzero(m)
    s = pd.DataFrame(dict(day=d, dj=b["j"][kk], side=1, stop=sl, target=tp, exit_j=flat_j[d]))
    s = s[np.isin(s.day, g.trading)]
    return execute(g, s, max_trades=max_trades)


def with_cost(t):
    t = t.copy(); t["net"] = (t.exit - t.entry) * t.side * 20 - 7.25 - (1 + (t.kind != 1)) * 5
    return t


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15)
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    print(__doc__.split("\n")[0])
    tr = g.trading; pos = pd.Series(np.arange(len(tr)), index=tr)
    C = pd.Series(g.c[tr, 900]).ffill()
    trend = {f"SMA{n}": np.sign(C - C.rolling(n).mean()).shift(1).to_numpy() for n in (20, 50, 200)}   # known before the day
    b60 = g.bars(60); flat = pd.Series(b60["c"].ravel()); ema60 = flat.ewm(span=20, adjust=False).mean()
    ok = flat.notna()
    ema60 = pd.Series(np.where(ok, ema60, np.nan)); c60 = flat
    c60f, e60f = c60.ffill().to_numpy(), ema60.ffill().to_numpy()

    def h60(day, j0):                       # last 60-min bar completed before the entry minute
        i = day * 24 + (j0 - 1) // 60
        return np.sign(c60f[i] - e60f[i]) if i >= 0 else np.nan

    lists = {}
    for k, (f, sa) in REPORTS.items():
        if k == "OND_MC": continue
        t = load_mc(g, f); t["date"] = pd.DatetimeIndex(g.ts[t.day.values])
        t = with_cost(t); t = t[t.date.dt.year >= 2018].reset_index(drop=True)
        ii = pos.reindex(t.day).to_numpy()
        t = t[~np.isnan(ii)].reset_index(drop=True); ii = ii[~np.isnan(ii)].astype(int)
        for nm, arr in trend.items(): t[nm] = arr[ii] * t.side
        t["H60"] = [h60(int(d), int(j)) * s for d, j, s in zip(t.day, t.j0, t.side)]
        lists[k] = (t, sa)

    print("\nA. Higher-timeframe agreement: average per NQ when the trade agrees (+) vs disagrees (-)")
    rows = []
    for k, (t, _) in lists.items():
        for nm in ("SMA20", "SMA50", "SMA200", "H60"):
            a, d_ = t.net[t[nm] > 0], t.net[t[nm] < 0]
            ya = t[t[nm] > 0].groupby(t.date.dt.year).net.mean(); yd = t[t[nm] < 0].groupby(t.date.dt.year).net.mean()
            yy = (ya - yd).dropna()
            diff_t = (a.mean() - d_.mean()) / np.sqrt(a.var() / len(a) + d_.var() / len(d_)) if len(a) > 2 and len(d_) > 2 else np.nan
            rows.append(dict(strategy=k, measure=nm, n_agree=len(a), agree=a.mean(), n_disagree=len(d_), disagree=d_.mean(),
                             diff_t=diff_t, years_agree_better=f"{int((yy > 0).sum())}/{len(yy)}"))
    A = pd.DataFrame(rows)
    print(A.to_string(index=False, float_format=lambda v: f"{v:,.1f}"))
    print(f"   {len(A)} comparisons; |diff t| >= 2 in {np.mean(np.abs(A.diff_t) >= 2):.0%}"
          f" (agree better: {int(((A.diff_t >= 2)).sum())}, disagree better: {int(((A.diff_t <= -2)).sum())})")

    print("\n   Funded bench (current 7-strategy plan, full size from $1,500), keeping only agreeing trades:")
    base1, base2 = lab.score(PLAN, 250, **CS), lab.score(PLAN, 500, **CS)
    print(f"   current plan: 1y ${base1['expected']:,.0f} 2y ${base2['expected']:,.0f} blown {base1['blown']:.0%} / {base2['blown']:.0%}")
    for nm in ("SMA20", "SMA50", "SMA200", "H60"):
        p = {}
        for k, v in PLAN.items():
            t, sa = lists[k]
            lab.add(f"{k}_{nm}", t[t[nm] > 0].reset_index(drop=True), stop_pts=sa * atr)
            p[f"{k}_{nm}"] = v
        a, b = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   all strategies filtered by {nm:<6}: 1y ${a['expected']:,.0f} 2y ${b['expected']:,.0f} blown {a['blown']:.0%} / {b['blown']:.0%}")
    best = A.sort_values("diff_t", ascending=False).head(3)
    for _, r in best.iterrows():
        p = {**PLAN}; v = p.pop(r.strategy); p[f"{r.strategy}_{r.measure}"] = v
        a, b = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   only {r.strategy} filtered by {r.measure:<6} (diff t {r.diff_t:.1f}): 1y ${a['expected']:,.0f} 2y ${b['expected']:,.0f}"
              f" blown {a['blown']:.0%} / {b['blown']:.0%}")

    print("\nB. Vault Break timeframe ensemble (Python), per NQ:")
    vb = {k: with_cost(vault_break_bars(g, k)) for k in (15, 30, 60)}
    for k, t in vb.items():
        t = t[t.date.dt.year >= 2018] if "date" in t else t
        t["date"] = pd.DatetimeIndex(g.ts[t.day.values]); vb[k] = t[t.date.dt.year >= 2018].reset_index(drop=True)
        x = vb[k].net; y = vb[k].date.dt.year
        print(f"   {k:>2}-min bars: n={len(x)} win {np.mean(x > 0):.0%} avg ${x.mean():.0f} PF {x[x>0].sum()/-x[x<0].sum():.2f}"
              f" t={x.mean()/x.std()*np.sqrt(len(x)):.1f} yrs+ {(x.groupby(y).sum()>0).sum()}/9 | 23+ ${x[y>=2023].mean():.0f}")
    vbmc = lists["VB"][0]
    print(f"   MultiCharts 30-min (reference): n={len(vbmc)} avg ${vbmc.net.mean():.0f} PF {vbmc.net[vbmc.net>0].sum()/-vbmc.net[vbmc.net<0].sum():.2f}")
    days = pd.DatetimeIndex(g.ts[tr]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    D = {k: dl(t) for k, t in vb.items()}
    print("   daily correlation 15/30/60:", pd.DataFrame(D).corr().round(2).values.tolist())
    print(M.table({"30-min x3": (3 * D[30], None), "15+30+60 x1 each": (D[15] + D[30] + D[60], None),
                   "15-min x3": (3 * D[15], None), "60-min x3": (3 * D[60], None)}))
    for k, t in vb.items(): lab.add(f"VBpy{k}", t.drop(columns=["net"]))
    p30 = {**{k: v for k, v in PLAN.items() if k != "VB"}, "VBpy30": 3}
    pens = {**{k: v for k, v in PLAN.items() if k != "VB"}, "VBpy15": 1, "VBpy30": 1, "VBpy60": 1}
    for nm, p in (("plan with Python VB 30-min x3", p30), ("plan with VB ensemble 15/30/60 x1", pens)):
        a, b = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<36} 1y ${a['expected']:,.0f} 2y ${b['expected']:,.0f} blown {a['blown']:.0%} / {b['blown']:.0%}")
