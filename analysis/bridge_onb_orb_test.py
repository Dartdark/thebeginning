"""The Bridge's OFB_OvernightBiasORB_Signal vs our Overnight Bias (ADX30 combine / ML v2 funded), 2026-10-13.

Python replica on 15-minute bars of the 1-minute grid (fills on 1-minute bars = Bar Magnifier), Central time
(the code's ET inputs -1 h: SessStart 8:30, OREnd 8:45, LastEntry 12:00, FlatTime 14:30, SessEnd 15:00):
  overnight range = 15-min bars from the date's first bar (00:00) to the 8:30 bar; bias from the 8:45 bar's open:
  >= 0.67 of the range long-only, <= 0.33 short-only. Opening range = the 8:45 bar. From the 9:00 bar to 12:00:
  a 15-min CLOSE beyond the opening range on the bias side -> next bar at market, if ADX(16) >= 20, the signal
  bar's range <= 2.5 x the average of the previous 20 bars, and the opening range <= 2 x its 20-day EMA (checked
  before today's update; off for the first 20 days). Stop = signal close -/+ 0.30 x ATR_ref (15-day average true
  range of the REGULAR session 8:31-15:00 with the previous regular close), target 3x; up to 4 trades a day, one
  at a time; flat at the open of the bar after 14:30.
Per NQ after $7.25 + 1 tick per market / stop fill (targets are limits). Ours: the MultiCharts trade lists.
  python3 analysis/bridge_onb_orb_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from candidates24 import _continuous_adx
from portfolio import load_mc
from funded_lab import with_slippage
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25
ONB30 = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx"
ONBML = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx"
DEF = dict(adx_n=16, adx_min=20, bias_hi=0.67, bias_lo=0.33, skip_mult=2.5, bar_avg=20, or_max=2.0, or_days=20,
           k=0.30, atr_days=15, rr=3.0, last=1200, flat=1430, max_tr=4, atr_kind="rth", anchor="signal")


def rth_atr(g, n=15):
    """ATR_ref known at the start of each calendar row: average true range of the last n regular sessions."""
    out = np.full(g.D, np.nan); hist = []; pc = np.nan
    seg = slice(jof(831), jof(1500) + 1)
    for d in range(g.D):
        if len(hist) >= n: out[d] = np.mean(hist[-n:])
        h = g.h[d, seg]
        if np.isnan(h).all(): continue
        hi, lo = np.nanmax(h), np.nanmin(g.l[d, seg]); r = g.c[d, seg]; cl = r[~np.isnan(r)][-1]
        tr = hi - lo if np.isnan(pc) else max(hi - lo, abs(hi - pc), abs(lo - pc))
        hist.append(tr); pc = cl
    return out


def run(g, ctx, rand=None, **kw):
    p = {**DEF, **kw}
    b, A, avgr = ctx["b"], ctx["adx"][p["adx_n"]], ctx["avgr"]
    atr = ctx["rth"] if p["atr_kind"] == "rth" else ctx["day"]
    ts = pd.DatetimeIndex(g.ts); rng = np.random.default_rng(rand) if rand is not None else None
    i830, i845 = jof(830) // 15, jof(845) // 15
    ema = 0.0; cnt = 0; out = []; tset = set(g.trading)
    for d in range(g.D):
        if np.isnan(b["c"][d, i845]): continue
        orh, orl = b["h"][d, i845], b["l"][d, i845]
        # OR-size band (before today's update), then update the EMA
        ok_band = True
        if ema > 0: ok_band = (orh - orl) <= p["or_max"] * ema
        ema = (orh - orl) if ema == 0 else ema + 2 / (p["or_days"] + 1) * ((orh - orl) - ema)
        cnt += 1
        if cnt < p["or_days"]: ok_band = True
        if d not in tset or ts[d].year < 2018 or np.isnan(atr[d]): continue
        with np.errstate(all="ignore"):
            onh, onl = np.nanmax(b["h"][d, :i830 + 1]), np.nanmin(b["l"][d, :i830 + 1])
        op = b["o"][d, i845]
        if np.isnan(onh) or onh <= onl: continue
        pos_ = (op - onl) / (onh - onl)
        bias = 1 if pos_ >= p["bias_hi"] else (-1 if pos_ <= p["bias_lo"] else 0)
        if bias == 0 or not ok_band: continue
        sp = p["k"] * atr[d]
        ntr = 0; pos = None; pend = None; xpend = False
        for i in range(i845 + 1, jof(1500) // 15 + 1):
            j = i * 15; t = (j // 60) * 100 + j % 60
            mins = range(j - 14, j + 1)
            if pend is not None:                                     # entry fill at the bar's open
                m0 = next((m for m in mins if not np.isnan(g.o[d, m])), None)
                if m0 is not None:
                    side, sc = pend; e = g.o[d, m0] + side * TICK
                    anchor = sc if p["anchor"] == "signal" else e - side * TICK
                    pos = dict(side=side, e=e, stop=anchor - side * sp, tgt=anchor + side * p["rr"] * sp, j0=m0)
                pend = None
            if pos is not None and xpend:
                m0 = next((m for m in mins if not np.isnan(g.o[d, m])), None)
                px = g.o[d, m0] - pos["side"] * TICK
                out.append(dict(day=d, date=ts[d], side=pos["side"], j0=pos["j0"], j1=m0, entry=pos["e"], exit=px, kind=2,
                                slips=0, net=(px - pos["e"]) * pos["side"] * PV - COST)); pos = None; xpend = False
            if pos is not None:
                s = pos["side"]
                for m in mins:
                    if m < pos["j0"] or np.isnan(g.h[d, m]): continue
                    if (g.l[d, m] <= pos["stop"]) if s > 0 else (g.h[d, m] >= pos["stop"]):
                        px = ((min(g.o[d, m], pos["stop"]) if s > 0 else max(g.o[d, m], pos["stop"])) if m > pos["j0"] else pos["stop"]) - s * TICK; kind = 0
                    elif (g.h[d, m] >= pos["tgt"]) if s > 0 else (g.l[d, m] <= pos["tgt"]):
                        px = (max(g.o[d, m], pos["tgt"]) if s > 0 else min(g.o[d, m], pos["tgt"])) if m > pos["j0"] else pos["tgt"]; kind = 1
                    else: continue
                    out.append(dict(day=d, date=ts[d], side=s, j0=pos["j0"], j1=m, entry=pos["e"], exit=px, kind=kind, slips=0,
                                    net=(px - pos["e"]) * s * PV - COST)); pos = None; break
            c = b["c"][d, i]
            if np.isnan(c): continue
            # bar-close logic
            if pos is None and pend is None and t <= p["last"] and ntr < p["max_tr"] and A[d, i] >= p["adx_min"]:
                rng_ok = np.isnan(avgr[d, i]) or (b["h"][d, i] - b["l"][d, i]) <= p["skip_mult"] * avgr[d, i]
                brk = 1 if c > orh else (-1 if c < orl else 0)
                if brk == bias and rng_ok:
                    side = bias if rng is None else int(rng.choice([-1, 1]))
                    pend = (side, c); ntr += 1
            if pos is not None and t >= p["flat"]: xpend = True
        if pos is not None:
            r = g.c[d, :jof(1500) + 1]; okj = np.flatnonzero(~np.isnan(r)); px = r[okj[-1]] - pos["side"] * TICK
            out.append(dict(day=d, date=ts[d], side=pos["side"], j0=pos["j0"], j1=int(okj[-1]), entry=pos["e"], exit=px,
                            kind=2, slips=0, net=(px - pos["e"]) * pos["side"] * PV - COST))
    return pd.DataFrame(out)


def line(t, nm, w=46):
    if len(t) < 3: return f"{nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    a, b = x[y < 2023], x[y >= 2023]
    return (f"{nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f} t={x.mean() / x.std() * np.sqrt(len(x)):4.1f}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${a.mean():4.0f} PF {pf(a):.2f} | 23-26 ${b.mean():4.0f} PF {pf(b):.2f}"
            f" | L ${x[t.side > 0].mean():4.0f} S ${x[t.side < 0].mean():4.0f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    b = g.bars(15)
    hl = pd.Series((b["h"] - b["l"]).ravel()); okb = hl.notna()
    av = pd.Series(np.nan, index=hl.index); av[okb] = hl[okb].rolling(20).mean().shift(1).to_numpy()
    ctx = dict(b=b, adx={n: _continuous_adx(b, n) for n in (14, 16)}, avgr=av.to_numpy().reshape(b["c"].shape),
               rth=rth_atr(g), day=g.daily_atr(15))
    print(__doc__.split("\n")[0])
    br = run(g, ctx)
    on30 = with_slippage(load_mc(g, ONB30)); on30["net"] = (on30.exit - on30.entry) * on30.side * PV - COST
    onml = with_slippage(load_mc(g, ONBML)); onml["net"] = (onml.exit - onml.entry) * onml.side * PV - COST
    for t in (on30, onml): t["date"] = pd.DatetimeIndex(g.ts[t.day.values])
    on30, onml = on30[on30.date.dt.year >= 2018].reset_index(drop=True), onml[onml.date.dt.year >= 2018].reset_index(drop=True)

    print("\n1. As written vs ours (per NQ, 1 contract):")
    print(line(br, "Bridge ORB (Python replica)"))
    print(line(on30, "ours: ONB ADX30 (MC, combine)"))
    print(line(onml, "ours: ONB ML v2 (MC, funded)"))
    print(f"   Bridge exits: stop {np.mean(br.kind == 0):.0%}, target {np.mean(br.kind == 1):.0%}, time {np.mean(br.kind == 2):.0%};"
          f" trades a day when it trades {br.groupby('date').size().mean():.2f}; second+ trades of a day"
          f" ${br[br.duplicated('date')].net.mean():.0f} (n {br.duplicated('date').sum()})")
    for nm, t in (("Bridge", br), ("ONB ADX30", on30), ("ONB ML v2", onml)):
        print(f"   {nm} by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    for nm, t in (("Bridge longs", br[br.side > 0]), ("Bridge shorts", br[br.side < 0]),
                  ("ADX30 longs", on30[on30.side > 0]), ("ADX30 shorts", on30[on30.side < 0])):
        print(line(t, "  " + nm))
    pl = [run(g, ctx, rand=r) for r in range(10)]
    print(f"   placebo (same signal bars, random side, 10 runs): ${np.mean([x.net.mean() for x in pl]):.0f}"
          f" ({min(x.net.mean() for x in pl):.0f}..{max(x.net.mean() for x in pl):.0f}) vs ${br.net.mean():.0f}")

    print("\n2. Each Bridge difference undone on its own (toward ours):")
    var = [("1 trade a day", dict(max_tr=1)), ("ADX(14) > 30 (our combine gate)", dict(adx_n=14, adx_min=30.01)),
           ("ADX(14) >= 20", dict(adx_n=14)), ("no bar-range skip", dict(skip_mult=1e9)), ("no OR-size band", dict(or_max=1e9)),
           ("24-hour daily ATR (ours)", dict(atr_kind="day")), ("stop from the fill (ours)", dict(anchor="fill")),
           ("last entry 14:00 (ours)", dict(last=1400)), ("stop 0.25 ATR", dict(k=0.25)), ("bias thirds 0.6667 / 0.3333", dict(bias_hi=2 / 3, bias_lo=1 / 3))]
    VR = {}
    for nm, kw in var:
        VR[nm] = run(g, ctx, **kw); print(line(VR[nm], nm))

    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print("\n3. Standard metrics per NQ, 1 contract:")
    rows = {"Bridge ORB": (dl(br), br.net), "Bridge longs": (dl(br[br.side > 0]), br.net[br.side > 0]),
            "Bridge shorts": (dl(br[br.side < 0]), br.net[br.side < 0]), "ONB ADX30 (MC)": (dl(on30), on30.net), "ONB ML v2 (MC)": (dl(onml), onml.net)}
    print(M.table(rows))
    bt, pm = R.report({f"{k} 2023+": v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}, n=3000); print(bt); print(pm)
    print(f"   daily correlation Bridge vs ADX30 {np.corrcoef(dl(br), dl(on30))[0, 1]:.2f}, vs ML v2 {np.corrcoef(dl(br), dl(onml))[0, 1]:.2f}")

    print("\n4. Funded bench (8-strategy plan; Overnight Bias ML $400 swapped or the Bridge added, risk-sized at 0.30 x RTH ATR):")
    from bridge_monday_confirm import load_bridge_mc
    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    lab.add("BR_ORB", br, stop_pts=0.30 * ctx["rth"], slippage=False)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500),
            "VCS_MC": 1, "MON_BR_MC": 1}
    base = {k: v for k, v in plan.items() if k != "ONB_ML2_MC"}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    for nm, pl_ in (("current plan (ONB ML $400)", plan), ("Bridge ORB $400 instead", {**base, "BR_ORB": ("risk", 400)}),
                    ("Bridge ORB $300 instead", {**base, "BR_ORB": ("risk", 300)}), ("ONB ML $400 + Bridge ORB $200", {**plan, "BR_ORB": ("risk", 200)})):
        a, c = lab.score(pl_, 250, **CS), lab.score(pl_, 500, **CS)
        print(f"   {nm:<32} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")

    print("\n5. Combine (VB 8 MNQ + Overnight Bias at $1,100 risk, 21 trading days, every start day):")
    from portfolio import paths, challenge
    tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year
    vb = with_slippage(load_mc(g, "mc_reports/Backtesting Strategy Performance Report VB v1.xlsx")); w, r = paths(g, vb); Vw, Vc = w[tr] / 10, r[tr] / 10
    for nm, t, stop in (("ONB ADX30 (MC)", on30, 0.25 * ctx["day"]), ("Bridge ORB", br, 0.30 * ctx["rth"])):
        w, r = paths(g, t); Ow, Oc = w[tr] / 10, r[tr] / 10
        q = np.floor(1100 / (np.nan_to_num(stop[tr], nan=1e12) * 2))[:, None]
        res = [challenge(Vw * 8 + Ow * q, Vc * 8 + Oc * q, np.arange(s, min(s + 21, D))) for s in range(D)]
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        print(f"   {nm:<16} pass {np.nanmean(o[yr >= 2018]):.1%} | 2023-26 {np.nanmean(o[yr >= 2023]):.1%}")
    pickle.dump(dict(br=br, VR=VR), open(SP + "bridge_orb.pkl", "wb"))

    print("\n6. The Bridge's OR-size band (OR <= 2 x its 20-day EMA) applied to OUR trade lists:")
    i845 = jof(845) // 15; ema = 0.0; cnt = 0; band = {}
    for d in range(g.D):
        if np.isnan(b["c"][d, i845]): continue
        rg = b["h"][d, i845] - b["l"][d, i845]
        okb_ = True if ema == 0 or cnt < 20 else rg <= 2.0 * ema
        ema = rg if ema == 0 else ema + 2 / 21 * (rg - ema); cnt += 1; band[d] = okb_
    for nm, t, key, stop in (("ONB ADX30 (MC)", on30, "ONB30_BAND", None), ("ONB ML v2 (MC)", onml, "ONBML_BAND", 0.30 * ctx["day"])):
        k_ = t.day.map(band).fillna(True).astype(bool)
        print(line(t[k_], f"{nm} kept"), "\n" + line(t[~k_], f"{nm} skipped"))
        if stop is not None:
            lab.add(key, t[k_].reset_index(drop=True), stop_pts=stop)
            a, c = lab.score({**base, key: ("risk", 400)}, 250, **CS), lab.score({**base, key: ("risk", 400)}, 500, **CS)
            print(f"   funded with ONB ML v2 band-filtered $400: 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
        else:
            w, r = paths(g, t[k_]); Ow, Oc = w[tr] / 10, r[tr] / 10
            q = np.floor(1100 / (np.nan_to_num(0.25 * ctx["day"][tr], nan=1e12) * 2))[:, None]
            res = [challenge(Vw * 8 + Ow * q, Vc * 8 + Oc * q, np.arange(s, min(s + 21, D))) for s in range(D)]
            o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
            print(f"   combine with ONB ADX30 band-filtered: pass {np.nanmean(o[yr >= 2018]):.1%} | 2023-26 {np.nanmean(o[yr >= 2023]):.1%}")
