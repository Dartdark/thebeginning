"""VIX-regime sizing on the PERSONAL book (user 2026-11-08). No Apex floor, so the measure is the personal ladder's: 1-year
Monte Carlo (20-day blocks, 2,000 runs) $ p50, bad year p5, drawdown p95, return / DD, capital = DD p95 / 0.20.
Book = the cleared personal pieces at 1 micro each (personal_portfolio.py minus the forward-log pieces FC2B, Kusho, S47, S30).
Regime = vix_regime_sizing.regime (prior-day VIX above its past-only median = volatile). Variants: VB + LDF (post hoc pick)
and all pieces (blanket), down on calm days and / or up on volatile days. Scored on 2018-26, 2018-22 and 2023+.
  tools/run_stamped.sh analysis/vix_sizing_personal.py > analysis/outputs/vix_sizing_personal_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
from vix_regime_sizing import regime

FWD = ["FC2B", "Kusho", "S47", "S30"]


def mc(x):
    d = MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1)
    return d["pnl_p50"], d["pnl_p5"], d["dd_p95"]


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    P = pd.read_pickle("scratch_data/personal_P.pkl"); P = P[[c for c in P.columns if c not in FWD]]
    vol = regime(P.index); sel2 = ["VaultBreak", "LateDayFlow"]
    V = {"book as is": (None, 1, 1), "VB + LDF calm x0.5": (sel2, 1.0, 0.5), "VB + LDF volatile x1.5": (sel2, 1.5, 1.0),
         "VB + LDF volatile x2": (sel2, 2.0, 1.0), "VB + LDF x1.5 / x0.5": (sel2, 1.5, 0.5),
         "ALL calm x0.5": (list(P.columns), 1.0, 0.5), "ALL volatile x1.5": (list(P.columns), 1.5, 1.0)}
    print(f"   pieces: {list(P.columns)}; volatile share of days {vol.mean():.0%}")
    for per, m in (("2018-26", np.ones(len(P), bool)), ("2018-22", P.index.year <= 2022), ("2023+", P.index.year >= 2023)):
        print(f"\n{per}:  {'variant':<26}{'$ a year p50':>13} {'bad yr p5':>10} {'DD p95':>9} {'ret/DD':>7} {'capital':>9}")
        for nm, (cols, up, dn) in V.items():
            Q = P.copy()
            if cols:
                f = np.where(vol, up, dn); Q[cols] = Q[cols].mul(f, axis=0)
            p50, p5, dd = mc(Q[m].sum(axis=1))
            print(f"         {nm:<26}${p50:>12,.0f} ${p5:>9,.0f} ${dd:>8,.0f} {p50 / dd:>7.2f} ${dd / 0.2:>8,.0f}")
