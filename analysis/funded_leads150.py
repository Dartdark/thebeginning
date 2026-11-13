"""Watchlist sizing leads for the funded book's big pieces, re-benched on the CORRECTED 150K funded base (bench150.LIVE_FUNDED,
2026-11-13; earlier benches used a base with VB and without MOC / RS / DT / OT). User 2026-11-13: 'improve the funded book's big pieces'.
Leads (each pre-existing on WATCHLIST, rules as written there, scaled x1.5 to 150K; nothing new invented here):
  #16 LDF by NQ's OU reversion regime (analysis/ou_regime_test.py 'mr' flag): MR 4.5 / other 1.5 ; MR 4.5 / other 3
  #29 LDF half size on calm-VIX days (prior-day VIX <= its past-only 252-day median): calm 1.5 / volatile 3
  #14 EOS sized up on calm-VIX days: calm $1,575 / volatile $1,050 (x1.5 on calm)
Funded bench: 600 paired 2-year histories, cushion sizing. A lead is adopted only if it beats the base in clearly more than half the
histories AND does not raise 'blown' (bench noise: a few $100 and ~50% 'beats' is a tie).
  tools/run_stamped.sh analysis/funded_leads150.py > analysis/outputs/funded_leads150_output.txt
"""
import sys, io, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import bench150 as BN
print(__doc__.split("\n")[0])
ctx = BN.setup(); lab = ctx["lab"]; dts = ctx["dts"]; B = BN.LIVE_FUNDED
with contextlib.redirect_stdout(io.StringIO()):
    ou = runpy.run_path("analysis/ou_regime_test.py"); Dou = ou["build"]("NQ")[4]
mr = Dou.mr.reindex(dts).fillna(False).to_numpy().astype(bool)
vix = pd.read_csv("data/VIX_daily.csv"); vix.columns = [c.lower() for c in vix.columns]
dc = [c for c in vix.columns if "date" in c][0]; cc = [c for c in vix.columns if "close" in c][0]
v = pd.Series(vix[cc].astype(float).values, index=pd.to_datetime(vix[dc])).sort_index()
med = v.rolling(252, min_periods=120).median()
calm_s = (v <= med).shift(1)                                     # prior day's VIX vs its past-only median, known before the open
calm = calm_s.reindex(dts, method="ffill").fillna(False).to_numpy().astype(bool)
print(f"days {len(dts)}: OU-MR regime {mr.mean():.0%}, calm-VIX {calm.mean():.0%}")
def split(name, m, tag):
    for suf, mm in (("F", m), ("N", ~m)):
        lab.W[name + tag + suf] = lab.W[name] * mm[:, None]; lab.C[name + tag + suf] = lab.C[name] * mm
        if name in lab.stop: lab.stop[name + tag + suf] = lab.stop[name]
split("LDF_MC", mr, "_MR"); split("LDF_MC", calm, "_CALM"); split("EOS", calm, "_CALM")
nol = {k: v for k, v in B.items() if k != "LDF_MC"}; noe = {k: v for k, v in B.items() if k != "EOS"}
V = {"#16 LDF MR 4.5 / other 1.5": {**nol, "LDF_MC_MRF": 4.5, "LDF_MC_MRN": 1.5},
     "#16 LDF MR 4.5 / other 3": {**nol, "LDF_MC_MRF": 4.5, "LDF_MC_MRN": 3.0},
     "#29 LDF calm 1.5 / volatile 3": {**nol, "LDF_MC_CALMF": 1.5, "LDF_MC_CALMN": 3.0},
     "#14 EOS calm $1,575 / volatile $1,050": {**noe, "EOS_CALMF": ("risk", 1575.0), "EOS_CALMN": ("risk", 1050.0)}}
BN.funded_bench(ctx, V)
