"""Jump-score library for the '5-min jump' strategy study (user upload 2026-11-11: pino1 screenshot + three CFM papers).

Papers: Joulin, Lefevre, Grunberg & Bouchaud 2008 (s-jumps: |r| > s x local mean |r|; most jumps are not news; volatility
relaxes slowly after them), Marcaccioli, Bouchaud & Benzaquen 2022 (jump score J = r / (sigma x f); endogenous jumps have a
precursor rise of volatility / trend, exogenous ones are abrupt), Bouchaud, Gefen, Potters & Wyart 2004 (impact of order flow
is transient: part of a move made by one-sided flow decays).

bars(tf=5)    -> 24h NQ bars from data/NQ_1min_*.csv + data/NQ_1min_ON_*.csv (close-stamped minutes, Central time), with:
  r        close - previous close (points)            rng   high - low
  sig      local volatility: sqrt(pi/2 x mean |r_i||r_i-1|) over the previous K bars (bipower, robust to jumps), no look-ahead
  f        intraday periodicity: trailing 60-session mean of |r|/sig for the same time-of-day slot (previous sessions only)
  J        r / (sig x f)   (Marcaccioli eq. 1)         s     |r| / mean |r| of the previous 24 bars (Joulin, 120 min)
  Sg, T, B EMA (kappa 0.12) of |J|, J, sign(J) over PREVIOUS bars, jump bars (|J| > 4) excluded (Marcaccioli III.B)
  clv      (close - low) / range                       vz    volume / trailing same-slot mean volume
minute()      -> the 1-minute frame used to walk trades (o, h, l, c arrays + timestamps)
"""
import glob, os, pickle
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "scratch_data")


def minute():
    p = os.path.join(CACHE, "jump_min.pkl")
    if os.path.exists(p): return pd.read_pickle(p)
    fs = sorted(glob.glob(os.path.join(ROOT, "data", "NQ_1min_2*.csv")) + glob.glob(os.path.join(ROOT, "data", "NQ_1min_ON_2*.csv")))
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    ts = pd.to_datetime(d.date.astype(str), format="%Y%m%d") + pd.to_timedelta(d.time // 100 * 60 + d.time % 100, unit="m")
    d = d.assign(ts=ts).drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    # session day: bars stamped after 17:00 belong to the next session
    d["sess"] = (d.ts + pd.Timedelta(hours=7) - pd.Timedelta(minutes=1)).dt.normalize()
    os.makedirs(CACHE, exist_ok=True); d.to_pickle(p); return d


def bars(tf=5, K=276, kappa=0.12, jthr=4.0):
    p = os.path.join(CACHE, f"jump_bars_{tf}_{K}.pkl")
    if os.path.exists(p): return pd.read_pickle(p)
    m = minute()
    end = m.ts.dt.ceil(f"{tf}min")
    g = m.groupby(end)
    b = pd.DataFrame({"o": g.open.first(), "h": g.high.max(), "l": g.low.min(), "c": g.close.last(), "v": g.volume.sum(),
                      "n": g.close.size(), "sess": g.sess.last(), "i1": g.apply(lambda x: x.index[-1])})
    b = b[b.n >= max(1, tf - 2)].copy(); b["ts"] = b.index; b = b.reset_index(drop=True)
    gap = b.ts.diff() > pd.Timedelta(minutes=tf * 2)                 # first bar after a break (17:00 reopen, halts, missing data)
    b["r"] = b.c.diff(); b.loc[gap, "r"] = np.nan
    b["rng"] = b.h - b.l
    a = b.r.abs()
    b["sig"] = np.sqrt(np.pi / 2 * (a * a.shift(1)).rolling(K, min_periods=K // 2).mean()).shift(1)
    slot = b.ts.dt.hour * 60 + b.ts.dt.minute; b["slot"] = slot
    x = a / b.sig
    b["f"] = x.groupby(slot).transform(lambda s: s.rolling(60, min_periods=20).mean().shift(1))
    b["f"] = b.f / b.f.rolling(K * 20, min_periods=K * 5).mean()      # scale so the average f is about 1
    b["J"] = b.r / (b.sig * b.f)
    b["s"] = a / a.rolling(24, min_periods=12).mean().shift(1)
    J = b.J.to_numpy(); Sg = np.full(len(b), np.nan); T = Sg.copy(); B = Sg.copy(); sg = 0.8; t = 0.0; bb = 0.0
    for i in range(len(b)):
        Sg[i], T[i], B[i] = sg, t, bb
        j = J[i]
        if np.isfinite(j) and abs(j) <= jthr:
            sg = kappa * abs(j) + (1 - kappa) * sg; t = kappa * j + (1 - kappa) * t; bb = kappa * np.sign(j) + (1 - kappa) * bb
    b["Sg"], b["T"], b["B"] = Sg, T, B
    b["clv"] = ((b.c - b.l) / b.rng.where(b.rng > 0)).fillna(0.5)
    b["vz"] = b.v / b.v.groupby(slot).transform(lambda s: s.rolling(20, min_periods=10).mean().shift(1))
    b["hhmm"] = b.ts.dt.hour * 100 + b.ts.dt.minute
    b.to_pickle(p); return b


def walk(m_arr, i0, side, stop, tgt, i_end, tick=0.25):
    """Walk 1-minute bars from index i0 (entry at that bar's open, market). Returns (exit price before slippage, reason, exit index).
    Stop checked before target inside a minute (conservative). Target is a limit: needs a trade THROUGH it? No: touch counts
    (MultiCharts default); the cost model charges no slippage on it."""
    o, h, l, c = m_arr
    for i in range(i0, i_end + 1):
        if side > 0:
            if l[i] <= stop: return min(stop, o[i]), "stop", i
            if h[i] >= tgt: return max(tgt, o[i]) if i > i0 else tgt, "tgt", i
        else:
            if h[i] >= stop: return max(stop, o[i]), "stop", i
            if l[i] <= tgt: return min(tgt, o[i]) if i > i0 else tgt, "tgt", i
    return c[i_end], "time", i_end
