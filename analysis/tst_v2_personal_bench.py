"""TrendSwingTrader V2 REBUILD (checks/candidates/tst_v2_rebuild/) against the PERSONAL book (user 2026-11-13 'yes' to the bench).
Longs only (the rebuild's shorts t 0.83; same treatment as the BTC ADX piece), spot signals executed on CME Micro Bitcoin with a
resting MBT stop at the initial 1.5-ATR distance, half off when spot halves, trailing exits copied at the spot exit time; marked at
every 16:00 CT close. Base = the personal book INCLUDING the BTC ADX piece now in the plan (free, 1 MBT a book), built exactly as
analysis/btc_adx_personal_bench.py. Variants: + rebuild 1 / 2 MBT; also vs the free V1 longs at 1 MBT for comparison.
Measure: 1-year block MC median year / p95 DD, mean of 5 seeds, paired vs the plan, 2019-26 / 2019-22 / 2023+.
  tools/run_stamped.sh analysis/tst_v2_personal_bench.py > analysis/outputs/tst_v2_personal_bench_output.txt
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
esrc = open("analysis/jesse_lib_btc_test.py", encoding="utf-8").read().split("adx_ref = P.run(P.setup())")[0]
E = {"__name__": "lib", "__doc__": "x\n"}; exec(compile(esrc, "jesse_lib_engine", "exec"), E)
b = E["bars"]("4h"); C = b.close.to_numpy(); A = E["atr"](b); _, _, ADX = E["dmi"](b); ema = E["ema"]


def tst(f, mi, sl, a_, S, T, R):
    e1, e2, e3 = ema(C, f), ema(C, mi), ema(C, sl)
    sig = np.where((e3 < e2) & (e2 < e1) & (e1 < C) & (ADX > a_), 1, np.where((e3 > e2) & (e2 > e1) & (e1 > C) & (ADX > a_), -1, 0)); sig[:200] = 0
    def plan(i, s, e): return e - s * S * A[i], e + s * T * A[i]
    def mg(j, pos, event=None):
        if event == "half": pos["stop"] = pos["e"]; return None
        if pos["half"]: pos["stop"] = max(C[j] - R * A[j], pos["e"]) if pos["s"] == 1 else min(C[j] + R * A[j], pos["e"])
    t = E["simulate"](b, sig, plan, manage=mg, half=True)
    return t[(t.side == 1) & (t.t >= FT[0]) & (t.tx <= FT[-1])].reset_index(drop=True)


ser = {}
for nm, prm in (("REBUILD", (21, 50, 200, 35, 1.5, 4.0, 2.0)), ("V1", (21, 50, 100, 25, 2.0, 3.0, 2.0)), ("BTCADX", None)):
    if prm is None:
        S = PB.run(PB.setup()); S = S[(S.t >= FT[0]) & (S.tx <= FT[-1]) & (S.side == 1)].reset_index(drop=True)
    else:
        S = tst(*prm)
    ser[nm], tr = g["mark"](S)
    print(f"{nm}: {len(tr)} long trades on MBT, ${sum(tr) / ((days[-1] - pd.Timestamp('2018-12-17')).days / 365.25):,.0f} a year per MBT")
cor = lambda a, c: np.corrcoef(a[a.index.year >= 2019], c[c.index.year >= 2019])[0, 1]
print(f"daily corr: rebuild vs BTC ADX {cor(ser['REBUILD'], ser['BTCADX']):+.2f}, vs the rest of the book {cor(ser['REBUILD'], P.sum(axis=1)):+.2f}")
plan = P.sum(axis=1) + ser["BTCADX"]
V = {"PLAN (book + BTC ADX 1 MBT a book)": plan, "+ TST V2 rebuild longs 1 MBT": plan + ser["REBUILD"], "+ TST V2 rebuild longs 2 MBT": plan + 2 * ser["REBUILD"],
     "+ free TST V1 longs 1 MBT (comparison)": plan + ser["V1"]}
mc = lambda x, sd: (lambda d: (d["pnl_p50"], d["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=sd))
for per, m in (("2019-26", days.year >= 2019), ("2019-22", (days.year >= 2019) & (days.year <= 2022)), ("2023+", days.year >= 2023)):
    print(f"\n{per}: {'variant':<42}{'$ a year p50':>13}{'DD p95':>9}{'ret/DD':>8}{'vs plan':>9}{'seeds better':>14}")
    R = {nm: [mc(x[m], sd) for sd in range(1, 6)] for nm, x in V.items()}
    pr = [a / b_ for a, b_ in R["PLAN (book + BTC ADX 1 MBT a book)"]]
    for nm, rr in R.items():
        r = [a / b_ for a, b_ in rr]
        print(f"        {nm:<42}${np.mean([a for a, _ in rr]):>11,.0f} ${np.mean([b_ for _, b_ in rr]):>7,.0f} {np.mean(r):7.2f} {np.mean(r) - np.mean(pr):+8.2f} {sum(a > b_ for a, b_ in zip(r, pr))}/5")
