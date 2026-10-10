"""The full 24-hour NQ day: the 08:00-15:15 exports (NQ_1min_<year>.csv) joined
with the overnight exports (NQ_1min_ON_<year>.csv, 15:16-07:59 CT).

Grid24 has one row per CALENDAR date (weekends and holidays included, mostly
empty, so the rows run back to back in time) and one column per minute:
column j is the 1-minute bar that closes at 00:00 + j minutes, so j = 0 is
the 00:00 bar (the first bar of the date, as MultiCharts stamps it) and
j = 1439 the 23:59 bar.

It works with grid.execute() and portfolio.py like Grid does. For Apex
challenges, use the rows in `trading` (the weekdays of the 08:00-15:15
grid), so a challenge counts the same trading days as before.
"""
import glob
import numpy as np
import pandas as pd

NMIN24 = 1440


def jof(hhmm):
    """Column of the 1-minute bar closing at hhmm (CT)."""
    hhmm = np.asarray(hhmm)
    return (hhmm // 100) * 60 + hhmm % 100


class Grid24:
    def __init__(self, day_pattern="NQ_1min_20*.csv", night_pattern="NQ_1min_ON_*.csv"):
        files = sorted(glob.glob(day_pattern)) + sorted(glob.glob(night_pattern))
        d = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
        d = d.drop_duplicates(["date", "time"])
        day_dates = np.array(sorted(pd.concat([pd.read_csv(f, usecols=["date", "time"])
                                               for f in sorted(glob.glob(day_pattern))])
                                    .groupby("date")["time"].max().loc[lambda x: x >= 1100].index))
        first = pd.Timestamp(str(d["date"].min())); last = pd.Timestamp(str(d["date"].max()))
        cal = pd.date_range(first, last, freq="D")
        self.ts = cal.to_numpy()
        self.dates = cal.strftime("%Y%m%d").astype(int).to_numpy()
        self.D = len(cal)
        row = np.searchsorted(self.dates, d["date"].to_numpy())
        col = jof(d["time"].to_numpy())
        for c in ("open", "high", "low", "close", "volume"):
            a = np.full((self.D, NMIN24), np.nan)
            a[row, col] = d[c].to_numpy(float)
            setattr(self, c[0] if c != "volume" else "v", a)
        has = ~np.isnan(self.c)
        self.last_j = np.where(has.any(1), NMIN24 - 1 - np.argmax(has[:, ::-1], axis=1), -1)
        self.trading = np.searchsorted(self.dates, day_dates)      # weekday trading rows
        self.jof = jof

    # ---------- bars of k minutes, aligned to midnight ----------
    def bars(self, k):
        """k-minute OHLCV (k divides 1440) as (D, 1440 // k) arrays; bar i of a
        row closes at column i * k (so bar 0 is the one closing at 00:00, which
        holds the last k - 1 minutes of the previous date, as on a chart)."""
        flat = {c: getattr(self, c).ravel() for c in ("o", "h", "l", "c", "v")}
        pad = k - 1
        n = len(flat["c"]) + pad
        tail = (-n) % k
        out = {}
        for c, a in flat.items():
            x = np.r_[np.full(pad, np.nan), a, np.full(tail, np.nan)].reshape(-1, k)
            with np.errstate(all="ignore"):
                if c == "h":
                    y = np.nanmax(x, axis=1)
                elif c == "l":
                    y = np.nanmin(x, axis=1)
                elif c == "v":
                    y = np.nansum(x, axis=1)
                elif c == "o":
                    y = x[np.arange(len(x)), np.argmax(~np.isnan(x), axis=1)]
                else:
                    y = x[np.arange(len(x)), k - 1 - np.argmax(~np.isnan(x[:, ::-1]), axis=1)]
            out[c] = y
        out["v"][np.isnan(out["c"])] = np.nan
        per = NMIN24 // k
        res = {c: out[c][:self.D * per].reshape(self.D, per) for c in out}
        res["j"] = np.arange(per) * k
        return res

    def vwap_rows(self, b=None, start_j=0):
        """Running VWAP per calendar date from column start_j, of 1-minute bars
        (b=None) or of the bars in dict b; (H+L+C)/3 x volume."""
        if b is None:
            h, l, c, v, J = self.h, self.l, self.c, self.v, np.arange(NMIN24)
        else:
            h, l, c, v, J = b["h"], b["l"], b["c"], b["v"], b["j"]
        tp = (h + l + c) / 3
        m = (J >= start_j)[None, :] & ~np.isnan(c)
        pv = np.where(m, tp * np.nan_to_num(v), 0).cumsum(1)
        vv = np.where(m, np.nan_to_num(v), 0).cumsum(1)
        with np.errstate(all="ignore"):
            out = pv / vv
        out[:, J < start_j] = np.nan
        return out

    def daily_atr(self, n=15):
        """ATR of the previous n weekday calendar dates (true range of each
        date's bars with the previous date's last close), known on each date."""
        hi = np.nanmax(self.h, axis=1); lo = np.nanmin(self.l, axis=1)
        has = ~np.isnan(self.c).all(1)
        last = np.array([r[~np.isnan(r)][-1] if ok else np.nan for r, ok in zip(self.c, has)])
        prev = pd.Series(last).where(has).ffill().shift(1).to_numpy()
        tr = np.nanmax(np.c_[hi - lo, np.abs(hi - prev), np.abs(lo - prev)], axis=1)
        wk = pd.DatetimeIndex(self.ts).dayofweek < 5
        keep = has & wk
        s = pd.Series(np.where(keep, tr, np.nan))
        avg = s.dropna().rolling(n).mean()
        # value known on date d = average of the n stored dates before d
        known = pd.Series(np.nan, index=range(self.D))
        known.loc[avg.index] = avg.values
        return known.shift(1).ffill().to_numpy()
