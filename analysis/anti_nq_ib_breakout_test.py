"""Antigravity's NQIBBreakout (antigravity/jesse strategies/NQIBBreakout, 2026-10-20): rebuild on our data, per NQ, our costs.
Rule (Jesse, 15-min 24h candles, CT): IB = high / low of the 4 candles opening 08:30-09:15; long when a candle opening
10:00-11:45 closes above the IB high and above the 200-candle SMA (24h candles); market at that close; stop 1.25 x / target
2.5 x ATR(14) (Wilder, 15-min), intrabar on 1-minute data (stop first if both in a minute); flat 15:50; one long a day.
Its report: in-sample 2018-22 t 3.27 after 4 iterations (window 10:00-11:45 picked in iteration 4; 9:30-13:00 gave t 1.96),
2023-26 t 1.39. Pre-registered here (2026-10-20): the as-coded rule, plus its iteration-2 window (9:30-13:00) as the
'neighbour' check, and a random-day placebo (same entry bar of the day, random days, 300 runs). $17.25 per NQ.
  python3 analysis/anti_nq_ib_breakout_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import anti_nq_breakout_atr_test as A

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def run(B, m, w0=1000, w1=1145, forced=None):
    C, E, tc, atr = B.C.to_numpy(), B.end.to_numpy(), B.t_close.to_numpy(), B.atr.to_numpy()
    H, L = B.H.to_numpy(), B.L.to_numpy(); sma = pd.Series(C).rolling(200).mean().to_numpy()
    day = (E // 1440); out = []
    start = int(np.searchsorted(B.date.to_numpy(), np.datetime64("2018-01-01")))
    i = start; n = len(B)
    while i < n:
        d = day[i]; j0 = i
        while i < n and day[i] == d: i += 1
        idx = np.arange(j0, i); t = tc[idx]
        ib = idx[(t >= 845) & (t <= 930)]
        if len(ib) < 4: continue
        hi = H[ib].max()
        cand = idx[(t >= w0 + 15) & (t <= w1 + 15)]
        if forced is not None: k = forced.get(d); ent = [k] if k is not None else []
        else: ent = [k for k in cand if C[k] > hi and C[k] > sma[k]][:1]
        if not ent: continue
        k = ent[0]; e = C[k]; sp = e - 1.25 * atr[k]; tp = e + 2.5 * atr[k]
        lo, end = E[k] + 1, d * 1440 + jof(1550)
        x = None
        for q in range(lo, end + 1):
            if m["l"][q] <= sp: x = min(sp, m["o"][q]) if not np.isnan(m["o"][q]) else sp; break
            if m["h"][q] >= tp: x = max(tp, m["o"][q]) if not np.isnan(m["o"][q]) else tp; break
        if x is None: x = pd.Series(m["c"][lo:end + 1]).ffill().iloc[-1]
        out.append((B.date.iloc[k], tc[k], (x - e) * 20 - 17.25, d))
    return pd.DataFrame(out, columns=["date", "t", "pnl", "day"])


def line(nm, t):
    ts = lambda v: v.mean() / v.std() * np.sqrt(len(v)); a, b = t[t.date < "2023"].pnl, t[t.date >= "2023"].pnl
    yr = t.groupby(t.date.dt.year).pnl.sum(); gp, gl = t.pnl[t.pnl > 0].sum(), -t.pnl[t.pnl < 0].sum()
    print(f"   {nm:<30} n {len(t)} ${t.pnl.mean():.0f} per NQ PF {gp / gl:.2f} t {ts(t.pnl):.2f} yrs+ {(yr > 0).sum()}/{len(yr)} | 18-22 ${a.mean():.0f} (t {ts(a):.2f}) 23+ ${b.mean():.0f} (t {ts(b):.2f})")
    print("      by year:", yr.round(0).to_dict()); return t


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); B, m = A.build(g); del g
    T = line("as coded (10:00-11:45)", run(B, m)); line("its iteration 2 window 9:30-13:00", run(B, m, 930, 1300))
    dd = T.drawdown = (T.pnl.cumsum() - T.pnl.cumsum().cummax()).min(); print(f"   max drawdown per NQ ${-dd:,.0f} (its report: $857)")
    rng = np.random.default_rng(2); B_day = (B.end.to_numpy() // 1440); tc = B.t_close.to_numpy()
    days = np.unique(B_day[B.date.to_numpy() >= np.datetime64("2018-01-01")]); real = T.pnl.mean(); hits = 0; means = []
    for _ in range(300):
        pick = rng.choice(days, len(T), replace=False); f = {}
        for d, tt in zip(pick, T.t):
            k = np.flatnonzero((B_day == d) & (tc == tt))
            if len(k): f[d] = k[0]
        p = run(B, m, forced=f); means.append(p.pnl.mean())
    means = np.array(means); print(f"   placebo (same entry time, random days, long): real ${real:.0f} vs ${means.mean():.0f}, p = {(np.sum(means >= real) + 1) / 301:.3f}")
