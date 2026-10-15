"""Do Large Trades Predict Price? (The Institutional Protocol, Order Flow Research N-01, M. Conti 2026; user's PDF 2026-10-15).
Paper (NQ MBO 2017-05 .. 2026-07, MultiCharts + The Bridge, gross): follow the minute's largest print (>= 100 contracts, its
aggressor side), entry next 1-min open, fixed hold. 1-min hold $1.88 vs candle $0.41; hold 13-23 min plateau $15-25; RTH only;
prints in the candle's WICK $34 at 15 min, body $8; into a BALANCED book (|depth imbalance, top 50 levels| < 10%) +$6.47 at
1 min vs aligned -$4 / opposed -$11. Final configuration (whale >= 100, balanced book, RTH 9:30-16:00 ET, hold 15, no stop):
3,171 trades, $26.85 gross, PF 1.13, t ~2.0, $12.85 after $14 friction. Filters found in-sample (their disclosure).
Our earlier test of the Bridge's version at 1-5 min (TIER_LIST: F) found $2-8 gross vs $17.25 costs.
Here: the Bridge's OF_1min_*.csv (2018-01 .. 2026-07, RTH 8:30-15:15 CT): big_trade (signed size), big_trade_px, depth
s52 / s53 (bid / ask, 50 levels). Rules as the paper's code: signal on bar t, market at bar t+1's open, exit at the open
HoldBars bars after entry; same-direction signals while in a trade are ignored, an opposite signal reverses; entries on
bars closing 8:31-15:00 CT (= 9:31-16:00 ET), 1 NQ, $7.25 + 1 tick a side ($17.25 a round trip).
  A  the final configuration (pre-registered: the paper's exact numbers), gross and net, by year, longs / shorts, placebo
  B  the paper's other cells at hold 15: whale only, wick, body, aligned, opposed; and wick + balanced
  C  hold sweep 5..30 for the final configuration (information only)
  python3 analysis/whale_balanced_book_test.py [SCRATCH_DIR]
"""
import sys, glob, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25


def features(g):
    d = pd.concat([pd.read_csv(f, usecols=["date", "time", "big_trade", "big_trade_px", "s52", "s53"]) for f in sorted(glob.glob("OF_1min_*.csv"))],
                  ignore_index=True)
    row = np.minimum(np.searchsorted(g.dates, d.date.values), g.D - 1); ok = g.dates[row] == d.date.values
    d, row = d[ok], row[ok]; col = jof(d.time.values - 100)
    F = {}
    for k, c in (("big", "big_trade"), ("px", "big_trade_px"), ("bid", "s52"), ("ask", "s53")):
        a = np.full((g.D, 1440), np.nan); a[row, col] = d[c].to_numpy(float); F[k] = a
    return F


def signals(g, F, mode, min_size=100, thr=10.0):
    big, px = F["big"], F["px"]; o, c = g.o, g.c
    pdir = np.where(np.abs(big) >= min_size, np.sign(big), 0); pdir = np.nan_to_num(pdir)
    imb = (F["bid"] - F["ask"]) / (F["bid"] + F["ask"]) * 100
    liq = np.where(imb >= thr, 1, np.where(imb <= -thr, -1, 0))
    bhi, blo = np.maximum(o, c), np.minimum(o, c); inbody = (px >= blo) & (px <= bhi)
    m = {"whale": pdir != 0, "balanced": (pdir != 0) & (liq == 0) & ~np.isnan(imb), "aligned": (pdir != 0) & (pdir == liq),
         "opposed": (pdir != 0) & (liq != 0) & (pdir != liq), "wick": (pdir != 0) & (px > 0) & ~inbody,
         "body": (pdir != 0) & (px > 0) & inbody, "wick+balanced": (pdir != 0) & (liq == 0) & ~np.isnan(imb) & (px > 0) & ~inbody}[mode]
    return np.where(m, pdir, 0)


def run(g, S, hold=15, rand=None):
    rng = np.random.default_rng(rand) if rand is not None else None
    ts = pd.DatetimeIndex(g.ts); out = []; a, z = jof(831), jof(1500)
    for d in g.trading:
        if ts[d].year < 2018: continue
        s = S[d]
        if not s[a:z + 1].any(): continue
        o = pd.Series(g.o[d]).bfill().to_numpy()
        pos, e, ej = 0, 0.0, 0
        for j in range(a, z + hold + 2):
            if pos != 0 and j - ej >= hold:                               # exit at this bar's open
                out.append(dict(date=ts[d], side=pos, gross=(o[j] - e) * pos * PV)); pos = 0
            sig = s[j - 1] if a <= j - 1 <= z else 0                     # signal on bar j-1 acts at bar j's open
            if rng is not None and sig != 0: sig = rng.choice([-1, 1])
            if sig != 0 and sig != pos:
                if pos != 0: out.append(dict(date=ts[d], side=pos, gross=(o[j] - e) * pos * PV))
                pos, e, ej = int(sig), o[j], j
        if pos != 0: out.append(dict(date=ts[d], side=pos, gross=(o[min(j, 1439)] - e) * pos * PV))
    t = pd.DataFrame(out); t["net"] = t.gross - COMM - 2 * TICK * PV
    return t


def line(t, nm, col="net", w=34):
    x = t.set_index("date")[col]; y = x.index.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):5d} {col} ${x.mean():6.2f} PF {pf:4.2f} t {x.mean() / x.std() * np.sqrt(len(x)):+4.1f} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${x[y < 2023].mean():6.1f} 23-26 ${x[y >= 2023].mean():6.1f} | L ${x[t.side.to_numpy() > 0].mean():6.1f} S ${x[t.side.to_numpy() < 0].mean():6.1f}")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); F = features(g)
    print("\nA. Final configuration: whale >= 100 into a balanced book (|imb 50 levels| < 10%), RTH, hold 15")
    S = signals(g, F, "balanced"); t = run(g, S)
    print(line(t, "gross", "gross")); print(line(t, "net ($17.25 a round trip)"))
    print("   net by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    pl = [run(g, S, rand=r).net.mean() for r in range(10)]
    print(f"   placebo (same entry times, random side, 10 runs): net ${np.mean(pl):.1f} (range {min(pl):.1f}..{max(pl):.1f})")
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[(days.year >= 2018) & (days <= "2026-07-06")]
    dl = t.groupby("date").net.sum().reindex(days, fill_value=0.0)
    print(M.table({"all": (dl, t.net), "longs": (t[t.side > 0].groupby("date").net.sum().reindex(days, fill_value=0.0), t.net[t.side > 0]),
                   "shorts": (t[t.side < 0].groupby("date").net.sum().reindex(days, fill_value=0.0), t.net[t.side < 0])}))
    bt, pm = R.report({"2023+": dl[dl.index >= "2023-01-01"]}, n=3000); print(bt); print(pm)
    print("\nB. The paper's other cells, hold 15 (gross / net):")
    for mode in ("whale", "wick", "body", "aligned", "opposed", "wick+balanced"):
        tt = run(g, signals(g, F, mode)); print(line(tt, mode + " gross", "gross")); print(line(tt, mode + " net"))
    print("\nC. Final configuration, hold sweep (gross / net a trade):")
    for h in (5, 10, 13, 15, 19, 23, 30):
        tt = run(g, S, hold=h)
        print(f"   hold {h:2d}: n {len(tt)} gross ${tt.gross.mean():6.2f} net ${tt.net.mean():6.2f} t {tt.net.mean() / tt.net.std() * np.sqrt(len(tt)):+.1f}")
