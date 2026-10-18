"""ES 'Core 3' (user's weekend finds, 2026-10-18): independent Python rebuild on our 1-minute ES (CT clock), costs
$5 + 1 tick per stop / market fill ($30 a round trip per ES). From the user's MultiCharts files
(Crabel_NR7_ES.txt, Crabel_2BarNR_ES.txt) and text:
 1 NR7 stretch breakout: yesterday's 8:30-15:00 range <= min of the last 7; stretch = 10-session mean of min(H-O, O-L);
   OCO stops at open +/- 2 x stretch from 8:30 to 12:00 CT, stop at the opposite level, out 14:58 CT; 1 trade a day.
 2 2-bar NR: the last 2 sessions' combined range <= the min of the last 20 such 2-day ranges; same at 1 x stretch.
 3 Monday after an up Friday: Friday close (15:00) > Thursday close -> buy the Sunday 17:00 CT reopen, sell Monday 10:00 CT.
Checks: per-strategy stats, the same breakout on ALL days (the NR filter's value), correlation among the three and with
the funded plan, and the bootstrapped funded bench (current plan + 1 / 2 MES each).
Same-minute ambiguity (both stops touched in one minute): counted as a full loss (conservative).
  python3 analysis/es_core3_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 50.0, 0.25, 30.0


def breakout(g, d, up, dn, last=jof(1200), out=jof(1458)):
    H, L, O, C = g.h[d], g.l[d], g.o[d], g.c[d]
    side = 0
    for j in range(jof(831), last + 1):
        if np.isnan(H[j]): continue
        hu, hd = H[j] >= up, L[j] <= dn
        if hu and hd: return dict(side=1, entry=up, exit=dn, j0=j, j1=j)          # both in one minute: full loss
        if hu: side, e, sp, j0 = 1, max(up, O[j]), dn, j; break
        if hd: side, e, sp, j0 = -1, min(dn, O[j]), up, j; break
    if not side: return None
    for j in range(j0 + 1, out + 1):
        if np.isnan(H[j]): continue
        if (side > 0 and L[j] <= sp) or (side < 0 and H[j] >= sp):
            return dict(side=side, entry=e, exit=(min(sp, O[j]) if side > 0 else max(sp, O[j])), j0=j0, j1=j)
    cc = C[j0:out + 1]; ok = np.flatnonzero(~np.isnan(cc))
    return dict(side=side, entry=e, exit=cc[ok[-1]], j0=j0, j1=j0 + ok[-1])


def stats(t, nm):
    if len(t) < 5: print(f"   {nm:<40} n={len(t)}"); return
    n = t.net; yrs = n.groupby(t.date.dt.year).sum(); gl = -n[n < 0].sum(); tt = n.mean() / n.std() * np.sqrt(len(n))
    eq = n.cumsum(); dd = (eq - eq.cummax()).min(); a, h = n[t.date < "2023"], n[t.date >= "2023"]
    print(f"   {nm:<40} n={len(n):4d} ${n.mean():5.0f} PF {n[n > 0].sum() / gl:4.2f} t {tt:4.1f} yrs+ {(yrs > 0).sum()}/{len(yrs)} "
          f"net ${n.sum():,.0f} maxDD ${dd:,.0f} | 18-22 ${a.mean():.0f} 23+ ${h.mean():.0f}")


def build(g):
    tr = g.trading; J0, J1 = jof(831), jof(1500)
    O = g.o[tr, J0]; H = np.nanmax(g.h[tr, J0:J1 + 1], 1); L = np.nanmin(g.l[tr, J0:J1 + 1], 1)
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); C = cf[tr * 1440 + J1]
    D = pd.DataFrame(dict(row=tr, O=O, H=H, L=L, C=C), index=pd.DatetimeIndex(g.ts[tr]).normalize())
    D["R"] = D.H - D.L; D["S"] = np.minimum(D.H - D.O, D.O - D.L)
    D["stretch"] = D.S.rolling(10).mean().shift(1)                                 # known at today's open
    D["nr7"] = (D.R <= D.R.rolling(7).min()).shift(1).fillna(False)
    two = pd.concat([D.H, D.H.shift(1)], axis=1).max(axis=1) - pd.concat([D.L, D.L.shift(1)], axis=1).min(axis=1)
    D["nr2"] = (two <= two.rolling(20).min()).shift(1).fillna(False)
    return D


def run_breakouts(g, D, flag, k):
    rows = []
    for dt, r in D[(D.index >= "2018-01-01") & flag & D.stretch.notna()].iterrows():
        if g.last_j[r.row] < jof(1458): continue
        x = breakout(g, r.row, r.O + k * r.stretch, r.O - k * r.stretch)
        if x: rows.append(dict(date=dt, day=r.row, **x, net=(x["exit"] - x["entry"]) * x["side"] * PV - COST))
    return pd.DataFrame(rows)


def run_monday(g, D):
    rows = []; idx = list(D.index)
    for i in range(2, len(idx)):
        dt = idx[i]
        if dt.dayofweek != 0 or dt < pd.Timestamp("2018-01-01") or idx[i - 1].dayofweek != 4: continue
        if not D.C.iloc[i - 1] > D.C.iloc[i - 2]: continue
        sun = D.row.iloc[i] - 1
        o = g.o[sun, jof(1700):jof(1715)]; ok = np.flatnonzero(~np.isnan(o))
        if not len(ok): continue
        e = o[ok[0]]; x = pd.Series(g.c[D.row.iloc[i], :jof(1000) + 1]).ffill().iloc[-1]
        if np.isnan(x): continue
        rows.append(dict(date=dt, day=D.row.iloc[i], side=1, entry=e, exit=x, j0=0, j1=jof(1000), net=(x - e) * PV - COST))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    g = pickle.load(open(SP + "ge.pkl", "rb")); D = build(g)
    T1 = run_breakouts(g, D, D.nr7, 2.0); T2 = run_breakouts(g, D, D.nr2, 1.0); T3 = run_monday(g, D)
    print("Per 1 ES after $30 a round trip:")
    stats(T1, "1 NR7 stretch breakout (K 2)"); stats(T2, "2 2-bar NR breakout (K 1)"); stats(T3, "3 Monday after an up Friday")
    print("The same breakout on ALL days (is the NR filter the edge?):")
    stats(run_breakouts(g, D, D.index == D.index, 2.0), "   all days, K 2"); stats(run_breakouts(g, D, D.index == D.index, 1.0), "   all days, K 1")
    print("Neighbours: NR7 at K 1.5 / 2.5:")
    stats(run_breakouts(g, D, D.nr7, 1.5), "   K 1.5"); stats(run_breakouts(g, D, D.nr7, 2.5), "   K 2.5")
    print("Monday: Friday down (the other half):")
    T3x = run_monday(g, D.assign(C=-D.C)); stats(T3x, "   Monday after a DOWN Friday")
    daily = pd.DataFrame({k: t.groupby("date").net.sum() for k, t in (("NR7", T1), ("NR2", T2), ("MON", T3))}).fillna(0)
    comb = daily.sum(axis=1); idx = pd.bdate_range(comb.index.min(), comb.index.max()); c = comb.reindex(idx, fill_value=0) / 10
    eq = c.cumsum()
    print(f"\nCombined, 1 MES each (= ES / 10): ${c.sum() / ((idx[-1] - idx[0]).days / 365.25):,.0f} a year, max DD ${(eq - eq.cummax()).min():,.0f}, "
          f"Sharpe {c.mean() / c.std() * np.sqrt(252):.2f}; by year {c.groupby(c.index.year).sum().round(0).to_dict()}")
    print("   correlation of trade days (daily P&L):\n" + daily.corr().round(2).to_string())
    pickle.dump(dict(T1=T1, T2=T2, T3=T3), open(SP + "es_core3.pkl", "wb"))
