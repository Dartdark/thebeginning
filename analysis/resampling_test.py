"""Bootstrap confidence intervals and drawdown permutation for the funded set and the
combine pair (analysis/resampling.py). Fixed sizes, $ per day with costs and slippage.
Expects the pickled funded lab from a scratch run; kept as the record."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import resampling as R
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
lab = pickle.load(open(SP + "lab.pkl", "rb")); g = lab.g
dates = pd.DatetimeIndex(g.ts[lab.tr]); m = dates.year >= 2018


def sized(plan):
    names, b = lab._base(plan); b = np.floor(b + 1e-9)
    return {k: pd.Series(lab.C[k] * b[i], index=dates)[m] for i, k in enumerate(names)}


F = sized({"VB": 3, "ONB_ML2_MC": ("risk", 400), "OND_MC": ("risk", 500), "EOS": ("risk", 700),
           "ONB_ML2_L": ("risk", 400), "ONB_ML2_S": ("risk", 400)})
funded = {"VB 3 MNQ": F["VB"], "ONB ML v2 $400": F["ONB_ML2_MC"], "  longs": F["ONB_ML2_L"],
          "  shorts": F["ONB_ML2_S"], "OND $500 (longs)": F["OND_MC"], "EOS $700 (shorts)": F["EOS"],
          "FUNDED PORTFOLIO": F["VB"] + F["ONB_ML2_MC"] + F["OND_MC"] + F["EOS"]}
C = sized({"VB": 8, "ONB": ("risk", 1100), "ONB_L": ("risk", 1100), "ONB_S": ("risk", 1100)})
combine = {"VB 8 MNQ": C["VB"], "ONB plain $1,100": C["ONB"], "  longs": C["ONB_L"],
           "  shorts": C["ONB_S"], "COMBINE PAIR": C["VB"] + C["ONB"]}

for setname, rows, limits in (("Funded set (recommended sizes)", funded, (1000, 2000, 3000)),
                              ("Combine pair (live sizes)", combine, (1000, 2000, 3000))):
    for per, lo in (("2018-2026", "2018"), ("2023-2026 holdout", "2023")):
        sub = {k: v[v.index >= lo] for k, v in rows.items()}
        B, P = R.report(sub, n=5000, block=10, limits=limits)
        print(f"\n=== {setname}, {per}: block bootstrap (10-day blocks, 5,000 runs), 90% interval ===")
        print(B)
        print(f"\n--- {setname}, {per}: day-order permutation (5,000 shuffles), max drawdown ---")
        print(P)

print("\n=== Apex window risk: share of start days with a $2,000 drawdown inside the next N trading days ===")
print("(real day order vs 500 shuffles of the same days; real above the shuffled 5-95% band = losses cluster)")
out = {}
for setname, rows in (("funded", funded), ("combine", combine)):
    for k, v in rows.items():
        for per, lo in (("2018-26", "2018"), ("2023-26", "2023")):
            for w in (20, 60):
                r = R.window_risk(v[v.index >= lo], window=w, limit=2000)
                out[(setname, k.strip(), per, w)] = r
W = pd.DataFrame(out).T
print(W.to_string(float_format=lambda v: f"{v:.0%}"))
