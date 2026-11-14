"""ES dip-buy (SPYTFDipLS port, in the personal plan) as an APEX-LEGAL intraday version (user 2026-11-13 'can es dip be intraday?').
Same engine and Apex rules as analysis/jesse_nq_intraday_test.py (no entries 14:45-17:00 CT, flat at the 15:00 1h close), on ES:
$5 + 1 tick ($12.50) a market / stop fill per ES; per MES = / 10 - $0.55. With and without the VIX/VIX3M-rising skip.
  tools/run_stamped.sh analysis/spy_dip_es_intraday_test.py > analysis/outputs/spy_dip_es_intraday_test_output.txt
"""
import sys; sys.path.insert(0, "analysis")
src = open("analysis/jesse_nq_intraday_test.py", encoding="utf-8").read().split('print("\nper NQ contract')[0]
src = src.replace('CO.load("NQ")', 'CO.load("ES")').replace('RA.roll_jumps(g, "NQ")', 'RA.roll_jumps(g, "ES")')
src = src.replace('t.ret * t.e * 20 - 7.25 - 5 - np.where(t.why == "target", 0.0, 5.0)', 't.ret * t.e * 50 - 5.0 - 12.5 - np.where(t.why == "target", 0.0, 12.5)')
g = {"__name__": "x", "__doc__": "x\n"}; exec(compile(src, "nq_intraday", "exec"), g)
np, pd, S, run, tt = g["np"], g["pd"], g["S"], g["run"], g["tt"]
print(__doc__.split("\n")[0])
from new_data_screen import RULES, prior
from data_sweep import series
vv = series()["VIX/VIX3M (term structure)"]
b, tf, sig, plan, mg, lim, cd = S["SPY"]
d = pd.DatetimeIndex((b.index + pd.Timedelta(hours=7)).normalize())          # CME session date (17:00 CT start)
rising = prior(vv, d, RULES["rising"]) == 1
for nm, sg in (("unfiltered", sig), ("skip VIX/VIX3M rising", np.where(rising, 0, sig))):
    for apex in (False, True):
        t = run(b, tf, sg, plan, mg, lim, apex=apex, cooldown=cd); x = t.usd / 10 - 0.55
        a, z = x[t.yr <= 2022], x[t.yr >= 2023]; yrs = (t.t.max() - t.t.min()).days / 365.25; e = x.groupby(t.tx.dt.normalize()).sum().cumsum()
        print(f"{nm:<22} {'APEX intraday' if apex else 'as coded (overnight)':<21} {len(t):5d} trades, ${x.mean():6.2f} per MES, PF {x[x > 0].sum() / -x[x < 0].sum():.2f}, t {tt(x):5.2f} | 2018-22 t {tt(a):5.2f} | 2023+ t {tt(z):5.2f} | ${x.sum() / yrs:,.0f} a year per MES, max DD ${(e - e.cummax()).min():,.0f} | longs t {tt(x[t.side == 1]):.2f} shorts t {tt(x[t.side == -1]):.2f}")
        if apex and nm != "unfiltered":
            pm = np.array([(run(b, tf, sg, plan, mg, lim, apex=True, seed=s, cooldown=cd).usd / 10 - 0.55).mean() for s in range(20)])
            print(f"   APEX placebo (random side, 20 runs): mean ${pm.mean():.2f}, p95 ${np.percentile(pm, 95):.2f}, p = {np.mean(pm >= x.mean()):.2f}")
