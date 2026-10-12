"""Fan charts (bootstrap and permutation) like the slides, 2023-2026 holdout, fixed sizes.
Expects the pickled funded lab from a scratch run; kept as the record."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import resampling as R
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
lab = pickle.load(open(SP + "lab.pkl", "rb")); g = lab.g
dates = pd.DatetimeIndex(g.ts[lab.tr]); m = dates.year >= 2023


def sized(plan):
    names, b = lab._base(plan); b = np.floor(b + 1e-9)
    return {k: pd.Series(lab.C[k] * b[i], index=dates)[m] for i, k in enumerate(names)}


F = sized({"VB": 3, "ONB_ML2_MC": ("risk", 400), "OND_MC": ("risk", 500), "EOS": ("risk", 700)})
C = sized({"VB": 8, "ONB": ("risk", 1100)})
charts = {"funded_portfolio": ("Funded portfolio 2023-26 (VB 3, ONB ML $400, OND $500, EOS $700)", sum(F.values())),
          "funded_vb": ("Vault Break 3 MNQ, 2023-26", F["VB"]),
          "funded_onb_ml": ("Overnight Bias ML v2 $400, 2023-26", F["ONB_ML2_MC"]),
          "funded_ond": ("Overnight Drift $500, 2023-26", F["OND_MC"]),
          "funded_eos": ("Expiration Open Short $700, 2023-26", F["EOS"]),
          "combine_pair": ("Combine pair 2023-26 (VB 8 MNQ + Overnight Bias $1,100)", C["VB"] + C["ONB"])}
for f, (title, d) in charts.items():
    R.fan_chart(d, title, f"analysis/charts/fan_{f}.png", limit=2000)
    print("wrote", f)
