"""NQ Opening Range Momentum: backtest (contractor submission for review)."""
import numpy as np
import pandas as pd

POINT_VALUE = 20.0          # NQ: $20 per point


def load(path="NQ_continuous_1min.csv"):
    df = pd.read_csv(path, parse_dates=["timestamp"])      # unadjusted front-month continuous series, CT clock
    df["date"] = df.timestamp.dt.date
    df["hhmm"] = df.timestamp.dt.hour * 100 + df.timestamp.dt.minute
    return df


def daily_stats(df):
    d = df.groupby("date").agg(high=("high", "max"), low=("low", "min"), close=("close", "last"), open=("open", "first"))
    tr = d.high - d.low
    d["atr"] = tr.rolling(14).mean()                         # ATR(14)
    d["active"] = (d.high - d.low) > MULT * d.atr            # active-day filter
    return d


def backtest(df, d, or_minutes, mult, target_r):
    global MULT; MULT = mult
    trades = []
    days = sorted(df.date.unique())
    for i, day in enumerate(days[:-1]):
        if not d.loc[day, "active"]:
            continue
        x = df[df.date == day]
        end = 830 + or_minutes if or_minutes < 30 else 900 + (or_minutes - 30)
        rng = x[(x.hhmm >= 830) & (x.hhmm < end)]
        hi, lo = rng.high.max(), rng.low.min(); width = hi - lo
        after = x[x.hhmm >= end]
        sig = after[(after.close > hi) | (after.close < lo)]
        if sig.empty:
            continue
        s = sig.iloc[0]; side = 1 if s.close > hi else -1
        entry = s.close
        stop = lo if side == 1 else hi
        target = entry + side * target_r * width
        exit_px = None
        for _, b in after[after.timestamp > s.timestamp].iterrows():
            if (side == 1 and b.high >= target) or (side == -1 and b.low <= target):
                exit_px = target; break
            if (side == 1 and b.low <= stop) or (side == -1 and b.high >= stop):
                exit_px = stop; break
        if exit_px is None:
            exit_px = d.loc[days[i + 1], "open"]              # hold to next day's open
        trades.append(dict(date=day, side=side, pnl=(exit_px - entry) * side * POINT_VALUE))
    return pd.DataFrame(trades)


def stats(t):
    sharpe = t.pnl.mean() / t.pnl.std() * np.sqrt(252)
    tstat = t.pnl.mean() / t.pnl.std() * np.sqrt(len(t))
    eq = t.pnl.cumsum(); mdd = (eq.cummax() - eq).max()
    return dict(trades=len(t), win=(t.pnl > 0).mean(), avg=t.pnl.mean(), total=t.pnl.sum(), sharpe=sharpe, t=tstat, maxdd=mdd)


if __name__ == "__main__":
    df = load()
    best = None
    for orm in (5, 10, 15, 20, 30, 45):
        for mult in (0.8, 1.0, 1.2, 1.4):
            for tr in (1, 2):
                d = daily_stats_cache = None
                MULT = mult; d = daily_stats(df)
                t = backtest(df, d, orm, mult, tr)
                s = stats(t)
                if best is None or s["sharpe"] > best[0]["sharpe"]:
                    best = (s, orm, mult, tr, t)
    s, orm, mult, tr, t = best
    print("best:", orm, mult, tr, s)
    oos = t[pd.to_datetime(t.date) >= "2023-01-01"]
    print("out of sample 2023+:", stats(oos))
