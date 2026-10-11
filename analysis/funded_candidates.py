"""Candidate funded strategies (see funded_strategies/README.md), on the 24-hour
1-minute grid of any instrument (grid24.Grid24 with that instrument's files).

  vwap_ema_pullback()  Bhatti (2026, SSRN 6650958), written for gold: 200-EMA
                       regime, pullback to the 50 EMA with a rejection candle,
                       above/below the New York VWAP, stop 0.5 ATR beyond the
                       signal bar, target 3R, close-only 50-EMA trailing stop
                       (20 EMA past 2.5R). 15-minute bars.

Trade lists have the columns portfolio.paths() needs, P&L per 1 contract of
`point_value` dollars per point (NQ 20, ES 50, GC 100, CL 1000).
"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
from grid24 import jof
from candidates24 import _early


def _ema(x, n):
    out = np.full(len(x), np.nan)
    a = 2 / (n + 1)
    m = np.nan
    for i, v in enumerate(x):
        if np.isnan(v):
            out[i] = m
            continue
        m = v if np.isnan(m) else a * v + (1 - a) * m
        out[i] = m
    return out


def _atr(h, l, c, n):
    pc = np.r_[np.nan, c[:-1]]
    tr = np.nanmax(np.c_[h - l, np.abs(h - pc), np.abs(l - pc)], axis=1)
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def vwap_ema_pullback(g, bar=15, sess_start=830, sess_end=1500, last_entry=1430, rr=3.0,
                      atr_n=14, stop_atr=0.5, vol_mult=1.1, range_mult=0.8, band=0.001,
                      tighten_r=2.5, point_value=20.0, cost=7.25, long_only=False):
    """Bhatti's rules on `bar`-minute bars of the 24-hour grid. VWAP from
    sess_start (8:30 CT = 13:30 UTC); entries only in the VWAP session; flat at
    sess_end. The paper's VWAP partial-exit protocol is left out (it needs
    discretionary 'approach' labels); everything else follows sections 3-4."""
    b = g.bars(bar)
    D, K = b["c"].shape
    flat = {k: b[k].ravel() for k in ("o", "h", "l", "c", "v")}
    ok = ~np.isnan(flat["c"])
    idx = np.nonzero(ok)[0]
    o, h, l, c, v = (flat[k][idx] for k in ("o", "h", "l", "c", "v"))
    e200, e50, e20 = _ema(c, 200), _ema(c, 50), _ema(c, 20)
    atr = _atr(h, l, c, atr_n)
    vma = pd.Series(v).rolling(20).mean().to_numpy()
    day = idx // K
    t = (b["j"][idx % K] // 60) * 100 + b["j"][idx % K] % 60
    in_sess = (t > sess_start) & (t <= sess_end)
    # session VWAP
    tp = (h + l + c) / 3
    key = np.where(in_sess, day, -1)
    pv = pd.Series(np.where(in_sess, tp * v, 0)).groupby(key).cumsum().to_numpy()
    vv = pd.Series(np.where(in_sess, v, 0)).groupby(key).cumsum().to_numpy()
    with np.errstate(all="ignore"):
        vw = np.where(in_sess, pv / vv, np.nan)
    early = _early(g)
    body = np.abs(c - o)
    lo_wick = np.minimum(o, c) - l
    up_wick = h - np.maximum(o, c)
    pc, po = np.r_[np.nan, c[:-1]], np.r_[np.nan, o[:-1]]
    pl, ph = np.r_[np.nan, l[:-1]], np.r_[np.nan, h[:-1]]
    rows = []
    i = 1
    n = len(c)
    trading = set(g.trading.tolist())
    while i < n - 1:
        d = day[i]
        if d not in trading or not in_sess[i] or t[i] >= (1100 if early[d] else last_entry) \
                or np.isnan(e200[i]) or np.isnan(vma[i]) or np.isnan(atr[i]):
            i += 1
            continue
        common = v[i] > vol_mult * vma[i] and (h[i] - l[i]) >= range_mult * atr[i]
        long_ok = (c[i] > e200[i] * (1 + band) and c[i] > vw[i] and min(l[i], pl[i]) <= e50[i] <= c[i]
                   and ((lo_wick[i] >= 2 * body[i] and up_wick[i] <= 0.5 * lo_wick[i])
                        or (c[i] > o[i] and pc[i] < po[i] and c[i] > po[i] and o[i] < pc[i])))
        short_ok = (not long_only and c[i] < e200[i] * (1 - band) and c[i] < vw[i]
                    and max(h[i], ph[i]) >= e50[i] >= c[i]
                    and ((up_wick[i] >= 2 * body[i] and lo_wick[i] <= 0.5 * up_wick[i])
                         or (c[i] < o[i] and pc[i] > po[i] and c[i] < po[i] and o[i] > pc[i])))
        side = 1 if (common and long_ok) else (-1 if (common and short_ok) else 0)
        if side == 0 or day[i + 1] != d:
            i += 1
            continue
        entry = o[i + 1]
        stop = l[i] - stop_atr * atr[i] if side > 0 else h[i] + stop_atr * atr[i]
        risk = (entry - stop) * side
        if risk <= 0:
            i += 1
            continue
        target = entry + side * rr * risk
        end_t = 1130 if early[d] else sess_end
        k = i + 1
        exit_px = None; kind = 2; slips = 2
        while k < n and day[k] == d:
            # stop / target inside bar k (stop first if both)
            if (side > 0 and l[k] <= stop) or (side < 0 and h[k] >= stop):
                exit_px = min(o[k], stop) if side > 0 else max(o[k], stop); kind = 0; break
            if (side > 0 and h[k] >= target) or (side < 0 and l[k] <= target):
                exit_px = target; kind = 1; slips = 1; break
            if t[k] >= end_t:
                exit_px = c[k]; break
            trail = e20[k] if (c[k] - entry) * side >= tighten_r * risk else e50[k]
            if (side > 0 and c[k] < trail) or (side < 0 and c[k] > trail):
                if k + 1 < n and day[k + 1] == d:
                    k += 1; exit_px = o[k]
                else:
                    exit_px = c[k]
                break
            k += 1
        if exit_px is None:
            k = min(k, n - 1); exit_px = c[k]
        # 1-minute columns for paths(): first minute of the entry bar, last minute of the exit bar
        j0 = int(b["j"][idx[i + 1] % K]) - bar + 1
        j1 = int(b["j"][idx[k] % K])
        rows.append((d, max(j0, 0), j1, side, entry, exit_px, kind, slips))
        i = k + 1
    tdf = pd.DataFrame(rows, columns=["day", "j0", "j1", "side", "entry", "exit", "kind", "slips"])
    tdf["pnl"] = (tdf["exit"] - tdf["entry"]) * tdf["side"] * point_value
    tdf["net"] = tdf["pnl"] - cost - tdf["slips"] * 0.25 * point_value
    tdf["date"] = g.ts[tdf["day"].to_numpy()]
    return tdf
