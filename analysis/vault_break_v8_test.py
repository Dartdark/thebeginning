"""VaultBreak v8 (longs only; the Bridge's version, user's paste) vs our Vault Break v1, 2026-10-13.

One 30-minute-bar engine on the 1-minute NQ grid (fills inside the bars on 1-minute bars = Bar Magnifier),
Central time, sessions = calendar dates from the 00:00 bar (as MultiCharts' Date <> Date[1]):
  entry      30-min close > session open + 0.30 x boundary ATR and > VWAP from 00:00, bars closing 10:00-14:00
             (Time < 14:30), max 3 a day, buy the next bar at market; target 40 / stop 75 points from the fill.
  v1 (ours)  boundary ATR = 15-day average TRUE RANGE of weekday dates; CME holiday half-days: entries until
             11:00, flat 11:30; time exit at the close of the 14:30 bar.
  v8         boundary ATR = 15-session average of each date's high - low, every date with bars (Sunday evenings
             included); VWAP exit: 7 consecutive 30-min closes below VWAP -> sell next bar; time exit at the
             open of the bar after 14:30; no holiday times (carry guard).
Validation: the v1 engine against the MultiCharts VB v1 trade list (the plan's Vault Break).
Costs per NQ: $7.25 + 1 tick per market / stop fill (targets are limits).
  python3 analysis/vault_break_v8_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from candidates24 import _early
from portfolio import load_mc
from funded_lab import with_slippage
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25
VB_FILE = "mc_reports/Backtesting Strategy Performance Report VB v1.xlsx"


def boundary(g, kind):
    """ATR known at the start of each calendar row. kind 'tr' = v1 (weekday true range, 15 days);
    'range' = v8 (high - low of every date with bars, 15 sessions)."""
    has = ~np.isnan(g.c).all(1)
    with np.errstate(all="ignore"):
        hi, lo = np.nanmax(g.h, 1), np.nanmin(g.l, 1)
    last = np.array([r[~np.isnan(r)][-1] if ok else np.nan for r, ok in zip(g.c, has)])
    out = np.full(g.D, np.nan); hist = []; prev_close = np.nan
    wk = pd.DatetimeIndex(g.ts).dayofweek < 5
    for d in range(g.D):
        if len(hist) >= 15: out[d] = np.mean(hist[-15:])
        if not has[d]: continue
        if kind == "tr":
            if wk[d]:
                tr = (max(hi[d], prev_close) - min(lo[d], prev_close)) if not np.isnan(prev_close) else hi[d] - lo[d]
                hist.append(tr)
            prev_close = last[d]
        else:
            if hi[d] - lo[d] > 0: hist.append(hi[d] - lo[d])
    return out


def run(g, version="v8", atr_kind=None, vwap_exit=None, time_exit=None, holidays=None, mult=0.30, tp=40.0, sl=75.0,
        first=1000, flat=1430, max_tr=3, years=(2018, 2026)):
    v8 = version == "v8"
    atr_kind = atr_kind or ("range" if v8 else "tr")
    vwap_exit = (7 if v8 else 0) if vwap_exit is None else vwap_exit
    time_exit = time_exit or ("next_open" if v8 else "close")
    holidays = (not v8) if holidays is None else holidays
    B = boundary(g, atr_kind); b = g.bars(30); early = _early(g)
    ts = pd.DatetimeIndex(g.ts); tset = set(g.trading); out = []
    for d in range(1, g.D):
        if not (years[0] <= ts[d].year <= years[1]) or d not in tset or np.isnan(B[d]): continue
        o, c, v, h, l = b["o"][d], b["c"][d], b["v"][d], b["h"][d], b["l"][d]
        okb = np.flatnonzero(~np.isnan(c))
        if len(okb) == 0: continue
        sess_open = o[okb[0]]; noise = sess_open + mult * B[d]
        last_e, flat_t = (1100, 1130) if (holidays and early[d]) else (flat, flat)
        tpv = vol = 0.0; below = 0; ntr = 0; pos = None; pend = False; xpend = False
        for i in okb:
            j = i * 30; t = (j // 60) * 100 + j % 60
            mins = range(max(j - 29, 0), j + 1)
            # fills inside this bar
            if pend:
                m0 = next((m for m in mins if not np.isnan(g.o[d, m])), None)
                if m0 is not None:
                    e = g.o[d, m0] + TICK; ef = e - TICK
                    pos = dict(e=e, stop=ef - sl, tgt=ef + tp, j0=m0, first=m0)
                pend = False
            if pos is not None and xpend:
                m0 = next((m for m in mins if not np.isnan(g.o[d, m])), None)
                px = g.o[d, m0] - TICK
                out.append(dict(day=d, date=ts[d], side=1, j0=pos["j0"], j1=m0, entry=pos["e"], exit=px, kind=2, slips=0,
                                net=(px - pos["e"]) * PV - COST, why=xpend)); pos = None; xpend = False
            if pos is not None:
                for m in mins:
                    if m < pos["first"] or np.isnan(g.h[d, m]): continue
                    if g.l[d, m] <= pos["stop"]:
                        px = min(g.o[d, m], pos["stop"]) - TICK if m > pos["first"] else pos["stop"] - TICK; kind = 0
                    elif g.h[d, m] >= pos["tgt"]:
                        px = max(g.o[d, m], pos["tgt"]) if m > pos["first"] else pos["tgt"]; kind = 1
                    else: continue
                    out.append(dict(day=d, date=ts[d], side=1, j0=pos["j0"], j1=m, entry=pos["e"], exit=px, kind=kind, slips=0,
                                    net=(px - pos["e"]) * PV - COST, why="bracket")); pos = None; break
            # bar close
            if v[i] > 0:
                tpv += (h[i] + l[i] + c[i]) / 3 * v[i]; vol += v[i]
            vw = tpv / vol if vol > 0 else c[i]
            below = below + 1 if c[i] < vw else 0
            if pos is None and not pend and c[i] > noise and c[i] > vw and first <= t < last_e and ntr < max_tr:
                pend = True; ntr += 1
            if pos is not None:
                if vwap_exit and below >= vwap_exit: xpend = "vwap"
                if t >= flat_t:
                    if time_exit == "close":
                        px = c[i] - TICK
                        out.append(dict(day=d, date=ts[d], side=1, j0=pos["j0"], j1=j, entry=pos["e"], exit=px, kind=2, slips=0,
                                        net=(px - pos["e"]) * PV - COST, why="time")); pos = None; xpend = False
                    else:
                        xpend = "time"
        if pos is not None:                                   # end of the date (holiday sessions): out at the last bar
            jl = okb[-1] * 30; px = c[okb[-1]] - TICK
            out.append(dict(day=d, date=ts[d], side=1, j0=pos["j0"], j1=jl, entry=pos["e"], exit=px, kind=2, slips=0,
                            net=(px - pos["e"]) * PV - COST, why="carry"))
    return pd.DataFrame(out)


def line(t, nm, w=50):
    if len(t) < 3: return f"{nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    a, b = x[y < 2023], x[y >= 2023]
    return (f"{nm:<{w}} n={len(x):5d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f} t={x.mean() / x.std() * np.sqrt(len(x)):4.1f}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${a.mean():4.0f} PF {pf(a):.2f} | 23-26 ${b.mean():4.0f} PF {pf(b):.2f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    print(__doc__.split("\n")[0])
    mc = with_slippage(load_mc(g, VB_FILE)); mc["net"] = (mc.exit - mc.entry) * mc.side * PV - COST
    mc["date"] = pd.DatetimeIndex(g.ts[mc.day.values]); mc = mc[mc.date.dt.year >= 2018].reset_index(drop=True)
    v1 = run(g, "v1"); v8 = run(g, "v8")
    print("\n1. Validation: our v1 in this engine vs the MultiCharts VB v1 trade list")
    print(line(mc, "MultiCharts VB v1")); print(line(v1, "engine, v1 settings"))
    k = lambda t: set(zip(t.day, t.j0 // 30))
    a, b_ = k(mc), k(v1)
    print(f"   same entry (day, 30-min bar): {len(a & b_)} of {len(a)} MC / {len(b_)} engine trades")
    m = pd.merge(mc.assign(k=mc.j0 // 30), v1.assign(k=v1.j0 // 30), on=["day", "k"], suffixes=("_mc", "_py"))
    print(f"   matched trades: P&L correlation {np.corrcoef(m.net_mc, m.net_py)[0, 1]:.3f}, mean |diff| ${np.mean(np.abs(m.net_mc - m.net_py)):.0f}")

    print("\n2. v8 vs v1, and each v8 change on its own (added to v1):")
    print(line(v8, "v8 (Bridge, as pasted)"))
    print(f"   v8 exits: {v8.why.value_counts(normalize=True).round(2).to_dict()}")
    var = {"v1 + v8 boundary (H-L, all sessions)": dict(version="v1", atr_kind="range"),
           "v1 + VWAP exit (7 bars)": dict(version="v1", vwap_exit=7),
           "v1 + time exit next bar open": dict(version="v1", time_exit="next_open"),
           "v1 without holiday times": dict(version="v1", holidays=False),
           "v8 without the VWAP exit": dict(version="v8", vwap_exit=0),
           "v8 VWAP exit 4 bars": dict(version="v8", vwap_exit=4),
           "v8 VWAP exit 10 bars": dict(version="v8", vwap_exit=10)}
    VR = {}
    for nm, kw in var.items():
        VR[nm] = run(g, **kw); print(line(VR[nm], nm))
    for nm, t in (("MC v1", mc), ("v8", v8)):
        print(f"   {nm} by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    same = len(k(v8) & k(v1))
    print(f"   v8 and v1 share {same} entries (v8 {len(v8)}, v1 {len(v1)})")

    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print("\n3. Standard metrics per NQ (longs only, so longs = all):")
    rows = {"MC VB v1": (dl(mc), mc.net), "engine v1": (dl(v1), v1.net), "v8": (dl(v8), v8.net)}
    print(M.table(rows))
    bt, pm = R.report({f"{k_} 2023+": v[0][v[0].index >= "2023-01-01"] for k_, v in rows.items() if k_ != "engine v1"}, n=3000)
    print(bt); print(pm)
    print(f"   daily correlation v8 vs MC v1: {np.corrcoef(dl(v8), dl(mc))[0, 1]:.2f}")

    print("\n4. Funded bench (8-strategy plan; Vault Break 3 MNQ swapped):")
    from bridge_monday_confirm import load_bridge_mc
    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    lab.add("VB8", v8, slippage=False); lab.add("VB1_PY", v1, slippage=False)
    lab.add("VB8_NOVW", VR["v8 without the VWAP exit"], slippage=False)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500),
            "VCS_MC": 1, "MON_BR_MC": 1}
    base = {k_: v for k_, v in plan.items() if k_ != "VB"}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    for nm, pl in (("current plan (MC VB v1 3 MNQ)", plan), ("engine v1 3 MNQ (check)", {**base, "VB1_PY": 3}),
                   ("v8 3 MNQ", {**base, "VB8": 3}), ("v8 2 MNQ", {**base, "VB8": 2}), ("v8 4 MNQ", {**base, "VB8": 4}),
                   ("v8 without VWAP exit 3 MNQ", {**base, "VB8_NOVW": 3})):
        a, c = lab.score(pl, 250, **CS), lab.score(pl, 500, **CS)
        print(f"   {nm:<32} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")

    print("\n5. Combine (VB 8 MNQ + ONB ADX30 $1,100, 21 trading days, every start day, with slippage):")
    from portfolio import paths, challenge
    tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year; atr = g.daily_atr(15)
    on = with_slippage(load_mc(g, "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx"))
    w, r = paths(g, on); Ow, Oc = w[tr] / 10, r[tr] / 10
    q = np.floor(1100 / (0.25 * np.nan_to_num(atr[tr], nan=1e12) * 2))[:, None]
    for nm, t in (("VB v1 (MC)", with_slippage(load_mc(g, VB_FILE))), ("VB v8", v8)):
        w, r = paths(g, t); Vw, Vc = w[tr] / 10, r[tr] / 10
        res = [challenge(Vw * 8 + Ow * q, Vc * 8 + Oc * q, np.arange(s, min(s + 21, D))) for s in range(D)]
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        print(f"   {nm:<12} pass {np.nanmean(o[yr >= 2018]):.1%} | 2023-26 {np.nanmean(o[yr >= 2023]):.1%}")
    pickle.dump(dict(v1=v1, v8=v8, VR=VR), open(SP + "vb8.pkl", "wb"))
