"""Time clusters in the plans' MultiCharts trade lists (user request, 2026-10-13).

Strategies (funded + combine): Vault Break, Overnight Bias ML v2, Overnight Bias ADX30, Monday Long, Expiration Open
Short, Late-Day Flow, NFP Fade, the Bridge's Monday Long. Per NQ after $7.25 + 1 tick per market / stop fill.
  1. Variable entry times (VB, ONB ML v2, ONB ADX30): by entry half-hour (CT), weekday, month; each cell 2018-22 vs
     2023-26 and a t for "this cell vs the rest". A cell only counts if it's on the same side in both periods.
  2. Fixed entry times (MON, EOS, LDF, NFP, Bridge Monday): the average P&L if the trade had been closed earlier
     (at each checkpoint; trades already closed by their stop / target keep their actual result). Later exits are not
     tested (the stop can't be replayed after the actual exit).
  3. Anything consistent in both periods is tested on the funded bench / combine simulator.
  python3 analysis/time_clusters_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25
SPLIT = pd.Timestamp("2023-01-01")
ONB30 = "Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx"


def trades(g):
    T = {}
    for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC"):
        T[k] = with_slippage(load_mc(g, REPORTS[k][0]))
    T["ONB_ADX30"] = with_slippage(load_mc(g, ONB30))
    T["MON_BR"] = load_bridge_mc(g)
    for k, t in T.items():
        t["net"] = (t.exit - t.entry) * t.side * PV - COST
        t["date"] = pd.DatetimeIndex(g.ts[t.day.values]); T[k] = t[t.date.dt.year >= 2018].reset_index(drop=True)
    return T


def cell_table(t, key, labels=None):
    rows = []
    for v, q in t.groupby(key):
        rest = t[t[key] != v]
        a, b = q.net, rest.net
        tt = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b)) if len(a) > 2 else np.nan
        d, h = q[q.date < SPLIT].net, q[q.date >= SPLIT].net
        pf = a[a > 0].sum() / max(1e-9, -a[a < 0].sum())
        rows.append(dict(cell=labels.get(v, v) if labels else v, n=len(a), win=np.mean(a > 0), avg=a.mean(), pf=pf,
                         avg_18_22=d.mean(), n18=len(d), avg_23_26=h.mean(), n23=len(h), t_vs_rest=tt))
    return pd.DataFrame(rows)


def show(df, title):
    print(f"\n   {title}")
    fm = {"win": "{:.0%}".format, "avg": "${:,.0f}".format, "pf": "{:.2f}".format, "avg_18_22": "${:,.0f}".format,
          "avg_23_26": "${:,.0f}".format, "t_vs_rest": "{:+.1f}".format}
    print(df.to_string(index=False, formatters=fm))
    flag = df[(np.abs(df.t_vs_rest) >= 2) & (np.sign(df.avg_18_22 - df.avg.mean()) == np.sign(df.avg_23_26 - df.avg.mean()))]
    if len(flag): print("   -> |t| >= 2 and the same side in both periods:", flag.cell.tolist())


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); T = trades(g)
    print(__doc__.split("\n")[0])
    WD = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri"}
    print("\n1. Variable entry times")
    for k in ("VB", "ONB_ML2_MC", "ONB_ADX30"):
        t = T[k].copy()
        hm = (t.j0 // 60) * 100 + t.j0 % 60
        t["slot"] = (t.j0 // 30) * 30; t["wd"] = t.date.dt.dayofweek; t["mo"] = t.date.dt.month; t["side_"] = t.side
        lab_ = {s: f"{s // 60:02d}:{s % 60:02d}" for s in t.slot.unique()}
        print(f"\n== {k}: {len(t)} trades, avg ${t.net.mean():.0f}")
        show(cell_table(t, "slot", lab_), "entry half-hour (CT, start of the slot)")
        show(cell_table(t, "wd", WD), "weekday")
        show(cell_table(t, "mo"), "month")
        if (t.side < 0).any():
            for sd, nm in ((1, "longs"), (-1, "shorts")):
                q = t[t.side == sd]
                show(cell_table(q, "slot", lab_), f"{nm}: entry half-hour")

    print("\n2. Fixed entry times: average $ per trade if closed at each checkpoint (actual stop / target exits kept)")
    CHK = {"MON_MC": [900, 930, 1000, 1030, 1100, 1200, 1300, 1400, 1500], "EOS": [845, 900, 915, 930, 945, 1000],
           "LDF_MC": [1415, 1430, 1445, 1455, 1500], "NFP_MC": [800, 815, 830, 845, 900],
           "MON_BR": [0, 300, 600, 830, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1555]}
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    for k, chk in CHK.items():
        t = T[k]
        out = {}
        for hm in chk:
            jx = jof(hm)
            vals = []
            for r in t.itertuples():
                d = int(r.day); j1 = int(r.j1)
                # MON_BR rows are booked on Monday from 00:00: checkpoints are Monday times
                if j1 <= jx: vals.append(r.net); continue
                px = cf[d * 1440 + jx] - r.side * TICK
                vals.append((px - r.entry) * r.side * PV - COST)
            v = pd.Series(vals, index=t.index)
            out[hm] = (v.mean(), v[t.date < SPLIT].mean(), v[t.date >= SPLIT].mean(), v.mean() / v.std() * np.sqrt(len(v)))
        print(f"\n== {k} ({len(t)} trades; actual average ${t.net.mean():.0f}, 2018-22 ${t[t.date < SPLIT].net.mean():.0f}, 2023-26 ${t[t.date >= SPLIT].net.mean():.0f})")
        for hm, (a, d_, h_, tt) in out.items():
            print(f"   exit by {hm:04d} CT: ${a:6.0f} | 2018-22 ${d_:6.0f} | 2023-26 ${h_:6.0f} | t {tt:4.1f}")
    for k in ("LDF_MC", "NFP_MC", "MON_MC"):
        t = T[k].copy(); t["wd"] = t.date.dt.dayofweek; t["mo"] = t.date.dt.month
        if k == "LDF_MC": show(cell_table(t, "wd", WD), f"{k}: weekday")
        show(cell_table(t, "mo"), f"{k}: month")
    pickle.dump(T, open(SP + "time_clusters.pkl", "wb"))

    print("\n3. Candidates on the funded bench (7-strategy plan) and in the combine:")
    atr = g.daily_atr(15)
    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    def sub(k, keep, nm, stop_mult):
        t = T[k][keep].reset_index(drop=True); lab.add(nm, t, stop_pts=stop_mult * atr, slippage=False); return t
    sub("VB", T["VB"].date.dt.month != 9, "VB_noSep", 0.30)
    sub("LDF_MC", T["LDF_MC"].date.dt.dayofweek != 4, "LDF_noFri", 0.25)
    sub("LDF_MC", ~T["LDF_MC"].date.dt.dayofweek.isin([0, 4]), "LDF_TueThu", 0.25)
    sub("ONB_ML2_MC", T["ONB_ML2_MC"].date.dt.dayofweek != 4, "ONBML_noFri", 0.30)
    nf = T["NFP_MC"].copy(); j845 = jof(845)
    for i, r in nf.iterrows():
        if r.j1 > j845:
            px = cf[int(r.day) * 1440 + j845] - r.side * TICK
            nf.loc[i, ["exit", "j1", "kind"]] = [px, j845, 2]
    lab.add("NFP_845", nf, stop_pts=0.50 * atr, slippage=False)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500),
            "MON_BR_MC": 1}
    sw = lambda old, new: {**{k_: v for k_, v in plan.items() if k_ != old}, new: plan[old]}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    from speed_to_13k import run as speed, fmt
    cands = {"current plan (7 strategies)": plan, "VB without September": sw("VB", "VB_noSep"),
             "LDF without Fridays": sw("LDF_MC", "LDF_noFri"), "LDF Tue-Thu only": sw("LDF_MC", "LDF_TueThu"),
             "ONB ML without Fridays": sw("ONB_ML2_MC", "ONBML_noFri"), "NFP exit 8:45": sw("NFP_MC", "NFP_845")}
    rows = {}
    for nm, p in cands.items():
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<30} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
        rows[nm] = speed(lab, p, fmin=0.5, fmax=1.0, ref=1500.0)
    print(fmt(pd.DataFrame(rows).T))
    for nm, t in (("NFP exit 8:45", nf), ("NFP current", T["NFP_MC"])):
        x = t.net if "net" in t and nm == "NFP current" else (t.exit - t.entry) * t.side * PV - COST
        y = t.date.dt.year
        print(f"   {nm}: avg ${x.mean():.0f}, PF {x[x > 0].sum() / -x[x < 0].sum():.2f}, years+ {(x.groupby(y).sum() > 0).sum()}/{y.nunique()}")
    from portfolio import paths, challenge
    tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year
    P = {}
    for nm, t in (("VB", T["VB"]), ("VBns", T["VB"][T["VB"].date.dt.month != 9]), ("ONB", T["ONB_ADX30"]), ("MBR", T["MON_BR"]), ("EOS", T["EOS"])):
        w, r = paths(g, t); P[nm] = (w[tr] / 10, r[tr] / 10)
    rk = lambda dl_, m: np.floor(dl_ / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    for nm, vb in (("combine (VB 8 + ONB30 + Bridge Monday 2 + EOS $500)", "VB"), ("same, VB without September", "VBns")):
        parts = [(P[vb], 8), (P["ONB"], rk(1100, 0.25)), (P["MBR"], 2), (P["EOS"], rk(500, 0.30))]
        W = sum(p_[0] * q for p_, q in parts); Rr = sum(p_[1] * q for p_, q in parts)
        res = [challenge(W, Rr, np.arange(s, min(s + 21, D))) for s in range(D)]
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        print(f"   {nm:<52} pass {np.nanmean(o[yr >= 2018]):.1%} | 2023-26 {np.nanmean(o[yr >= 2023]):.1%}")
