"""Long after a green RTH day, NQ (idea from the Bertola control row, 2026-11-08; POST HOC: the full sample was already seen,
so no holdout is clean and promotion needs t >= metrics.t_threshold(N items)).
Rule as first seen (frozen): RTH candle green (15:00 CT close > 08:30 open) -> long 1 NQ at the 15:00 close (+1 tick),
exit at the next RTH 15:00 close (-1 tick), stop 0.50% below entry on the 24h 1-min path. Costs $7.25 / $5 + 1 tick a fill.
Holds overnight: personal account only (not Apex). Also:
  split   overnight part (15:00 -> 08:30 open) vs next-day RTH part (Apex-legal: 08:30 open -> 14:59, stop 0.50%)
  family  no stop, stop 1.0%, green by > 0.5%, red days (mirror)
  placebo 1,000 random sets of the same number of days from ALL days (same exits): where does green sit?
  other   ES (same rule, out-of-market check)
  costs   resampling bootstrap / permutation on 2023+, Monte Carlo at 1 MNQ, daily corr with the plan pieces
  tools/run_stamped.sh analysis/long_after_green_test.py > analysis/outputs/long_after_green_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R, montecarlo as MC

J0, J1, JE = jof(831), jof(1500), jof(1459); TICK = 0.25


def one(g, k, mode, sl):
    """P&L in points (before costs) of a long signalled at the close of trading row k; None if data missing."""
    T = g.trading; r, rn = T[k], T[k + 1]; o, h, l, c = g.o, g.h, g.l, g.c
    e = c[r, J1]
    if mode == "full":   path = [(rr, j) for rr in range(r, rn + 1) for j in range(J1 + 1 if rr == r else 0, (J1 if rr == rn else 1439) + 1)]; xe = c[rn, J1]
    elif mode == "night": path = [(rr, j) for rr in range(r, rn + 1) for j in range(J1 + 1 if rr == r else 0, (J0 - 1 if rr == rn else 1439) + 1)]; xe = o[rn, J0]
    else:                 e = o[rn, J0]; path = [(rn, j) for j in range(J0, JE + 1)]; xe = c[rn, JE]
    if np.isnan(e) or np.isnan(xe): return None
    stp = e * (1 - sl) if sl else -1e18
    for rr, j in path:
        if np.isnan(c[rr, j]): continue
        if l[rr, j] <= stp: return (min(o[rr, j], stp) - TICK) - (e + TICK), "stop"
    return (xe - TICK) - (e + TICK), "exit"


def run(g, pv, comm, sel, mode="full", sl=0.005):
    T = g.trading; out = []
    for k in sel:
        if k + 1 >= len(T): continue
        z = one(g, k, mode, sl)
        if z is None: continue
        out.append((pd.Timestamp(g.ts[T[k + 1]]), z[0] * pv - 2 * comm, z[1]))
    return pd.DataFrame(out, columns=["date", "net", "kind"])


def candles(g):
    T = g.trading; op = g.o[T, J0]; cl = g.c[T, J1]
    ok = ~np.isnan(op) & ~np.isnan(cl); ks = np.arange(len(T))
    keep = ok & (pd.DatetimeIndex(g.ts[T]) >= "2018-01-01")
    return op, cl, ks, keep


def ts(x): return x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 1 else np.nan


def line(t, nm):
    x = t.net; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum()); y = t.groupby(t.date.dt.year).net.sum()
    a, b = t[t.date < "2023"].net, t[t.date >= "2023"].net
    return (f"   {nm:<40} n={len(x):5d} ${x.mean():6.0f} PF {pf:4.2f} t {ts(x):5.2f} stop {np.mean(t.kind == 'stop'):4.0%} "
            f"yrs+ {(y > 0).sum()}/{len(y)} | 18-22 ${a.mean():5.0f} t {ts(a):4.1f} | 23+ ${b.mean():5.0f} t {ts(b):4.1f}")


def daily(t, idx): return t.groupby("date").net.sum().reindex(idx, fill_value=0.0)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); pv, comm = 20.0, 7.25
    op, cl, ks, keep = candles(g)
    green = ks[keep & (cl > op)]; red = ks[keep & (cl < op)]; alld = ks[keep]
    base = run(g, pv, comm, green)
    print("\n1. Frozen rule, NQ per contract:"); print(line(base, "long after green, 0.5% stop (frozen)"))
    print("      by year $:", base.groupby(base.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("\n2. Where the money is (same green days):")
    print(line(run(g, pv, comm, green, "night"), "overnight only 15:00 -> 08:30 open"))
    print(line(run(g, pv, comm, green, "day"), "next RTH only 08:30 -> 14:59 (Apex-legal)"))
    print(line(run(g, pv, comm, alld, "night"), "control: overnight, ALL days"))
    print(line(run(g, pv, comm, alld, "day"), "control: next RTH, ALL days"))
    print("\n3. Family (information; each is a trial):")
    print(line(run(g, pv, comm, green, sl=0), "no stop"))
    print(line(run(g, pv, comm, green, sl=0.01), "stop 1.0%"))
    big = ks[keep & (cl > op * 1.005)]; print(line(run(g, pv, comm, big), "green by > 0.5% only"))
    print(line(run(g, pv, comm, red), "mirror: long after RED"))
    allt = run(g, pv, comm, alld); print(line(allt, "control: long after EVERY day"))
    print("\n4. Placebo: 1,000 random day-sets of the same size from all days (same exits):")
    m = allt.set_index(allt.index); pnl = allt.net.to_numpy(); n = len(base); rng = np.random.default_rng(7)
    pl = np.array([pnl[rng.choice(len(pnl), n, replace=False)].mean() for _ in range(1000)])
    print(f"   green ${base.net.mean():.0f} vs placebo mean ${pl.mean():.0f}, 95th ${np.percentile(pl, 95):.0f}, 99th ${np.percentile(pl, 99):.0f}; p = {np.mean(pl >= base.net.mean()):.3f}")
    ge = pickle.load(open("scratch_data/ge.pkl", "rb")); o2, c2, k2, kp2 = candles(ge)
    print("\n5. ES (same rule, $5 + 1 tick):")
    print(line(run(ge, 50.0, 5.0, k2[kp2 & (c2 > o2)]), "ES long after green"))
    print(line(run(ge, 50.0, 5.0, k2[kp2]), "ES control: every day"))
    idx = pd.date_range("2018-01-01", base.date.max(), freq="B"); d = daily(base, idx)
    print("\n6. Metrics per NQ (daily):")
    print(M.table({"green 2018+": (d, base.set_index("date").net), "green 2023+": (d[d.index >= "2023"], base[base.date >= "2023"].set_index("date").net)}))
    nt = len([1 for l_ in open("TIER_LIST.md") if l_.startswith("| ") and not l_.startswith("| Item") and "---" not in l_])
    print(f"   t needed for promotion above C: {M.t_threshold(nt):.2f} (N = {nt} items); deflated Sharpe (N = {nt}) {M.deflated_sharpe(d.values, nt):.2f}")
    b_, p_ = R.report({"green 2023+": d[d.index >= "2023"]}, limits=(2000, 5000, 10000)); print(b_); print(p_)
    print(MC.report(base.net.values, daily=d.values, size=0.1, label="long after green, 1 MNQ"))
    pdp = pd.read_csv("agents/tasks/plan_daily_pnl.csv", index_col=0, parse_dates=True)
    print("   daily corr with plan pieces:", pdp.corrwith(d.reindex(pdp.index, fill_value=0.0)).round(2).to_dict())
