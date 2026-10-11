"""Intraday NQ strategies from the research list (multi_strategy/RESEARCH_TOPICS.md),
tested on the 1-minute data (Grid24, regular session 8:30-15:00 CT, flat at the
15:00 close; holiday half-days flat at their last bar).

  1. VWAP trend         Zarattini & Aziz, "VWAP: The Holy Grail for Day Trading
                        Systems" (SSRN 4631351): long above the session VWAP, short
                        below, checked every k minutes; optional buffer.
  2. Noise area         Zarattini, Aziz & Barbon, "Beat the Market" (2024): band =
                        max/min(open, previous close) x (1 +/- m x average absolute
                        move from the open at that minute over 14 days); checks
                        every 30 minutes from 9:00; trailing stop at the band or
                        VWAP; re-entries and reversals during the day.
  3. Big-move reversal  Grant, Wolf & Yu (2005); Nagel (2012): fade an L-minute move
                        that is k times the normal move for that time of day,
                        optionally only when volatility is high; target half the
                        move back, stop one move further, time stop.
  4. Round numbers      Osler (2003): (a) fade the first touch of a 100/50-point level,
                        (b) follow a close through a level.

Costs: $7.25 per NQ round trip, plus 1 tick (0.25 point) of slippage on every
market or stop fill (limit entries and targets get no slippage; targets need
price 1 point through, as in the other tests). Slippage is put into the fill
prices, so portfolio.paths() and the funded simulator see it too.

Usage (from the repo root): python3 analysis/intraday_research.py   (a few minutes)
"""
import sys
import warnings
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
warnings.filterwarnings("ignore")
from grid import _walk, njit, FILL_THROUGH, POINT_VALUE, COST
from grid24 import Grid24, jof

TICK = 0.25
J_OPEN = jof(830)          # column of the bar closing 8:30; the session opens at J_OPEN + 1
J_FLAT = jof(1500)


# ---------------------------------------------------------------- data
class Data:
    def __init__(self, g):
        tr = g.trading
        self.g, self.tr = g, tr
        self.O, self.H, self.L, self.C, self.V = (getattr(g, k)[tr] for k in ("o", "h", "l", "c", "v"))
        self.D = len(tr)
        self.ts = g.ts[tr]
        self.yr = pd.DatetimeIndex(self.ts).year.to_numpy()
        rth = np.zeros(self.D, dtype=np.int64)
        for i in range(self.D):
            ok = np.nonzero(~np.isnan(self.C[i, J_OPEN + 1:J_FLAT + 1]))[0]
            rth[i] = J_OPEN + 1 + ok[-1] if len(ok) else -1
        self.flat = rth                                           # last regular-session column
        self.open = self.O[:, J_OPEN + 1]
        self.close = np.array([self.C[i, f] if f > 0 else np.nan for i, f in enumerate(rth)])
        self.prev_close = np.r_[np.nan, self.close[:-1]]
        self.atr = g.daily_atr(15)[tr]
        # session VWAP from 8:30, value at each 1-minute close
        tp = (self.H + self.L + self.C) / 3
        m = np.zeros(1440, bool); m[J_OPEN + 1:] = True
        v = np.where(m[None, :] & ~np.isnan(self.C), np.nan_to_num(self.V), 0.0)
        pv = np.where(v > 0, tp, 0.0) * v
        with np.errstate(all="ignore"):
            self.VW = np.cumsum(pv, 1) / np.cumsum(v, 1)
        self.Cf = pd.DataFrame(self.C).ffill(axis=1).to_numpy()   # last close at each minute


def trades_df(d, rec, name):
    t = pd.DataFrame(rec, columns=["i", "j0", "j1", "side", "entry", "exit", "kind"])
    t = t[t.i >= 0].reset_index(drop=True)
    t["i"] = t.i.astype(int); t["j0"] = t.j0.astype(int); t["j1"] = t.j1.astype(int)
    t["side"] = t.side.astype(int); t["kind"] = t.kind.astype(int)
    t["day"] = d.tr[t.i.to_numpy()]
    t["date"] = d.ts[t.i.to_numpy()]
    t["pnl"] = (t.exit - t.entry) * t.side * POINT_VALUE
    t["net"] = t.pnl - COST
    t.attrs["name"] = name
    return t


@njit(cache=True)
def _put(out, n, i, j0, j1, side, entry, exit_, kind):
    out[n, 0] = i; out[n, 1] = j0; out[n, 2] = j1; out[n, 3] = side
    out[n, 4] = entry; out[n, 5] = exit_; out[n, 6] = kind


# ---------------------------------------------------------------- 1. VWAP trend
@njit(cache=True)
def _vwap_trend(O, C, VW, flat, step, buf, long_only, first_j, last_j):
    D = O.shape[0]
    out = np.full((D * 60, 7), -1.0); n = 0
    for i in range(D):
        fj = flat[i]
        if fj < 0:
            continue
        pos = 0; ent = 0.0; j0 = 0
        for j in range(first_j, fj):
            if (j - J_OPEN) % step != 0 or np.isnan(C[i, j]) or np.isnan(VW[i, j]):
                continue
            want = pos
            if C[i, j] > VW[i, j] + buf[i]:
                want = 1
            elif C[i, j] < VW[i, j] - buf[i]:
                want = 0 if long_only else -1
            if j >= last_j and want != 0 and pos == 0:
                want = 0
            if want != pos and not np.isnan(O[i, j + 1]):
                px = O[i, j + 1]
                if pos != 0:
                    _put(out, n, i, j0, j + 1, pos, ent, px - pos * TICK, 2); n += 1
                pos = want
                if pos != 0:
                    ent = px + pos * TICK; j0 = j + 1
        if pos != 0:
            _put(out, n, i, j0, fj, pos, ent, C[i, fj] - pos * TICK, 2); n += 1
    return out[:n]


def vwap_trend(d, step=1, buf_atr=0.0, long_only=False, start=830, last=1430):
    buf = np.nan_to_num(buf_atr * d.atr)
    rec = _vwap_trend(d.O, d.C, d.VW, d.flat, step, buf, long_only, jof(start) + step, jof(last))
    return trades_df(d, rec, f"VWAP trend {step}m buf {buf_atr}")


# ---------------------------------------------------------------- 2. noise area
def noise_sigma(d, lookback=14):
    """Average |close / session open - 1| at each minute over the previous
    `lookback` trading days (known before the day)."""
    mv = np.abs(d.Cf / d.open[:, None] - 1)
    mv[:, :J_OPEN + 1] = np.nan
    s = pd.DataFrame(mv).rolling(lookback, min_periods=lookback).mean().shift(1)
    return s.to_numpy()


@njit(cache=True)
def _noise(O, C, VW, flat, op, pc, sig, mult, step, first_j, long_only, trail_vwap, last_j):
    D = O.shape[0]
    out = np.full((D * 20, 7), -1.0); n = 0
    for i in range(D):
        fj = flat[i]
        if fj < 0 or np.isnan(pc[i]) or np.isnan(op[i]):
            continue
        hi_ref = max(op[i], pc[i]); lo_ref = min(op[i], pc[i])
        pos = 0; ent = 0.0; j0 = 0
        for j in range(first_j, fj):
            if (j - J_OPEN) % step != 0 or np.isnan(C[i, j]) or np.isnan(sig[i, j]):
                continue
            ub = hi_ref * (1 + mult * sig[i, j]); lb = lo_ref * (1 - mult * sig[i, j])
            c = C[i, j]
            want = pos
            if pos == 1:
                stop = max(ub, VW[i, j]) if trail_vwap else ub
                if c < stop:
                    want = 0
            elif pos == -1:
                stop = min(lb, VW[i, j]) if trail_vwap else lb
                if c > stop:
                    want = 0
            if want == 0 and j < last_j:
                if c > ub:
                    want = 1
                elif c < lb and not long_only:
                    want = -1
            if want != pos and not np.isnan(O[i, j + 1]):
                px = O[i, j + 1]
                if pos != 0:
                    _put(out, n, i, j0, j + 1, pos, ent, px - pos * TICK, 2); n += 1
                pos = want
                if pos != 0:
                    ent = px + pos * TICK; j0 = j + 1
        if pos != 0:
            _put(out, n, i, j0, fj, pos, ent, C[i, fj] - pos * TICK, 2); n += 1
    return out[:n]


def noise_area(d, sig, mult=1.0, step=30, first=900, long_only=False, trail_vwap=True, last=1430):
    rec = _noise(d.O, d.C, d.VW, d.flat, d.open, d.prev_close, sig, mult, step, jof(first),
                 long_only, trail_vwap, jof(last))
    return trades_df(d, rec, f"Noise area m{mult} {step}m")


# ---------------------------------------------------------------- 3. big-move reversal
@njit(cache=True)
def _reversal(O, H, L, C, Cf, flat, norm, ok_day, lag, k, back, stop_m, hold, first_j, last_j, max_tr):
    D = O.shape[0]
    out = np.full((D * max_tr, 7), -1.0); n = 0
    for i in range(D):
        fj = flat[i]
        if fj < 0 or not ok_day[i]:
            continue
        busy_to = -1; cnt = 0
        for j in range(first_j, min(last_j, fj)):
            if j <= busy_to or cnt >= max_tr or np.isnan(C[i, j]) or np.isnan(norm[i, j]):
                continue
            mv = Cf[i, j] - Cf[i, j - lag]
            if norm[i, j] <= 0 or abs(mv) < k * norm[i, j] or np.isnan(O[i, j + 1]):
                continue
            side = -1 if mv > 0 else 1
            e = O[i, j + 1]
            size = abs(mv)
            stop_px = e - side * stop_m * size
            tgt_px = e + side * back * size
            jend = min(j + 1 + hold, fj)
            j1, px, kind, w = _walk(O[i], H[i], L[i], C[i], j + 1, jend, side, stop_px, tgt_px, FILL_THROUGH)
            xpx = px if kind == 1 else px - side * TICK
            _put(out, n, i, j + 1, j1, side, e + side * TICK, xpx, kind); n += 1
            cnt += 1; busy_to = j1
    return out[:n]


def move_norm(d, lag, lookback=20):
    mv = np.abs(d.Cf - np.roll(d.Cf, lag, axis=1))
    mv[:, :J_OPEN + 1 + lag] = np.nan
    return pd.DataFrame(mv).rolling(lookback, min_periods=lookback).mean().shift(1).to_numpy()


def high_vol_days(d, window=250):
    v = pd.Series(d.atr / d.open)
    return (v > v.rolling(window, min_periods=60).median().shift(1)).to_numpy()


def reversal(d, norm, lag=30, k=2.5, back=0.5, stop_m=1.0, hold=60, cond=None, first=900, last=1430, max_tr=3):
    ok = np.ones(d.D, bool) if cond is None else cond
    rec = _reversal(d.O, d.H, d.L, d.C, d.Cf, d.flat, norm, ok, lag, k, back, stop_m, hold,
                    jof(first), jof(last), max_tr)
    return trades_df(d, rec, f"Reversal {lag}m k{k}")


# ---------------------------------------------------------------- 4. round numbers
@njit(cache=True)
def _round(O, H, L, C, flat, atr, R, mode, s_atr, t_atr, b_atr, hold, first_j, last_j, max_tr):
    """mode 0: fade the first touch of each level (limit at the level).
    mode 1: follow a 1-minute close at least b x ATR through a level."""
    D = O.shape[0]
    out = np.full((D * max_tr, 7), -1.0); n = 0
    for i in range(D):
        fj = flat[i]
        if fj < 0 or np.isnan(atr[i]):
            continue
        s = s_atr * atr[i]; t = t_atr * atr[i]; b = b_atr * atr[i]
        touched = np.zeros(64)       # levels already traded today (ring)
        nt = 0; busy_to = -1; cnt = 0
        for j in range(first_j, min(last_j, fj)):
            if j <= busy_to or cnt >= max_tr or np.isnan(C[i, j - 1]) or np.isnan(H[i, j]):
                continue
            p = C[i, j - 1]
            up = np.ceil(p / R) * R; dn = np.floor(p / R) * R
            if mode == 0:
                for side, lev in ((-1, up), (1, dn)):
                    if lev == p:
                        continue
                    hit = H[i, j] >= lev + TICK if side < 0 else L[i, j] <= lev - TICK
                    if not hit:
                        continue
                    seen = False
                    for q in range(nt):
                        if touched[q] == lev:
                            seen = True
                    if seen:
                        continue
                    touched[nt % 64] = lev; nt += 1
                    e = max(O[i, j], lev) if side < 0 else min(O[i, j], lev)
                    stop_px = e - side * s; tgt_px = e + side * t
                    # same bar: assume the stop is hit if the bar reached it
                    if (side < 0 and H[i, j] >= stop_px) or (side > 0 and L[i, j] <= stop_px):
                        _put(out, n, i, j, j, side, e, stop_px - side * TICK, 0); n += 1
                        cnt += 1; busy_to = j
                        break
                    jend = min(j + hold, fj)
                    j1, px, kind, w = _walk(O[i], H[i], L[i], C[i], j + 1, jend, side, stop_px, tgt_px, FILL_THROUGH)
                    xpx = px if kind == 1 else px - side * TICK
                    _put(out, n, i, j, j1, side, e, xpx, kind); n += 1
                    cnt += 1; busy_to = j1
                    break
            else:
                c = C[i, j]
                lev_up = np.floor((c - b) / R) * R       # level crossed upward
                if p < lev_up + b <= c and not np.isnan(O[i, j + 1]):
                    side = 1; lev = lev_up
                else:
                    lev_dn = np.ceil((c + b) / R) * R
                    if p > lev_dn - b >= c and not np.isnan(O[i, j + 1]):
                        side = -1; lev = lev_dn
                    else:
                        continue
                seen = False
                for q in range(nt):
                    if touched[q] == lev * side:
                        seen = True
                if seen:
                    continue
                touched[nt % 64] = lev * side; nt += 1
                e = O[i, j + 1]
                stop_px = lev - side * s; tgt_px = e + side * t
                if (side > 0 and stop_px >= e) or (side < 0 and stop_px <= e):
                    continue
                jend = min(j + 1 + hold, fj)
                j1, px, kind, w = _walk(O[i], H[i], L[i], C[i], j + 1, jend, side, stop_px, tgt_px, FILL_THROUGH)
                xpx = px if kind == 1 else px - side * TICK
                _put(out, n, i, j + 1, j1, side, e + side * TICK, xpx, kind); n += 1
                cnt += 1; busy_to = j1
    return out[:n]


def round_numbers(d, R=100.0, mode=0, s_atr=0.05, t_atr=0.05, b_atr=0.02, hold=60,
                  first=835, last=1430, max_tr=5):
    rec = _round(d.O, d.H, d.L, d.C, d.flat, d.atr, R, mode, s_atr, t_atr, b_atr, hold,
                 jof(first), jof(last), max_tr)
    return trades_df(d, rec, f"Round {R:.0f} {'fade' if mode == 0 else 'break'}")


# ---------------------------------------------------------------- reporting
def stats(d, t, ref=None):
    daily = np.zeros(d.D); np.add.at(daily, t.i.to_numpy(), t.net.to_numpy())
    td = np.zeros(d.D, bool); td[t.i.to_numpy()] = True
    w, l = t.net[t.net > 0].sum(), -t.net[t.net < 0].sum()
    by = pd.Series(daily[td]).groupby(d.yr[td]).mean()
    dd = daily[td]
    out = dict(trades=len(t), per_day=len(t) / d.D, win=(t.net > 0).mean(), avg=t.net.mean(),
               pf=w / l if l > 0 else np.nan, t_days=dd.mean() / dd.std() * np.sqrt(len(dd)),
               sharpe=daily.mean() / daily.std() * np.sqrt(252), yrs_pos=int((by > 0).sum()),
               avg_18_22=t.net[d.yr[t.i] < 2023].mean(), avg_23_26=t.net[d.yr[t.i] >= 2023].mean())
    if ref is not None:
        for k, r in ref.items():
            out["corr_" + k] = np.corrcoef(daily, r)[0, 1]
    return out, daily


def table(rows):
    df = pd.DataFrame(rows).T
    fm = {"per_day": "{:.2f}", "win": "{:.0%}", "avg": "{:.0f}", "pf": "{:.2f}", "t_days": "{:.1f}",
          "sharpe": "{:.2f}", "avg_18_22": "{:.0f}", "avg_23_26": "{:.0f}"}
    for c in df:
        if c.startswith("corr_"):
            fm[c] = "{:.2f}"
    print(df.to_string(formatters={k: v.format for k, v in fm.items() if k in df}))


def reference_daily(d):
    """Daily P&L per NQ of the plan's strategies (MultiCharts reports, Python OND)."""
    from grid import execute
    from portfolio import load_mc
    from candidates24 import overnight_drift24
    from multi_strategy24 import VB_REPORT, ONB_REPORT
    pos = {r: i for i, r in enumerate(d.tr)}
    s, kw = overnight_drift24(d.g)
    ref = {}
    for k, t in (("VB", load_mc(d.g, VB_REPORT)), ("ONB", load_mc(d.g, ONB_REPORT)),
                 ("OND", execute(d.g, s, **kw))):
        x = np.zeros(d.D)
        for day, net in zip(t.day, t.net):
            if day in pos:
                x[pos[day]] += net
        ref[k] = x
    return ref


if __name__ == "__main__":
    d = Data(Grid24())
    ref = reference_daily(d)

    print("1. VWAP trend (per NQ, after costs and 1 tick slippage per market fill)")
    rows = {}
    for step in (1, 5, 15, 30):
        for buf in (0.0, 0.02, 0.05):
            t = vwap_trend(d, step=step, buf_atr=buf)
            rows[f"{step}m, buffer {buf} ATR"] = stats(d, t, ref)[0]
    for step in (5, 15):
        t = vwap_trend(d, step=step, buf_atr=0.02, long_only=True)
        rows[f"{step}m, buffer 0.02 ATR, long only"] = stats(d, t, ref)[0]
    table(rows)

    print("\n2. Noise area, the paper's full version")
    sig = noise_sigma(d)
    rows = {}
    for mult in (1.0, 1.5):
        for step in (30, 15):
            for lo in (False, True):
                t = noise_area(d, sig, mult=mult, step=step, long_only=lo)
                rows[f"m {mult}, every {step}m{', long only' if lo else ''}"] = stats(d, t, ref)[0]
    t = noise_area(d, sig, trail_vwap=False)
    rows["m 1.0, 30m, band stop only (no VWAP trail)"] = stats(d, t, ref)[0]
    table(rows)

    print("\n3. Big-move reversal")
    rows = {}
    hv = high_vol_days(d)
    for lag in (15, 30, 60):
        nm = move_norm(d, lag)
        for k in (2.0, 3.0):
            for cond, cn in ((None, "all days"), (hv, "high-vol days")):
                t = reversal(d, nm, lag=lag, k=k, hold=lag * 2, cond=cond)
                rows[f"{lag}m move > {k}x normal, {cn}"] = stats(d, t, ref)[0]
    table(rows)

    print("\n4. Round numbers")
    rows = {}
    for R in (100.0, 50.0):
        for s, tg in ((0.03, 0.03), (0.05, 0.05), (0.05, 0.10), (0.10, 0.10)):
            t = round_numbers(d, R=R, mode=0, s_atr=s, t_atr=tg)
            rows[f"fade {R:.0f}s, stop {s} / target {tg} ATR"] = stats(d, t, ref)[0]
        for s, tg in ((0.03, 0.06), (0.05, 0.10), (0.05, 0.20)):
            t = round_numbers(d, R=R, mode=1, s_atr=s, t_atr=tg)
            rows[f"break {R:.0f}s, stop {s} / target {tg} ATR"] = stats(d, t, ref)[0]
    table(rows)
