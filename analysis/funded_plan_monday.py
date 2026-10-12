"""Funded plan update (2026-10-12): Monday Long (fixed 1 MNQ: its 0.5 ATR stop is ~$467 per MNQ at
October 2026 prices, so RiskPerTrade 300 skips every trade) replaces Overnight Drift. Size check with cushion
sizing (f = clip(cushion / $2,000, 0.5, 1)), all MultiCharts trade lists + 1 tick per fill.
Expects the funded lab with MON_MC (scratch lab_mon.pkl from monday_long_confirm.py)."""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R, funded_sim as F
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
lab = pickle.load(open(SP + "lab_mon.pkl", "rb")); g = lab.g
CS = dict(fmin=0.5, fmax=1.0, ref=2000.0)
old = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "OND_MC": ("risk", 500), "EOS": ("risk", 700)}
new = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700)}
plans = {"Old plan (with Overnight Drift)": old, "NEW: Monday 1 MNQ": new}
for vb in (2, 4): plans[f"  VB {vb}"] = {**new, "VB": vb}
for r in (300, 500): plans[f"  ONB ML ${r}"] = {**new, "ONB_ML2_MC": ("risk", r)}
for r in (300, 500): plans[f"  Monday ${r} risk"] = {**new, "MON_MC": ("risk", r)}
plans["  Monday 2 MNQ"] = {**new, "MON_MC": 2}
for r in (500, 900): plans[f"  EOS ${r}"] = {**new, "EOS": ("risk", r)}
rows = {}
for nm, p in plans.items():
    a = lab.score(p, 250, **CS); b = lab.score(p, 500, **CS)
    rows[nm] = {"1y": a["expected"], "1y 2018-22": a["s2018_22"], "1y 2023+": a["s2023_on"], "2y": b["expected"],
                "blown 1y": a["blown"], "blown 2y": b["blown"], "any payout": a["any_payout"], "all 6 (2y)": b["all_6"],
                "days to 1st": a["days_to_1st"], "worst start yr": a["worst_year"]}
df = pd.DataFrame(rows).T
fm = {c: "${:,.0f}".format for c in ("1y", "1y 2018-22", "1y 2023+", "2y", "worst start yr")}
fm.update({c: "{:.0%}".format for c in ("blown 1y", "blown 2y", "any payout", "all 6 (2y)")}); fm["days to 1st"] = "{:.0f}".format
print("Funded bench, cushion sizing (payouts per account):"); print(df.to_string(formatters=fm))
print("\nFixed size (no cushion sizing), for reference:")
print(lab.table({"Old plan": old, "New plan": new}, 250))
# per strategy and portfolio at the new sizes
dates = pd.DatetimeIndex(g.ts[lab.tr]); m = dates.year >= 2018
names, b = lab._base(new); b = np.floor(b + 1e-9)
P = {k: pd.Series(lab.C[k] * b[i], index=dates)[m] for i, k in enumerate(names)}
nm = {"VB": "Vault Break 3 MNQ", "ONB_ML2_MC": "Overnight Bias ML $400", "MON_MC": "Monday Long 1 MNQ", "EOS": "Expiration Open Short $700"}
rows = {nm[k]: (v, None) for k, v in P.items()}; rows["NEW PORTFOLIO"] = (sum(P.values()), None)
no, bo = lab._base(old); bo = np.floor(bo + 1e-9)
rows["old portfolio (with OND)"] = (sum(pd.Series(lab.C[k] * bo[i], index=dates)[m] for i, k in enumerate(no)), None)
print("\nStandard metrics at funded size (full size, 2018-2026):"); print(M.table(rows))
print("\nCorrelation of daily P&L:"); print(pd.DataFrame(P).rename(columns=nm).corr().round(2).to_string())
port = sum(P.values()); print("\nNew portfolio by year:", port.groupby(port.index.year).sum().round(0).astype(int).to_dict())
B, Pm = R.report({"new 2023-26": port[port.index.year >= 2023], "new 2018-26": port}, n=5000)
print("\nBootstrap:"); print(B); print(Pm)
