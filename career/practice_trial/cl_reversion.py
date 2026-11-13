"""Crude Oil Morning Reversion: backtest (contractor submission for review)."""
import numpy as np
import pandas as pd

POINT_VALUE = 1000.0        # $ per 1.00 move
COST = 2.50                 # per round trip


def load(path="CL_daily_bars.csv"):
    # one row per day: open_0800, high_0800_1100, low_0800_1100, price_1100, close (16:00 settlement)
    return pd.read_csv(path, parse_dates=["date"]).set_index("date")


def signals(d, z_thr):
    mu, sd = d.open_0800.mean(), d.open_0800.std()          # average and spread of the 08:00 open
    d["z"] = (d.open_0800 - mu) / sd
    short = (d.z > z_thr) & (d.close < d.open_0800)          # confirmed reversion
    long = (d.z < -z_thr) & (d.close > d.open_0800)
    d["side"] = np.where(short, -1, np.where(long, 1, 0))
    return d


def trades(d):
    out = []
    for day, r in d[d.side != 0].iterrows():
        entry = r.open_0800
        stop = entry * (1 - 0.01 * r.side)
        if (r.side == 1 and r.price_1100 < stop) or (r.side == -1 and r.price_1100 > stop):
            exit_px = stop                                   # stopped out
        else:
            exit_px = r.price_1100
        out.append(dict(date=day, side=r.side, pnl=(exit_px - entry) * r.side * POINT_VALUE - COST))
    t = pd.DataFrame(out)
    cut = t.pnl.mean() - 3 * t.pnl.std()
    return t[t.pnl > cut]                                    # remove data errors


def walk_forward(d):
    res = []
    for y in sorted(set(d.index.year)):
        dy = d[d.index.year == y].copy()
        best = max((trades(signals(dy.copy(), z)) for z in (1.0, 1.5, 2.0)), key=lambda t: t.pnl.sum())
        res.append(best)
    return pd.concat(res)


if __name__ == "__main__":
    d = load()
    t = walk_forward(d)
    yearly = t.groupby(pd.to_datetime(t.date).dt.year).pnl.sum()
    print(len(t), "trades, win", (t.pnl > 0).mean(), "total", t.pnl.sum())
    print("profit factor", t.pnl[t.pnl > 0].sum() / -t.pnl[t.pnl < 0].sum())
    print(yearly)
