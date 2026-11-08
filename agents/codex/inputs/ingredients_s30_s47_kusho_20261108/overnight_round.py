"""Overnight / multi-day round for a future personal account (user, 2026-10-18). Pre-registered before looking; NOT Apex
(holds overnight). Our data: 1-minute continuous futures, NOT back-adjusted, 2018-2026.

A  Overnight long ES / NQ: buy the 15:00 CT close, sell the next session's 8:30 open. All nights, and after a down regular
   session (the old Overnight Drift's condition). Nights in the index roll weeks (days 8-17 of Mar / Jun / Sep / Dec) are
   left out (the data switches contract then). (SPY cross-check dropped: data/SPY_daily.csv has closes only.)
B  Turn of the month ES / NQ: buy the 15:00 close of the 2nd-to-last trading day, sell the 15:00 close of the 3rd trading
   day of the new month; no stop, and a 1.0 x ATR15 stop on 1-minute lows.
C  Time-series momentum (Moskowitz, Ooi & Pedersen 2012) on 6 markets (ES, NQ, ZN, CL, GC, 6E): signal = mean of the signs
   of the 1-, 3- and 12-month returns; size = signal x 4% / annualised 60-day volatility per market (about 10% for the
   portfolio); rebalanced at Friday's 15:00 close; cost 3 bp of notional per side of turnover (micros: commission + 1 tick).
   Returns are roll-adjusted: in each roll window, the single largest 1-minute jump at a contract-switch time (17:00-17:05,
   03:30-03:35, 05:20-05:30 CT) is removed (if a real gap was removed instead, that is noise, not bias).
   Carry is not tested: it needs the second contract month, which our data does not have.
Costs A / B per contract round trip: ES $10 + 2 ticks = $35, NQ $14.50 + 2 ticks = $24.50.
  python3 analysis/overnight_round.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import grid24
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MK = {"ES": ("ge", 50.0, 35.0), "NQ": ("g24", 20.0, 24.5), "ZN": ("zn", 1000.0, None), "CL": ("cl", 1000.0, None),
      "GC": ("gc", 100.0, None), "6E": ("e6", 125000.0, None)}
WIN = {"ES": ((3, 6, 9, 12), 3, 20), "NQ": ((3, 6, 9, 12), 3, 20), "6E": ((3, 6, 9, 12), 3, 20), "ZN": ((2, 5, 8, 11), 15, 31),
       "CL": (tuple(range(1, 13)), 10, 26), "GC": ((1, 3, 5, 7, 9, 11), 15, 31)}
SWITCH = [(1700, 1705), (330, 335), (520, 530)]


def load(sym):
    return pickle.load(open(SP + MK[sym][0] + ".pkl", "rb"))


def stats(x, dates, nm, unit="$"):
    x = pd.Series(np.asarray(x, float), index=pd.DatetimeIndex(dates)).dropna()
    if len(x) < 5: print(f"   {nm:<42} n={len(x)}"); return
    t = x.mean() / x.std() * np.sqrt(len(x)); yrs = x.groupby(x.index.year).sum(); gl = -x[x < 0].sum()
    a, h = x[x.index < "2023"], x[x.index >= "2023"]
    print(f"   {nm:<42} n={len(x):4d} {unit}{x.mean():7.1f} PF {x[x > 0].sum() / gl if gl else np.inf:4.2f} t {t:4.1f} "
          f"yrs+ {(yrs > 0).sum()}/{len(yrs)} | 18-22 {unit}{a.mean():.0f} 23+ {unit}{h.mean():.0f}")


def roll_minutes(g, sym):
    """Flat minute index of the presumed contract switch in each roll window."""
    c = g.c.ravel(); ok = np.flatnonzero(~np.isnan(c)); d = np.abs(np.diff(c[ok]) / c[ok][:-1]); j = ok[1:]
    mins = j % 1440; hhmm = (mins // 60) * 100 + mins % 60
    cand = np.zeros(len(j), bool)
    for a, b in SWITCH: cand |= (hhmm >= a) & (hhmm <= b)
    ts = pd.DatetimeIndex(g.ts[j // 1440]); months, d0, d1 = WIN[sym]
    inwin = np.isin(ts.month, months) & (ts.day >= d0) & (ts.day <= d1)
    base = np.median(d[cand & ~inwin])
    out = []
    s = pd.DataFrame(dict(d=d, j=j, ym=ts.year * 100 + ts.month))[cand & inwin]
    for _, grp in s.groupby("ym"):
        k = grp.d.idxmax()
        if grp.at[k, "d"] > 6 * base: out.append(int(grp.at[k, "j"]))
    return np.array(out)


def daily_returns(g, sym):
    """Roll-adjusted close-to-close returns at 15:00 CT on trading rows."""
    tr = g.trading; cf = pd.Series(g.c.ravel()).ffill().to_numpy(); m15 = tr * 1440 + jof(1500)
    px = cf[m15]; r = px[1:] / px[:-1] - 1
    R = roll_minutes(g, sym); c = g.c.ravel(); ok = np.flatnonzero(~np.isnan(c))
    for j in R:                                            # remove that one minute's jump from the day's return
        k = np.searchsorted(m15, j); p = ok[np.searchsorted(ok, j) - 1]
        if 1 <= k < len(m15): r[k - 1] -= (c[j] - c[p]) / px[k - 1]
    return pd.Series(r, index=pd.DatetimeIndex(g.ts[tr[1:]]).normalize()), len(R)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    print("\nA. Overnight long, 15:00 close -> next 8:30 open (per contract, after costs)")
    for sym in ("ES", "NQ"):
        g = load(sym); _, pv, cost = MK[sym]; tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= "2018-01-01"]
        cf = pd.Series(g.c.ravel()).ffill().to_numpy()
        c15 = cf[tr * 1440 + jof(1500)]; o830 = g.o[tr, jof(831)]; c830 = g.o[tr, jof(831)]
        dts = pd.DatetimeIndex(g.ts[tr])
        night = (o830[1:] - c15[:-1]) * pv - cost; down = (c15[:-1] - c830[:-1]) < 0
        d0 = dts[:-1]; gapdays = (dts[1:] - dts[:-1]).days
        rollwk = np.isin(d0.month, (3, 6, 9, 12)) & (d0.day >= 8) & (d0.day <= 17)
        ok = ~rollwk & ~np.isnan(night)
        print(f" {sym}  ({rollwk.sum()} roll-week nights left out)")
        stats(night[ok], d0[ok], "every night")
        stats(night[ok & down], d0[ok & down], "after a down 8:30-15:00 session")
        stats(night[ok & ~down], d0[ok & ~down], "after an up session")
        stats(night[ok & (gapdays > 1)], d0[ok & (gapdays > 1)], "  (weekend / holiday nights only)")
        stats((night + cost)[ok], d0[ok], "  (gross, before costs)")

    print("\nB. Turn of the month: 15:00 close of day -2 -> 15:00 close of day +3 (per contract, after costs)")
    for sym in ("ES", "NQ"):
        g = load(sym); _, pv, cost = MK[sym]; tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= "2018-01-01"]
        dts = pd.DatetimeIndex(g.ts[tr]); cf = pd.Series(g.c.ravel()).ffill().to_numpy(); atr = g.daily_atr(15)[tr]
        ym = dts.year * 100 + dts.month; pos = np.arange(len(tr)); res = {"no stop": [], "1 ATR stop": []}; ds = []
        for y in np.unique(ym)[:-1]:
            last = pos[ym == y][-1]; i0, i1 = last - 1, last + 3
            if i1 >= len(tr): continue
            e = cf[tr[i0] * 1440 + jof(1500)]; x = cf[tr[i1] * 1440 + jof(1500)]
            res["no stop"].append((x - e) * pv - cost)
            lo = np.nanmin(np.r_[g.l[tr[i0], jof(1501):], np.concatenate([g.l[tr[k]] for k in range(i0 + 1, i1)]), g.l[tr[i1], :jof(1500) + 1]])
            sp = e - atr[i0]
            res["1 ATR stop"].append(((sp - 0.25 * (sym == "ES") - 0.25 * (sym == "NQ")) - e) * pv - cost if lo <= sp else (x - e) * pv - cost)
            ds.append(dts[i0])
        for k, v in res.items(): stats(v, ds, f"{sym} {k}")

    print("\nC. Time-series momentum portfolio (ES NQ ZN CL GC 6E), weekly, 4% vol per market, 3 bp a side")
    R = {}
    for sym in MK:
        r, n = daily_returns(load(sym), sym); R[sym] = r; print(f"   {sym}: {n} roll jumps removed")
    R = pd.DataFrame(R).sort_index(); R = R[R.index >= "2018-01-01"].fillna(0.0)
    lp = np.log1p(R).cumsum()
    sig = sum(np.sign(lp - lp.shift(k)) for k in (21, 63, 252)) / 3
    vol = R.ewm(span=60).std() * np.sqrt(252)
    raw = sig * 0.04 / vol; fri = np.repeat((lp.index.dayofweek == 4)[:, None], raw.shape[1], 1)
    w = raw.where(fri).ffill().shift(1)        # set at Friday's close, held from Monday
    w = w[lp.index >= lp.index[252]]
    gross = (w * R.loc[w.index]).sum(axis=1); cost = w.diff().abs().sum(axis=1) * 3e-4; net = gross - cost
    for nm, x in (("portfolio, net", net), ("portfolio, gross", gross)):
        ann = x.mean() * 252; sd = x.std() * np.sqrt(252); eq = x.cumsum(); dd = (eq - eq.cummax()).min()
        yrs = x.groupby(x.index.year).sum()
        print(f"   {nm:<18} {x.index[0].date()}..{x.index[-1].date()}: return {ann:.1%}/yr, vol {sd:.1%}, Sharpe {ann / sd:.2f}, "
              f"max DD {dd:.1%}, t {x.mean() / x.std() * np.sqrt(len(x)):.1f}")
    print("   by year (net):", {y: f"{v:.1%}" for y, v in net.groupby(net.index.year).sum().items()})
    per = (w * R.loc[w.index])
    print("   per market Sharpe (gross):", {k: round(per[k].mean() / per[k].std() * np.sqrt(252), 2) for k in per})
    print(f"   average gross leverage (sum |weight|): {w.abs().sum(axis=1).mean():.2f}x")
    pickle.dump(dict(net=net, gross=gross, w=w, R=R), open(SP + "overnight_tsmom.pkl", "wb"))
