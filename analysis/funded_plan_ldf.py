"""Funded plan update (2026-10-12): add Late-Day Flow (MultiCharts trades, fixed 2 MNQ) to
VB 3, ONB ML $400, Monday Long 1 MNQ, EOS $700. Cushion sizing f = clip(cushion / $2,000, 0.5, 1).
Expects the funded lab with MON_MC and LDF_MC (scratch lab_mon.pkl from late_day_flow_confirm.py)."""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
lab = pickle.load(open(SP + "lab_mon.pkl", "rb")); g = lab.g
CS = dict(fmin=0.5, fmax=1.0, ref=2000.0)
old = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700)}
new = {**old, "LDF_MC": 2}
plans = {"Previous plan (4 strategies)": old, "NEW: + Late-Day Flow 2 MNQ": new,
         "  VB 2": {**new, "VB": 2}, "  ONB ML $300": {**new, "ONB_ML2_MC": ("risk", 300)},
         "  EOS $500": {**new, "EOS": ("risk", 500)}, "  Late-Day Flow 3 MNQ": {**new, "LDF_MC": 3}}
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
print("\nFixed size (no cushion sizing), for reference:"); print(lab.table({"Previous plan": old, "New plan": new}, 250))
dates = pd.DatetimeIndex(g.ts[lab.tr]); m = dates.year >= 2018
names, b = lab._base(new); b = np.floor(b + 1e-9)
P = {k: pd.Series(lab.C[k] * b[i], index=dates)[m] for i, k in enumerate(names)}
nm = {"VB": "Vault Break 3 MNQ", "ONB_ML2_MC": "Overnight Bias ML $400", "MON_MC": "Monday Long 1 MNQ",
      "EOS": "Expiration Open Short $700", "LDF_MC": "Late-Day Flow 2 MNQ"}
rows = {nm[k]: (v, None) for k, v in P.items()}
port = sum(P.values()); rows["NEW PORTFOLIO"] = (port, None)
rows["previous portfolio"] = (sum(v for k, v in P.items() if k != "LDF_MC"), None)
print("\nStandard metrics at funded size (full size, 2018-2026):"); print(M.table(rows))
print("\nCorrelation of daily P&L:"); print(pd.DataFrame(P).rename(columns=nm).corr().round(2).to_string())
print("\nNew portfolio by year:", port.groupby(port.index.year).sum().round(0).astype(int).to_dict())
B, Pm = R.report({"new 2023-26": port[port.index.year >= 2023], "new 2018-26": port}, n=5000)
print("\nBootstrap:"); print(B); print(Pm)
