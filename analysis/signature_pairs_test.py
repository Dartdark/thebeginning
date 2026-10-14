"""Signature pairs trading (Guo, Jin, Kuang, Qian & Wang 2025, arXiv 2505.05332) on NQ/ES, ES/YM, NQ/YM and GC/6E, 1-minute bars.

Paper: z-score pairs trading (60-min window, in at |z| >= 2, out at z = 0) filtered by (1) the 'segmented signature' C (sum of
|Levy area| between chord crossings of the 2-D log-price path over the window) below its historical mean, and (2) the
'covariation of increments' D = 0.5 x dX1 x dX2 over the window > 0. Data Nov-Dec 2024 only; hedge ratio fitted on the whole
sample (look-ahead); 0.05% of notional a round trip. GC/SI Sharpe 0.30 -> 2.91 with both filters; GC/PA, SI/PA lose unfiltered.
Here: 2018-2026, 8:30-15:00 CT (window from 8:30, signals 9:30-14:50, flat 15:00); hedge ratio beta = cov / var of 1-minute log
returns over the previous 5 sessions (no look-ahead); leg 1 = 1 contract, leg 2 = beta x leg-1 notional (fractional contracts,
research only); entry at the close of the minute AFTER the signal (also same-minute for reference); costs $7.25 + 1 tick a
contract a fill on both legs (ES $5 + 1 tick).  C threshold = expanding mean of past C values (no look-ahead).
Result (2026-10-14): every pair and filter loses $41-59 net a trade, ~4-5 trades a day, 0/9 years; adding back both legs'
costs (leg 2 is ~1.4 contracts) leaves ~$0-5 gross a trade; the C / C+D filters change nothing.
  python3 analysis/signature_pairs_test.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from numpy.lib.stride_tricks import sliding_window_view as swv
from grid24 import jof
from co_oc_reversal_test import load, cost, SPEC, line

W, ZIN = 60, 2.0
J0, JS, JE, JF = jof(830), jof(930), jof(1450), jof(1500)


def closes(g):
    return pd.DataFrame(g.c[:, J0:JF + 1], index=pd.DatetimeIndex(g.ts)).ffill(axis=1)


def seg_area(p1, p2):
    """p1, p2: (n, W+1) windows of log prices. Returns Levy area A, segmented C, covariation D per window."""
    x = p1 - p1[:, :1]; y = p2 - p2[:, :1]
    a = 0.5 * (x[:, :-1] * y[:, 1:] - y[:, :-1] * x[:, 1:])            # shoelace steps from the start point
    A = a.sum(1)
    cx, cy = x[:, -1:], y[:, -1:]
    side = np.sign(x * cy - y * cx)                                     # side of the chord
    newseg = np.concatenate([np.zeros((len(x), 1), bool), (side[:, 1:] != side[:, :-1]) & (side[:, 1:] != 0)], 1)[:, 1:]
    segid = np.cumsum(newseg, 1)
    C = np.zeros(len(x))
    for r in range(len(x)):
        C[r] = np.abs(np.bincount(segid[r], weights=a[r])).sum()
    D = 0.5 * x[:, -1] * y[:, -1]
    return A, C, D


def run_pair(s1, s2):
    g1, g2 = load(s1), load(s2)
    c1, c2 = closes(g1), closes(g2)
    days = c1.index.intersection(c2.index)
    days = [d for d in days if d.dayofweek < 5 and d.year >= 2017]
    c1, c2 = c1.loc[days], c2.loc[days]
    ok = c1.notna().all(1) & c2.notna().all(1); c1, c2 = c1[ok], c2[ok]
    L1, L2 = np.log(c1.to_numpy()), np.log(c2.to_numpy())
    r1, r2 = np.diff(L1, axis=1), np.diff(L2, axis=1)
    pv1, pv2 = SPEC[s1][0], SPEC[s2][0]; k1, k2 = cost(s1), cost(s2)
    trades = {v: [] for v in ("none", "C", "C+D")}; same = []
    histC = []
    for i in range(5, len(c1)):
        x, y = r1[i - 5:i].ravel(), r2[i - 5:i].ravel()
        beta = np.cov(x, y)[0, 1] / np.var(y)
        S = L1[i] - beta * L2[i]
        Sw = swv(S, W + 1)                                               # window t-W..t, row t-W
        mu = Sw[:, :-1].mean(1); sd = Sw[:, :-1].std(1, ddof=1)
        Z = (Sw[:, -1] - mu) / sd                                        # Z at minute (row + W)
        _, Cv, Dv = seg_area(swv(L1[i], W + 1), swv(L2[i], W + 1))
        thr = np.mean(histC) if histC else np.inf
        histC.extend(Cv[::10].tolist())                                 # thresholds from earlier days only
        date = c1.index[i]
        for v in trades:
            pos = 0; m_in = None
            for k in range(len(Z)):
                m = k + W
                if m < JS - J0: continue
                if pos == 0 and m <= JE - J0 and m + 1 <= JF - J0 and abs(Z[k]) >= ZIN:
                    if v in ("C", "C+D") and not Cv[k] < thr: continue
                    if v == "C+D" and not Dv[k] > 0: continue
                    pos = -np.sign(Z[k]); m_in = m + 1                    # enter at the next minute's close
                    if v == "none": same.append((date, pos, m, None))
                elif pos != 0 and (np.sign(Z[k]) != np.sign(-pos) or m >= JF - J0):
                    m_out = min(m + 1, JF - J0)
                    e1, e2, x1, x2 = c1.iat[i, m_in], c2.iat[i, m_in], c1.iat[i, m_out], c2.iat[i, m_out]
                    q2 = beta * e1 * pv1 / (e2 * pv2)
                    pnl = pos * ((x1 - e1) * pv1 - q2 * (x2 - e2) * pv2) - (k1 + abs(q2) * k2)
                    trades[v].append((date, pnl))
                    if v == "none" and same and same[-1][3] is None:
                        d0, p0, ms, _ = same[-1]; ms_out = m
                        f1, f2, y1, y2 = c1.iat[i, ms], c2.iat[i, ms], c1.iat[i, ms_out], c2.iat[i, ms_out]
                        pn = p0 * ((y1 - f1) * pv1 - q2 * (y2 - f2) * pv2) - (k1 + abs(q2) * k2)
                        same[-1] = (d0, p0, ms, pn)
                    pos = 0
            if pos != 0:
                pass
    out = {v: pd.Series([p for _, p in t], index=pd.DatetimeIndex([d for d, _ in t])) for v, t in trades.items()}
    out["same-minute entry (ref)"] = pd.Series([s[3] for s in same if s[3] is not None],
                                               index=pd.DatetimeIndex([s[0] for s in same if s[3] is not None]))
    return out


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for s1, s2 in (("NQ", "ES"), ("ES", "YM"), ("NQ", "YM"), ("GC", "6E")):
        res = run_pair(s1, s2)
        print(f"\n{s1}/{s2} (leg 1 = 1 {s1}; costs ${cost(s1):.2f} + beta-scaled ${cost(s2):.2f})")
        for v, x in res.items():
            print(line(x, f"{v:>24}", 30), f"| trades/day {len(x) / max(1, x.index.normalize().nunique()):.1f}")
            d = x.groupby(x.index.normalize()).sum()
        x = res["C+D"]; dd = x.groupby(x.index.normalize()).sum()
