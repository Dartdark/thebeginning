"""Gold Asian-range breakout: a filter to cut the losing streaks (watchlist #6, user's request 2026-10-14).

Base trade (analysis/gold_asian_breakout_gc_test.py, "as described"): range 20:00 -> 00:00 CT, OCO stops at the edges,
stop 1.0 x range, no target, out 10:00 CT, one trade a day, 1 GC, $7.25 + 1 tick a fill. Measured in R = net / (range
width x $100) so gold's price level doesn't dominate.
Candidate filters, all known at the moment of entry (no look-ahead):
  A. range width / 14-day ATR (prior days)          - quiet coil vs wide range
  B. fill time (CT): Asia 0-2, London 2-7, US 7-10   - which session takes the break
  C. trend: breakout side vs the 20-day trend (sign of yesterday's 13:30 close - 20 sessions earlier)
  D. yesterday's direction vs the breakout side
  E. volatility regime: 14-day ATR percentile (trailing year)
  F. weekday
Protocol: buckets measured on 2018-22 only; a filter is kept only if its pattern is monotone / clear there; the chosen
filter(s) are then run once on 2023-26, then the funded bench (MGC, fixed and risk-sized) and the losing-streak stats.
  python3 analysis/gold_breakout_filter_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import asian_breakout_test as AB
import gold_asian_breakout_gc_test as GT
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPLIT = pd.Timestamp("2023-01-01")


def features(gc, t):
    atr = gc.daily_atr(14)
    cf = pd.Series(gc.c.ravel()).ffill().to_numpy()
    tr = gc.trading; c1330 = pd.Series(cf[tr * 1440 + jof(1330)], index=tr)
    o0800 = pd.Series(gc.o[tr, jof(801)], index=tr)
    pos = pd.Series(np.arange(len(tr)), index=tr)
    atr_s = pd.Series(atr[tr], index=tr); atr_pct = atr_s.rolling(250, min_periods=120).apply(lambda v: (v[:-1] < v[-1]).mean(), raw=True)
    f = pd.DataFrame(index=t.index)
    f["wr"] = t.width.values / atr[t.day.values]
    f["hour"] = (t.t0.values % 1440) // 60
    trend, ydir, apct = [], [], []
    for r in t.itertuples():
        i = pos.get(r.day)
        if i is None or i < 21: trend.append(np.nan); ydir.append(np.nan); apct.append(np.nan); continue
        y = tr[i - 1]; y20 = tr[i - 21]
        trend.append(np.sign(c1330[y] - c1330[y20]) * r.side); ydir.append(np.sign(c1330[y] - o0800[y]) * r.side)
        apct.append(atr_pct.get(r.day, np.nan))
    f["trend"] = trend; f["ydir"] = ydir; f["apct"] = apct
    f["wd"] = t.date.dt.dayofweek.values
    f["R"] = t.net.values / (t.width.values * 100.0)
    f["date"] = t.date.values
    return f


def bucket(f, col, bins=None, labels=None):
    x = f.copy()
    x["b"] = pd.cut(x[col], bins, labels=labels) if bins is not None else x[col]
    d, h = x[x.date < SPLIT], x[x.date >= SPLIT]
    out = pd.DataFrame({"n_18_22": d.groupby("b").R.size(), "R_18_22": d.groupby("b").R.mean(),
                        "t_18_22": d.groupby("b").R.apply(lambda v: v.mean() / v.std() * np.sqrt(len(v)) if len(v) > 2 else np.nan),
                        "n_23_26": h.groupby("b").R.size(), "R_23_26": h.groupby("b").R.mean()})
    return out


def streaks(net):
    s = "".join("L" if v < 0 else "W" for v in net)
    return max(len(z) for z in s.split("W")), net.rolling(20).sum().min()


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    gc = GT.load_gc()
    t = AB.run(gc, "GC"); t = t[t.date >= pd.Timestamp("2018-01-01")].reset_index(drop=True)
    f = features(gc, t)
    print(f"base: {len(t)} trades, {f.R.mean():+.3f} R (2018-22 {f.R[f.date < SPLIT].mean():+.3f}, 2023-26 {f.R[f.date >= SPLIT].mean():+.3f})")
    fm = lambda df: df.to_string(float_format=lambda v: f"{v:,.3f}")
    print("\nA. range width / 14-day ATR"); print(fm(bucket(f, "wr", [0, 0.15, 0.2, 0.25, 0.3, 0.4, 9])))
    print("\nB. fill hour (CT)"); print(fm(bucket(f, "hour", [-1, 1, 3, 6, 10], ["00-01", "02-03", "04-06", "07-09"])))
    print("\nC. breakout side vs 20-day trend (+1 with, -1 against)"); print(fm(bucket(f, "trend")))
    print("\nD. breakout side vs yesterday's direction"); print(fm(bucket(f, "ydir")))
    print("\nE. ATR percentile (trailing year)"); print(fm(bucket(f, "apct", [0, 0.33, 0.67, 1.01], ["low", "mid", "high"])))
    print("\nF. weekday"); print(fm(bucket(f, "wd")))
    pickle.dump(dict(t=t, f=f), open(SP + "gold_filter.pkl", "wb"))

    print("\n=== Chosen on 2018-22 (pre-registered): B = cancel unfilled orders at 02:00 CT (fills 00:00-01:59 only);"
          " B+D = also skip breakouts in yesterday's direction. Run once on 2023-26.")
    V = {"base (as described)": f.index == f.index, "B: fills before 02:00": f.hour < 2, "B+D: + against yesterday": (f.hour < 2) & (f.ydir < 0),
         "B+C: + against the 20-day trend": (f.hour < 2) & (f.trend < 0)}
    days = pd.DatetimeIndex(gc.ts[gc.trading]); days = days[days.year >= 2018]
    dl = lambda x: x.groupby(x.date).net.sum().reindex(days, fill_value=0.0)
    tab, hold, kept = {}, {}, {}
    for nm, m in V.items():
        tt_ = t[np.asarray(m)]; Rr = f.R[np.asarray(m)]; y = tt_.date.dt.year
        ls, w20 = streaks(tt_.net / 10)
        print(f"   {nm:<34} n {len(tt_):4d} ({len(tt_) / 8.8:.0f}/yr) win {np.mean(tt_.net > 0):.0%} | {Rr.mean():+.3f} R t {Rr.mean() / Rr.std() * np.sqrt(len(Rr)):.1f}"
              f" | 2018-22 {Rr[y < 2023].mean():+.3f} R, 2023-26 {Rr[y >= 2023].mean():+.3f} R | years+ (R) {(Rr.groupby(y).sum() > 0).sum()}/{y.nunique()}"
              f" | ${tt_.net.mean():.0f} per GC | longest losing streak {ls}, worst 20 trades ${w20:,.0f} per MGC")
        tab[nm] = (dl(tt_), tt_.net); tab["  longs"] = (dl(tt_[tt_.side > 0]), tt_.net[tt_.side > 0]); tab["  shorts"] = (dl(tt_[tt_.side < 0]), tt_.net[tt_.side < 0])
        print(M.table({nm: tab[nm], "  longs": tab["  longs"], "  shorts": tab["  shorts"]}))
        hold[nm + " 2023+"] = dl(tt_)[days >= SPLIT]; kept[nm] = tt_
        print("      R by year: " + " | ".join(f"{yy} {v:+.3f}" for yy, v in Rr.groupby(y).mean().items()))
    b_, p_ = R.report(hold, n=3000); print(b_); print(p_)
    rng = np.random.default_rng(9)
    for nm in ("B: fills before 02:00", "B+D: + against yesterday"):
        k = len(kept[nm]); pl = [f.R.sample(k, random_state=int(rng.integers(1e9))).mean() for _ in range(2000)]
        print(f"   placebo for {nm}: random {k} of the base trades {np.mean(pl):+.3f} R, 95th pct {np.percentile(pl, 95):+.3f} vs {f.R[np.asarray(V[nm])].mean():+.3f}")

    print("\n   Funded bench (plan + gold on MGC; gold's own intraday path)")
    g = pickle.load(open(SP + "g24.pkl", "rb")); lab = pickle.load(open(SP + "lab.pkl", "rb"))
    from bridge_monday_confirm import load_bridge_mc
    lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    dts2 = pd.DatetimeIndex(g.ts[lab.tr]); dpos = pd.Series(np.arange(lab.D), index=dts2)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    cands = {"current plan": plan}
    for nm, key in (("base (as described)", "G0"), ("B: fills before 02:00", "GB"), ("B+D: + against yesterday", "GBD")):
        tt_ = kept[nm]; GT.add_to_lab(lab, key, tt_, gc)
        st_arr = np.full(lab.D, 1e12)
        for r in tt_.itertuples():
            if r.date in dpos.index: st_arr[dpos[r.date]] = r.width * 5.0
        lab.stop[key] = st_arr
        cands[f"+ {nm} 1 MGC"] = {**plan, key: 1}
        cands[f"+ {nm} risk $100"] = {**plan, key: ("risk", 100)}
    from speed_to_13k import run as speed, fmt
    sp = {}
    for nm, p in cands.items():
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<44} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
        sp[nm] = speed(lab, p, **CS)
    print(fmt(pd.DataFrame(sp).T))
    corr = {k: round(float(np.corrcoef(lab.C["GB"], lab.C[k])[0, 1]), 2) for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC")}
    print("   daily correlation of B with the plan:", corr)

    print("\n   Gold alone in its own funded account (no NQ strategies), MGC")
    for key, nm in (("GB", "B"), ("GBD", "B+D")):
        for q in (1, 2, 3, 4):
            p = {key: q}; a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS); s_ = speed(lab, p, **CS)
            print(f"   {nm:<4} {q} MGC: 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%} | median days to $13k {s_['median']}, 3y ${s_['exp3y']:,.0f}")
        for risk in (100, 200, 300):
            p = {key: ("risk", risk)}; a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS); s_ = speed(lab, p, **CS)
            print(f"   {nm:<4} risk ${risk}: 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%} | median days to $13k {s_['median']}, 3y ${s_['exp3y']:,.0f}")
