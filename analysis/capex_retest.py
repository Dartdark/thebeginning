"""Capital-expansion bench retested against the CURRENT personal book (user 2026-11-08). Base = personal_P (the plan's pieces, 1 micro each;
FC2B / Kusho / S47 / S30 out, as in every personal bench) with Overnight Tick at 2 MNQ (adopted 11/08); FINRA longs (pending) not in.
Each bench piece added at 1 micro from its saved trade list (per NQ net / 10 - $0.55 a trade for micro costs; S30 = its own per-micro
daily file): 1-year block-bootstrap MC (2,000 runs, 20-day blocks): median year, bad year (p5), DD p95, return/DD, capital at the 20%
rule; 2018-26, 2018-22, 2023+. Promotion rule (PORTFOLIO): return/DD must improve; otherwise it stays on the bench.
Not retested (no trade list in this repo): Anson momentum, R2Vault, S03 v2 (Codex's results), futures trend (never tested).
  tools/run_stamped.sh analysis/capex_retest.py > analysis/outputs/capex_retest_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
from ingredient_ablation5 import swing

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    Pp = pd.read_pickle("scratch_data/personal_P.pkl"); Pp = Pp[[c for c in Pp.columns if c not in ("FC2B", "Kusho", "S47", "S30")]]
    base = Pp.sum(axis=1) + Pp.OvernightTick; idx = Pp.index
    dm = lambda d, net: (pd.Series(np.asarray(net, float) / 10 - 0.55, index=pd.DatetimeIndex(d))).groupby(level=0).sum().reindex(idx, fill_value=0.0)
    C = {}
    s30 = pd.read_csv("checks/candidates/s30_ibs/daily_nq_es_per_micro.csv", index_col=0, parse_dates=True).iloc[:, 0]; C["S30 IBS (NQ + ES)"] = s30.reindex(idx, fill_value=0.0)
    f = pd.read_csv("checks/candidates/fvb/trades.csv", parse_dates=["date"]); C["FVB First Valid Breakout"] = dm(f.date, f.net)
    v = pd.read_csv("checks/candidates/prior_vwap_trap/trades_python.csv"); v["date"] = pd.to_datetime(v.date.astype(str)); C["Prior VWAP Trap"] = dm(v.date, v.pnl)
    r = pd.read_csv("checks/candidates/rollzone_24h/python_trades_ATR.csv", parse_dates=["date"]); C["RollZone 24h (plain stop)"] = dm(r.date, r.net)
    k = pd.read_csv("checks/candidates/ricochet_1144/python_trades.csv", parse_dates=["date"]); C["Ricochet 1144 (commission only)"] = dm(k.date, k.net)
    import drift_pullback_test as DP
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); t = DP.run(g, DP.prep(g), window=99, start=900, end=1430, flat=1455, slip_ticks=1); C["DriftPullBack v3"] = dm(t.date, t.net)
    S = swing(g); C["Swing Target 2nd MNQ (both sides)"] = dm(S.date, S.net); C["Swing Target 2nd MNQ (shorts only)"] = dm(S[S.side < 0].date, S[S.side < 0].net)
    def mc(x):
        d = MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1); return d["pnl_p50"], d["pnl_p5"], d["dd_p95"], d["pnl_p50"] / d["dd_p95"]
    for per, m in (("2018-26", np.ones(len(idx), bool)), ("2018-22", idx.year <= 2022), ("2023+", idx.year >= 2023)):
        b = mc(base[m]); print(f"\n{per}: current book median ${b[0]:,.0f}  p5 ${b[1]:,.0f}  DD p95 ${b[2]:,.0f}  ret/DD {b[3]:.2f}  capital ${b[2] / 0.2 / 1000:.1f}k")
        rows = []
        for nm, s in C.items():
            x = mc((base + s)[m]); rows.append((nm, x[0] - b[0], x[1] - b[1], x[2] - b[2], x[3], x[3] - b[3], (x[2] - b[2]) / 0.2, s[m].corr(base[m])))
        for nm, dmed, dp5, ddd, rd, drd, cap, cr in sorted(rows, key=lambda z: -z[5]):
            print(f"   {nm:<36} median {dmed:+7,.0f}  p5 {dp5:+7,.0f}  DD {ddd:+6,.0f}  ret/DD {rd:.2f} ({drd:+.2f})  capital {cap:+7,.0f}  corr {cr:+.2f}", flush=True)
