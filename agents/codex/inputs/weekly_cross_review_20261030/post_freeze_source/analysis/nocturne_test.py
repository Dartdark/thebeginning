"""Nocturne (L. Franceschetti research note, user upload 2026-10-30; checks/candidates/nocturne/): Blose-Gondhalekar-Kort
(2018) gold overnight effect moved to NQ. Rule as given: long at the 17:05 CT reopen, out 07:20 CT, only when the 5-minute
closes of the last two CME sessions fit a straight line with R^2 >= 0.3; 25-point profit target; one optional re-entry per
night after a target (at the next 5-minute bar); no stop. The author's split: development 2017 - 2022-10-25, OOS 1 to
2023-12-31, OOS 2 2024 - 2026-09 (he reports t 5.10 / 3.09 / 1.58, ~7.3 million configurations counted, 'fragile').
Variants fixed before running (user request 2026-10-30, 3 trials):
  N0  the rule as given (no stop)
  N1  N0 + a protective stop 0.5 x 15-day ATR below each entry (Apex needs a bounded night)
  N2  N0 without the R^2 filter (does the filter add anything over the plain overnight premium?)
Our conventions: 1-minute NQ grid (data/NQ_1min*), entry = open of the 17:06 bar (17:05 price), exit = open of the 07:21
bar; target fills only on a 1-point trade-through; $7.25 + 1 tick per market / stop fill; contract-switch nights dropped;
one night per session, booked on the exit day. Also: overlap with Overnight Tick / VIX (our plan's overnight long).
  python3 analysis/nocturne_test.py SCRATCH_DIR > analysis/outputs/nocturne_test_output.txt
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from overnight_round import roll_minutes
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM, TGT, THR = 20.0, 0.25, 7.25, 25.0, 1.0
PERIODS = [("dev 2017-22/10", "2017-01-01", "2022-10-25"), ("OOS1 22/10-23", "2022-10-26", "2023-12-31"), ("OOS2 2024-26", "2024-01-01", "2026-12-31")]


def r2(y):
    y = y[np.isfinite(y)]
    if len(y) < 50: return np.nan
    x = np.arange(len(y)); c = np.corrcoef(x, y)[0, 1]
    return c * c


def walk(o, h, l, a, b, ep, stop):
    """Long from the open of a to the open of b: first target (entry + 25, 1-pt through) or stop. Returns (exit_j, px, kind, low)."""
    low = ep
    for j in range(a, b):
        if not np.isfinite(o[j]): continue
        if stop is not None and j > a and o[j] <= stop: return j, o[j], 0, min(low, o[j])
        if stop is not None and l[j] <= stop: return j, stop, 0, min(low, stop)
        if h[j] >= ep + TGT + THR: return j, ep + TGT, 1, min(low, l[j])
        low = min(low, l[j])
    k = b
    while not np.isfinite(o[k]) and k > a: k -= 1
    return b, o[k], 2, low


def nights(g):
    tr = np.array(sorted(g.trading.tolist())); trs = set(tr.tolist()); atr = g.daily_atr(15)
    rolls = np.sort(roll_minutes(g, "NQ")); o, h, l, c = (getattr(g, k).ravel() for k in "ohlc"); out = []
    for r in range(2, g.D - 1):
        a, b = r * 1440 + jof(1706), (r + 1) * 1440 + jof(721)
        if not (np.isfinite(o[a]) and np.isfinite(o[b])) or (r + 1) not in trs: continue
        k = np.searchsorted(tr, r, side="right") - 1          # last trading session that ended at or before this evening
        if k < 1: continue
        rp, rp2 = tr[k], tr[k - 1]
        win = c[(rp2 - 1) * 1440 + jof(1701): rp * 1440 + jof(1600) + 1]
        q = r2(win[4::5])                                     # 5-minute closes
        roll = ((rolls > a) & (rolls <= b)).any(); i_atr = np.searchsorted(tr, rp)
        A = atr[i_atr] if i_atr < len(atr) else np.nan
        for var in ("N0", "N1", "N2"):
            if var != "N2" and not (q >= 0.3): continue
            stop_d = 0.5 * A if var == "N1" and np.isfinite(A) else None
            j, net, adv, n_tr, ep = a, 0.0, 0.0, 0, o[a]
            while n_tr < 2 and j < b:
                ep = o[j]; st = ep - stop_d if stop_d else None
                x, px, kind, low = walk(o, h, l, j, b, ep, st)
                slip = TICK * (1 + (kind != 1))
                adv = min(adv, net + (low - ep - slip) * PV - COMM)
                net += (px - ep - slip) * PV - COMM; n_tr += 1
                if kind != 1: break
                j = x + 1
                while j < b and (j % 5 != 1 or not np.isfinite(o[j])): j += 1   # next 5-minute bar's open
            out.append(dict(var=var, date=pd.Timestamp(g.ts[r + 1]), sess=pd.Timestamp(g.ts[rp]), r2=q, roll=roll,
                            trades=n_tr, net=net, adv=min(adv, net)))
    N = pd.DataFrame(out)
    N = N[~N.roll].drop_duplicates(["var", "sess"], keep="first")
    return N[N.date >= "2017-01-01"].reset_index(drop=True)


def line(x, nm):
    if len(x) < 3: return f"   {nm:<22} n {len(x)}"
    t = x.mean() / x.std() * np.sqrt(len(x)); pf = x[x > 0].sum() / -x[x < 0].sum()
    return f"   {nm:<22} nights {len(x):4d}  net ${x.sum():>9,.0f}  avg ${x.mean():6.1f}  t {t:5.2f}  PF {pf:4.2f}  win {(x > 0).mean():.0%}  worst ${x.min():,.0f}"


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); N = nights(g)
    os.makedirs("checks/candidates/nocturne", exist_ok=True); N.to_csv("checks/candidates/nocturne/python_nights.csv", index=False)
    days = pd.DatetimeIndex(g.ts[g.trading])
    for var in ("N0", "N1", "N2"):
        x = N[N["var"] == var].set_index("date")
        print(f"\n{var}: entries per night avg {x.trades.mean():.2f} (author: 2,021 trades over ~1,800 nights)")
        print(line(x.net, "2017-2026 all"))
        for nm, a, b in PERIODS: print(line(x.net[a:b], nm))
        print("   by year: " + "  ".join(f"{y} ${v / 1e3:,.1f}k" for y, v in x.net.groupby(x.index.year).sum().items()))
        print(f"   worst night ${x.net.min():,.0f} ({x.net.idxmin().date()}), worst open loss ${x.adv.min():,.0f}; nights below -$5,000: {(x.adv < -5000).sum()}")
        for lab, a, b in (("2018-26", "2018-01-01", "2026-12-31"), ("2023+", "2023-01-01", "2026-12-31")):
            d = x.net[a:b].reindex(days[(days >= a) & (days <= b)], fill_value=0.0)
            p = M.perf(d.values, x.net[a:b].values)
            print(f"   metrics {lab}: Sharpe {p['sharpe']:.2f}  Sortino {p['sortino']:.2f}  PF {p['profit_factor']:.2f}  Calmar {p['calmar']:.2f}  Ulcer {p['ulcer']:.2f}  maxDD ${p['max_dd']:,.0f}")
    # filter check: R^2 >= 0.3 nights vs the rest, same exits (N2 = all nights)
    a2 = N[N["var"] == "N2"].set_index("sess")
    print("\nR^2 filter (N2 nights split by the filter):")
    print(line(a2.net[a2.r2 >= 0.3], "R2 >= 0.3")); print(line(a2.net[~(a2.r2 >= 0.3)], "R2 < 0.3"))
    for nm, a, b in PERIODS:
        s = a2.loc[a:b]; print(f"   {nm}: filtered ${s.net[s.r2 >= 0.3].mean():.0f} vs rest ${s.net[~(s.r2 >= 0.3)].mean():.0f} a night")
    # overlap with Overnight Tick / VIX
    ot = pd.read_csv("checks/candidates/overnight_tick/python_trades.csv", parse_dates=["date"]).set_index("date")
    for var in ("N0", "N1"):
        x = N[N["var"] == var].set_index("date"); both = x.index.intersection(ot.index)
        j = pd.concat([x.net.rename("n"), ot.net.rename("o")], axis=1).fillna(0.0)
        j = j[(j.index >= ot.index.min()) & (j.index <= ot.index.max())]
        print(f"\nOverlap {var} vs Overnight Tick: {len(both)} shared nights of {len(x)} / {len(ot)}; daily P&L corr {j.n.corr(j.o):+.2f}")
