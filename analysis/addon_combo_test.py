"""Combined funded add-on of the three small uncorrelated edges (2026-10-13):
Headline Shock Follow (HSF), NFP Fade (NFP) and Vol-Control Sell Flow (VCS), each tier C and
within noise on its own. Does the bundle clear the noise bar?

1. Overlap and correlation of the three, and the standard metrics of the bundle (per NQ and at
   funded size), longs / shorts, by year, bootstrap + permutation on 2023-26.
2. Funded bench: every size combination (HSF 0-2 MNQ, NFP $0/300/500, VCS 0-2 MNQ) on top of the
   current plan, cushion sizing, 1 and 2 years.
3. Noise: paired difference (plan + add-on minus plan) per start day, block bootstrap over start
   days (60-day blocks) -> 90% interval of the gain; and by start year.
4. Nasdaq-100 special rebalance: only one in the data (July 2023); the NQ moves around it.
  python3 analysis/addon_combo_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle, itertools; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R, funded_sim as F
from news_meanrev_test import row
from cta_volcontrol_test import vc_exposure

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
CS = dict(fmin=0.5, fmax=1.0, ref=2000.0)
PLAN = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2}


def vcs_trades(g, es, atr, q=0.06, sk=0.25):
    tr = g.trading; dts = pd.DatetimeIndex(g.ts[tr])
    ei = pd.Series(np.arange(len(es.dates)), index=es.dates).reindex(g.dates[tr]).to_numpy()
    ok = ~np.isnan(ei); ei = np.where(ok, ei, 0).astype(int)
    e900 = pd.Series(np.where(ok, es.c[ei, 900], np.nan)).ffill().to_numpy()
    r = np.r_[np.nan, e900[1:] / e900[:-1] - 1]
    E = vc_exposure(r); f = np.r_[np.nan, E[:-1]] - np.r_[np.nan, np.nan, E[:-2]]
    rows = []
    for k in np.where(f < -q)[0]:
        d = tr[k]
        if dts[k].year < 2018 or np.isnan(atr[d]) or np.isnan(g.o[d, 841]): continue
        e = g.o[d, 841]
        x = row(g, d, 841, -1, jof(1500), (e - 0.25) + sk * atr[d], None)
        if x: rows.append(x)
    return pd.DataFrame(rows)


def per_start(lab, plan, h):
    names, b = lab._base(plan)
    W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names])
    st = np.arange(0, lab.D - h)
    return F.simulate_sized(W, C, b, horizon=h, starts=st, **CS)["paid"], lab.yr[st]


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
    atr = g.daily_atr(15)
    hsf = pd.read_pickle(SP + "hsf_trades.pkl"); nfp = pd.read_pickle(SP + "nfp_trades.pkl")
    vcs = vcs_trades(g, es, atr)
    print(__doc__.split("\n")[0])
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]; D2 = days[days.year >= 2023]
    dl = lambda t, ix=days: t.groupby(t.date).net.sum().reindex(ix, fill_value=0.0)

    # ---------------- 1. overlap, correlation, metrics per NQ (1 NQ each)
    T = {"HSF": hsf, "NFP": nfp, "VCS": vcs}
    print("\n1. Trades and overlap (days both trade):")
    for a, b in itertools.combinations(T, 2):
        both = len(set(T[a].date.dt.normalize()) & set(T[b].date.dt.normalize()))
        print(f"   {a} {len(T[a])} / {b} {len(T[b])}: {both} shared days")
    Dd = pd.DataFrame({k: dl(v) for k, v in T.items()})
    print("   daily correlation:"); print(Dd.corr().round(2).to_string())
    allt = pd.concat([v.assign(src=k) for k, v in T.items()], ignore_index=True)
    rows = {k: (dl(v), v.net) for k, v in T.items()}
    rows["BUNDLE (1 NQ each)"] = (dl(allt), allt.net)
    rows["  bundle longs"] = (dl(allt[allt.side > 0]), allt.net[allt.side > 0])
    rows["  bundle shorts"] = (dl(allt[allt.side < 0]), allt.net[allt.side < 0])
    print("\n   Standard metrics per NQ, 2018-26:"); print(M.table(rows))
    h = allt[allt.date.dt.year >= 2023]
    print("   2023-26:"); print(M.table({"BUNDLE": (dl(h, D2), h.net), "  longs": (dl(h[h.side > 0], D2), h.net[h.side > 0]),
                                       "  shorts": (dl(h[h.side < 0], D2), h.net[h.side < 0])}))
    print("   bundle by year:", allt.groupby(allt.date.dt.year).net.sum().round(0).astype(int).to_dict())

    # ---------------- 2. funded bench grid
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    lab.add("HSF", hsf, slippage=False)
    lab.add("NFP", nfp, stop_pts=0.5 * atr, slippage=False)
    lab.add("VCS", vcs, stop_pts=0.25 * atr, slippage=False)
    base1, base2 = lab.score(PLAN, 250, **CS), lab.score(PLAN, 500, **CS)
    res = []
    for hs, nf, vc in itertools.product((0, 1, 2), (0, 300, 500), (0, 1, 2)):
        p = dict(PLAN)
        if hs: p["HSF"] = hs
        if nf: p["NFP"] = ("risk", nf)
        if vc: p["VCS"] = vc
        a, b = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        res.append(dict(HSF=hs, NFP=nf, VCS=vc, y1=a["expected"], y1_23=a["s2023_on"], y2=b["expected"],
                        blown1=a["blown"], blown2=b["blown"], days1st=a["days_to_1st"]))
    R_ = pd.DataFrame(res); R_["sum"] = R_.y1 + R_.y2
    R_ = R_.sort_values("sum", ascending=False)
    fm = {c: "${:,.0f}".format for c in ("y1", "y1_23", "y2", "sum")}
    fm.update({"blown1": "{:.0%}".format, "blown2": "{:.0%}".format, "days1st": "{:.0f}".format})
    print(f"\n2. Funded bench (cushion sizing), current plan ${base1['expected']:,.0f} / ${base2['expected']:,.0f}; top 12 by 1y + 2y:")
    print(R_.head(12).to_string(index=False, formatters=fm))
    print("   ... bottom 3:"); print(R_.tail(3).to_string(index=False, formatters=fm))

    # ---------------- 3. noise of the gain (paired by start day)
    cands = {"HSF 1 + NFP $500 + VCS 1": {**PLAN, "HSF": 1, "NFP": ("risk", 500), "VCS": 1},
             "NFP $500 + VCS 1": {**PLAN, "NFP": ("risk", 500), "VCS": 1},
             "HSF 1 + NFP $300 + VCS 1": {**PLAN, "HSF": 1, "NFP": ("risk", 300), "VCS": 1}}
    best = R_.iloc[0]
    if best.HSF or best.NFP or best.VCS:
        p = dict(PLAN)
        if best.HSF: p["HSF"] = int(best.HSF)
        if best.NFP: p["NFP"] = ("risk", int(best.NFP))
        if best.VCS: p["VCS"] = int(best.VCS)
        cands[f"best of grid: HSF {best.HSF:.0f}, NFP ${best.NFP:.0f}, VCS {best.VCS:.0f}"] = p
    print("\n3. Gain over the current plan, paired by start day; 90% block-bootstrap interval (60-day blocks):")
    rng = np.random.default_rng(11)
    for h_ in (250, 500):
        p0, yr = per_start(lab, PLAN, h_)
        for nm, p in cands.items():
            p1, _ = per_start(lab, p, h_)
            d = p1 - p0; n = len(d); B = 60
            boots = []
            for _ in range(2000):
                s = rng.integers(0, n - B, n // B + 1)
                idx = (s[:, None] + np.arange(B)[None]).ravel()[:n]
                boots.append(d[idx].mean())
            by = pd.Series(d).groupby(yr).mean()
            print(f"   {h_ // 250}y {nm:<40} gain ${d.mean():6,.0f} (90%: ${np.percentile(boots, 5):,.0f} to ${np.percentile(boots, 95):,.0f})"
                  f" | start years better {int((by > 0).sum())}/{len(by)}: " + " ".join(f"{y % 100:02d}:{v:+.0f}" for y, v in by.items()))

    # ---------------- portfolio metrics at funded size, with the recommended bundle
    pick = cands["HSF 1 + NFP $500 + VCS 1"]
    dts2 = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts2.year >= 2018
    names, b = lab._base(pick); b = np.floor(b + 1e-9)
    Q = {k: pd.Series(lab.C[k] * b[i], index=dts2)[mk] for i, k in enumerate(names)}
    port = sum(Q.values()); port0 = sum(v for k, v in Q.items() if k not in ("HSF", "NFP", "VCS"))
    addon = sum(v for k, v in Q.items() if k in ("HSF", "NFP", "VCS"))
    print("\n   Portfolio at full size (HSF 1 MNQ, NFP $500, VCS 1 MNQ):")
    print(M.table({"current plan": (port0, None), "plan + bundle": (port, None), "bundle alone": (addon, None)}))
    print("   correlation of the bundle with the plan:", round(addon.corr(port0), 2))
    Bt, Pm = R.report({"bundle 2023-26": addon[addon.index.year >= 2023], "plan + bundle 2023-26": port[port.index.year >= 2023],
                       "plan 2023-26": port0[port0.index.year >= 2023]}, n=5000)
    print(Bt); print(Pm)

    # ---------------- 4. Nasdaq-100 special rebalance, July 2023
    print("\n4. Nasdaq-100 special rebalance (announced Fri 7 Jul 2023, traded at the close Fri 21 Jul 2023):")
    for dstr in ("2023-07-07", "2023-07-10", "2023-07-20", "2023-07-21", "2023-07-24"):
        d = np.searchsorted(g.dates, int(dstr.replace("-", "")))
        o, c14, c15, c1515 = g.o[d, 511], g.c[d, 840], g.c[d, 900], g.c[d, 915]
        print(f"   {dstr}: 8:30->14:00 {c14 - o:+7.1f} pts, 14:00->15:00 {c15 - c14:+6.1f}, 15:00->15:15 {c1515 - c15:+6.1f}"
              f" (15-day ATR {atr[d]:.0f})")
    print("   One event: can't be tested as a strategy (the next one depends on Nasdaq's concentration rule being hit).")
