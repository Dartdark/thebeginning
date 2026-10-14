"""Does sizing Late-Day Flow by the 0DTE gamma flip help the funded plan? (user's question, 2026-10-14)

Funded bench (analysis/funded_lab.py, same simulator and cushion sizing as the plan), the 7-strategy plan with LDF at a
per-day size: on days with Bridge gamma (2023-03-28 .. 2026-07-07) by the regime at 14:00 (below / above the flip /
weak), else the plan's 2 MNQ. Only accounts starting 2023-03-28 or later are scored (1-year horizon: starts to Oct 2025;
2-year: to Oct 2024), so every account lives in the gamma era. Placebo: the same sizes with the regime labels shuffled
across the gamma days (50 runs).
  python3 analysis/ldf_gamma_sizing_check.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import funded_sim as F
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
PLAN = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}


def run(lab, b_ldf, horizon, starts):
    names, b = lab._base(PLAN)
    b[names.index("LDF_MC")] = b_ldf
    W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names])
    r = F.simulate_sized(W, C, b, horizon=horizon, starts=starts, **CS)
    t = np.where(r["payouts"] == 6, r["days"], np.inf)
    return dict(paid=r["paid"].mean(), blown=r["blown"].mean(), any=(r["payouts"] > 0).mean(), all6=(r["payouts"] == 6).mean(),
                med6=np.median(t))


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    G = pickle.load(open(SP + "gamma_momentum.pkl", "rb"))["G"]
    dates = pd.DatetimeIndex(g.ts[lab.tr])
    reg = pd.Series("none", index=dates); reg.loc[G.index.intersection(dates)] = G.reg00.reindex(G.index.intersection(dates)).values
    gam = (reg != "none").to_numpy()
    print(__doc__.split("\n")[0])
    print(f"gamma days {gam.sum()}: below {np.mean(reg[gam] == 'below'):.0%}, above {np.mean(reg[gam] == 'above'):.0%}, weak {np.mean(reg[gam] == 'weak/none'):.0%}")
    first = int(np.argmax(dates >= pd.Timestamp("2023-03-28")))
    VERS = {"current (LDF 2 everywhere)": (2, 2, 2), "below 3 / above 1": (3, 1, 2), "below 4 / above 2": (4, 2, 2),
            "below 3 / above 2": (3, 2, 2), "below 4 / above 1": (4, 1, 2), "below 2 / above 0 (skip above)": (2, 0, 2),
            "below 4 / above 0": (4, 0, 2), "LDF 3 everywhere (size control)": (3, 3, 3)}
    for H in (250, 500):
        st = np.arange(first, lab.D - H)
        print(f"\n=== horizon {H} trading days, {len(st)} start days ({dates[st[0]].date()} .. {dates[st[-1]].date()})")
        rows = {}
        for nm, (bl, ab, wk) in VERS.items():
            b = np.full(lab.D, 2.0)
            b[gam & (reg == "below").to_numpy()] = bl; b[gam & (reg == "above").to_numpy()] = ab; b[gam & (reg == "weak/none").to_numpy()] = wk
            rows[nm] = run(lab, b, H, st)
        df = pd.DataFrame(rows).T
        print(df.to_string(formatters={"paid": "${:,.0f}".format, "blown": "{:.0%}".format, "any": "{:.0%}".format, "all6": "{:.0%}".format,
                                       "med6": lambda v: ">H" if not np.isfinite(v) else f"{v:.0f}"}))
        # placebo for the two main versions
        lab_reg = reg[gam].to_numpy(); rng = np.random.default_rng(11)
        for nm in ("below 3 / above 1", "below 4 / above 2"):
            bl, ab, wk = VERS[nm]; pp = []
            for _ in range(50):
                sh = rng.permutation(lab_reg); b = np.full(lab.D, 2.0); ix = np.flatnonzero(gam)
                b[ix] = np.where(sh == "below", bl, np.where(sh == "above", ab, wk)); pp.append(run(lab, b, H, st)["paid"])
            print(f"   placebo {nm} (shuffled regimes, 50 runs): ${np.mean(pp):,.0f} (5-95% ${np.percentile(pp, 5):,.0f} .. ${np.percentile(pp, 95):,.0f}) vs real ${rows[nm]['paid']:,.0f}")
