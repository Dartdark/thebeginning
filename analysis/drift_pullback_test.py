"""DriftPullback v2.1 (Francesco Agnello, shared in The Bridge's Strategies Feedbacks; user's paste), 2026-10-13.

Python replica on the 1-minute NQ grid, Central time (the code's defaults):
  15-min signal bars (24 h): session VWAP of (H+L+C)/3 x volume over the 15-min bars closing 8:45-15:00, reset
  at midnight, frozen inside each 15-min bar; drift = 15-min close vs 4 bars back (%). At each 15-min close: arm
  long if close > VWAP, VWAP rising (vs the previous 15-min boundary) and drift >= +0.10%; arm short mirrored;
  otherwise disarm. An arm also expires after 6 five-minute bars and is used up by an entry.
  5-min execution bars: armed long and a red 5-min bar (close < open) -> buy the next bar at market (short: armed
  short and a green bar); only bars closing 9:30-14:25; at most 4 trades and 2 losses a day; flat; 1 contract.
  Exits from the bar after the entry bar (MultiCharts places them at the entry bar's close): long stop 80 /
  target 40 points, short stop 80 / target 50; the stop carries the code's 2 ticks of extra slippage; market
  flat at the open of the 15:00 bar (FlatTime 1455); on early closes at the session's last bar. Fills inside the 5-min bars on 1-minute bars (Bar
  Magnifier); if one minute touches both, the stop counts first.
Costs: $7.25 per NQ + 1 tick on market entries and the flat exit; stops: the code's 2 ticks; targets: limits.
  python3 analysis/drift_pullback_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25
DEF = dict(drift=0.10, dlen=4, window=6, lsl=80.0, ltp=40.0, ssl=80.0, stp=50.0, slip_ticks=2, longs=True,
           shorts=True, max_tr=4, max_loss=2, start=930, end=1430, flat=1455, anchor=2, malen=20, exit_atr=None, through=0.0)


def prep(g):
    b15, b5 = g.bars(15), g.bars(5)
    c15 = b15["c"].ravel(); ok = np.flatnonzero(~np.isnan(c15))
    pos = np.full(len(c15), -1); pos[ok] = np.arange(len(ok))           # index in the series of existing 15-min bars
    seq = c15[ok]
    return dict(b15=b15, b5=b5, pos=pos, seq=seq, per15=1440 // 15)


def run(g, P, rand=None, **kw):
    p = {**DEF, **kw}
    b15, b5, pos, seq = P["b15"], P["b5"], P["pos"], P["seq"]
    ts = pd.DatetimeIndex(g.ts); rng = np.random.default_rng(rand) if rand is not None else None
    slip = p["slip_ticks"] * TICK
    atr5 = None
    if p["exit_atr"] is not None:          # ATR(14) of 5-min bars, frozen at entry
        h5, l5, c5 = b5["h"].ravel(), b5["l"].ravel(), b5["c"].ravel()
        okk = ~np.isnan(c5); idx = np.flatnonzero(okk)
        pc = np.r_[np.nan, c5[idx][:-1]]
        tr = np.nanmax(np.c_[h5[idx] - l5[idx], np.abs(h5[idx] - pc), np.abs(l5[idx] - pc)], 1)
        a = pd.Series(tr).rolling(14).mean().to_numpy(); atr5 = np.full(len(c5), np.nan); atr5[idx] = a
    out = []
    for d in g.trading:
        if ts[d].year < 2018: continue
        spv = svol = vw = vlast = vprev = 0.0
        armL = armS = False; armed_bars = 0
        trades = losses = 0
        pos_ = None; pend = None; flat_pend = False
        for i5 in range(jof(835) // 5, jof(1505) // 5 + 1):          # 5-min bars closing 8:35 .. 15:05
            j = i5 * 5; t = (j // 60) * 100 + j % 60
            mins = range(j - 4, j + 1)
            o5, c5 = b5["o"][d, i5], b5["c"][d, i5]
            # ---- fills during this bar ----
            if pend is not None:
                k0 = next((m for m in mins if not np.isnan(g.o[d, m])), None)
                if k0 is not None:
                    side = pend[0]; e = g.o[d, k0] + side * TICK
                    if p["exit_atr"] is not None:
                        av = pend[1]
                        sl = (p["exit_atr"][0] if side > 0 else p["exit_atr"][2]) * av
                        tp = (p["exit_atr"][1] if side > 0 else p["exit_atr"][3]) * av
                    else:
                        sl, tp = (p["lsl"], p["ltp"]) if side > 0 else (p["ssl"], p["stp"])
                    efill = e - side * TICK                                  # MC's EntryPrice (before our slippage)
                    pos_ = dict(side=side, e=e, stop=efill - side * (sl + slip), tgt=efill + side * tp, bar=i5, j0=k0)
                pend = None
            elif pos_ is not None and flat_pend:
                k0 = next((m for m in mins if not np.isnan(g.o[d, m])), None)
                if k0 is not None:
                    px = g.o[d, k0] - pos_["side"] * TICK
                    out.append(dict(day=d, date=ts[d], side=pos_["side"], j0=pos_["j0"], j1=k0, entry=pos_["e"], exit=px,
                                    kind=2, slips=0, net=(px - pos_["e"]) * pos_["side"] * PV - COST))
                    trades_closed = out[-1]; pos_ = None
                    if trades_closed["net"] < 0: losses += 1
                flat_pend = False
            elif pos_ is not None and pos_["bar"] < i5:
                s = pos_["side"]
                for m in mins:
                    if np.isnan(g.h[d, m]): continue
                    hit_s = (g.l[d, m] <= pos_["stop"]) if s > 0 else (g.h[d, m] >= pos_["stop"])
                    hit_t = (g.h[d, m] >= pos_["tgt"] + p["through"]) if s > 0 else (g.l[d, m] <= pos_["tgt"] - p["through"])
                    if hit_s:
                        px = min(g.o[d, m], pos_["stop"]) if s > 0 else max(g.o[d, m], pos_["stop"]); kind = 0
                    elif hit_t:
                        px = max(g.o[d, m], pos_["tgt"]) if s > 0 else min(g.o[d, m], pos_["tgt"]); kind = 1
                    else: continue
                    out.append(dict(day=d, date=ts[d], side=s, j0=pos_["j0"], j1=m, entry=pos_["e"], exit=px, kind=kind,
                                    slips=0, net=(px - pos_["e"]) * s * PV - COST))
                    if out[-1]["net"] < 0: losses += 1
                    pos_ = None; break
            if np.isnan(c5): continue
            # ---- bar-close logic ----
            if j % 15 == 0:                                                   # a new 15-min bar
                vprev = vlast
                if p["anchor"] == 2:
                    if 830 < t <= 1500 and not np.isnan(b15["c"][d, j // 15]):
                        h, l, c, v = (b15[x][d, j // 15] for x in ("h", "l", "c", "v"))
                        spv += (h + l + c) / 3 * v; svol += v
                    if svol > 0: vw = spv / svol
                vlast = vw
                k = pos[d * P["per15"] + j // 15]
                if k >= p["dlen"]:
                    c2 = seq[k]; drift = (c2 - seq[k - p["dlen"]]) / seq[k - p["dlen"]] * 100
                    if p["anchor"] == 2:
                        ma, mp = vlast, (vprev if vprev > 0 else vlast)
                    else:                                                     # anchor 0: SMA of 15-min closes
                        ma = seq[k - p["malen"] + 1:k + 1].mean(); mp = seq[k - p["malen"]:k].mean()
                    if ma > 0 and c2 > ma and ma > mp and drift >= p["drift"]:
                        armL, armS, armed_bars = True, False, 0
                    elif ma > 0 and c2 < ma and ma < mp and drift <= -p["drift"]:
                        armS, armL, armed_bars = True, False, 0
                    else:
                        armL = armS = False
            if armL or armS:
                armed_bars += 1
                if armed_bars > p["window"]: armL = armS = False
            if pos_ is None and pend is None and p["start"] <= t < p["end"] and trades < p["max_tr"] and losses < p["max_loss"]:
                side = 0
                if p["longs"] and armL and c5 < o5: side = 1; armL = False
                elif p["shorts"] and armS and c5 > o5: side = -1; armS = False
                if side:
                    if rng is not None: side = int(rng.choice([-1, 1]))
                    av = atr5[d * 288 + i5] if atr5 is not None else None
                    pend = (side, av); trades += 1
            if pos_ is not None and t >= p["flat"]: flat_pend = True
        if pos_ is not None:                     # early closes / holidays: SetExitOnClose at the session's last bar
            r = g.c[d, :jof(1505) + 1]; okj = np.flatnonzero(~np.isnan(r)); jx = okj[-1]
            px = r[jx] - pos_["side"] * TICK
            out.append(dict(day=d, date=ts[d], side=pos_["side"], j0=pos_["j0"], j1=max(int(jx), pos_["j0"]), entry=pos_["e"],
                            exit=px, kind=2, slips=0, net=(px - pos_["e"]) * pos_["side"] * PV - COST))
    return pd.DataFrame(out)


def line(t, nm, w=46):
    if len(t) < 3: return f"{nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    a, b = x[y < 2023], x[y >= 2023]
    return (f"{nm:<{w}} n={len(x):5d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf:.2f} t={x.mean() / x.std() * np.sqrt(len(x)):4.1f}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${a.mean():4.0f} PF {a[a > 0].sum() / max(1e-9, -a[a < 0].sum()):.2f}"
            f" | 23-26 ${b.mean():4.0f} PF {b[b > 0].sum() / max(1e-9, -b[b < 0].sum()):.2f} | L ${x[t.side > 0].mean():4.0f} S ${x[t.side < 0].mean():4.0f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); P = prep(g)
    print(__doc__.split("\n")[0])
    base = run(g, P)
    print("\n1. Defaults (session-VWAP anchor, drift 0.10%, long 80/40, short 80/50, 9:30-14:30 CT):")
    print(line(base, "defaults"))
    print(f"   exits: stop {np.mean(base.kind == 0):.0%}, target {np.mean(base.kind == 1):.0%}, flat {np.mean(base.kind == 2):.0%};"
          f" trades a year {len(base) / base.date.dt.year.nunique():.0f}")
    print("   by year:", base.groupby(base.date.dt.year).net.sum().round(0).astype(int).to_dict())
    L_, S_ = base[base.side > 0], base[base.side < 0]
    print(line(L_, "  longs")); print(line(S_, "  shorts"))
    for nm, q in (("longs", L_), ("shorts", S_)):
        print(f"   {nm} by year:", q.groupby(q.date.dt.year).net.sum().round(0).astype(int).to_dict())
    pl = [run(g, P, rand=r) for r in range(10)]
    print(f"   placebo (same entry bars, random side with that side's stop / target, 10 runs): ${np.mean([x.net.mean() for x in pl]):.0f}"
          f" ({min(x.net.mean() for x in pl):.0f}..{max(x.net.mean() for x in pl):.0f}) vs ${base.net.mean():.0f}")
    plL = [x[x.side > 0].net.mean() for x in pl]; plS = [x[x.side < 0].net.mean() for x in pl]
    print(f"   placebo longs ${np.mean(plL):.0f}, shorts ${np.mean(plS):.0f}")

    print("\n2. Neighbours (one change at a time):")
    var = [("drift 0.05%", dict(drift=0.05)), ("drift 0.15%", dict(drift=0.15)), ("drift 0.20%", dict(drift=0.20)),
           ("stop 60", dict(lsl=60, ssl=60)), ("stop 100", dict(lsl=100, ssl=100)),
           ("targets 30 / 40", dict(ltp=30, stp=40)), ("targets 50 / 60", dict(ltp=50, stp=60)), ("targets 60 / 75", dict(ltp=60, stp=75)),
           ("start 8:45 (incl. first hour)", dict(start=845)), ("no daily caps", dict(max_tr=99, max_loss=99)),
           ("anchor 0: SMA(20) of 15-min closes", dict(anchor=0)),
           ("ExitMode 1: ATR 3.0 / 1.5, 3.0 / 1.9", dict(exit_atr=(3.0, 1.5, 3.0, 1.9))),
           ("targets must trade through by 1 tick", dict(through=0.25)), ("targets through by 1 point", dict(through=1.0))]
    VR = {}
    for nm, kw in var:
        VR[nm] = run(g, P, **kw); print(line(VR[nm], nm))

    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print("\n3. Standard metrics per NQ (defaults):")
    rows = {"all": (dl(base), base.net), "longs": (dl(L_), L_.net), "shorts": (dl(S_), S_.net)}
    print(M.table(rows))
    b, pm = R.report({f"{k} 2023+": v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}, n=3000); print(b); print(pm)

    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    for nm, t in (("DPB", base), ("DPB_L", L_.reset_index(drop=True)), ("DPB_S", S_.reset_index(drop=True))):
        lab.add(nm, t, slippage=False)
    dts = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts.year >= 2018
    C = pd.DataFrame({k: lab.daily(k) for k in ("DPB", "DPB_L", "DPB_S", "VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "VCS_MC")}, index=dts)[mk]
    print("\n4. Daily correlation with the plan:")
    print(C.corr().round(2).loc[["DPB", "DPB_L", "DPB_S"], ["VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "VCS_MC"]].to_string())
    print("\n5. Funded bench (current 8-strategy plan; the Bridge Monday Long added from its MC trades):")
    from bridge_monday_confirm import load_bridge_mc
    lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500),
            "VCS_MC": 1, "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    for nm, pl_ in (("current plan", plan), ("+ DriftPullback 1 MNQ", {**plan, "DPB": 1}), ("+ DriftPullback 2 MNQ", {**plan, "DPB": 2}),
                    ("+ longs only 1 MNQ", {**plan, "DPB_L": 1}), ("+ shorts only 1 MNQ", {**plan, "DPB_S": 1})):
        a, c = lab.score(pl_, 250, **CS), lab.score(pl_, 500, **CS)
        print(f"   {nm:<26} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
    pickle.dump(dict(base=base, VR=VR), open(SP + "drift_pullback.pkl", "wb"))
