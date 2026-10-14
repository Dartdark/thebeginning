"""Option-income (covered-call) ETF roll flows on NQ (2026-10-14).

Idea (forced, scheduled flow): covered-call funds sell Nasdaq-100 calls on a fixed schedule. QYLD follows the Cboe
NASDAQ-100 BuyWrite index (BXN): the expiring 1-month at-the-money NDX call settles at the 3rd-Friday open and the new
call is sold at the VWAP of 11:30-12:00 ET = 10:30-11:00 CT that day (XYLD does the same on SPX via BXM). The dealers
who buy those calls get long delta (they hedge by SELLING futures in the window) and long gamma (which damps moves
and pins price near the strike afterwards). JEPQ (May 2022 on) and the QQQI / QDTE wave (2024 on) write weekly / daily
OTM calls with no published minute, so the weekly test is coarser (every Friday, 2022+ vs before).
Measures, NQ 2018-2026, $ per NQ before costs unless a trade:
  A. 3rd-Friday sell window 10:30 -> 11:00 CT (and before / after it) vs other Fridays and other days; by year;
     pre-2022 vs 2022+. ES as a check (BXM / XYLD sell in the same window).
  B. Volatility after the roll: RTH range / ATR on the 1..5 trading days after the 3rd Friday vs the same day count
     after other Fridays.
  C. Pin: |close - roll price (11:00 CT on the 3rd Friday)| / ATR over the next 1..10 days vs the same from other
     Fridays' 11:00 price; and a fade of the 8:30 gap away from the roll price.
  D. Roll-week drift (week after the 3rd Friday vs other weeks).
  E. Weekly (JEPQ era): every Friday's 10:30 -> 11:00 and 14:00 -> 15:00, 2018-21 vs 2022+ vs 2024+.
  python3 analysis/option_income_etf_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV = {"NQ": 20.0, "ES": 50.0}


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def tdiff(a, b):
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b)) if min(len(a), len(b)) > 5 else np.nan


def line(x, nm, w=46, unit="$"):
    x = pd.Series(x).dropna()
    if len(x) < 6: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; f = (lambda v: f"${v:7.0f}") if unit == "$" else (lambda v: f"{v:7.3f}")
    by = x.groupby(y).mean()
    return (f"   {nm:<{w}} n={len(x):4d} avg {f(x.mean())} t {tstat(x):5.1f} up {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-21 {f(x[y < 2022].mean())} 22-26 {f(x[y >= 2022].mean())} 24-26 {f(x[y >= 2024].mean())}")


def roll_rows(g, tr):
    """Trading row of each monthly roll: the 3rd Friday, or the Thursday before it when Friday is a holiday."""
    idx = pd.DatetimeIndex(g.ts[tr]); out = []
    for (y, m), grp in pd.Series(np.arange(len(tr)), index=idx).groupby([idx.year, idx.month]):
        fr = pd.date_range(pd.Timestamp(y, m, 1), periods=31, freq="D"); fr = fr[(fr.month == m) & (fr.dayofweek == 4)]
        f3 = fr[2]; hit = grp[grp.index <= f3]
        if len(hit) and hit.index[-1] >= f3 - pd.Timedelta(days=1): out.append(hit.iloc[-1])
    return np.array(out)


def measures(g, sym, start="2018-01-01"):
    tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= start]; idx = pd.DatetimeIndex(g.ts[tr])
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); px = lambda t: pd.Series(cf[tr * 1440 + jof(t)], index=idx)
    atr = pd.Series(g.daily_atr(15)[tr], index=idx)
    pv = PV[sym]; k = roll_rows(g, tr); is_roll = np.zeros(len(tr), bool); is_roll[k] = True
    fri = (idx.dayofweek == 4)
    seg = {"8:30-10:30": (830, 1030), "10:30-11:00 sell window": (1030, 1100), "11:00-15:00": (1100, 1500), "10:00-10:30": (1000, 1030)}
    S = {nm: (px(b) - px(a)) * pv for nm, (a, b) in seg.items()}
    S["10:30-11:00 in ATR"] = (px(1100) - px(1030)) / atr
    hi = pd.Series(np.nanmax(g.h[tr][:, jof(831):jof(1500) + 1], 1), index=idx); lo = pd.Series(np.nanmin(g.l[tr][:, jof(831):jof(1500) + 1], 1), index=idx)
    wr = pd.Series(np.nanmax(g.h[tr][:, jof(1031):jof(1100) + 1], 1) - np.nanmin(g.l[tr][:, jof(1031):jof(1100) + 1], 1), index=idx) / atr
    return dict(tr=tr, idx=idx, px=px, atr=atr, pv=pv, k=k, is_roll=is_roll, fri=fri, S=S, rng=(hi - lo) / atr, wr=wr)


def after(series_by_row, rows, n, D):
    """Values on the n-th trading day after each row (positions in the trading index)."""
    p = rows + n; p = p[p < D]; return series_by_row.iloc[p]


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
    Q = measures(g, "NQ"); E = measures(es, "ES")
    idx, k, rl, fri = Q["idx"], Q["k"], Q["is_roll"], Q["fri"]; D = len(idx)
    print(f"monthly roll days {len(k)} ({idx[k][0].date()} .. {idx[k][-1].date()}); Thursday rolls: {int((idx[k].dayofweek == 3).sum())}")

    print("\nA. 3rd-Friday sell window (dealers short futures to hedge the calls they bought?)")
    for sym, X in (("NQ", Q), ("ES", E)):
        r_, f_ = X["is_roll"], X["fri"]
        for nm, s in X["S"].items():
            u = "x" if "ATR" in nm else "$"
            print(line(s[r_], f"{sym} {nm}: roll days", unit=u)); print(line(s[f_ & ~r_], f"{sym} {nm}: other Fridays", unit=u))
            print(f"      roll minus other Fridays t {tdiff(s[r_], s[f_ & ~r_]):.1f}; minus all other days t {tdiff(s[r_], s[~r_]):.1f}")
    s = Q["S"]["10:30-11:00 sell window"]
    print("   NQ window on roll days by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in s[rl].groupby(idx[rl].year).mean().items()))
    print(line(Q["wr"][rl], "NQ window range / ATR: roll days", unit="x")); print(line(Q["wr"][fri & ~rl], "NQ window range / ATR: other Fridays", unit="x"))

    print("\nB. Volatility after the roll: RTH range / ATR on day +n (dealers long gamma -> lower?)")
    ofr = np.where(fri & ~rl)[0]
    for n in (0, 1, 2, 3, 4, 5, 10):
        a, b = after(Q["rng"], k, n, D), after(Q["rng"], ofr, n, D)
        y = a.index.year; yb = b.index.year
        print(f"   day +{n:<2d} roll {a.mean():.3f} vs other Fridays {b.mean():.3f} (t {tdiff(a, b):5.1f}) | 18-21 {a[y < 2022].mean():.3f} vs {b[yb < 2022].mean():.3f}"
              f" | 22-26 {a[y >= 2022].mean():.3f} vs {b[yb >= 2022].mean():.3f} (t {tdiff(a[y >= 2022], b[yb >= 2022]):.1f})")

    print("\nC. Pin to the roll price (11:00 CT close on the roll day): |close 15:00 on day +n - roll price| / ATR")
    c15, c11, o831 = Q["px"](1500), Q["px"](1100), pd.Series(g.o[Q["tr"], jof(831)], index=idx)
    for n in (1, 2, 3, 5, 10):
        def dist(rows):
            p = rows + n; ok = p < D; return pd.Series(np.abs(c15.iloc[p[ok]].to_numpy() - c11.iloc[rows[ok]].to_numpy()) / Q["atr"].iloc[rows[ok]].to_numpy(), index=idx[rows[ok]])
        a, b = dist(k), dist(ofr); y, yb = a.index.year, b.index.year
        print(f"   day +{n:<2d} roll {a.mean():.3f} vs other Fridays {b.mean():.3f} (t {tdiff(a, b):5.1f}) | 22-26 {a[y >= 2022].mean():.3f} vs {b[yb >= 2022].mean():.3f} (t {tdiff(a[y >= 2022], b[yb >= 2022]):.1f})")
    print("   fade the 8:30 gap away from the roll price, days +1..+5 (long if open below the roll price), 8:31 -> 15:00, $ per NQ before costs:")
    for grp, rows in (("roll", k), ("other Fridays", ofr)):
        v = []
        for n in range(1, 6):
            p = rows + n; ok = p < D; pp, rr = p[ok], rows[ok]
            gap = (o831.iloc[pp].to_numpy() - c11.iloc[rr].to_numpy()) / Q["atr"].iloc[rr].to_numpy()
            v.append(pd.Series(-np.sign(gap) * (c15.iloc[pp].to_numpy() - o831.iloc[pp].to_numpy()) * 20.0, index=idx[pp])[np.abs(gap) > 0.25])
        print(line(pd.concat(v).sort_index(), f"gap fade |gap| > 0.25 ATR, after {grp}"))

    print("\nD. Drift: NQ 15:00 on the roll day -> 15:00 five days later, $ per NQ")
    def drift(rows):
        p = rows + 5; ok = p < D; return pd.Series((c15.iloc[p[ok]].to_numpy() - c15.iloc[rows[ok]].to_numpy()) * 20.0, index=idx[rows[ok]])
    print(line(drift(k), "week after the roll")); print(line(drift(ofr), "week after other Fridays"))
    def pre(rows):
        p = rows - 5; ok = p >= 0; return pd.Series((c11.iloc[rows[ok]].to_numpy() - c15.iloc[p[ok]].to_numpy()) * 20.0, index=idx[rows[ok]])
    print(line(pre(k), "week into the roll (to 11:00)")); print(line(pre(ofr), "week into other Fridays (to 11:00)"))

    print("\nE. Weekly writers (JEPQ from May 2022, QQQI / QDTE 2024+): every Friday and every Monday")
    mon = idx.dayofweek == 0
    for nm in ("10:30-11:00 sell window", "11:00-15:00"):
        print(line(Q["S"][nm][fri & ~rl], f"Fri {nm} (not roll)")); print(line(Q["S"][nm][mon], f"Mon {nm}"))
        print(line(Q["S"][nm][~fri & ~mon], f"Tue-Thu {nm}"))
    for n in (1, 2):
        a = after(Q["rng"], np.where(fri)[0], n, D); b = Q["rng"][~fri]
        print(f"   range / ATR day +{n} after any Friday 2022+: {a[a.index.year >= 2022].mean():.3f} vs all non-Fridays {b[b.index.year >= 2022].mean():.3f}; 2018-21 {a[a.index.year < 2022].mean():.3f} vs {b[b.index.year < 2022].mean():.3f}")
    pickle.dump(dict(k=k, idx=idx), open(SP + "option_income.pkl", "wb"))
