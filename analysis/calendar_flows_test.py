"""Calendar-flow tests (2026-10-12): turn of month, month-end rebalancing, options expiration
(raw session returns), then the expiration-open short in the funded bench (commented block).
Expects pickled grids from a scratch run; kept as the record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
import calendar_flows as CF
from grid24 import jof
for name, f, pv, cost in (("NQ", "g24.pkl", 20, 7.25 + 2*5), ("ES", "ge.pkl", 50, 5 + 2*12.5)):
    g = pickle.load(open(f"/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/{f}","rb"))
    cal = CF.calendar(g); r = CF.session_returns(g, pv)
    df = cal.join(r); df = df[df.date.dt.year >= 2018]
    yr = df.date.dt.year
    def rep(lab, m, col="rth", sign=1):
        x = sign * df.loc[m, col].dropna()
        if len(x) < 10: return
        by = (x - cost).groupby(yr[x.index]).mean()
        print(f"  {lab:<58} n={len(x):4d} net ${x.mean()-cost:6.0f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f} win {(x-cost>0).mean():.0%} yrs+ {(by>0).sum()}/{len(by)}")
    print(f"\n{name}: long, 8:30->15:00 (and 17:00 prev -> 15:00 where noted)")
    rep("all days", df.index == df.index)
    rep("all days (17:00->15:00)", df.index == df.index, "glob")
    print(" turn of month")
    for lab, m in (("last trading day", df.tdm_end == 1), ("first 3 trading days", df.tdm <= 3), ("TOM window (last + first 3)", (df.tdm_end == 1) | (df.tdm <= 3)),
                   ("days 4 to last-1 (rest of month)", (df.tdm > 3) & (df.tdm_end > 1)), ("last 3 days before last", (df.tdm_end >= 2) & (df.tdm_end <= 4))):
        rep(lab, m); rep(lab + " (17:00->15:00)", m, "glob")
    print(" month-end rebalancing: last 3 trading days, short if month-to-date > +X, long if < -X")
    for X in (0.0, 0.02, 0.04):
        m = (df.tdm_end <= 3) & (df.mtd.abs() > X)
        s = -np.sign(df.mtd)
        x = (s * df.rth)[m].dropna(); xg = (s * df.glob)[m].dropna()
        for lab2, xx in (("8:30->15:00", x), ("17:00->15:00", xg)):
            by = (xx - cost).groupby(yr[xx.index]).mean()
            print(f"  |MTD|>{X:.0%} {lab2:<14} n={len(xx):4d} net ${xx.mean()-cost:6.0f} t={xx.mean()/xx.std()*np.sqrt(len(xx)):4.1f} yrs+ {(by>0).sum()}/{len(by)}")
    print(" options expiration")
    for lab, m in (("expiration Friday", df.opex), ("quarterly expiration (triple witching)", df.quarterly), ("expiration week Mon-Thu", df.opex_week & ~df.opex),
                   ("week after expiration", df.week_after), ("Monday before expiration", df.opex_week & (df.date.dt.dayofweek == 0)),
                   ("Monday after expiration", df.week_after & (df.date.dt.dayofweek == 0))):
        rep(lab, m); rep(lab + " (17:00->15:00)", m, "glob")
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# from grid import execute
# from grid24 import jof
# import calendar_flows as CF, intraday_research as IR
# from funded_lab import BENCHMARK
# g = pickle.load(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/g24.pkl","rb"))
# lab = pickle.load(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/lab.pkl","rb"))
# cal = CF.calendar(g); atr = g.daily_atr(15)
# opex = cal.index[cal.opex].to_numpy()
# for name, ex, st in (("OPEXS10", 1000, 0.3), ("OPEXS10w", 1000, 0.5), ("OPEXS", 1500, 0.5)):
#     s = pd.DataFrame(dict(day=opex, dj=jof(830), side=-1, stop=st * atr[opex], target=np.inf, exit_j=jof(ex)))
#     t = execute(g, s, max_trades=1); lab.add(name, t, stop_pts=st * atr)
#     t2 = t[pd.DatetimeIndex(t.date).year >= 2018].copy(); t2["slips"] = 2; t2["net"] -= 10
#     print(name, IR.summary(t2)); print("   by year:", t2.groupby(pd.DatetimeIndex(t2.date).year).net.mean().round().to_dict())
# plans = {"Benchmark": BENCHMARK}
# for k in ("OPEXS", "OPEXS10", "OPEXS10w"):
#     for rk in (300, 500):
#         p = dict(BENCHMARK); p[k] = ("risk", rk); plans[f"Benchmark + {k} ${rk}"] = p
# print(lab.table(plans)); print(lab.table(plans, horizon=500))
# pickle.dump(lab, open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/lab.pkl","wb"), protocol=4)
