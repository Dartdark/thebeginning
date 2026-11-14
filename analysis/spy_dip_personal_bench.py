"""SPYTFDipLS lead (data sweep 2026-11-13: skip trades entered on days when volatility is rising) against the PERSONAL book
(user 2026-11-13 'bench it'). Trades: analysis/jesse_lib_rest_test.py (as coded, NQ / ES 1h with a completed-4h SuperTrend regime,
holds overnight), per contract after costs; micro = / 10 - $0.55 extra micro commission a trade; booked on the exit day (not marked
overnight). Filters (from the sweep, POST HOC): NQ keep when VXN is NOT rising; ES keep when VIX/VIX3M is NOT rising (last close
before the entry day, data_sweep series and new_data_screen 'rising' rule).
Base = the personal plan now: personal_portfolio pieces (minus forward-log / retired), Noise longs, FINRA, ZT, OT x2, CL OVX sizing,
BTC ADX longs 1 MBT a book, TrendSwingTrader V1 longs 1 MBT. Variants: add filtered NQ 1 / 2 MNQ, unfiltered NQ 1 MNQ (control),
filtered ES 1 / 2 MES, both filtered; and REPLACE the piece the filtered NQ series correlates with most.
1-year block MC median year / p95 DD, mean of 5 seeds, paired vs the plan; 2018-26 / 2018-22 / 2023+.
  tools/run_stamped.sh analysis/spy_dip_personal_bench.py > analysis/outputs/spy_dip_personal_bench_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
src = open("analysis/jesse_rebuilds_personal_bench.py", encoding="utf-8").read().split("plan = P.sum(axis=1) + btc")[0]
g = {"__name__": "bench", "__doc__": __doc__}; exec(compile(src.replace("print(__doc__.split", "pass  # (__doc__.split"), "rebuild_bench", "exec"), g)
print(__doc__.split("\n")[0])
np, pd, P, MC, days, ns, btc, tst = g["np"], g["pd"], g["P"], g["MC"], g["days"], g["ns"], g["btc"], g["ser"]["TST longs"]
from new_data_screen import RULES, prior
from data_sweep import series
SR = series()


def daily(sym, filt):
    t = pd.read_csv(f"scratch_data/jesse_lib_SPY_{sym}.csv", parse_dates=["t", "tx"])
    ent = pd.DatetimeIndex(t.t.dt.normalize()); v = prior(SR[filt], ent, RULES["rising"]) if filt else np.zeros(len(t))
    keep = ~(v == 1) if filt else np.ones(len(t), bool)
    k = t[keep]; net = k.usd / 10 - 0.55
    ex = pd.DatetimeIndex(k.tx.dt.normalize()); ex = ex[ex <= days[-1]]; net = net[:len(ex)] if len(ex) < len(net) else net
    s = pd.Series(net.to_numpy()[:len(ex)], index=ns["to_trading_day"](ex)).groupby(level=0).sum().reindex(days, fill_value=0.0)
    yrs = len(days[days.year >= 2018]) / 252
    print(f"{sym} {'filter ' + filt + ' not rising' if filt else 'unfiltered'}: {keep.sum()} of {len(t)} trades kept, ${s[s.index.year >= 2018].sum() / yrs:,.0f} a year per micro, "
          f"max DD ${(s.cumsum() - s.cumsum().cummax()).min():,.0f}; by year " + " ".join(f"{y} {x:+,.0f}" for y, x in s.groupby(s.index.year).sum().items() if y >= 2018))
    return s


NQf, NQu, ESf = daily("NQ", "VXN"), daily("NQ", None), daily("ES", "VIX/VIX3M (term structure)")
plan = P.sum(axis=1) + btc + tst
cor = {c: np.corrcoef(NQf[NQf.index.year >= 2018], P[c][P.index.year >= 2018])[0, 1] for c in P}
top = max(cor, key=lambda c: cor[c])
print("daily corr of filtered NQ with each piece: " + ", ".join(f"{c} {v:+.2f}" for c, v in sorted(cor.items(), key=lambda kv: -kv[1])[:6]) + f" | with the whole plan {np.corrcoef(NQf, plan)[0, 1]:+.2f}; most-overlapping: {top}")
V = {"PLAN (book + BTC ADX + TST V1 longs)": plan,
     "+ SPY dip NQ filtered 1 MNQ": plan + NQf, "+ SPY dip NQ filtered 2 MNQ": plan + 2 * NQf, "+ SPY dip NQ UNFILTERED 1 MNQ (control)": plan + NQu,
     "+ SPY dip ES filtered 1 MES": plan + ESf, "+ SPY dip ES filtered 2 MES": plan + 2 * ESf, "+ both filtered (1 MNQ + 1 MES)": plan + NQf + ESf,
     f"{top} -> SPY dip NQ filtered 1 MNQ": plan - P[top] + NQf}
mc = lambda x, sd: (lambda d: (d["pnl_p50"], d["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=sd))
for per, m in (("2018-26", days.year >= 2018), ("2018-22", (days.year >= 2018) & (days.year <= 2022)), ("2023+", days.year >= 2023)):
    print(f"\n{per}: {'variant':<46}{'$ a year p50':>13}{'DD p95':>9}{'ret/DD':>8}{'vs plan':>9}{'seeds better':>14}")
    R = {nm: [mc(x[m], sd) for sd in range(1, 6)] for nm, x in V.items()}
    pr = [a / b_ for a, b_ in R["PLAN (book + BTC ADX + TST V1 longs)"]]
    for nm, rr in R.items():
        r = [a / b_ for a, b_ in rr]
        print(f"        {nm:<46}${np.mean([a for a, _ in rr]):>11,.0f} ${np.mean([b_ for _, b_ in rr]):>7,.0f} {np.mean(r):7.2f} {np.mean(r) - np.mean(pr):+8.2f} {sum(a > b_ for a, b_ in zip(r, pr))}/5")
