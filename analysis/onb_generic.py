"""Market-agnostic Overnight Bias (2026-11-13; checks/candidates/jump_onb_other_markets/PREREG.md part B): candidates24.overnight_bias24
with the session, point value, tick, commission and target fill-through as inputs. Net = after commission + 1 tick on the stop-order
entry + 1 tick on a stop / time exit (as funded_lab.with_slippage).
  run(g, mk, t0, last_entry, flat, ...) -> trades
"""
import sys; sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid import _walk
from grid24 import jof
from candidates24 import _continuous_adx, _early, _hhmm


def run(g, mk, t0=830, last_entry=1400, flat=1430, on_start=2300, frac=1 / 3, adx_n=14, adx_min=30, atr_n=15, stop_atr=0.25, rr=3.0,
        early_last=1100, early_flat=1130, through=None, rng=None):
    pv, tick, comm = mk["pv"], mk["tick"], mk["comm"]; through = tick if through is None else through
    b = g.bars(15); A = _continuous_adx(b, adx_n); atr = g.daily_atr(atr_n); early = _early(g); J = b["j"]
    or_end = (t0 // 100 * 60 + t0 % 100 + 15); or_end = or_end // 60 * 100 + or_end % 60
    i_on_end, i_or, i_on_start = J.searchsorted(jof(t0)), J.searchsorted(jof(or_end)), J.searchsorted(jof(on_start)); out = []
    for d in g.trading:
        if d == 0 or np.isnan(atr[d]): continue
        with np.errstate(all="ignore"):
            onh = np.nanmax(np.r_[b["h"][d - 1, i_on_start + 1:], b["h"][d, :i_on_end + 1]]); onl = np.nanmin(np.r_[b["l"][d - 1, i_on_start + 1:], b["l"][d, :i_on_end + 1]])
        op = b["o"][d, i_or]
        if np.isnan(onh) or np.isnan(op) or onh <= onl or np.isnan(b["c"][d, i_or]): continue
        pos = (op - onl) / (onh - onl); side = 1 if pos >= 1 - frac else (-1 if pos <= frac else 0)
        if side == 0: continue
        if rng is not None: side = int(rng.choice([-1, 1]))
        level = b["h"][d, i_or] if side > 0 else b["l"][d, i_or]
        le = min(early_last, last_entry) if early[d] else last_entry; fl = jof(min(early_flat, flat) if early[d] else flat); sp = stop_atr * atr[d]
        for i in range(i_or, len(J) - 1):
            if _hhmm(J[i]) >= le: break
            if not (A[d, i] > adx_min): continue
            fill = None
            for j in range(J[i] + 1, min(J[i + 1], fl) + 1):
                o, h, l = g.o[d, j], g.h[d, j], g.l[d, j]
                if np.isnan(o): continue
                if side > 0 and h >= level: fill = (j, max(o, level)); break
                if side < 0 and l <= level: fill = (j, min(o, level)); break
            if fill is None: continue
            j0, px0 = fill
            j1, px, kind, worst = _walk(g.o[d], g.h[d], g.l[d], g.c[d], j0, fl, side, px0 - side * sp, px0 + side * rr * sp, through)
            gross = (px - px0) * side * pv
            out.append((g.ts[d], d, j0, j1, side, px0, px, kind, gross, gross - comm - tick * pv * (1 + (kind != 1)), sp)); break
    t = pd.DataFrame(out, columns=["date", "day", "j0", "j1", "side", "entry", "exit", "kind", "gross", "net", "stop_pts"])
    t["date"] = pd.to_datetime(t.date); return t
