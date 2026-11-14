"""BTC ADX PREMIUM (6 ADX books 40-50) vs the plan's FREE version (2 books 40 / 50, 1 MBT a book) in the PERSONAL book
(user 2026-11-13 'yes, bench it'). Base, BTC marking (every CME 16:00 CT close), resting MBT stop, costs: exactly as
analysis/btc_adx_personal_bench.py (17 pieces, CL OVX sizing, OT x2, FINRA + ZT + Noise longs). Longs only, spot signals.
Variants: base without BTC | plan = + FREE 1 MBT a book (max 2) | + PREMIUM 1/3 MBT a book (max 2, equal risk; NOT tradeable,
reference) | + PREMIUM 1/2 MBT a book (max 3; not tradeable) | + PREMIUM 1 MBT a book (max 6; tradeable).
Measure: 1-year block MC median year / p95 DD (2,000 runs, mean of 5 seeds, paired vs the plan), 2019-26 / 2019-22 / 2023+.
  tools/run_stamped.sh analysis/btc_adx_premium_personal_bench.py > analysis/outputs/btc_adx_premium_personal_bench_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
src = open("analysis/btc_adx_personal_bench.py", encoding="utf-8").read()
head = src.split("S = PB.run(PB.setup())")[0]
loop = src.split("seg_d, seg_v, tr_usd, peak = [], [], [], []\n")[1].split("ref = pd.read_csv")[0]
g = {"__name__": "bench", "__doc__": __doc__}
exec(compile(head.replace("print(__doc__.split", "pass  # (__doc__.split"), "personal_bench_head", "exec"), g)
print(__doc__.split("\n")[0])
exec(compile("def mark(S):\n    global seg_d, seg_v, tr_usd, peak\n    seg_d, seg_v, tr_usd, peak = [], [], [], []\n"
             + "\n".join("    " + l for l in loop.split("\n")) + "\n    return btc, tr_usd\n", "mark", "exec"), g)
np, pd, PB, MC, days, P, FT = (g[k] for k in ("np", "pd", "PB", "MC", "days", "P", "FT"))
ctx = PB.setup()
ser = {}
for nm, books in (("FREE", (40, 50)), ("PREMIUM", (40, 42, 44, 46, 48, 50))):
    S = PB.run(ctx, books=books); S = S[(S.t >= FT[0]) & (S.tx <= FT[-1]) & (S.side == 1)].reset_index(drop=True)
    b, tr = g["mark"](S); ser[nm] = b
    print(f"{nm}: {len(tr)} long book trades on MBT, ${sum(tr):,.0f} per MBT a book in total, ${b.sum() / ((days[-1] - pd.Timestamp('2018-12-17')).days / 365.25):,.0f} a year per MBT a book")
base = P.sum(axis=1)
V = {"base (no BTC)": base, "PLAN: + FREE 1 MBT a book (max 2)": base + ser["FREE"],
     "+ PREMIUM 1/3 MBT a book (max 2, ref)": base + ser["PREMIUM"] / 3, "+ PREMIUM 1/2 MBT a book (max 3, ref)": base + ser["PREMIUM"] / 2,
     "+ PREMIUM 1 MBT a book (max 6)": base + ser["PREMIUM"]}
mc = lambda x, sd: (lambda d: (d["pnl_p50"], d["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=sd))
for per, m in (("2019-26", days.year >= 2019), ("2019-22", (days.year >= 2019) & (days.year <= 2022)), ("2023+", days.year >= 2023)):
    print(f"\n{per}: {'variant':<40}{'$ a year p50':>13}{'DD p95':>9}{'ret/DD':>8}{'vs plan':>9}{'seeds better':>14}{'backtest $/yr / max DD':>24}")
    R = {nm: [mc(x[m], sd) for sd in range(1, 6)] for nm, x in V.items()}
    pr = [a / b for a, b in R["PLAN: + FREE 1 MBT a book (max 2)"]]
    for nm, rr in R.items():
        r = [a / b for a, b in rr]; x = V[nm][m]; e = x.cumsum(); bt = (x.sum() / (m.sum() / 252)) / -(e - e.cummax()).min()
        print(f"        {nm:<40}${np.mean([a for a, _ in rr]):>11,.0f} ${np.mean([b for _, b in rr]):>7,.0f} {np.mean(r):7.2f} {np.mean(r) - np.mean(pr):+8.2f} "
              f"{sum(a > b for a, b in zip(r, pr))}/5{'':>9}{bt:>12.2f}")
