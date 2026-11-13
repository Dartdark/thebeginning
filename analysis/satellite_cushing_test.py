"""Satellite Trader (user upload 2026-11-10: The Bridge's SatelliteTrader code + M. Conti's video). PRE-REGISTERED (header
committed before the first run).
The pipeline reads Cushing's 434 floating-roof tanks from Sentinel-2 and calls the sign of EIA's weekly Cushing stock change before
the release (claimed: right 76% in 2017-23, 72% in 2024-26 vs 71% / 58% for 'repeat last week's sign'); its money strategy is
operator stocks vs AMLP, held weekly (stocks: personal account at most). Rebuilding the satellite history here is not possible
(Copernicus login, every 2017-26 pass, the user's PC). So this asks what a Cushing call is worth on CL, the futures we can trade:
Data: EIA weekly Cushing stocks (data/eia/cushing_weekly.csv, W_EPC0_SAX_YCUOK_MBBLw, week ending Friday), released Wednesday
9:30 CT (Thursday in weeks with a Mon-Wed federal holiday); 2022-06-29 carries the weeks of 06-17 and 06-24, 2023-11-15 the weeks
of 11-03 and 11-10 (no release 2022-06-22 / 2023-11-08). Signal side: a draw (change < 0) -> long CL, a build -> short.
CL $1,000 a point, $7.25 + 1 tick per fill ($27.25 a round trip), 1 CL; 2018-26, 2018-22 vs 2023+.
Windows: W1 in at the 9:29 close, out at the 9:35 close; W2 out 10:30; W3 out 13:29; W4 overnight, the previous session's 13:29
close -> the release day's 13:29 close (holds overnight: personal account only).
C  CEILING (context, not tradeable): side from the TRUE Cushing change, all four windows; gross and net; also big changes only
   (|change| >= 1,000 kbbl). If even this does not pay after costs, no satellite can make it pay on CL.
B  ITEMS (tradeable now, the video's baseline): side from LAST week's published change; W1-W4 = 4 items, bar t_threshold(4),
   both periods positive. Its hit rate vs the true sign by year (the video: 71% / 58%).
S  What the satellite would add: value at hit rate h = mean over weeks of (2h - 1) x |ceiling gross| - cost (errors assumed
   independent of move size) at h = 0.58, 0.72, 0.76; break-even h per window.
Any item that passes: random-side placebo (500), standard test, data sweep (standing rule).
  tools/run_stamped.sh analysis/satellite_cushing_test.py > analysis/outputs/satellite_cushing_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from grid24 import jof
from metrics import t_threshold
from cl_forced_flows_test import load, line, PV, COST


def releases(idx):
    hol = USFederalHolidayCalendar().holidays("2017-12-01", "2026-12-31")
    wk = idx.to_period("W"); hw = set(pd.DatetimeIndex(hol[hol.dayofweek <= 2]).to_period("W"))
    rel = idx[((idx.dayofweek == 2) & ~wk.isin(hw)) | ((idx.dayofweek == 3) & wk.isin(hw))]
    return rel[~rel.isin(pd.DatetimeIndex(["2022-06-22", "2023-11-08"]))]


def changes():
    C = pd.read_csv("data/eia/cushing_weekly.csv", parse_dates=["week_ending"]).set_index("week_ending").cushing_kbbl
    return C.diff().dropna()


def week_of(d):
    return d - pd.Timedelta(days=(d.dayofweek - 4) % 7)          # the Friday before the release day


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    cl = load("CL"); rows = cl.trading[pd.DatetimeIndex(cl.ts[cl.trading]) >= pd.Timestamp("2018-01-01")]
    idx = pd.DatetimeIndex(cl.ts[rows]); cf = pd.Series(cl.c.ravel()).ffill().to_numpy(); pos = pd.Series(rows, index=idx)
    dC = changes(); rel = releases(idx); recs = []
    for k, d in enumerate(rel):
        f = week_of(d)
        if d == pd.Timestamp("2022-06-29"): ch = dC.get(pd.Timestamp("2022-06-17"), np.nan) + dC.get(pd.Timestamp("2022-06-24"), np.nan)
        elif d == pd.Timestamp("2023-11-15"): ch = dC.get(pd.Timestamp("2023-11-03"), np.nan) + dC.get(pd.Timestamp("2023-11-10"), np.nan)
        else: ch = dC.get(f, np.nan)
        prev = recs[-1]["ch"] if recs else np.nan
        r = pos[d]; ip = idx.get_loc(d)
        px = {h: cf[r * 1440 + jof(h)] for h in (929, 935, 1030, 1329)}
        p0 = cf[pos.iloc[ip - 1] * 1440 + jof(1329)] if ip > 0 else np.nan
        recs.append(dict(date=d, ch=ch, prev=prev, W1=(px[935] - px[929]) * PV, W2=(px[1030] - px[929]) * PV,
                         W3=(px[1329] - px[929]) * PV, W4=(px[1329] - p0) * PV))
    T = pd.DataFrame(recs).set_index("date").dropna(subset=["ch"]); T = T[T.ch != 0]
    print(f"   release days {len(T)} ({T.index[0].date()} .. {T.index[-1].date()}); Cushing weekly change median |{T.ch.abs().median():.0f}| kbbl")
    print(f"   check: corr(9:29->9:35 CL move, Cushing change) {T.W1.corr(T.ch):+.3f}; draws -> CL mean move ${T.W1[T.ch < 0].mean():.0f}, builds ${T.W1[T.ch > 0].mean():.0f}")
    W = {"W1 9:29->9:35": "W1", "W2 9:29->10:30": "W2", "W3 9:29->13:29": "W3", "W4 overnight 13:29->13:29": "W4"}

    print("\nC. CEILING: side from the TRUE Cushing change (known only after the release):")
    side = -np.sign(T.ch)
    for nm, c in W.items():
        g = side * T[c]; print(line(g, f"{nm} gross")); print(line(g - COST, f"{nm} net"))
    big = T.ch.abs() >= 1000
    for nm, c in W.items(): print(line((side * T[c] - COST)[big], f"{nm} net, |change| >= 1,000 kbbl"))

    print(f"\nB. ITEMS: side from LAST week's change (bar t >= {t_threshold(4):.2f}, both periods > 0):")
    sb = -np.sign(T.prev); ok = T.prev.notna() & (T.prev != 0); hit = (np.sign(T.prev) == np.sign(T.ch))[ok]
    print("   hit rate vs the true sign: all {:.0%}; by year ".format(hit.mean()) + " ".join(f"{y}:{v:.0%}" for y, v in hit.groupby(hit.index.year).mean().items())
          + f" | 2018-23 {hit[hit.index.year <= 2023].mean():.0%}, 2024+ {hit[hit.index.year >= 2024].mean():.0%}")
    res = {}
    for nm, c in W.items():
        x = (sb * T[c] - COST)[ok]; res[c] = x; tt = x.mean() / x.std() * np.sqrt(len(x)); y = x.index.year
        print(line(x, f"ITEM {nm}") + ("  PASS" if tt >= t_threshold(4) and x[y < 2023].mean() > 0 and x[y >= 2023].mean() > 0 else ""))

    print("\nS. What a satellite call would be worth per CL trade (net of $27.25):")
    for nm, c in W.items():
        a = T[c].abs().mean(); be = 0.5 * (1 + COST / a)
        print(f"   {nm:<28} mean |move| ${a:5.0f}: h 0.58 ${0.16 * a - COST:6.0f}, h 0.72 ${0.44 * a - COST:6.0f}, h 0.76 ${0.52 * a - COST:6.0f}; break-even h {be:.0%}")
    real = {c: (side * T[c]).mean() / T[c].abs().mean() for c in W.values()}
    print("   (the TRUE sign itself only reaches an effective h of " + ", ".join(f"{c} {0.5 * (1 + v):.0%}" for c, v in real.items())
          + ": the price does not follow Cushing one-for-one, so a 72% call is worth (2 x 0.72 - 1) x that)")
    for c in W.values():
        a = T[c].abs().mean(); print(f"   {c}: 72% satellite x the true-sign edge ~ ${(2 * 0.72 - 1) * (side * T[c]).mean() - COST:6.0f} net a trade")
    T.assign(net_W4=res["W4"]).to_csv("analysis/outputs/satellite_cushing_trades.csv")
