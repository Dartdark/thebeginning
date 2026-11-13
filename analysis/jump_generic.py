"""Market-agnostic Jump Fade (2026-11-13; checks/candidates/jump_onb_other_markets/PREREG.md part A). Reuses analysis/jump_lib.py
(bars / score) and jump_study.Mkt with a per-market cache folder (scratch_data/jump_<SYM>/); trades() is jump_study.trades with the
tick, point value and commission as inputs (the NQ version rounds the stop to 0.25).
  use(sym) -> (b, M)        bars with J, and the 1-minute market frame
  trades(b, M, mask, side, mk, ...) -> trades (net after commission + 1 tick per market / stop fill)
"""
import sys, os, glob; sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import jump_lib as L, jump_study as S

MK = {"NQ": dict(pv=20.0, tick=0.25, comm=7.25), "ES": dict(pv=50.0, tick=0.25, comm=5.0), "YM": dict(pv=5.0, tick=1.0, comm=5.0),
      "GC": dict(pv=100.0, tick=0.1, comm=5.0), "CL": dict(pv=1000.0, tick=0.01, comm=5.0), "ZN": dict(pv=1000.0, tick=1 / 64, comm=5.0),
      "6E": dict(pv=125000.0, tick=0.00005, comm=5.0), "NG": dict(pv=10000.0, tick=0.001, comm=5.0)}
_ROOT_CACHE = L.CACHE


def use(sym):
    if sym == "NQ": L.CACHE = _ROOT_CACHE
    else:
        L.CACHE = os.path.join(_ROOT_CACHE, f"jump_{sym}"); os.makedirs(L.CACHE, exist_ok=True)
        p = os.path.join(L.CACHE, "jump_min.pkl")
        if not os.path.exists(p):
            fs = sorted(glob.glob(os.path.join(L.ROOT, "data", f"{sym}_1min_2*.csv")))
            d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
            ts = pd.to_datetime(d.date.astype(str), format="%Y%m%d") + pd.to_timedelta(d.time // 100 * 60 + d.time % 100, unit="m")
            d = d.assign(ts=ts).drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
            d["sess"] = (d.ts + pd.Timedelta(hours=7) - pd.Timedelta(minutes=1)).dt.normalize(); d.to_pickle(p)
    return L.bars(), S.Mkt()


def trades(b, M, mask, side, mk, k=1.5, tp=0.3, hold=240, min_ticks=8, rng=None):
    tick, pv, comm = mk["tick"], mk["pv"], mk["comm"]; tv = tick * pv
    R = (b.rng * k).to_numpy(); i1 = b.i1.to_numpy(); o = M.arr[0]; rows = []; busy = -1; sd = np.asarray(side)
    for q in np.flatnonzero(np.asarray(mask)):
        e = i1[q] + 1
        if e >= len(o) - 1 or e <= busy: continue
        if M.late[e] or M.ts[e] - M.ts[e - 1] > np.timedelta64(2, "m"): continue
        r = R[q]; s = int(sd[q])
        if rng is not None: s = int(rng.choice([-1, 1]))
        if not np.isfinite(r) or r < min_ticks * tick - 1e-12 or s == 0: continue
        r = round(r / tick) * tick; px = o[e]; iend = min(M.end[e], e + hold)
        if iend <= e: continue
        ex, why, ix = L.walk(M.arr, e, s, px - s * r, px + s * round(tp * r / tick) * tick, iend)
        gross = s * (ex - px) * pv
        rows.append((M.ts[e], s, r, px, ex, why, gross, gross - (comm + tv + (0 if why == "tgt" else tv)), ix - e + 1)); busy = ix
    return pd.DataFrame(rows, columns=["ts", "side", "R", "entry", "exit", "why", "gross", "net", "mins"])
