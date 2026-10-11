"""Intraday research from multi_strategy/RESEARCH_TOPICS.md, on the 24-hour
1-minute grid (grid24.py), with costs ($7.25 per NQ round trip) plus one tick
(0.25 point, $5 per NQ) of slippage on every market or stop fill.

  1. noise_momentum()   Zarattini, Aziz & Barbon, "Beat the Market" (2024):
                        time-of-day noise band from the 8:30 open, checks every
                        30 minutes, trailing exit at max(band, VWAP) (long),
                        flat 15:00. Vault Break is a cut-down version of it.
  2. vol_fade()         fade large 30/60-minute moves (Grant, Wolf & Yu 2005;
                        Nagel 2012), optionally only in high-volatility regimes
  3. round_levels()     Osler (2003): first touches of 100-point levels vs
                        placebo levels (event study), then fade / breakout rules

All trade lists have the columns portfolio.paths() needs (day, j0, j1, side,
entry, exit, kind, pnl, net, date); P&L per 1 NQ.
"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
from grid24 import jof
from candidates24 import _early

PV = 20.0
COST = 7.25
SLIP = 0.25                     # points per market / stop fill


def _frame(rows, g):
    t = pd.DataFrame(rows, columns=["day", "j0", "j1", "side", "entry", "exit", "kind", "slips"])
    t["pnl"] = (t["exit"] - t["entry"]) * t["side"] * PV
    t["net"] = t["pnl"] - COST - t["slips"] * SLIP * PV
    t["date"] = g.ts[t["day"].to_numpy()]
    return t


def rth_basics(g):
    """Per trading row: RTH open (open of the 8:31 bar), previous RTH close
    (15:00 bar, last bar before it on half-days), forward-filled closes."""
    tr = g.trading
    C = pd.DataFrame(g.c).ffill(axis=1).to_numpy()
    op = g.o[tr, jof(831)]
    cl = C[tr, jof(1500)]
    prev_cl = np.r_[np.nan, cl[:-1]]
    return tr, C, op, prev_cl


# ---------------------------------------------------------------- 1. noise momentum
def noise_momentum(g, lookback=14, mult=1.0, first=900, last=1430, step=30, flat=1500,
                   long_only=False, trail=True, stop_pts=None, tp_pts=None, vwap_trail=True):
    """Beat the Market on NQ (CT times; the paper's 10:00 ET = 9:00 CT).
    sigma_T = average |close at T / day open - 1| over the previous `lookback`
    trading days. Upper band = max(open, prev close) x (1 + mult x sigma_T),
    lower = min(open, prev close) x (1 - mult x sigma_T). At each decision
    time: flat and close above the upper band -> long at the next minute's
    open (below the lower -> short); long and close below max(upper, VWAP) ->
    exit (trail=True). Optional fixed stop / target in points, checked on
    1-minute bars. Flat at the close of the `flat` bar."""
    tr, C, op, prev_cl = rth_basics(g)
    times = list(range(first, last + 1, 100)) if step == 60 else \
        [t for t in range(first, last + 1, 5) if (t % 100) % step == 0 and t % 100 < 60]
    J = np.array([jof(t) for t in times])
    R = np.abs(C[tr][:, J] / op[:, None] - 1)
    sig = pd.DataFrame(R).rolling(lookback).mean().shift(1).to_numpy()
    # VWAP from 8:31 on 1-minute bars
    a = jof(831)
    tp = (g.h + g.l + g.c) / 3
    vol = np.nan_to_num(g.v)
    early = _early(g)
    rows = []
    for i, d in enumerate(tr):
        if np.isnan(op[i]) or np.isnan(prev_cl[i]) or np.isnan(sig[i]).any():
            continue
        hi_ref, lo_ref = max(op[i], prev_cl[i]), min(op[i], prev_cl[i])
        endj = min(jof(flat), g.last_j[d])
        if early[d]:
            endj = min(endj, jof(1145))
        pv = np.cumsum(np.nan_to_num(tp[d, a:endj + 1]) * vol[d, a:endj + 1])
        vv = np.cumsum(vol[d, a:endj + 1])
        with np.errstate(all="ignore"):
            vw = pv / vv
        pos = 0; entry = j0 = None
        for k, (t, jt) in enumerate(zip(times, J)):
            if jt + 1 > endj:
                break
            px = C[d, jt]
            ub = hi_ref * (1 + mult * sig[i, k]); lb = lo_ref * (1 - mult * sig[i, k])
            w = vw[jt - a]
            # fixed stop / target inside the last interval
            if pos != 0 and (stop_pts or tp_pts):
                j_from = j0 if k == 0 else max(j0, J[k - 1] + 1)
                hit = _bracket(g, d, j_from, jt, pos, entry, stop_pts, tp_pts)
                if hit:
                    jx, px_x, kind, sl = hit
                    rows.append((d, j0, jx, pos, entry, px_x, kind, 1 + sl)); pos = 0
            if pos == 1 and trail and px < (max(ub, w) if vwap_trail else ub):
                rows.append((d, j0, jt + 1, 1, entry, g.o[d, jt + 1], 2, 2)); pos = 0
            elif pos == -1 and trail and px > (min(lb, w) if vwap_trail else lb):
                rows.append((d, j0, jt + 1, -1, entry, g.o[d, jt + 1], 2, 2)); pos = 0
            if pos == 0:
                side = 1 if px > ub else (-1 if px < lb and not long_only else 0)
                if side and t < last + 1:
                    j0 = jt + 1; entry = g.o[d, j0]; pos = side
                    if np.isnan(entry):
                        pos = 0
        if pos != 0:
            if stop_pts or tp_pts:
                j_from = j0 if j0 > J[k - 1] else J[k - 1] + 1
                hit = _bracket(g, d, j_from, endj, pos, entry, stop_pts, tp_pts)
                if hit:
                    jx, px_x, kind, sl = hit
                    rows.append((d, j0, jx, pos, entry, px_x, kind, 1 + sl)); continue
            rows.append((d, j0, endj, pos, entry, C[d, endj], 2, 2))
    return _frame(rows, g)


def _bracket(g, d, j_from, j_to, side, entry, stop_pts, tp_pts):
    """First stop / target hit on 1-minute bars from j_from to j_to (stop first
    when both are in one bar). Returns (j, price, kind, extra slippage fills)."""
    for j in range(j_from, j_to + 1):
        h, l, o = g.h[d, j], g.l[d, j], g.o[d, j]
        if np.isnan(h):
            continue
        if stop_pts:
            sp = entry - side * stop_pts
            if (side > 0 and l <= sp) or (side < 0 and h >= sp):
                fill = min(o, sp) if side > 0 else max(o, sp)
                return j, fill, 0, 1
        if tp_pts:
            tp = entry + side * tp_pts
            if (side > 0 and h >= tp + 1) or (side < 0 and l <= tp - 1):
                return j, tp, 1, 0
    return None


# ---------------------------------------------------------------- shared reporting
def summary(t):
    y = pd.DatetimeIndex(t["date"]).year
    w, l = t.net[t.net > 0].sum(), -t.net[t.net < 0].sum()
    days = t["day"].nunique()
    by = t.groupby(y).net.mean()
    def rnd(x):
        return round(x) if pd.notna(x) else np.nan
    return dict(trades=len(t), per_day=round(len(t) / max(days, 1), 2), win=f"{(t.net > 0).mean():.0%}",
                avg=round(t.net.mean()), pf=round(w / l, 2) if l else np.nan,
                t_stat=round(t.net.mean() / t.net.std() * np.sqrt(len(t)), 1),
                avg_2018_22=rnd(t.net[y < 2023].mean()), avg_2023_26=rnd(t.net[y >= 2023].mean()),
                years_pos=f"{(by > 0).sum()}/{len(by)}")


def daily(g, t):
    s = t.groupby("day").net.sum()
    return s.reindex(g.trading, fill_value=0.0).to_numpy()


# ---------------------------------------------------------------- 2. volatility-conditioned fade
def vol_fade(g, look=30, k=2.0, first=900, last=1400, step=15, hold=60, tgt_frac=0.5,
             stop_frac=1.0, max_trades=3, regime=None, lookback=14, flat=1500):
    """At each `step`-minute close from first to last: move = close - close
    `look` minutes earlier; normal size = average |move| at that time of day
    over the previous `lookback` days. If |move| > k x normal: fade it at the
    next minute's open, target tgt_frac x |move| back, stop stop_frac x |move|
    beyond the entry, out after `hold` minutes or at `flat`. `regime`: boolean
    array per trading row (trade only where True)."""
    tr, C, op, prev_cl = rth_basics(g)
    times = [t for t in range(first, last + 1, 5) if (t % 100) % step == 0 and t % 100 < 60]
    J = np.array([jof(t) for t in times])
    M = C[tr][:, J] - C[tr][:, J - look]
    norm = pd.DataFrame(np.abs(M)).rolling(lookback).mean().shift(1).to_numpy()
    early = _early(g)
    rows = []
    for i, d in enumerate(tr):
        if regime is not None and not regime[i]:
            continue
        if np.isnan(norm[i]).any():
            continue
        endj = min(jof(flat), g.last_j[d])
        if early[d]:
            endj = min(endj, jof(1145))
        busy_until = -1; n = 0
        for kk, jt in enumerate(J):
            if jt + 1 > endj or n >= max_trades:
                break
            if jt < busy_until:
                continue
            mv = M[i, kk]
            if np.isnan(mv) or abs(mv) <= k * norm[i, kk]:
                continue
            side = -1 if mv > 0 else 1
            j0 = jt + 1; entry = g.o[d, j0]
            if np.isnan(entry):
                continue
            jend = min(j0 + hold - 1, endj)
            hit = _bracket(g, d, j0, jend, side, entry, stop_frac * abs(mv), tgt_frac * abs(mv))
            if hit:
                jx, px, kind, sl = hit
                rows.append((d, j0, jx, side, entry, px, kind, 1 + sl))
            else:
                jx = jend
                rows.append((d, j0, jx, side, entry, C[d, jx], 2, 2))
            busy_until = jx; n += 1
    return _frame(rows, g)


def high_vol_regime(g, atr_n=15, base=100):
    """True where the 15-day ATR known before the day is above its own
    `base`-day median (also known before the day)."""
    a = pd.Series(g.daily_atr(atr_n)[g.trading])
    return (a > a.rolling(base).median()).to_numpy()


# ---------------------------------------------------------------- 3. round numbers
def level_events(g, offsets=(0, 50, 25, 75, 37, 63, 12, 88), step=100, first=845, last=1430,
                 x_pts=(10, 20), horizon=30, cross_pts=5):
    """Event study of first touches of price levels L = n x step + offset in
    the RTH window. For each first touch of the day (from below: high >= L
    after closing below it; from above: the mirror), records:
      rev_X  : 1 if price went X points back (away from L, against the
               approach) before X points through L, within `horizon` minutes
      fwd    : move from L to the close `horizon` minutes later, in the
               direction of the approach (+ = continued through)
      cross  : 1 if a close went cross_pts through L within the horizon, and
      cont_X : after that close, 1 if X more points came before a return to L
    Returns a DataFrame of events with the level's offset."""
    tr = g.trading
    a, b = jof(first), jof(last)
    out = []
    for d in tr:
        h, l, c = g.h[d], g.l[d], g.c[d]
        if np.isnan(c[a]):
            continue
        with np.errstate(all="ignore"):
            lo, hi = np.nanmin(l[a:b + 1]), np.nanmax(h[a:b + 1])
        if np.isnan(lo):
            continue
        for off in offsets:
            n0 = int(np.floor((lo - off) / step)); n1 = int(np.ceil((hi - off) / step))
            for n in range(n0, n1 + 1):
                L = n * step + off
                start = c[a]
                if np.isnan(start) or abs(start - L) < 2:
                    continue
                side = 1 if start < L else -1               # approach direction
                jt = None
                for j in range(a + 1, b + 1):
                    if np.isnan(h[j]):
                        continue
                    if (side > 0 and h[j] >= L) or (side < 0 and l[j] <= L):
                        jt = j; break
                if jt is None:
                    continue
                end = min(jt + horizon, g.last_j[d])
                ev = dict(day=d, off=off, side=side, j=jt)
                for X in x_pts:
                    res = np.nan
                    for j in range(jt + 1, end + 1):
                        if np.isnan(h[j]):
                            continue
                        up = (h[j] >= L + X) if side > 0 else (l[j] <= L - X)
                        dn = (l[j] <= L - X) if side > 0 else (h[j] >= L + X)
                        if up and dn:
                            res = np.nan; break
                        if dn:
                            res = 1; break
                        if up:
                            res = 0; break
                    ev[f"rev_{X}"] = res
                cc = c[end] if not np.isnan(c[end]) else np.nan
                ev["fwd"] = (cc - L) * side
                # crossing by cross_pts on a close, then continuation
                jc = None
                for j in range(jt, end + 1):
                    if not np.isnan(c[j]) and (c[j] - L) * side >= cross_pts:
                        jc = j; break
                ev["cross"] = 0 if jc is None else 1
                for X in x_pts:
                    res = np.nan
                    if jc is not None:
                        ref = c[jc]
                        for j in range(jc + 1, min(jc + horizon, g.last_j[d]) + 1):
                            if np.isnan(h[j]):
                                continue
                            up = (h[j] >= ref + X) if side > 0 else (l[j] <= ref - X)
                            back = (l[j] <= L) if side > 0 else (h[j] >= L)
                            if up and back:
                                break
                            if back:
                                res = 0; break
                            if up:
                                res = 1; break
                    ev[f"cont_{X}"] = res
                out.append(ev)
    return pd.DataFrame(out)


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    from grid24 import Grid24
    from portfolio import load_mc
    from multi_strategy24 import VB_REPORT
    g = Grid24()
    pd.set_option("display.width", 250)
    vb = load_mc(g, VB_REPORT)
    vb["net"] = vb["net"] - SLIP * PV * (1 + (vb["kind"] != 1))
    rows = {"Vault Break (MultiCharts list)": summary(vb)}
    for name, kw in {"Beat the Market: long + short, trailing exit": {},
                     "long only, trailing exit": dict(long_only=True),
                     "long only, trailing exit + 75 pt stop": dict(long_only=True, stop_pts=75),
                     "long only, Vault Break exits (40/75)": dict(long_only=True, trail=False, stop_pts=75, tp_pts=40)
                     }.items():
        rows[name] = summary(noise_momentum(g, **kw))
    print("1. Noise momentum, per NQ after costs and 1 tick slippage"); print(pd.DataFrame(rows).T.to_string())
    hv = high_vol_regime(g)
    rows = {}
    for look, k in ((30, 2.0), (30, 3.0), (60, 2.0)):
        for reg, r in (("all days", None), ("high-vol days", hv)):
            rows[f"{look}-min move > {k}x normal, {reg}"] = summary(vol_fade(g, look=look, k=k, regime=r))
    print("\n2. Fading large moves"); print(pd.DataFrame(rows).T.to_string())
    ev = level_events(g)
    ev["kind"] = ev.off.map({0: "100s", 50: "50s", 25: "placebo", 75: "placebo", 37: "placebo",
                             63: "placebo", 12: "placebo", 88: "placebo"})
    print("\n3. First touches of price levels: share reversing 10 / 20 pts first; continuation after a 5-pt close through")
    print(ev.groupby("kind").agg(events=("fwd", "size"), rev10=("rev_10", "mean"), rev20=("rev_20", "mean"),
                                 fwd30_pts=("fwd", "mean"), cont10=("cont_10", "mean"),
                                 cont20=("cont_20", "mean")).round(3).to_string())
