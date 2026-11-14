"""BTC ADX longs on MBT: the plan's bench sold HALF a contract at the half-off (1 MBT a book, untradeable). Tradeable versions
(2026-11-14, found writing the MultiCharts code): (a) 1 MBT a book, NO half-off (the half-off event ignored; book runs to its exit);
(b) 2 MBT a book, 1 sold at the half-off (= 2 x the plan's fractional series). Same personal base and MC as the bench.
  tools/run_stamped.sh analysis/btc_adx_whole_contract_check.py > analysis/outputs/btc_adx_whole_contract_check_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
src = open("analysis/jesse_rebuilds_personal_bench.py", encoding="utf-8").read().split("esrc = open(")[0]
g = {"__name__": "bench", "__doc__": __doc__}; exec(compile(src.replace("print(__doc__.split", "pass  # (__doc__.split"), "rb", "exec"), g)
print(__doc__.split("\n")[0])
np, pd, PB, MC, days, P, FT, mark = (g[k] for k in ("np", "pd", "PB", "MC", "days", "P", "FT", "mark"))
S0 = PB.run(PB.setup()); S0 = S0[(S0.t >= FT[0]) & (S0.tx <= FT[-1]) & (S0.side == 1)].reset_index(drop=True)
frac, n = mark(S0.assign(side=1)); whole, _ = mark(S0.assign(side=1, th=pd.NaT))
yrs = (days[-1] - pd.Timestamp("2018-12-17")).days / 365.25
V = {"plan (half a contract at half-off)": frac, "(a) 1 MBT a book, no half-off": whole, "(b) 2 MBT a book, 1 off at half": 2 * frac}
for nm, x in V.items():
    print(f"{nm:<36} ${x.sum() / yrs:,.0f} a year, max DD ${(x.cumsum() - x.cumsum().cummax()).min():,.0f}; by year " + " ".join(f"{y} {v:+,.0f}" for y, v in x.groupby(x.index.year).sum().items() if y >= 2019))
base = P.sum(axis=1)
mc = lambda x, sd: (lambda d: (d["pnl_p50"], d["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=sd))
for per, m in (("2019-26", days.year >= 2019), ("2019-22", (days.year >= 2019) & (days.year <= 2022)), ("2023+", days.year >= 2023)):
    R = {nm: [mc((base + x)[m], sd) for sd in range(1, 6)] for nm, x in {"base (no BTC ADX)": 0 * frac, **V}.items()}
    pr = np.mean([a / b for a, b in R["plan (half a contract at half-off)"]])
    for nm, rr in R.items():
        r = np.mean([a / b for a, b in rr]); print(f"{per} {nm:<36} p50 ${np.mean([a for a, _ in rr]):,.0f} DD p95 ${np.mean([b for _, b in rr]):,.0f} ret/DD {r:.2f} vs plan {r - pr:+.2f}")
