"""Our 1-minute grids -> Jesse candle arrays (2026-10-17, Jesse cross-check).

Jesse needs [timestamp_ms (bar OPEN), open, close, high, low, volume] for every minute: it builds 5 / 15 / 30-minute
bars by counting 1-minute candles, so a missing minute would shift every later bar. Missing minutes (closed market,
weekends, holidays) are filled with a flat volume-0 candle (see candles()); the strategies ignore volume-0 bars
where it matters (ADX, bar counts). Timestamps are the exchange clock written as if it were UTC (no daylight-saving
jumps): NQ in Central time; CL shifted to Eastern (+60 min), as on its MultiCharts chart.
  python3 analysis/jesse/build_candles.py [SCRATCH_DIR]   ->  SCRATCH_DIR/jesse_nq.npy, jesse_cl_et.npy
"""
import sys, pickle; sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def candles(g, shift_min=0, start="2017-11-01"):
    D, M = g.c.shape
    o, h, l, c, v = (getattr(g, k).ravel().copy() for k in ("o", "h", "l", "c", "v"))
    # column j of a date = the bar CLOSING at 00:00 + j min -> it opens at j - 1 min
    t0 = np.asarray(g.ts).astype("datetime64[ms]").astype(np.int64)
    ts = (t0[:, None] + (np.arange(M)[None, :] - 1 + shift_min) * 60000).ravel()
    cf = pd.Series(c).ffill().to_numpy()
    miss = np.isnan(c)
    # a missing minute takes the NEXT real open if a real minute follows it in the same (midnight-aligned) 5-minute block,
    # else the last close: every 5 / 15 / 30-minute bar then has the open / high / low / close of its real trades only
    # (with the last close everywhere, a bar whose first minute had no trade would open at the previous close: the CL
    # Sunday bar then showed no gap on 2019-09-15 and 2026-03-01)
    blk = ts // 300_000
    nxt = pd.Series(o).groupby(blk).bfill().to_numpy()
    fill = np.where(np.isnan(nxt), cf, nxt)
    o[miss] = fill[miss]; h[miss] = fill[miss]; l[miss] = fill[miss]; c[miss] = fill[miss]; v[miss] = 0.0
    v = np.nan_to_num(v)
    keep = ~np.isnan(cf) & (ts >= np.datetime64(start, "ms").astype(np.int64))
    first = np.argmax(keep & (ts % 86_400_000 == 0))           # start at a midnight so 5 / 15 / 30-minute bars align
    keep[:first] = False
    out = np.column_stack([ts, o, c, h, l, v])[keep]
    assert (np.diff(out[:, 0]) == 60000).all(), "candles must be continuous"
    return out


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    nq = candles(g); np.save(SP + "jesse_nq.npy", nq); print("NQ", nq.shape, pd.Timestamp(nq[0, 0], unit="ms"), pd.Timestamp(nq[-1, 0], unit="ms"))
    from cl_forced_flows_test import load
    cl = load("CL"); x = candles(cl, shift_min=60); np.save(SP + "jesse_cl_et.npy", x)
    print("CL (Eastern)", x.shape, pd.Timestamp(x[0, 0], unit="ms"), pd.Timestamp(x[-1, 0], unit="ms"))
