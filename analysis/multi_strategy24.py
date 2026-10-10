"""Multi-strategy plan on the full 24-hour data, with Overnight Bias.

Joins the 08:00-15:15 exports with the overnight exports (grid24.py), runs
Overnight Bias and VWAP Pullback ADX in Python (candidates24.py), loads v3,
Vault Break and Opening Drive from their MultiCharts reports, and prints:
  - per-strategy results and daily correlations
  - Overnight Bias pass rates by $ risk per trade
  - per-account pass rates and accounts started together
  - the best single combined account (sizes chosen on 2018-2022 starts)
  - days and cost to the first funded account for each way of running them

Overnight Bias comes from its MultiCharts report (ONB_REPORT) when that file
exists, otherwise from the Python version.

Usage (from the repo root): python3 analysis/multi_strategy24.py   (about 1 minute)
"""
import os
import sys
import itertools
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
from grid import execute
from grid24 import Grid24
from portfolio import load_mc, paths, challenge
from candidates24 import overnight_bias24, vwap_pullback_adx24, vault_break24
from multi_strategy import V3_REPORT, zero_edge

VB_REPORT = "Backtesting Strategy Performance Report VB v1.xlsx"
OD_REPORT = "Backtesting Strategy Performance Report OD v1.xlsx"
ONB_REPORT = "Backtesting Strategy Performance Report ONB v2.xlsx"
ONB_RISK = 1100            # $ lost at the stop per Overnight Bias trade
FEE = 50


def summary(t):
    y = pd.DatetimeIndex(t["date"]).year
    w, l = t.net[t.net > 0].sum(), -t.net[t.net < 0].sum()
    return dict(trades=len(t), win=f"{(t.net > 0).mean():.0%}", avg=round(t.net.mean()),
                pf=round(w / l, 2), avg_2018_22=round(t.net[y < 2023].mean()),
                avg_2023_26=round(t.net[y >= 2023].mean()),
                worst_year=round(t.groupby(y).net.mean().min()))


def risk_sized(g, t, risk, stop_frac=0.30):
    """Size each trade in whole MNQ so the stop loses at most `risk` dollars."""
    t = t.copy()
    stop_pts = stop_frac * g.daily_atr(15)[t["day"].to_numpy()]
    t["qty"] = np.floor(risk / (stop_pts * 2.0)) / 10.0
    t = t[t["qty"] > 0].reset_index(drop=True)
    t["net"] = (t["pnl"] - 7.25) * t["qty"]
    return t


class Sim:
    """Real-day challenges on the trading days of the 24-hour grid."""
    def __init__(self, g):
        self.g, self.tr = g, g.trading
        self.D = len(self.tr)
        self.yr = pd.DatetimeIndex(g.ts[self.tr]).year
        self.P = {}

    def add(self, name, t):
        w, r = paths(self.g, t)
        self.P[name] = (w[self.tr], r[self.tr])

    def results(self, sizes):
        w = sum(self.P[k][0] * s / 10 for k, s in sizes.items())
        r = sum(self.P[k][1] * s / 10 for k, s in sizes.items())
        return [challenge(w, r, np.arange(s, min(s + 21, self.D))) for s in range(self.D)]


def passed(res):
    return np.array([np.nan if x is None else float(x[0] == "pass") for x in res])


def first_funded(R, plan, D):
    """Buy an account per strategy in `plan`; replace each failed one the next
    day; stop at the first pass. Returns (days, accounts bought) per start."""
    out = []
    for start in range(D - 300):
        nxt = {k: start for k in plan}; bought = 0; best = None
        while True:
            k = min(nxt, key=nxt.get); s = nxt[k]
            if s >= D - 21 or (best is not None and s >= best) or R[k][s] is None:
                break
            o, n = R[k][s]
            bought += 1; end = s + n - 1
            if o == "pass":
                best = end if best is None else min(best, end); nxt[k] = 10 ** 9
            else:
                nxt[k] = end + 1
            if all(v >= 10 ** 9 for v in nxt.values()):
                break
        if best is not None:
            out.append((best - start + 1, bought))
    return np.array(out)


if __name__ == "__main__":
    g = Grid24()
    s, kw = vault_break24(g)
    vb_py = execute(g, s, **kw)
    s, kw = vwap_pullback_adx24(g)
    T = {"V3": load_mc(g, V3_REPORT), "VB": load_mc(g, VB_REPORT), "OD": load_mc(g, OD_REPORT),
         "ONB": load_mc(g, ONB_REPORT) if os.path.exists(ONB_REPORT) else overnight_bias24(g),
         "VPA": execute(g, s, **kw)}
    print("Overnight Bias:", ONB_REPORT if os.path.exists(ONB_REPORT) else "Python version")
    m = T["VB"]
    same = len(set(zip(m.day, m.j0)) & set(zip(vb_py.day, vb_py.j0)))
    print(f"Check: Python Vault Break reproduces {same} of {len(m)} MultiCharts trades")

    print("\nPer strategy, per NQ, after costs")
    print(pd.DataFrame({k: summary(t) for k, t in T.items()}).T.to_string())
    sim = Sim(g)
    for k, t in T.items():
        sim.add(k, t)
    daily = pd.DataFrame({k: sim.P[k][1][:, -1] for k in T})
    print("\nCorrelation of daily P&L"); print(daily.corr().round(2).to_string())

    IS = sim.yr < 2023
    print("\nOvernight Bias, one account, sized by $ risk per trade")
    for risk in (700, 900, 1100, 1300, 1500):
        t = risk_sized(g, T["ONB"], risk)
        sim.add("tmp", t); o = passed(sim.results({"tmp": 10}))
        sim.add("tmp", zero_edge(t)); z = passed(sim.results({"tmp": 10}))
        print(f"  ${risk:,}: pass {np.nanmean(o):.0%} (no edge {np.nanmean(z):.0%})  2018-22 {np.nanmean(o[IS]):.0%}"
              f"  2023-26 {np.nanmean(o[~IS]):.0%}  worst year {pd.Series(o).groupby(sim.yr).mean().min():.0%}")
    sim.add("ONB", risk_sized(g, T["ONB"], ONB_RISK))     # from here on: size 10 = $ONB_RISK a trade

    ACC = {"V3": {"V3": 10}, "VB": {"VB": 12}, "OD": {"OD": 10}, "ONB": {"ONB": 10}}
    R = {k: sim.results(v) for k, v in ACC.items()}
    O = pd.DataFrame({k: passed(v) for k, v in R.items()})
    print(f"\nPer account (V3 10, VB 12, OD 10 MNQ; ONB ${ONB_RISK:,} a trade)")
    for k in O:
        print(f"  {k:<4} pass {O[k].mean():.0%}  2018-22 {O[k][IS].mean():.0%}  2023-26 {O[k][~IS].mean():.0%}"
              f"  worst year {O[k].groupby(sim.yr).mean().min():.0%}")
    print("Correlation of pass/fail, accounts started the same day"); print(O.corr().round(2).to_string())
    print("Accounts started together: chance at least one passes")
    for plan in (["VB"], ["VB", "ONB"], ["VB", "OD", "ONB"], ["V3", "VB", "OD", "ONB"]):
        a = O[plan].max(axis=1, skipna=False)
        print(f"  {' + '.join(plan):<20} {a.mean():.0%}  2023-26 {a[~IS].mean():.0%}  worst year {a.groupby(sim.yr).mean().min():.0%}")

    rows = []
    combos = [dict(VB=vb, ONB=on) for vb, on in itertools.product((6, 8, 10, 12), (5, 7, 10))]
    combos += [dict(VB=vb, OD=od, ONB=on) for vb, od, on in itertools.product((6, 8, 10), (4, 6), (5, 7, 10))]
    for c in combos:
        o = passed(sim.results(c))
        rows.append(dict(sizes=c, p=np.nanmean(o), p_2018_22=np.nanmean(o[IS]), p_2023_26=np.nanmean(o[~IS]),
                         worst_year=pd.Series(o).groupby(sim.yr).mean().min()))
    df = pd.DataFrame(rows).sort_values("p_2018_22", ascending=False)
    print("\nOne combined account, best sizes by 2018-22 starts (ONB 10 = $1,100 a trade)")
    print(df.head(6).to_string(index=False, formatters={c: "{:.0%}".format for c in ("p", "p_2018_22", "p_2023_26", "worst_year")}))
    two = df[df.sizes.map(len) == 2].iloc[0].sizes
    three = df[df.sizes.map(len) == 3].iloc[0].sizes
    R["BOOK2"], R["BOOK3"] = sim.results(two), sim.results(three)

    print("\nFirst funded account (replace failed accounts the next day)")
    for name, plan in ((f"one at a time: VB", ["VB"]), (f"one at a time: ONB", ["ONB"]),
                       (f"one at a time: one account {two}", ["BOOK2"]),
                       (f"one at a time: one account {three}", ["BOOK3"]),
                       ("two at once: VB + ONB", ["VB", "ONB"]),
                       ("three at once: VB + OD + ONB", ["VB", "OD", "ONB"])):
        x = first_funded(R, plan, sim.D)
        print(f"  {name:<58} days: typical {np.median(x[:, 0]):.0f}, 1 in 5 {np.percentile(x[:, 0], 80):.0f}+,"
              f" worst 5% {np.percentile(x[:, 0], 95):.0f}+ | accounts {x[:, 1].mean():.1f} = ${x[:, 1].mean() * FEE:.0f}")
