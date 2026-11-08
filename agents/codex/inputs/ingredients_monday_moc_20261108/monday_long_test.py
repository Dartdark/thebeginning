"""Monday Long (2026-10-12): new direction source from the direction search (analysis/direction_search.py,
direction_ridge.py: price-pattern signals failed out of sample; weekday flow did not).

Finding: NQ's RTH gain is concentrated on Mondays. 8:30 open -> 15:00 close, per NQ after costs:
Mon $427 (t 3.1, 8/9 years) vs Tue-Fri about $0; 2018-22 $150 (t 1.0), 2023-26 $796 (t 3.2).
ES the same (Mon t 2.1, other days negative). Up after both up and down Fridays / weekend gaps.
Trade: long at the 8:30 CT open on Mondays (first trading day of the week when Monday is a holiday
is NOT used), stop = StopAtr x 15-day ATR, exit at ExitTime. Costs $7.25 + 1 tick per market/stop fill.
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g = pickle.load(open(SP + "g24.pkl", "rb"))
PV, COST, TICK = 20.0, 7.25, 0.25
atr = g.daily_atr(15)
dts_all = pd.DatetimeIndex(g.ts)


def trades(stop_atr=0.5, exit_j=900, dow=0, side=1, entry_j=511):
    rows = []
    for d in g.trading:
        if dts_all[d].dayofweek != dow or dts_all[d].year < 2018 or np.isnan(atr[d]): continue
        o, h, l, c = g.o[d], g.h[d], g.l[d], g.c[d]
        if np.isnan(o[entry_j]): continue
        e = o[entry_j] + side * TICK; sp = stop_atr * atr[d] if stop_atr else 1e9; sl = e - side * sp
        jx = exit_j
        while np.isnan(c[jx]) and jx > entry_j: jx -= 1           # early close: last bar
        px, j1, kind = None, jx, 0
        for j in range(entry_j, jx + 1):
            if np.isnan(c[j]): continue
            if (l[j] <= sl) if side > 0 else (h[j] >= sl):
                px = (min(o[j], sl) if side > 0 else max(o[j], sl)) - side * TICK; j1 = j; break
        if px is None: px = c[jx] - side * TICK
        rows.append(dict(day=d, j0=entry_j, j1=j1, side=side, entry=e, exit=px, kind=kind,
                         pnl=(px - e) * side * PV, net=(px - e) * side * PV - COST, date=dts_all[d], slips=0,
                         stop_pts=sp))
    return pd.DataFrame(rows)


def line(t, name):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); h = x[y >= 2023]; d_ = x[y <= 2022]
    pf = lambda s: s[s > 0].sum() / max(1e-9, -s[s < 0].sum())
    return (f"{name:<34} n={len(x)} win {np.mean(x>0):.0%} avg ${x.mean():4.0f} PF {pf(x):.2f} t={x.mean()/x.std()*np.sqrt(len(x)):.1f}"
            f" yrs+ {(by>0).sum()}/{len(by)} | 2018-22 ${d_.mean():4.0f} PF {pf(d_):.2f} | 2023+ ${h.mean():4.0f} PF {pf(h):.2f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    print("\nVariants (Monday long, per NQ):")
    for sa in (0.3, 0.5, 0.75, 1.0, 0):
        for ex in (870, 900):
            print(line(trades(sa, ex), f"stop {sa if sa else 'none'} ATR, exit {ex//60}:{ex%60:02d}"))
    print("\nPlacebo: the same trade (stop 0.5 ATR, exit 15:00) on other weekdays:")
    for k, nm in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri"]):
        print(line(trades(0.5, 900, dow=k), f"long {nm}"))
    print("\nShort side (process step 2): short Thursday, the weakest day:")
    print(line(trades(0.5, 900, dow=3, side=-1), "short Thu stop 0.5 ATR"))
    t = trades(0.5, 900)
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    stop = np.full(g.D, np.nan); stop[t.day.values] = t.stop_pts.values
    stop = pd.Series(stop).ffill().bfill().to_numpy()
    lab.add("MON", t, stop_pts=stop, slippage=False)
    dates = pd.DatetimeIndex(g.ts[lab.tr]); m = dates.year >= 2018
    print("\nCorrelation of daily P&L with the funded set:")
    print(lab.corr(["MON", "VB", "ONB_ML2_MC", "OND_MC", "EOS"]).round(2).loc["MON"].to_string())
    d = pd.Series(lab.daily("MON"), index=dates)[m]
    print("\nStandard metrics, per NQ (long-only strategy):")
    print(M.table({"Monday Long 2018-26": (d, t.net.values), "Monday Long 2023-26": (d[d.index.year >= 2023], t.net[t.date.dt.year >= 2023].values)}))
    B, P = R.report({"Monday Long 2023-26": d[d.index.year >= 2023], "Monday Long 2018-26": d}, n=5000)
    print("\nBootstrap (10-day blocks):"); print(B); print("\nPermutation:"); print(P)
    base = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "OND_MC": ("risk", 500), "EOS": ("risk", 700)}
    plans = {"Funded set (recommended)": base}
    for r in (300, 500, 700):
        plans[f"+ Monday Long ${r}"] = {**base, "MON": ("risk", r)}
    plans["Monday Long $500 replaces OND"] = {k: v for k, v in base.items() if k != "OND_MC"} | {"MON": ("risk", 500)}
    print("\nFunded bench, 1 year (fixed sizes):"); print(lab.table(plans, 250))
    print("\nFunded bench, 2 years:"); print(lab.table(plans, 500))
    pickle.dump(lab, open(SP + "lab_mon.pkl", "wb"))

# ---------------- cushion sizing (size x clip(cushion / $2,000, 0.5, 1)), as recommended for the funded set
def cushion_table(lab, plans):
    rows = {}
    for nm, p in plans.items():
        for h in (250, 500):
            s = lab.score(p, h, fmin=0.5, fmax=1.0, ref=2000.0)
            rows[(nm, f"{h // 250}y")] = s
    df = pd.DataFrame(rows).T
    fm = {c: "${:,.0f}".format for c in ("expected", "s2018_22", "s2023_on", "worst_year")}
    fm.update({c: "{:.0%}".format for c in ("blown", "any_payout", "all_6")}); fm["days_to_1st"] = "{:.0f}".format
    return df.to_string(formatters=fm)
