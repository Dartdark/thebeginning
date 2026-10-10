"""Apex challenges started on real days and run on the real days that followed.

The random-day simulation (prop_sim.simulate) mixes quiet and volatile days in
every challenge. With the volatility filter, quiet stretches last for months,
so when a challenge starts matters. This script starts a challenge on every
trading day in the data and walks the actual following days, then compares:
  - starting on any day
  - starting only on days the volatility filter is on
  - starting only on the first day it turns on after being off

Usage: python3 analysis/start_timing.py
"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
from prop_sim import load_trades, challenge_from, PRESETS
from replica import load_bars, run, daily_features

RULES = PRESETS["APEX_50K_EOD"]
SIZES = (10, 12, 15)
COST = 7.25


def day_list(trades, calendar):
    g = {d: x.sort_values("entry_key") for d, x in trades.groupby("date")}
    empty = (np.zeros(0), np.zeros(0))
    return [(g[d]["pnl"].to_numpy(), g[d]["mae"].to_numpy()) if d in g else empty
            for d in calendar]


def from_mc(path):
    t = load_trades(path)
    return t.assign(entry_key=t["entry"])[["date", "pnl", "mae", "entry_key"]]


def from_replica(r):
    return pd.DataFrame({"date": pd.to_datetime(r["date"]), "pnl": r["pnl"] - COST,
                         "mae": r["mae"] + COST, "entry_key": r["entry_time"]})


def evaluate(days, starts, label):
    for s in SIZES:
        res = [challenge_from(days, i, s, RULES) for i in starts]
        res = [x for x in res if x is not None]
        o = pd.Series([x[0] for x in res])
        d = pd.Series([x[1] for x in res])[o.values == "pass"]
        print(f"  {label:<34} {s:>2} MNQ  starts {len(res):>4}  pass {(o == 'pass').mean():5.1%}  "
              f"ran out of time {(o == 'fail_time').mean():5.1%}  "
              f"median days to pass {d.median() if len(d) else float('nan'):.0f}")


if __name__ == "__main__":
    bars = load_bars("NQ_1min_*.csv")
    feats = daily_features(bars)
    calendar = pd.to_datetime(pd.Series(sorted(bars["date"].unique())).astype(str))
    avg = feats["avg10_range_pct"].reindex(sorted(bars["date"].unique())).to_numpy()

    def flt(dist, vol):
        return lambda i, side: ((i["close"] - i["vwap"]) / i["vwap"] * 100 * side >= dist
                                and i.get("avg10_range_pct", np.nan) >= vol)

    sets = {
        "MultiCharts filtered 0.35/1.50": (from_mc("Backtesting Strategy Performance Report v2 filtered.xlsx"), 1.50),
        "Python copy 0.35/1.50": (from_replica(run(bars, entry_filter=flt(0.35, 1.50))), 1.50),
        "Python copy 0.35/1.30": (from_replica(run(bars, entry_filter=flt(0.35, 1.30))), 1.30),
    }
    for name, (trades, thr) in sets.items():
        days = day_list(trades, calendar)
        on = np.nan_to_num(avg) >= thr
        any_day = list(range(len(days)))
        on_days = [i for i in any_day if on[i]]
        turn_on = [i for i in on_days if i > 0 and not on[i - 1]]
        print(f"\n{name}: filter on {on.mean():.0%} of days; {len(turn_on)} times it switched on")
        evaluate(days, any_day, "start on any day")
        evaluate(days, on_days, "start only while filter is on")
        evaluate(days, turn_on, "start the day it switches on")
