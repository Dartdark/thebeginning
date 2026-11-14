"""TST V1 longs MBT timing check (2026-11-14, found while writing the MultiCharts code). Check: TST V1 longs on MBT, bench timing (t = 4h candle OPEN) vs correct timing (entry at the 4h close, exit at the minute).
  tools/run_stamped.sh analysis/tst_mbt_timing_check.py > analysis/outputs/tst_mbt_timing_check_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
src = open("analysis/jesse_rebuilds_personal_bench.py", encoding="utf-8").read().split("plan = P.sum(axis=1) + btc")[0]
g = {"__name__": "bench", "__doc__": "x\n"}; exec(compile(src.replace("print(__doc__.split", "pass  # (__doc__.split"), "rb", "exec"), g)
np, pd, E, mark, P, MC, days, btc, TS = g["np"], g["pd"], g["E"], g["mark"], g["P"], g["MC"], g["days"], g["btc"], g["TS"]
# exit minute: rerun simulate with a patched copy that records MT[k] at the exit
import inspect
s = inspect.getsource(E["simulate"]) if False else None
code = open("analysis/jesse_lib_btc_test.py", encoding="utf-8").read()
fn = code[code.index("def simulate("):code.index("def tt(")]
fn = fn.replace('why = "stop"; cst = FEE + SLIP; break', 'why = "stop"; cst = FEE + SLIP; txm = MT[k]; break').replace('px = pos["tgt"]; why = "target"; cst = FEE; break', 'px = pos["tgt"]; why = "target"; cst = FEE; txm = MT[k]; break')
fn = fn.replace("def simulate(", "def simulate2(").replace('pos.get("th", np.datetime64("NaT"))))', 'pos.get("th", np.datetime64("NaT")), txm))').replace('"R", "th"]', '"R", "th", "txm"]')
fn = fn.replace("px = None; parts = []", "px = None; parts = []; txm = np.datetime64('NaT')").replace('px = C[j]; why = "signal"', 'txm = b.index[j] + (b.index[1] - b.index[0]); px = C[j]; why = "signal"')
exec(fn, E)
b4 = E["bars"]("4h"); C4 = b4.close.to_numpy(); A4 = E["atr"](b4); _, _, X4 = E["dmi"](b4)
e1, e2, e3 = E["ema"](C4, 21), E["ema"](C4, 50), E["ema"](C4, 100)
s4 = np.where((e3 < e2) & (e2 < e1) & (e1 < C4) & (X4 > 25), 1, 0); s4[:200] = 0
def mg(j, pos, event=None):
    if event == "half": pos["stop"] = pos["e"]; return None
    if pos["half"]: pos["stop"] = max(C4[j] - 2 * A4[j], pos["e"])
T2 = E["simulate2"](b4, s4, lambda i, s, e: (e - 2 * A4[i], e + 3 * A4[i]), manage=mg, half=True)
FT = g["FT"]; w = lambda t: t[(t.t >= FT[0]) & (t.tx <= FT[-1])].reset_index(drop=True)
old, n0 = mark(w(TS))
fix = T2.assign(t=T2.t + pd.Timedelta(hours=4), tx=pd.to_datetime(T2.txm))
new, n1 = mark(w(fix))
print("same trades as the bench:", len(T2) == len(TS), "| lag check (exit minute - tx, hours) median", ((pd.to_datetime(T2.txm) - T2.tx).dt.total_seconds() / 3600).median())
yrs = (days[-1] - pd.Timestamp("2018-12-17")).days / 365.25
for nm, x, n in (("bench timing (4h OPEN)", old, n0), ("correct timing", new, n1)):
    print(f"{nm:<24} {n} trades, ${x.sum() / yrs:,.0f} a year per MBT, max DD ${(x.cumsum() - x.cumsum().cummax()).min():,.0f}; by year " + " ".join(f"{y} {v:+,.0f}" for y, v in x.groupby(x.index.year).sum().items() if y >= 2019))
plan = g["P"].sum(axis=1) + btc
mc = lambda x, sd: (lambda d: (d["pnl_p50"], d["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=sd))
for per, m in (("2019-26", days.year >= 2019), ("2023+", days.year >= 2023)):
    base = [mc(plan[m], sd) for sd in range(1, 6)]
    for nm, x in (("+ TST bench timing", old), ("+ TST correct timing", new)):
        rr = [mc((plan + x)[m], sd) for sd in range(1, 6)]
        print(f"{per} {nm:<22} p50 ${np.mean([a for a, _ in rr]):,.0f} DD p95 ${np.mean([b for _, b in rr]):,.0f} ret/DD {np.mean([a / b for a, b in rr]):.2f} vs plan {np.mean([a / b for a, b in rr]) - np.mean([a / b for a, b in base]):+.2f}")
