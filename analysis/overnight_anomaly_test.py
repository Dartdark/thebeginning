"""OvernightAnomaly v4.1 (Block B of the user's merged OvernightBiasORB + Anomaly file, 2026-10-24;
checks/candidates/overnight_anomaly/). Pre-specified rebuild of the file's defaults on the 24-hour NQ grid, 2018-2026:
  long at the close of the 15-min bar ending 17:30 CT when the prior RTH session (08:30-15:00, open of the first 15-min bar,
  close of the last) closed below its open and did not end before 14:00 (half day); exit at the close of the 02:30 bar;
  disaster stop entry - 4 x Avg_WinRange (Avg_WinRange = (19 x avg + range) / 20 of the 17:15-02:30 range, half days skipped).
Costs per NQ round trip $7.25 + 1 tick per fill (both are market fills). Nights whose window holds a contract switch are dropped.
Controls: every night long (no filter), after up days, random nights with the same count (1,000 draws).
Trades are dated by the exit day (the Apex trading day that starts 17:00 CT).
  python3 analysis/overnight_anomaly_test.py SCRATCH_DIR
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from overnight_round import roll_minutes
from co_oc_reversal_test import line
import metrics as M, resampling as R, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25


def nights(g):
    tr = set(g.trading.tolist()); rows = []; avg = 0.0
    rolls = np.sort(roll_minutes(g, "NQ"))
    for r in range(1, g.D - 1):
        e = g.c[r, jof(1716):jof(1730) + 1]
        if not np.isfinite(e).any() or not np.isfinite(g.c[r + 1, jof(230)]): continue
        rp = next((k for k in range(r, r - 4, -1) if k in tr), None)
        if rp is None: continue
        jj = np.arange(jof(831), jof(1500) + 1); c = g.c[rp, jj]
        if not np.isfinite(c).any(): continue
        last = jj[np.flatnonzero(np.isfinite(c))[-1]]; half = last < jof(1400)
        o = g.o[rp, jj][np.isfinite(g.o[rp, jj])][0]; cl = c[np.isfinite(c)][-1]
        ep = e[np.isfinite(e)][-1]
        flat = np.concatenate([np.arange(r * 1440 + jof(1716), r * 1440 + 1440), np.arange((r + 1) * 1440, (r + 1) * 1440 + jof(230) + 1)])
        hi, lo = np.nanmax(g.h.ravel()[flat]), np.nanmin(g.l.ravel()[flat])
        after = flat[flat > r * 1440 + jof(1730)]
        roll = ((rolls > flat[0]) & (rolls <= flat[-1])).any()
        stop = ep - 4 * avg if avg > 0 else np.nan
        lows = g.l.ravel()[after]; hit = np.flatnonzero(np.isfinite(lows) & (lows <= stop)) if np.isfinite(stop) else []
        if len(hit):
            j = after[hit[0]]; xo = g.o.ravel()[j]; xp = min(stop, xo) - TICK; how = "stop"
        else:
            xp = g.c[r + 1, jof(230)] - TICK; how = "time"
        held = after[:hit[0] + 1] if len(hit) else after
        net = (xp - ep - TICK) * PV - COMM; adv = min(net, (np.nanmin(g.l.ravel()[held]) - ep - TICK) * PV - COMM)
        rows.append(dict(date=pd.Timestamp(g.ts[r + 1]), entry_date=pd.Timestamp(g.ts[r]), down=cl < o, half=half, roll=roll,
                         ep=ep + TICK, xp=xp, how=how, avg=avg, net=net, adv=adv))
        if not half and hi > lo: avg = (hi - lo) if avg == 0 else (avg * 19 + (hi - lo)) / 20
    N = pd.DataFrame(rows)
    return N[(N.date >= "2018-01-01") & ~N.roll].reset_index(drop=True)


def stats(x, nm, days):
    p = M.perf(x.groupby(x.index).sum().reindex(days, fill_value=0.0), x.values)
    return (f"   {nm:<30} Sharpe {p['sharpe']:4.2f} Sortino {p['sortino']:4.2f} PF {p['profit_factor']:4.2f} "
            f"Calmar {p['calmar']:4.2f} Ulcer {p['ulcer']:4.2f} maxDD ${p['max_dd']:,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    N = nights(g); s = lambda m: N.net[m].set_axis(N.date[m])
    B = (N.down & ~N.half)
    print(f"nights {len(N)}, Block B trades {B.sum()}, disaster stops {(N.how[B] == 'stop').sum()}\n\nper NQ, 2018-2026:")
    for nm, m in (("Block B (down RTH, no half day)", B), ("every night long", ~N.half), ("after up RTH days", ~N.down & ~N.half),
                  ("Block B 2025-01 -> 2026-09", B & (N.date >= "2025-01-01") & (N.date < "2026-10-01"))):
        print(line(s(m), nm, 34))
    print("\nby year, Block B vs every night (sum per NQ):")
    yb, ya = s(B).groupby(lambda d: d.year).sum(), s(~N.half).groupby(lambda d: d.year).sum()
    print(pd.DataFrame({"Block B": yb, "every night": ya}).round(0).to_string())

    rng = np.random.default_rng(20261024); pool = s(~N.half).values; k = B.sum(); mb = s(B).mean()
    draws = np.array([rng.choice(pool, k, replace=False).mean() for _ in range(1000)])
    print(f"\nrandom nights (same count {k}): mean ${draws.mean():.1f}, Block B ${mb:.1f}, beaten by {np.mean(draws >= mb):.1%} of draws")

    print("\nmetrics (daily, per NQ):")
    for nm, m in (("Block B all", B), ("Block B 2023+", B & (N.date >= "2023-01-01")), ("every night all", ~N.half),
                  ("every night 2023+", ~N.half & (N.date >= "2023-01-01"))):
        print(stats(s(m), nm, pd.DatetimeIndex(N.date[N.date >= ("2023-01-01" if "2023" in nm else "2018-01-01")].unique())))
    d23 = pd.DatetimeIndex(N.date[N.date >= "2023-01-01"].unique())
    x = s(B & (N.date >= "2023-01-01")); d = x.groupby(x.index).sum().reindex(d23, fill_value=0.0)
    print("\nresampling, Block B 2023+ (per NQ):"); print("\n".join(R.report({"Block B": d})))
    mnq = (s(B) + COMM) / 10 - 0.725 - 0.55
    dm = mnq.groupby(mnq.index).sum().reindex(pd.DatetimeIndex(N.date.unique()), fill_value=0.0)
    for k in (1, 2): print(MC.report(mnq.values, dm, size=k, label=f"Block B {k} MNQ"))
    t = s(B); print(f"\nt {M.t_threshold(287):.2f} bar; DSR (288 items) {M.deflated_sharpe(t.groupby(t.index).sum(), 288):.2f}")
    N.to_csv(SP + "overnight_anomaly_nights.csv", index=False)
