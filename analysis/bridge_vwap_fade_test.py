"""The Bridge's OFB_VWAPFade_SIG: fade the Globex VWAP 2-sigma bands (user's paste), 2026-10-13.

Rules (1-minute chart, Central time = the code's ET inputs -1 h): Globex VWAP from 17:00 CT (Mode 3) and its
volume-weighted sigma; a close above VWAP + 2 sigma -> short next bar at market, below VWAP - 2 sigma -> long; only
when flat and between 8:30 and 14:00 CT; take profit = limit at VWAP +/- 1 sigma (re-set every bar), no stop; time
exit after 60 bars; flat at 14:00 (FlatAtEnd). VWAP / sigma rebuilt from 1-minute bars ((H+L+C)/3 x volume);
checked against the Bridge's tape-exact RTH values exported earlier: VWAP within 0.1 point (median), sigma 0.99x.
Per NQ after $7.25 + 1 tick per market fill (the target is a limit).
  python3 analysis/bridge_vwap_fade_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25


def globex_vwap(g):
    """VWAP and sigma per minute of each trading row, accumulated from 17:01 CT of the previous calendar row."""
    tp = np.nan_to_num((g.h + g.l + g.c) / 3); v = np.nan_to_num(g.v)
    V = np.full((g.D, 1440), np.nan); S = V.copy()
    a = jof(1701)
    for d in g.trading:
        x = np.r_[tp[d - 1, a:], tp[d]]; w = np.r_[v[d - 1, a:], v[d]]
        cw = np.cumsum(w); cpv = np.cumsum(w * x); cpv2 = np.cumsum(w * x * x)
        with np.errstate(all="ignore"):
            vw = cpv / cw; sd = np.sqrt(np.maximum(cpv2 / cw - vw ** 2, 0))
        n0 = 1440 - a
        V[d], S[d] = vw[n0:], sd[n0:]
    return V, S


def run(g, V, S, dev=2.0, tpdev=1.0, max_bars=60, start=830, end=1400, flat=True, longs=True, shorts=True,
        stop_sd=None, rand=None):
    ts = pd.DatetimeIndex(g.ts); rng = np.random.default_rng(rand) if rand is not None else None
    out = []; js, je = jof(start), jof(end)
    for d in g.trading:
        if ts[d].year < 2018: continue
        o, h, l, c = g.o[d], g.h[d], g.l[d], g.c[d]
        pos = None; pend = 0
        for j in range(js - 1, jof(1500) + 1):
            if np.isnan(c[j]): continue
            vw, sd = V[d, j], S[d, j]
            # fills during bar j
            if pend and not np.isnan(o[j]):
                e = o[j] + pend * TICK; pos = dict(side=pend, e=e, j0=j, bars=0, x=None); pend = 0
            elif pos is not None and pos["x"] is not None:
                px = o[j] - pos["side"] * TICK
                out.append(dict(day=d, date=ts[d], side=pos["side"], j0=pos["j0"], j1=j, entry=pos["e"], exit=px, kind=2, slips=0,
                                net=(px - pos["e"]) * pos["side"] * PV - COST, why=pos["x"])); pos = None
            elif pos is not None and pos.get("tp") is not None:
                s = pos["side"]; tpx = pos["tp"]
                if stop_sd is not None and ((l[j] <= pos["stop"]) if s > 0 else (h[j] >= pos["stop"])):
                    px = (min(o[j], pos["stop"]) if s > 0 else max(o[j], pos["stop"])) - s * TICK
                    out.append(dict(day=d, date=ts[d], side=s, j0=pos["j0"], j1=j, entry=pos["e"], exit=px, kind=0, slips=0,
                                    net=(px - pos["e"]) * s * PV - COST, why="stop")); pos = None
                elif (h[j] >= tpx) if s > 0 else (l[j] <= tpx):
                    px = max(o[j], tpx) if s > 0 else min(o[j], tpx)
                    out.append(dict(day=d, date=ts[d], side=s, j0=pos["j0"], j1=j, entry=pos["e"], exit=px, kind=1, slips=0,
                                    net=(px - pos["e"]) * s * PV - COST, why="target")); pos = None
            if np.isnan(vw) or not sd > 0: continue
            t = (j // 60) * 100 + j % 60
            # bar-close logic
            if pos is None and not pend and js <= j < je:
                if shorts and c[j] > vw + dev * sd: pend = -1
                elif longs and c[j] < vw - dev * sd: pend = 1
                if pend and rng is not None: pend = int(rng.choice([-1, 1]))
            elif pos is not None:
                s = pos["side"]
                pos["tp"] = vw - tpdev * sd if s > 0 else vw + tpdev * sd       # long TP at VWAP - 1 sigma, short at + 1 sigma
                if stop_sd is not None and "stop" not in pos:
                    pos["stop"] = vw - stop_sd * sd if s > 0 else vw + stop_sd * sd
                if j > pos["j0"]: pos["bars"] += 1
                if pos["bars"] >= max_bars - 1: pos["x"] = "time"
                if flat and j >= je: pos["x"] = "eod"
        if pos is not None:
            r = c[:jof(1500) + 1]; okj = np.flatnonzero(~np.isnan(r)); px = r[okj[-1]] - pos["side"] * TICK
            out.append(dict(day=d, date=ts[d], side=pos["side"], j0=pos["j0"], j1=int(okj[-1]), entry=pos["e"], exit=px, kind=2,
                            slips=0, net=(px - pos["e"]) * pos["side"] * PV - COST, why="close"))
    return pd.DataFrame(out)


def line(t, nm, w=44):
    if len(t) < 3: return f"{nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    a, b = x[y < 2023], x[y >= 2023]
    return (f"{nm:<{w}} n={len(x):5d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f} t={x.mean() / x.std() * np.sqrt(len(x)):5.1f}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${a.mean():4.0f} | 23-26 ${b.mean():4.0f} | L ${x[t.side > 0].mean():4.0f} S ${x[t.side < 0].mean():4.0f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    V, S = globex_vwap(g)
    print(__doc__.split("\n")[0])
    base = run(g, V, S)
    print("\n1. Defaults (2 sigma in, 1 sigma out, no stop, 60 bars, 8:30-14:00 CT):")
    print(line(base, "defaults"))
    print(f"   exits: {base.why.value_counts(normalize=True).round(2).to_dict()}; trades a year {len(base) / base.date.dt.year.nunique():.0f};"
          f" worst trade ${base.net.min():,.0f}")
    print("   by year:", base.groupby(base.date.dt.year).net.sum().round(0).astype(int).to_dict())
    L_, S_ = base[base.side > 0], base[base.side < 0]
    print(line(L_, "  longs (below -2 sigma)")); print(line(S_, "  shorts (above +2 sigma)"))
    pl = [run(g, V, S, rand=r).net.mean() for r in range(5)]
    print(f"   placebo (same entry bars, random side, 5 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f}) vs ${base.net.mean():.0f}")

    print("\n2. Variants:")
    VR = {}
    for nm, kw in (("entry 2.5 sigma", dict(dev=2.5)), ("entry 3 sigma", dict(dev=3.0)), ("target at VWAP", dict(tpdev=0.0)),
                   ("target 1.5 sigma", dict(tpdev=1.5)), ("time exit 30 bars", dict(max_bars=30)), ("time exit 120 bars", dict(max_bars=120)),
                   ("stop at 3 sigma", dict(stop_sd=3.0)), ("stop at 3.5 sigma", dict(stop_sd=3.5)), ("entries from 9:00", dict(start=900)),
                   ("3 sigma, target VWAP, stop 4 sigma", dict(dev=3.0, tpdev=0.0, stop_sd=4.0))):
        VR[nm] = run(g, V, S, **kw); print(line(VR[nm], nm))

    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print("\n3. Standard metrics per NQ (defaults):")
    rows = {"all": (dl(base), base.net), "longs": (dl(L_), L_.net), "shorts": (dl(S_), S_.net)}
    print(M.table(rows))
    bt, pm = R.report({f"{k} 2023+": v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}, n=3000); print(bt); print(pm)

    print("\n4. Funded bench (8-strategy plan):")
    from bridge_monday_confirm import load_bridge_mc
    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    best = max(VR.items(), key=lambda kv: kv[1].net.mean() / kv[1].net.std() * np.sqrt(len(kv[1])))
    lab.add("VWF", base, slippage=False); lab.add("VWF_BEST", best[1], slippage=False)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500),
            "VCS_MC": 1, "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    for nm, p in (("current plan", plan), ("+ VWAP fade defaults 1 MNQ", {**plan, "VWF": 1}),
                  (f"+ best variant ({best[0]}) 1 MNQ", {**plan, "VWF_BEST": 1})):
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<52} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
