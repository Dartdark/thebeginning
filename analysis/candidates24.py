"""Strategies that need the overnight session, on the 24-hour grid (grid24.py).
Each follows the PowerLanguage version in multi_strategy/ line by line.

  vault_break24       NQ_Vault_Break.txt      (30-minute bars, midnight open and VWAP)
  vwap_pullback_adx24 NQ_VWAP_Pullback_ADX.txt (1-minute bars, midnight VWAP)
  overnight_bias24    NQ_Overnight_Bias.txt    (15-minute bars, 23:00-8:30 range,
                                                stop-order entries)
  overnight_drift24   NQ_Overnight_Drift.txt   (long midnight to 3:00 after a
                                                down regular session)
The first two and overnight_drift24 return signals for grid.execute(); overnight_bias24 executes
its own stop-order entries and returns trades.
"""
import numpy as np
import pandas as pd
from grid import execute, _walk, POINT_VALUE, COST, FILL_THROUGH
from grid24 import jof
from candidates import adx
from replica import is_early_close


def _hhmm(J):
    return (J // 60) * 100 + J % 60


def _early(g):
    return np.array([is_early_close(pd.Timestamp(t)) for t in g.ts])


def _continuous_adx(b, n):
    ok = ~np.isnan(b["c"])
    A = np.full(b["c"].shape, np.nan)
    A[ok] = adx(b["h"][ok], b["l"][ok], b["c"][ok], n)
    return A


def vault_break24(g, mult=0.30, atr_n=15, first=1000, last=1430, flat=1430,
                  tp_pts=40.0, sl_pts=75.0, max_trades=3, early_last=1100, early_flat=1130):
    b = g.bars(30)
    t = _hhmm(b["j"])
    atr = g.daily_atr(atr_n)
    has = ~np.isnan(b["c"])
    first_i = np.argmax(has, axis=1)
    sess_open = b["o"][np.arange(g.D), first_i]
    noise = sess_open + mult * atr
    vw = g.vwap_rows(b)
    early = _early(g)
    last_e = np.where(early, early_last, last)[:, None]
    flat_j = np.where(early, jof(early_flat), jof(flat))
    win = (t[None, :] >= first) & (t[None, :] < last_e)
    m = win & (b["c"] > noise[:, None]) & (b["c"] > vw) & has
    d, k = np.nonzero(m)
    s = pd.DataFrame(dict(day=d, dj=b["j"][k], side=1, stop=sl_pts, target=tp_pts, exit_j=flat_j[d]))
    return s, dict(max_trades=max_trades)


def vwap_pullback_adx24(g, or_start=830, or_end=900, adx_n=14, adx_min=20, tp_bars=5,
                        sl_bars=20, last_entry=1430, flat=1555, max_trades=1,
                        vwap_start=0, early_last=1100, early_flat=1145):
    vw = g.vwap_rows(None, jof(vwap_start) if vwap_start else 0)
    A = _continuous_adx(dict(h=g.h, l=g.l, c=g.c), adx_n)
    early = _early(g)
    a0, e0 = jof(or_start) + 1, jof(or_end)
    rows = []
    for d in g.trading:
        h, l, c = g.h[d], g.l[d], g.c[d]
        with np.errstate(all="ignore"):
            orh = np.nanmax(h[a0:e0 + 1])
        if np.isnan(orh):
            continue
        le = early_last if early[d] else last_entry
        fl = early_flat if early[d] else flat
        broke = pulled = False
        for j in range(e0 + 1, min(jof(le), g.last_j[d])):
            if np.isnan(c[j]) or np.isnan(vw[d, j]):
                continue
            if not broke:
                broke = c[j] > orh
                continue
            if l[j] <= vw[d, j]:
                pulled = True
            prev = A[d, j - 1] if j > 0 else np.nan
            if pulled and c[j] > vw[d, j] and A[d, j] > adx_min and A[d, j] <= prev:
                tp = np.nanmax(h[max(0, j - tp_bars + 1):j + 1])
                sl = np.nanmin(l[max(0, j - sl_bars + 1):j + 1])
                if tp > c[j] and sl < c[j]:
                    rows.append((d, j, 1, c[j] - sl, tp - c[j], jof(fl)))
                    if max_trades == 1:
                        break
    s = pd.DataFrame(rows, columns=["day", "dj", "side", "stop", "target", "exit_j"])
    return s, dict(max_trades=max_trades)


def overnight_bias24(g, on_start=2300, on_end=830, or_end=845, frac=1 / 3, adx_n=14,
                     adx_min=20, atr_n=15, stop_atr=0.30, rr=3.0, last_entry=1400,
                     flat=1430, early_last=1100, early_flat=1130):
    b = g.bars(15)
    A = _continuous_adx(b, adx_n)
    atr = g.daily_atr(atr_n)
    early = _early(g)
    J = b["j"]
    i_on_end, i_or = J.searchsorted(jof(on_end)), J.searchsorted(jof(or_end))
    i_on_start = J.searchsorted(jof(on_start))              # first bar AFTER 23:00 is i_on_start + 1
    out = []
    for d in g.trading:
        if d == 0 or np.isnan(atr[d]):
            continue
        # overnight range: bars closing after 23:00 on the previous date through 8:30
        prev_h = b["h"][d - 1, i_on_start + 1:]; prev_l = b["l"][d - 1, i_on_start + 1:]
        cur_h = b["h"][d, :i_on_end + 1]; cur_l = b["l"][d, :i_on_end + 1]
        with np.errstate(all="ignore"):
            onh = np.nanmax(np.r_[prev_h, cur_h]); onl = np.nanmin(np.r_[prev_l, cur_l])
        op = b["o"][d, i_or]                                  # open of the 8:30-8:45 bar
        if np.isnan(onh) or np.isnan(op) or onh <= onl or np.isnan(b["c"][d, i_or]):
            continue
        pos = (op - onl) / (onh - onl)
        side = 1 if pos >= 1 - frac else (-1 if pos <= frac else 0)
        if side == 0:
            continue
        orh, orl = b["h"][d, i_or], b["l"][d, i_or]
        level = orh if side > 0 else orl
        le = early_last if early[d] else last_entry
        fl = jof(early_flat if early[d] else flat)
        sp = stop_atr * atr[d]
        # stop order placed at each 15-minute close from 8:45 while ADX > adx_min,
        # working during the next 15-minute bar
        for i in range(i_or, len(J) - 1):
            if _hhmm(J[i]) >= le:
                break
            if not (A[d, i] > adx_min):
                continue
            j_from, j_to = J[i] + 1, min(J[i + 1], fl)
            fill = None
            for j in range(j_from, j_to + 1):
                o, h, l = g.o[d, j], g.h[d, j], g.l[d, j]
                if np.isnan(o):
                    continue
                if side > 0 and h >= level:
                    fill = (j, max(o, level)); break
                if side < 0 and l <= level:
                    fill = (j, min(o, level)); break
            if fill is None:
                continue
            j0, px0 = fill
            stop_px = px0 - side * sp; tgt_px = px0 + side * rr * sp
            j1, px, kind, worst = _walk(g.o[d], g.h[d], g.l[d], g.c[d], j0, fl, side,
                                        stop_px, tgt_px, FILL_THROUGH)
            pnl = (px - px0) * side * POINT_VALUE
            out.append((d, j0, j1, side, px0, px, kind, pnl, abs(worst - px0) * POINT_VALUE, 1.0))
            break
    t = pd.DataFrame(out, columns=["day", "j0", "j1", "side", "entry", "exit", "kind", "pnl", "mae", "qty"])
    t["date"] = g.ts[t["day"].to_numpy()]
    t["net"] = t["pnl"] - COST
    return t


def overnight_drift24(g, entry=0, exit=300, rth_start=830, rth_end=1500, stop_atr=0.30,
                      atr_n=15, down_only=True):
    """Long from midnight (open of the first bar after `entry`) to the close of
    the `exit` bar, on trading days whose previous regular session closed
    down (close of the last bar up to rth_end below the close of the
    rth_start bar). Stop stop_atr x the 15-day ATR, no target."""
    atr = g.daily_atr(atr_n)
    C = pd.DataFrame(g.c).ffill(axis=1).to_numpy()
    tr = g.trading
    rows = []
    for i in range(1, len(tr)):
        d, p = tr[i], tr[i - 1]
        if np.isnan(atr[d]):
            continue
        chg = C[p, jof(rth_end)] - C[p, jof(rth_start)]
        if down_only and not chg < 0:
            continue
        rows.append((d, jof(entry), 1, stop_atr * atr[d], np.inf, jof(exit)))
    s = pd.DataFrame(rows, columns=["day", "dj", "side", "stop", "target", "exit_j"])
    return s, dict(max_trades=1)
