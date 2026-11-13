"""Replication: the gold overnight effect (Blose, Gondhalekar & Kort 2018) as adapted to Nasdaq-100 futures by a practitioner
note: long NQ at the 17:05 CT reopen, out at 07:20 CT, only when the 5-minute closes of the last two sessions fit a straight
line with R^2 >= 0.3; 25-point target, one re-entry per night after a target, no stop.

Standalone: needs only numpy + pandas and 1-minute NQ bars as CSV files with columns
    date (YYYYMMDD), time (HHMM, Chicago time, stamped at the bar's END), open, high, low, close, volume
Data is not included (vendor licence). Costs: $7.25 commission + 1 tick slippage per market fill ($20 per point);
the target is a limit order filled only on a 1-point trade-through. Nights that span a quarterly contract roll are dropped.

  python3 overnight_nq.py 'path/to/NQ_1min_*.csv'      # real data
  python3 overnight_nq.py --selftest                   # synthetic data: checks the plumbing, not the edge
"""
import glob, sys
import numpy as np
import pandas as pd

PV, TICK, COMM, TGT, THR, R2_MIN = 20.0, 0.25, 7.25, 25.0, 1.0, 0.3
PERIODS = [("design 2017 - 2022-10-25", "2017-01-01", "2022-10-25"), ("out of sample 1: to 2023", "2022-10-26", "2023-12-31"),
           ("out of sample 2: 2024 +", "2024-01-01", "2030-12-31")]


def load(pattern):
    df = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(pattern))], ignore_index=True)
    ts = pd.to_datetime(df.date.astype(str), format="%Y%m%d") + pd.to_timedelta(df.time // 100 * 60 + df.time % 100, unit="m")
    return df.set_index(ts)[["open", "high", "low", "close"]].sort_index().loc[lambda d: ~d.index.duplicated()]


def roll_nights(bars):
    """Calendar dates whose evening contains the quarterly contract switch: in Mar/Jun/Sep/Dec days 3-20, the largest
    one-minute jump in 17:00-17:05 that is > 6x the typical jump at that clock."""
    c = bars.close; jump = (c.diff().abs() / c.shift()).dropna()
    clock = jump.index.hour * 100 + jump.index.minute
    j = jump[(clock >= 1700) & (clock <= 1705)]
    base = j[~(j.index.month.isin([3, 6, 9, 12]) & (j.index.day >= 3) & (j.index.day <= 20))].median()
    out = set()
    win = j[j.index.month.isin([3, 6, 9, 12]) & (j.index.day >= 3) & (j.index.day <= 20)]
    for _, g in win.groupby([win.index.year, win.index.month]):
        if g.max() > 6 * base: out.add(g.idxmax().normalize())
    return out


def r2(y):
    y = y[np.isfinite(y)]
    if len(y) < 50: return np.nan
    c = np.corrcoef(np.arange(len(y)), y)[0, 1]
    return c * c


def nights(bars):
    o, h, l, c = (bars[k] for k in ("open", "high", "low", "close"))
    days = bars.index.normalize()
    clock = bars.index.hour * 100 + bars.index.minute
    trading = np.array(sorted(set(days[(clock >= 830) & (clock <= 1500) & (bars.index.dayofweek < 5)])))
    rolls, out = roll_nights(bars), []
    for D in pd.date_range(trading[0], trading[-1]):
        a, b = D + pd.Timedelta(hours=17, minutes=6), D + pd.Timedelta(days=1, hours=7, minutes=21)
        if a not in o.index or b not in o.index or (D + pd.Timedelta(days=1)) not in set(trading[-400:]) | set(trading):
            continue
        k = np.searchsorted(trading, D, side="right") - 1
        if k < 1 or D in rolls: continue
        s0, s1 = trading[k - 1] - pd.Timedelta(days=1) + pd.Timedelta(hours=17, minutes=1), trading[k] + pd.Timedelta(hours=16)
        win = c[s0:s1]; q = r2(win[win.index.minute % 5 == 0].to_numpy())
        if not q >= R2_MIN: continue
        night = bars[a:b]; net, n_tr, t = 0.0, 0, 0
        idx, oo, hh = night.index, night.open.to_numpy(), night.high.to_numpy()
        while n_tr < 2 and t < len(night) - 1:
            ep = oo[t]; hit = None
            for u in range(t, len(night) - 1):
                if hh[u] >= ep + TGT + THR: hit = u; break
            px, kind = (ep + TGT, "target") if hit is not None else (oo[-1], "time")
            net += (px - ep - TICK * (1 + (kind == "time"))) * PV - COMM; n_tr += 1
            if hit is None: break
            t = hit + 1
            while t < len(night) - 1 and idx[t].minute % 5 != 1: t += 1      # next 5-minute bar's open
        out.append(dict(date=D + pd.Timedelta(days=1), net=net, trades=n_tr, r2=q))
    return pd.DataFrame(out).set_index("date")


def report(N):
    def line(x, nm):
        t = x.mean() / x.std() * np.sqrt(len(x)); pf = x[x > 0].sum() / -x[x < 0].sum()
        return f"  {nm:<28} nights {len(x):4d}  net ${x.sum():>9,.0f}  avg ${x.mean():6.1f}  t {t:5.2f}  PF {pf:4.2f}  win {(x > 0).mean():.0%}"
    print(line(N.net, "all"))
    for nm, a, b in PERIODS:
        x = N.net[a:b]
        if len(x) > 2: print(line(x, nm))
    print("  by year: " + "  ".join(f"{y} ${v / 1e3:,.1f}k" for y, v in N.net.groupby(N.index.year).sum().items()))


def selftest():
    """Synthetic bars with a planted overnight drift: the rule must find it; with no drift, it must not."""
    rng = np.random.default_rng(0); out = {}
    for drift in (0.0, 0.08):
        idx = pd.date_range("2018-01-01 17:01", "2019-12-31 16:00", freq="min")
        idx = idx[(idx.dayofweek < 5) | ((idx.dayofweek == 6) & (idx.hour >= 17))]
        idx = idx[~((idx.hour == 16) & (idx.minute > 0))]
        night = (idx.hour >= 17) | (idx.hour < 8)
        ret = rng.normal(0, 1.2, len(idx)) + np.where(night, drift, -drift * 0.5) + 0.02
        cl = 10000 + np.cumsum(ret); op = np.r_[cl[0], cl[:-1]]
        bars = pd.DataFrame(dict(open=op, high=np.maximum(op, cl) + 0.5, low=np.minimum(op, cl) - 0.5, close=cl), index=idx)
        out[drift] = nights(bars).net.mean()
    print(f"self-test: avg $ per night, no drift {out[0.0]:.0f}, planted drift {out[0.08]:.0f}")
    assert out[0.08] > out[0.0] + 50, "rule failed to find a planted overnight drift"
    print("self-test passed")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest": selftest(); sys.exit()
    print(__doc__.split("\n")[0]); N = nights(load(sys.argv[1] if len(sys.argv) > 1 else "NQ_1min_*.csv")); report(N)
