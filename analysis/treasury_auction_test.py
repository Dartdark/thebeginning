"""Treasury auction price pressure (Fleming, Liu & Nguyen 2026, NY Fed SR 1188) on ZN, and its spillover to GC / 6E.

Paper: yields on on-the-run Treasuries rise in the 3 hours before a coupon auction closes (13:00 ET = 12:00 CT) and fall
in the 3 hours after the results; 10-year 1991-2024 total 1.19 bp (pre 0.44, post 0.75), 2015-24 only 0.59 bp.
Trades here, 1 contract, as in the paper's windows:
  pre   short ZN at the 9:00 CT close, cover at the 11:59 close (yields up = price down)
  post  long ZN at the 12:01 close (after the results), out at the 15:00 close; also from 12:10 (robustness)
  both  pre + post on the same day
Auction days: data/treasury_auctions.csv (fiscaldata.treasury.gov auctions_query, notes and bonds 2017-12 .. 2026-10),
nominal coupons (no TIPS / FRN) closing at 1:00 PM ET = 12:00 CT; reopenings grouped with their maturity (9-Year 11-Month
= 10-year). The first run (no calendar reachable) used the 12:00 CT ZN volume spike instead; kept as auction_days().
Placebo: the same windows on all other weekdays. Costs: ZN $1,000 a point, tick 1/64 ($15.625), $7.25 + 1 tick a fill =
$38.50 a round trip; GC $100 a point, $27.25; 6E $125,000, tick $6.25, $19.75.
  python3 analysis/treasury_auction_test.py [SCRATCH_DIR]
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24, jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPEC = {"ZN": (1000.0, 1 / 64), "GC": (100.0, 0.10), "6E": (125000.0, 0.00005)}


def cost(sym):
    pv, tick = SPEC[sym]; return 7.25 + 2 * tick * pv


def load(sym):
    os.makedirs(SP, exist_ok=True)
    pk = SP + f"{sym.lower()}.pkl"
    if os.path.exists(pk): return pickle.load(open(pk, "rb"))
    g = Grid24(f"data/{sym}_1min_20*.csv", night_pattern=""); pickle.dump(g, open(pk, "wb"), protocol=4); return g


def closes(g, hhmm):
    """Close of the bar ending at hhmm (last close at or before it), per trading row."""
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    r = g.trading
    return pd.Series(cf[r * 1440 + jof(hhmm)], index=pd.DatetimeIndex(g.ts[r]))


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def line(x, nm, w=46):
    x = pd.Series(x).dropna()
    if len(x) < 5: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.1f} PF {pf:4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${x[y < 2023].mean():6.1f} 23-26 ${x[y >= 2023].mean():6.1f}")


def auction_days(zn):
    r = zn.trading
    spike = np.nansum(zn.v[r, jof(1200):jof(1202) + 1], 1) / 3
    base = np.nanmedian(zn.v[r, jof(1130):jof(1159) + 1], 1)
    ratio = pd.Series(spike / base, index=pd.DatetimeIndex(zn.ts[r]))
    return ratio


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    zn = load("ZN")
    cal = pd.read_csv("data/treasury_auctions.csv")
    cal = cal[(cal.inflation_index_security == "No") & (cal.floating_rate == "No") & (cal.closing_time_comp == "01:00 PM")]
    yrs = cal.security_term.str.extract(r"^(\d+)-Year")[0].astype(int)
    cal["fam"] = yrs.map(lambda y: {9: 10, 19: 20, 29: 30}.get(y, y))
    cal["d"] = pd.to_datetime(cal.auction_date)
    fam = cal.groupby("d").fam.max()          # one per day (the longest maturity)
    print("\nCalendar: 1:00 PM ET nominal coupon auction days by maturity (longest per day):", fam.value_counts().sort_index().to_dict())
    ratio = auction_days(zn)
    ratio = ratio[(ratio.index >= "2018-01-01")].dropna()
    print("\nAuction-day detection: 12:00-12:02 CT volume / 11:30-11:59 median")
    print("   ratio quantiles:", " ".join(f"{q:.0%}:{ratio.quantile(q):.1f}" for q in (.5, .7, .75, .8, .85, .9, .95)))
    for th in (3, 4, 5, 6, 8):
        a = ratio[ratio >= th]; print(f"   ratio >= {th}: {len(a)} days, {len(a) / (len(ratio) / 252):.0f} a year")
    A = pd.DatetimeIndex(fam.index[fam.index >= "2018-01-01"])
    print(f"   volume ratio on calendar auction days: median {ratio.reindex(A).median():.1f}; on other days {ratio[~ratio.index.isin(A)].median():.1f}")
    print(f"   calendar days: weekday mix", pd.Series(A.dayofweek).value_counts().sort_index().to_dict(),
          "| day-of-month mix", np.histogram(A.day, bins=[1, 6, 16, 20, 32])[0].tolist(), "(1-5, 6-15, 16-19, 20-31)")

    for sym in ("ZN", "GC", "6E"):
        g = zn if sym == "ZN" else load(sym)
        pv, _ = SPEC[sym]; c = cost(sym)
        P = {h: closes(g, h) for h in (900, 1159, 1201, 1210, 1500)}
        idx = P[900].index; idx = idx[(idx >= "2018-01-01")]
        P = {h: s.reindex(idx) for h, s in P.items()}
        isA = pd.Series(idx.isin(A), index=idx)
        pre = -(P[1159] - P[900]) * pv; post = (P[1500] - P[1201]) * pv; post10 = (P[1500] - P[1210]) * pv
        print(f"\n{sym} ({idx[0].date()} .. {idx[-1].date()}), cost ${c:.2f} a round trip; gross first, then net")
        for nm, x in (("pre short 9:00-11:59", pre), ("post long 12:01-15:00", post), ("post long 12:10-15:00", post10),
                      ("both (gross sum of the two)", pre + post)):
            print(line(x[isA], f"auction  {nm} gross"))
            print(line(x[~isA], f"placebo  {nm} gross"))
        print(line(pre[isA] - c, "auction  pre short NET"))
        print(line(post[isA] - c, "auction  post long NET"))
        print(line(pre[isA] + post[isA] - 2 * c, "auction  both NET"))
        if sym == "ZN":
            F = fam.reindex(idx)
            for f in (2, 3, 5, 7, 10, 20, 30):
                m = F == f
                print(line(pre[m] + post[m], f"both gross, {f}-year auction days"))
            m = F.isin([10, 30])
            print(line(pre[m], "pre short gross, 10 + 30-year days")); print(line(post[m], "post long gross, 10 + 30-year days"))
            ZN_both = (pre + post)[isA]

    # standard metrics on the net ZN trade (whole, and each leg = 'longs' post / 'shorts' pre)
    print("\nZN net, 1 ZN per auction day (daily P&L over all weekdays):")
    zidx = closes(zn, 900).index; zidx = zidx[zidx >= "2018-01-01"]
    P = {h: closes(zn, h).reindex(zidx) for h in (900, 1159, 1201, 1500)}
    isA = pd.Series(zidx.isin(A), index=zidx); c = cost("ZN")
    pre = (-(P[1159] - P[900]) * 1000 - c).where(isA); post = ((P[1500] - P[1201]) * 1000 - c).where(isA)
    rows = {"both": ((pre.fillna(0) + post.fillna(0)), pd.concat([pre.dropna(), post.dropna()])),
            "shorts (pre)": (pre.fillna(0), pre.dropna()), "longs (post)": (post.fillna(0), post.dropna())}
    print(M.table(rows))
    h = {k: v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}
    b, p = R.report(h, n=2000)
    print("\n2023+ bootstrap:\n" + b + "\n\n2023+ drawdown permutation:\n" + p)
