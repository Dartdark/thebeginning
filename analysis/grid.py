"""1-minute NQ bars as a day x minute grid, plus a small execution engine.

Shared by the multi-strategy research (analysis/candidates.py,
analysis/portfolio.py). Grid column j is the 1-minute bar that CLOSES at
08:00 CT + j minutes, so j = 0 is the 08:00 bar and j = 435 the 15:15 bar.
Missing minutes (holiday half-days) are NaN.

5-minute bars are stamped at their close like MultiCharts: the 5-minute bar
stamped 10:10 is 1-minute columns 10:06..10:10, and "next bar at market"
after it fills at the open of the 10:11 column.

Execution matches analysis/replica.py: stop and target checked on 1-minute
bars (Bar Magnifier), O-H-L-C path when the open is nearer the high,
targets fill only when price trades 1 point through, a stop that gaps fills
at the open. P&L is per 1 NQ ($20/point), before costs.

Check: replaying the 3,497 MultiCharts v3 trades (entries from the report,
exits walked here with the 80/40/50 brackets) gives the same entry price on
100% and the same P&L on 99.4%; the rest are targets MultiCharts filled
right at the 1-point fill-through edge.
"""
import glob
import numpy as np
import pandas as pd

try:
    from numba import njit
except ImportError:                     # works without numba, just slower
    def njit(*a, **k):
        return (lambda f: f) if not (a and callable(a[0])) else a[0]

POINT_VALUE = 20.0
FILL_THROUGH = 1.0
COST = 7.25                             # $ per NQ round trip, as in the notebook
NMIN = 436                              # 08:00 .. 15:15


def j_of(hhmm):
    """Grid column of the 1-minute bar closing at hhmm (CT)."""
    return (hhmm // 100) * 60 + hhmm % 100 - 480


def hhmm_of(j):
    m = j + 480
    return (m // 60) * 100 + m % 60


class Grid:
    def __init__(self, pattern="NQ_1min_*.csv"):
        d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(pattern))], ignore_index=True)
        d = d.drop_duplicates(["date", "time"])
        last = d.groupby("date")["time"].transform("max")
        d = d[last >= 1100]                     # drop days with no real session (e.g. 2025-01-09)
        self.dates = np.array(sorted(d["date"].unique()))
        self.ts = pd.to_datetime(pd.Series(self.dates).astype(str)).to_numpy()
        di = np.searchsorted(self.dates, d["date"].to_numpy())
        mj = j_of(d["time"].to_numpy())
        ok = (mj >= 0) & (mj < NMIN)
        shape = (len(self.dates), NMIN)
        for c in ("open", "high", "low", "close", "volume"):
            a = np.full(shape, np.nan)
            a[di[ok], mj[ok]] = d[c].to_numpy(float)[ok]
            setattr(self, c[0] if c != "volume" else "v", a)
        self.D = len(self.dates)
        self.last_j = np.array([np.max(np.nonzero(~np.isnan(r))[0]) if (~np.isnan(r)).any() else -1
                                for r in self.c])
        self._daily()

    def _daily(self):
        """Regular-session (08:31-15:15) daily values and features known before the open."""
        rth = slice(j_of(831), NMIN)
        hi = np.nanmax(self.h[:, rth], axis=1)
        lo = np.nanmin(self.l[:, rth], axis=1)
        cl = np.array([r[~np.isnan(r)][-1] for r in self.c[:, rth]])
        op = self.o[:, j_of(831)]
        self.rth_open, self.rth_high, self.rth_low, self.rth_close = op, hi, lo, cl
        rng = (hi - lo) / cl * 100
        s = pd.Series(rng)
        self.range_pct = rng
        self.avg10 = s.rolling(10).mean().shift(1).to_numpy()          # same as the filter line
        self.prev_close = np.r_[np.nan, cl[:-1]]
        self.prev_high = np.r_[np.nan, hi[:-1]]
        self.prev_low = np.r_[np.nan, lo[:-1]]

    def bars(self, k=5):
        """k-minute OHLCV arrays (D, K), aligned to 08:00 and stamped at their close
        (k=5: 08:05 .. 15:15; k=30: 08:30 .. 15:00), with "j" = the last 1-minute
        column of each bar. A bar with no data is NaN."""
        ks = np.arange(1, (NMIN - 1) // k + 1) * k
        o = np.full((self.D, len(ks)), np.nan); h = o.copy(); l = o.copy(); c = o.copy(); v = o.copy()
        rows = np.arange(self.D)
        for i, je in enumerate(ks):
            sl = slice(je - k + 1, je + 1)
            ob, cb = self.o[:, sl], self.c[:, sl]
            with np.errstate(all="ignore"):
                h[:, i] = np.nanmax(self.h[:, sl], axis=1)
                l[:, i] = np.nanmin(self.l[:, sl], axis=1)
                v[:, i] = np.nansum(self.v[:, sl], axis=1)
            o[:, i] = ob[rows, np.argmax(~np.isnan(ob), axis=1)]
            c[:, i] = cb[rows, k - 1 - np.argmax(~np.isnan(cb[:, ::-1]), axis=1)]
            v[np.isnan(c[:, i]), i] = np.nan
        return dict(o=o, h=h, l=l, c=c, v=v, j=ks)

    def five(self):
        return self.bars(5)

    def vwap_from(self, start=800):
        """Running VWAP of 1-minute (H+L+C)/3 x volume from the bar closing after
        `start` (CT). Value known at the close of each 1-minute column."""
        a = j_of(start) + 1
        tp = (self.h + self.l + self.c) / 3
        vv = np.nan_to_num(self.v); pv = np.nan_to_num(tp) * vv
        out = np.full((self.D, NMIN), np.nan)
        cv = np.cumsum(vv[:, a:], axis=1)
        with np.errstate(all="ignore"):
            out[:, a:] = np.cumsum(pv[:, a:], axis=1) / cv
        return out

    def vwap15(self, anchor=830):
        """The strategy's VWAP: 15-minute buckets after the anchor, (H+L+C)/3 x volume.
        Returns (D, NMIN) arrays of the VWAP and the previous VWAP value known
        at the close of each 1-minute column (updates only at bucket ends)."""
        a = j_of(anchor)
        vw = np.full((self.D, NMIN), np.nan); vp = vw.copy()
        cpv = np.zeros(self.D); cv = np.zeros(self.D)
        now = np.full(self.D, np.nan); prev = np.full(self.D, np.nan)
        for je in range(a + 15, NMIN, 15):
            sl = slice(je - 14, je + 1)
            with np.errstate(all="ignore"):
                hh = np.nanmax(self.h[:, sl], axis=1); ll = np.nanmin(self.l[:, sl], axis=1)
                vv = np.nansum(self.v[:, sl], axis=1)
            cb = self.c[:, sl]
            li = 14 - np.argmax(~np.isnan(cb[:, ::-1]), axis=1)
            cc = cb[np.arange(self.D), li]
            good = ~np.isnan(cc) & (vv > 0)
            cpv[good] += (hh[good] + ll[good] + cc[good]) / 3 * vv[good]
            cv[good] += vv[good]
            prev = np.where(good, now, prev)
            now = np.where(good, cpv / np.where(cv > 0, cv, np.nan), now)
            vw[:, je:je + 15] = now[:, None]
            vp[:, je:je + 15] = prev[:, None]
        return vw, vp


@njit(cache=True)
def _walk(o, h, l, c, j0, jend, side, stop_px, tgt_px, fill_through):
    """From the open of column j0 to the close of column jend, find the exit.
    Returns (exit_j, exit_px, kind, worst_px); kind 0 stop, 1 target, 2 time."""
    entry = o[j0]
    worst = entry
    for j in range(j0, jend + 1):
        oo = o[j]; hh = h[j]; ll = l[j]
        if np.isnan(oo):
            continue
        if side > 0:
            if j > j0 and oo <= stop_px:
                return j, oo, 0, min(worst, oo)
            hit_t = hh >= tgt_px + fill_through
            hit_s = ll <= stop_px
            if hit_t and hit_s:
                if (hh - oo) <= (oo - ll):
                    return j, tgt_px, 1, min(worst, ll)
                return j, stop_px, 0, stop_px if stop_px < worst else worst
            if hit_s:
                return j, stop_px, 0, min(worst, stop_px)
            if hit_t:
                return j, tgt_px, 1, min(worst, ll)
            worst = min(worst, ll)
        else:
            if j > j0 and oo >= stop_px:
                return j, oo, 0, max(worst, oo)
            hit_t = ll <= tgt_px - fill_through
            hit_s = hh >= stop_px
            if hit_t and hit_s:
                if (oo - ll) <= (hh - oo):
                    return j, tgt_px, 1, max(worst, hh)
                return j, stop_px, 0, stop_px if stop_px > worst else worst
            if hit_s:
                return j, stop_px, 0, max(worst, stop_px)
            if hit_t:
                return j, tgt_px, 1, max(worst, hh)
            worst = max(worst, hh)
    # time exit at the close of jend (or the last bar of the day)
    k = jend
    while k > j0 and np.isnan(c[k]):
        k -= 1
    return k, c[k], 2, worst


def execute(g, sig, max_trades=99, max_losses=99, name=""):
    """Turn signals into trades, one position at a time.

    sig: DataFrame with columns day, dj (decision column: the 1-minute column
    at whose close the signal is known), side (+1/-1), stop (points),
    target (points, np.inf = none), exit_j (time-exit column), optional qty
    (position size in NQ, default 1; P&L columns are per position). A signal is
    taken only if the strategy is flat by the close of dj and the day's trade
    and loss caps allow it. Entry is at the open of column dj + 1.
    """
    sig = sig.sort_values(["day", "dj"], kind="stable")
    out = []
    o, h, l, c = g.o, g.h, g.l, g.c
    if "qty" not in sig:
        sig = sig.assign(qty=1.0)
    for day, s in sig.groupby("day", sort=True):
        flat_at = -1; n = 0; losses = 0
        for dj, side, sp, tp, xj, q in zip(s["dj"].to_numpy(), s["side"].to_numpy(),
                                           s["stop"].to_numpy(), s["target"].to_numpy(),
                                           s["exit_j"].to_numpy(), s["qty"].to_numpy()):
            if q <= 0:
                continue
            if dj < flat_at or n >= max_trades or losses >= max_losses:
                continue
            j0 = int(dj) + 1
            xj = int(min(xj, g.last_j[day]))
            if j0 > xj or np.isnan(o[day, j0]):
                continue
            entry = o[day, j0]
            stop_px = entry - side * sp
            tgt_px = entry + side * tp if np.isfinite(tp) else (np.inf if side > 0 else -np.inf)
            xj_, px, kind, worst = _walk(o[day], h[day], l[day], c[day], j0, xj, int(side),
                                         stop_px, tgt_px, FILL_THROUGH)
            pnl = (px - entry) * side * POINT_VALUE
            out.append((day, j0, xj_, int(side), entry, px, kind, pnl * q,
                        abs(worst - entry) * POINT_VALUE * q, q))
            n += 1; losses += pnl < 0
            flat_at = xj_
    t = pd.DataFrame(out, columns=["day", "j0", "j1", "side", "entry", "exit", "kind", "pnl", "mae", "qty"])
    t["date"] = g.ts[t["day"].to_numpy()] if len(t) else pd.Series(dtype="datetime64[ns]")
    t["net"] = t["pnl"] - COST * t["qty"]
    t.attrs["name"] = name
    return t
