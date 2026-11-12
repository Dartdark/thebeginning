"""Minute P&L paths of NQ Jump Fade (apex_strategies/NQ_Jump_Fade.txt, MC-verified v2 / v3) per MNQ on the bench150 grid rows.
jf_paths(dts, D, vol_ratio=0.0) -> (W, R): (D, 1440) arrays, $ per MNQ incl. costs + $0.55 micro fee. vol_ratio 0 = the live setting
(MinVolRatio 0, live on #5 at 2 MNQ from 2026-11-13). Used by bench150.setup for the live evaluation base.
"""
import sys; sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import jump_lib as L, jump_study as S
EXTRA = 0.55


def jf_trades(vol_ratio=0.0):
    b = L.bars(); M = S.Mkt(); yr = b.ts.dt.year.to_numpy(); sgn = np.sign(b.r).fillna(0).to_numpy()
    mask = (yr >= 2018) & (b.J.abs().to_numpy() > 3) & np.isin(b.ts.dt.hour.to_numpy(), [7, 8, 9])
    if vol_ratio > 0: mask &= b.vz.to_numpy() >= vol_ratio
    return S.trades(b, M, mask, -sgn, "rng", 1.5, tp=0.3, hold=240), M


def jf_paths(dts, D, vol_ratio=0.0):
    T, M = jf_trades(vol_ratio); ix = np.searchsorted(M.ts, T.ts.to_numpy()); tpos = pd.Series(np.arange(len(dts)), index=dts)
    W = np.zeros((D, 1440)); R = np.zeros((D, 1440)); hi, lo = M.arr[1], M.arr[2]; fee = np.zeros(D)
    for t, e in zip(T.itertuples(), ix):
        day = pd.Timestamp(t.ts).normalize()
        if day not in tpos.index: continue
        r = tpos[day]; n = int(t.mins); mins = pd.DatetimeIndex(M.ts[e:e + n]); js = mins.hour * 60 + mins.minute
        if (mins.normalize() != day).any(): continue
        cost = t.gross - t.net; adv = ((lo[e:e + n] if t.side > 0 else hi[e:e + n]) - t.entry) * t.side * 20 - cost
        adv[-1] = t.net if t.why == "tgt" else min(adv[-1], t.net)
        W[r, js] += adv; W[r, js[-1] + 1:] += t.net; R[r, js[-1]:] += t.net; fee[r] += EXTRA
    return W / 10 - fee[:, None], R / 10 - fee[:, None]
