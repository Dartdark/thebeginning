"""Topstep 50K Trading Combine simulator for a MultiCharts trade list.

Same bag-of-days method as the Colab notebook (whole real days resampled
with replacement, intraday order kept, floor checked at each trade's MAE),
with the Topstep rules the notebook's Apex presets do not model:

  - Maximum Loss Limit $2,000, trailing the END-OF-DAY balance high,
    enforced on live equity, and locking once it reaches the start balance.
  - Daily Loss Limit $1,000 (optional at checkout): liquidates at the limit
    and ends the day; not a failure.
  - Optional consistency target (off by default): best day must be at most
    50% of total profit, so a $2,000 day means $4,000 is needed to pass.
    Set RULES["consistency"] = 0.50 to switch it on.
  - Minimum 2 trading days, no deadline (monthly subscription); simulated
    up to HORIZON_DAYS trading days.
  - Max 50 MNQ.

Verify every number against help.topstep.com before relying on it.

Usage: python3 analysis/topstep_sim.py <report.xlsx> [more reports...]
"""
import sys
import numpy as np
import pandas as pd

RULES = dict(start=50_000.0, target=3_000.0, mll=2_000.0, dll=1_000.0,
             consistency=None, min_days=2, max_mnq=50)
HORIZON_DAYS = 63                       # ~3 months of subscription
COST_PER_NQ = 2.25 + 5.0                # commission + slippage per NQ round trip
SEED = 42


def load_trades(path):
    """Entry rows of a MultiCharts 'List of Trades' export, one per trade."""
    raw = pd.read_excel(path, sheet_name="List of Trades", header=2)
    ent = raw[raw["Type"].astype(str).str.startswith("Entry")].reset_index(drop=True)
    ex = raw[raw["Type"].astype(str).str.startswith("Exit")].reset_index(drop=True)
    t = pd.DataFrame({
        "entry": pd.to_datetime(ent["Date"]),
        "exit": pd.to_datetime(ex["Date"]),
        "direction": ent["Signal"].astype(str).str.upper(),
        "exit_signal": ex["Signal"].astype(str),
        "pnl": ent["Profit ($)"].astype(float) - COST_PER_NQ,
        "mae": ent["Drawdown ($)"].astype(float).abs() + COST_PER_NQ,
    })
    t["date"] = t["entry"].dt.normalize()
    t["hhmm"] = t["entry"].dt.hour * 100 + t["entry"].dt.minute
    return t[t["date"].dt.dayofweek < 5]


def day_bag(t, first=None, last=None):
    """Every weekday in the window, with that day's (pnl, mae) arrays in order."""
    first = first or t["date"].min()
    last = last or t["date"].max()
    days = pd.date_range(first, last, freq="B")
    g = {d: x for d, x in t.groupby("date")}
    empty = (np.zeros(0), np.zeros(0))
    return [(g[d]["pnl"].to_numpy(), g[d]["mae"].to_numpy()) if d in g else empty
            for d in days]


def one_challenge(bag, rng, mnq, r=RULES):
    scale = mnq / 10.0                  # backtest is 1 NQ = 10 MNQ
    bal = r["start"]; hwm = bal; floor = bal - r["mll"]
    best_day = 0.0; trade_days = 0
    for day in range(1, HORIZON_DAYS + 1):
        pnls, maes = bag[rng.integers(len(bag))]
        day_start = bal
        dll_level = day_start - r["dll"] if r["dll"] else -np.inf
        if len(pnls):
            trade_days += 1
        for p, m in zip(pnls, maes):
            worst = bal - m * scale
            if worst <= floor and floor >= dll_level:
                return "fail_mll", day
            if worst <= dll_level:      # DLL liquidates first: day over at the limit
                bal = dll_level
                break
            bal += p * scale
            if bal <= floor:
                return "fail_mll", day
            profit = bal - r["start"]
            best_day = max(best_day, bal - day_start)
            need = (max(r["target"], best_day / r["consistency"])
                    if r["consistency"] else r["target"])
            if profit >= need and trade_days >= r["min_days"]:
                return "pass", day
        best_day = max(best_day, bal - day_start)
        if bal > hwm:                   # end-of-day trailing, locks at start balance
            hwm = bal
            floor = min(hwm - r["mll"], r["start"])
    return "fail_time", HORIZON_DAYS


def simulate(bag, mnq, n=4000, seed=SEED):
    rng = np.random.default_rng(seed)
    res = [one_challenge(bag, rng, mnq) for _ in range(n)]
    out = pd.Series([o for o, _ in res]).value_counts(normalize=True)
    days = [d for o, d in res if o == "pass"]
    return dict(p=out.get("pass", 0.0), mll=out.get("fail_mll", 0.0),
                time=out.get("fail_time", 0.0),
                med_days=float(np.median(days)) if days else float("nan"), n=n)


def ci(p, n, z=1.96):
    d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    m = (z / d) * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return c - m, c + m


def zero_edge(t):
    return t.assign(pnl=t["pnl"] - t["pnl"].mean())


def size_sweep(bag, sizes=(2, 3, 4, 5, 6, 8, 10, 12, 15, 20), n=4000):
    rows = []
    for s in sizes:
        r = simulate(bag, s, n)
        lo, hi = ci(r["p"], n)
        rows.append(dict(mnq=s, p=r["p"], lo=lo, hi=hi, mll=r["mll"],
                         time=r["time"], med_days=r["med_days"]))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    for path in sys.argv[1:]:
        t = load_trades(path)
        print(f"\n{path}\n  {len(t)} trades, {t.date.min().date()} -> {t.date.max().date()}, "
              f"win {(t.pnl > 0).mean():.1%}, avg ${t.pnl.mean():.2f} net")
        sw = size_sweep(day_bag(t))
        zs = size_sweep(day_bag(zero_edge(t)))
        sw["zero_edge_p"] = zs["p"]
        print(sw.to_string(index=False, formatters={
            "p": "{:.1%}".format, "lo": "{:.1%}".format, "hi": "{:.1%}".format,
            "mll": "{:.1%}".format, "time": "{:.1%}".format,
            "zero_edge_p": "{:.1%}".format}))
