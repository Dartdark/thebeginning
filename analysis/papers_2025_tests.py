"""Two recent papers on our data (user, 2026-10-18), pre-registered before looking:

A  Bogousslavsky & Muravyev, "Who Trades at the Close?" (J. Financial Markets 2023): closing-auction volume spikes on
   option-expiration Fridays (3rd Friday), index-rebalancing days (S&P quarterly = March/June/Sept/Dec 3rd Friday;
   Russell reconstitution = last Friday of June) and month-ends (last trading day). Prediction: ES MOC Follow (MultiCharts
   trades) earns MORE on those heavy-close days than on other days. 1 test.
B  Adams, Dim, Eraker, Fontaine, Ornthanalai & Vilkov, "Do S&P 500 Options Increase Market Volatility? Evidence from
   0DTEs" (SSRN 5641974): dealers' hedging (long gamma) dampens intraday momentum. Prediction: the plan's momentum
   trades earn more when NQ is BELOW the Bridge's 0DTE gamma flip (dealers short gamma) than above it. Late-Day Flow was
   already split this way (below $158 vs above $36, t 2.0, analysis/gamma_momentum_test.py); new here: ES MOC Follow
   (regime at 14:50, NDX gamma as the proxy for ES) and Vault Break (regime at the entry bar). 2 tests.
Costs: ES $5 + 1 tick a side ($35 a trade), NQ $7.25 + 1 tick a side ($34.50).
  python3 analysis/papers_2025_tests.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.path.insert(0, "analysis/jesse")
import numpy as np, pandas as pd
from grid24 import jof
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
sys.argv = sys.argv[:1]
import compare as C
from gamma_regime_test import load_gex, Regime, START, END


def split(x, k, nm_on, nm_off):
    a, b = x[k], x[~k]; se = np.sqrt(a.net.var() / len(a) + b.net.var() / len(b))
    per = lambda y: f"18-22 ${y[y.entry_time < '2023'].net.mean():.0f} / 23+ ${y[y.entry_time >= '2023'].net.mean():.0f}"
    print(f"   {nm_on:<28} n={len(a):3d} ${a.net.mean():5.0f} ({per(a)})\n   {nm_off:<28} n={len(b):3d} ${b.net.mean():5.0f} ({per(b)})"
          f"\n   difference ${a.net.mean() - b.net.mean():.0f}, t {(a.net.mean() - b.net.mean()) / se:.1f}")


def heavy_close(days):
    d = pd.DatetimeIndex(days)
    third_fri = (d.dayofweek == 4) & (d.day >= 15) & (d.day <= 21)
    russell = (d.month == 6) & (d.dayofweek == 4) & (d.day >= 24)
    bd = pd.bdate_range("2017-12-01", "2026-12-31"); last = set(pd.Series(bd).groupby([bd.year, bd.month]).max())
    month_end = np.array([x in last for x in d])          # last weekday of the month (holiday month-ends: close enough)
    return third_fri | russell | month_end


if __name__ == "__main__":
    print("A. ES MOC Follow on heavy-close days (3rd Friday, Russell recon, month-end)")
    path, pv, tick, cost = C.REPORTS["ESMOCFollow"]
    m = C.mc_trades(path); m["net"] = m.points * pv - 2 * cost - 2 * tick * pv
    k = heavy_close(m.entry_time.dt.normalize())
    split(m, k, "heavy-close days", "other days")
    print("   by type:", {nm: (int(f.sum()), round(m.net[f].mean())) for nm, f in
                         (("3rd Friday", (m.entry_time.dt.dayofweek == 4).to_numpy() & m.entry_time.dt.day.between(15, 21).to_numpy()),
                          ("month-end", k & ~((m.entry_time.dt.dayofweek == 4).to_numpy() & m.entry_time.dt.day.between(15, 21).to_numpy())))})

    print("\nB. Below vs above the 0DTE gamma flip (Bridge NDX gamma, 2023-03-28 .. 2026-07-07)")
    g = pickle.load(open(SP + "g24.pkl", "rb")); Rg = Regime(g, load_gex(g))
    pos = pd.Series(np.arange(g.D), index=pd.DatetimeIndex(g.ts).normalize())
    for nm, dec in (("ESMOCFollow", lambda t: jof(1450)), ("VaultBreak", lambda t: jof(t.hour * 100 + t.minute))):
        path, pv, tick, cost = C.REPORTS[nm]
        m = C.mc_trades(path); m["net"] = m.points * pv - 2 * cost - 2 * tick * pv
        m = m[(m.entry_time >= START) & (m.entry_time <= END + pd.Timedelta(days=1))].copy()
        # decision = the bar before the entry: ES MOC decides at 14:50; VB at the 30-min close before its entry bar
        regs = []
        for t in m.entry_time:
            d = pos.get(t.normalize())
            if d is None: regs.append("n/a"); continue
            j = dec(t) if nm == "ESMOCFollow" else jof((t - pd.Timedelta(minutes=30)).hour * 100 + (t - pd.Timedelta(minutes=30)).minute)
            regs.append(Rg.at(d, j)[0])
        m["reg"] = regs
        print(f" {nm}: {len(m)} trades in the gamma era; regimes {m.reg.value_counts().to_dict()}")
        mm = m[m.reg.isin(["below", "above"])]
        split(mm, (mm.reg == "below").to_numpy(), "below the flip", "above the flip")
