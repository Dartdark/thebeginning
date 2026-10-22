"""Antigravity's NQRelWeaknessShort (antigravity/jesse strategies/NQRelWeaknessShort, 2026-10-20): rebuild on our data.
Rule as coded (Jesse, 15-min 24h candles, CT, candle times = OPEN times): IB low = low of the candles opening 08:30-09:15;
short when a candle opening 09:30-11:30 closes below the IB low AND (NQ % from the 08:30 open) - 1.25 x (ES % from its 08:30
open) <= -0.25% AND ES is below its 08:30 open; market at that close; stop 1.25 x / target 2.0 x ATR(14); at a candle close
>= 1 ATR in profit the stop moves to entry - 1 pt; flat at the close of the candle opening 15:00; one a day.
Its report quotes FIXED points (stop 45 / target 90 / breakeven at 35) and t 5.41 full, 4.12 on 2018-22 -- the code uses ATR.
Both are rebuilt here (pre-registered 2026-10-20): A = the code (ATR), B = the report's points; fills on 1-minute data,
stop first when stop and target share a minute; $17.25 per NQ. Compared with its trades.csv (367 trades). Random-day
placebo: same entry time of day, random days, short, same exits (300 runs).
  python3 analysis/anti_nq_rel_weakness_short_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import anti_nq_breakout_atr_test as A

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def run(B, m, esc, eso, mode="atr", forced=None):
    C, E, tc, atr, L = B.C.to_numpy(), B.end.to_numpy(), B.t_close.to_numpy(), B.atr.to_numpy(), B.L.to_numpy()
    day = E // 1440; out = []; n = len(B); i = int(np.searchsorted(B.date.to_numpy(), np.datetime64("2018-01-01")))
    while i < n:
        d = day[i]; j0 = i
        while i < n and day[i] == d: i += 1
        idx = np.arange(j0, i); t = tc[idx]; ib = idx[(t >= 845) & (t <= 930)]
        if len(ib) < 4: continue
        o830 = m["o"][d * 1440 + jof(831)]; e830 = eso[d * 1440 + jof(831)]
        if not (o830 > 0 and e830 > 0): continue
        lo = L[ib].min(); k = None
        if forced is not None: k = forced.get(d)
        else:
            for q in idx[(t >= 945) & (t <= 1145)]:
                ec = esc[E[q]]; sp = (C[q] - o830) / o830 - 1.25 * (ec - e830) / e830
                if C[q] < lo and sp <= -0.0025 and ec < e830: k = q; break
        if k is None: continue
        e = C[k]; a = atr[k]
        if mode == "atr": st, tg, be = e + 1.25 * a, e - 2.0 * a, a
        else: st, tg, be = e + 45, e - 90, 35
        x = None; kind = "flat"; on = False; q = k + 1
        while q < i and x is None:
            for mm in range(E[q - 1] + 1, E[q] + 1):
                if m["h"][mm] >= st: x = max(st, m["o"][mm]) if not np.isnan(m["o"][mm]) else st; kind = "stop"; break
                if m["l"][mm] <= tg: x = min(tg, m["o"][mm]) if not np.isnan(m["o"][mm]) else tg; kind = "target"; break
            if x is None:
                if tc[q] >= 1515: x = C[q]; break
                if not on and e - C[q] >= be: st = e - 1.0; on = True
            q += 1
        if x is None: x = C[min(q, n - 1)]
        out.append((B.date.iloc[k], tc[k], (e - x) * 20 - 17.25, kind, d))
    return pd.DataFrame(out, columns=["date", "t", "pnl", "kind", "day"])


def line(nm, t):
    ts = lambda v: v.mean() / v.std() * np.sqrt(len(v)); a, b = t[t.date < "2023"].pnl, t[t.date >= "2023"].pnl
    yr = t.groupby(t.date.dt.year).pnl.sum(); gp, gl = t.pnl[t.pnl > 0].sum(), -t.pnl[t.pnl < 0].sum()
    dd = (t.pnl.cumsum() - t.pnl.cumsum().cummax()).min()
    print(f"   {nm:<26} n {len(t)} ${t.pnl.mean():.0f}/NQ PF {gp / gl:.2f} t {ts(t.pnl):.2f} win {(t.pnl > 0).mean():.0%} yrs+ {(yr > 0).sum()}/{len(yr)} | 18-22 ${a.mean():.0f} (t {ts(a):.2f}) 23+ ${b.mean():.0f} (t {ts(b):.2f}) | maxDD ${-dd:,.0f}/NQ")
    print("      by year:", yr.round(0).to_dict(), "| exits", t.kind.value_counts().to_dict())


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); B, m = A.build(g)
    es = pickle.load(open(SP + "ge.pkl", "rb"))
    # ES 1-minute close / open on the NQ grid's calendar (same calendar dates)
    off = int(np.searchsorted(es.dates, g.dates[0])); n = g.D * 1440
    esc = pd.Series(es.c[off:off + g.D].ravel()).ffill().to_numpy()[:n]; eso = es.o[off:off + g.D].ravel()[:n]
    assert es.dates[off] == g.dates[0]
    TA = run(B, m, esc, eso, "atr"); line("A code (ATR exits)", TA)
    TB = run(B, m, esc, eso, "pts"); line("B report (45 / 90 / 35 pts)", TB)
    th = pd.read_csv(SP + "anti/rws_trades.csv"); th["date"] = pd.to_datetime(th.date.astype(str))
    for nm, T in (("A", TA), ("B", TB)):
        mg = th.merge(T, on="date", how="outer", indicator=True)
        both = mg[mg._merge == "both"]
        print(f"   vs its trades.csv ({len(th)}): {nm} shares {len(both)} days; P&L corr {both.net_full_nq.corr(both.pnl):.2f}; its avg on shared ${both.net_full_nq.mean():.0f} vs ours ${both.pnl.mean():.0f}")
    print(f"   its trades.csv: n {len(th)} ${th.net_full_nq.mean():.0f}/NQ, win {(th.net_full_nq > 0).mean():.0%}, stop exits avg {th[th.kind == 'stop'].pts.mean():.1f} pts")
    rng = np.random.default_rng(4); Bd = B.end.to_numpy() // 1440; tc = B.t_close.to_numpy()
    days = np.unique(Bd[B.date.to_numpy() >= np.datetime64("2018-01-01")])
    for nm, T, md in (("A", TA, "atr"), ("B", TB, "pts")):
        means = []
        for _ in range(300):
            f = {}
            for d, tt in zip(rng.choice(days, len(T), replace=False), T.t):
                k = np.flatnonzero((Bd == d) & (tc == tt))
                if len(k): f[d] = k[0]
            means.append(run(B, m, esc, eso, md, forced=f).pnl.mean())
        means = np.array(means); print(f"   placebo {nm}: real ${T.pnl.mean():.0f} vs random-day shorts ${means.mean():.0f}, p = {(np.sum(means >= T.pnl.mean()) + 1) / 301:.3f}")
    TA.to_csv(SP + "rws_A.csv", index=False)
