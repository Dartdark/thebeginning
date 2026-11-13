"""Overnight Strategy v2 (user's MultiCharts paste 2026-11-09): trend filter + volatility-targeted sizing. PRE-REGISTERED (header
committed before the first run). v1 (trend + VIX + Fear & Greed vote) was tested 2026-10-23 (analysis/overnight_sentiment_vote_test.py,
F: the filters remove the better nights); the paste's own comment drops VIX / F&G. The 3 visualizer studies are display only (no test).
Rule as coded: long at the 15:00 CT RTH close when that day's daily close > its 20-day average (Data2 daily RTH bar completes at the
same 15:00 bar), out at the next 08:30 CT open. Size = round(TargetRisk / (sd of the last 20 overnight gaps (open - prev close) / prev
close x close x $ per point)), clipped 1..50; TargetRisk $1,500. Costs per contract round trip as overnight_round.py (NQ $24.50,
ES $35; MNQ = NQ / 10 - $0.55); roll-week nights left out (as in the v1 test).
Items (4): NQ and ES x {trend + vol sizing (the paste), trend fixed 1}; context rows (not items): every night fixed, every night + vol
sizing (does sizing alone help?), the paste's sizing at MNQ (DollarsPerPoint 2; at NQ $20 it rounds to 1 almost every night).
Report: per night $, Sharpe / Sortino / PF / Calmar / Ulcer of the daily series 2018-26, 2018-22, 2023+ (longs only: the rule has no
shorts); 2023+ bootstrap Sharpe band; by year. Not Apex-legal (held through the 16:00 CT close): personal book only, as an addition
at the paste's MNQ sizing scaled to ~2 MNQ average and as a replacement of Overnight Tick (the overnight piece it overlaps), personal
1-year MC return / DD p95; daily corr with Overnight Tick.
  tools/run_stamped.sh analysis/overnight_v2_volsize_test.py > analysis/outputs/overnight_v2_volsize_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import overnight_round as O
from grid24 import jof
from metrics import perf
from resampling import bootstrap
import bench150 as BB


def nights(sym, target=1500.0, dpp=None, lookback=20, ma=20):
    g = O.load(sym); _, pv, cost = O.MK[sym]; tr = g.trading
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); dts = pd.DatetimeIndex(g.ts[tr]).normalize()
    c15 = pd.Series(cf[tr * 1440 + jof(1500)], index=dts); o830 = pd.Series(g.o[tr, jof(831)], index=dts)
    gross_pts = pd.Series(np.r_[o830.values[1:] - c15.values[:-1], np.nan], index=dts)        # tonight: today's close -> tomorrow's open
    trend = c15 > c15.rolling(ma).mean()
    gap = (o830 - c15.shift(1)) / c15.shift(1)                                                # gaps already realized this morning
    sd = gap.rolling(lookback).std(ddof=0)
    dpp = pv if dpp is None else dpp
    size = (target / (sd * c15 * dpp)).add(0.5).fillna(1).astype(int).clip(1, 50)
    rollwk = np.isin(dts.month, (3, 6, 9, 12)) & (dts.day >= 8) & (dts.day <= 17)
    ok = (~rollwk) & gross_pts.notna().values & sd.notna().values & (dts >= "2018-01-01")
    return pd.DataFrame({"pts": gross_pts, "trend": trend, "size": size, "pv": pv, "cost": cost}, index=dts)[ok]


def show(nm, x, dts_all):
    d = x.reindex(dts_all, fill_value=0.0); P, A, H = perf(d), perf(d[d.index < "2023"]), perf(d[d.index >= "2023"])
    b = bootstrap(d[d.index >= "2023"].values, n=2000, block=10).loc["sharpe"]
    xs = x[x != 0]; t = xs.mean() / xs.std() * np.sqrt(len(xs))
    print(f"   {nm:<40} n {len(xs):4d} ${xs.mean():6.1f}/night t {t:4.1f} | Sharpe {P['sharpe']:.2f} Sortino {P['sortino']:.2f} PF {P['profit_factor']:.2f} "
          f"Calmar {P['calmar']:.2f} Ulcer {P['ulcer']:.1f} DD ${P['max_dd']:,.0f} | 18-22 Sh {A['sharpe']:.2f} | 23+ Sh {H['sharpe']:.2f} (band {b.p5:.2f} / {b.p95:.2f})")
    return d


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    keep = {}
    for sym in ("NQ", "ES"):
        N = nights(sym); dts_all = N.index; net1 = N.pts * N.pv - N.cost
        print(f"\n {sym} (per contract; sized rows = contracts x per-contract net; paste sizing at {sym} $ per point):")
        print(f"   paste size at {sym}: median {N['size'].median():.0f}, share > 1: {(N['size'] > 1).mean():.0%}")
        show("every night, 1 contract (context)", net1, dts_all)
        show("every night + vol sizing (context)", net1 * N["size"], dts_all)
        show("ITEM trend, 1 contract", net1.where(N.trend, 0.0), dts_all)
        d = show("ITEM trend + vol sizing (the paste)", (net1 * N["size"]).where(N.trend, 0.0), dts_all)
        x = (net1 * N["size"]).where(N.trend, 0.0); print(f"      by year $: {x.groupby(x.index.year).sum().round(0).astype(int).to_dict()}")
        if sym == "NQ":
            Nm = nights("NQ", dpp=2.0); m_net = (Nm.pts * Nm.pv - Nm.cost) / 10 - 0.55
            print(f"   paste at MNQ ($2 / point): median {Nm['size'].median():.0f} MNQ, mean {Nm['size'].mean():.1f}")
            xm = (m_net * Nm["size"]).where(Nm.trend, 0.0); show("context: trend + vol sizing at MNQ", xm, dts_all)
            sc = 2.0 / Nm["size"][Nm.trend].mean(); keep["sized"] = xm * sc                  # scaled to ~2 MNQ average
            keep["fixed2"] = (2 * m_net).where(Nm.trend, 0.0)
            print(f"      personal version: MNQ sizing x {sc:.2f} (avg ~2 MNQ on trade nights)")
    P = pd.read_pickle("scratch_data/personal_P.pkl")
    # night P&L booked on the exit morning (the day it is realized)
    for k in keep: keep[k] = pd.Series(keep[k].values, index=keep[k].index).shift(1).dropna()
    ot = P.OvernightTick; s = keep["sized"].reindex(P.index, fill_value=0.0)
    print(f"\n   daily corr with Overnight Tick (2 MNQ in the book): {np.corrcoef(s, ot)[0, 1]:.2f}; with the book: {np.corrcoef(s, P.drop(columns=['FC2B', 'Kusho', 'S47', 'S30']).sum(axis=1))[0, 1]:.2f}")
    print("\n   Personal book 1-year MC return / DD p95:")
    BB.personal({"+ v2 sized ~2 MNQ": keep["sized"], "+ trend fixed 2 MNQ": keep["fixed2"]})
    print("   replacing Overnight Tick:")
    BB.personal({"v2 sized for OT": keep["sized"], "trend fixed 2 for OT": keep["fixed2"]}, drop=("OvernightTick",))
