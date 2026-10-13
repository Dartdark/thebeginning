"""Follow-up to speed_to_13k.py (2026-10-13): combine the safe speed-ups, real max size (only
strategies that traded that day, at the top of the sizing curve), and the time to each payout
(for running several accounts with the same trades in parallel).
  python3 analysis/speed_to_13k_followup.py [SCRATCH_DIR]
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import funded_sim as F, addon_combo_test as A
from speed_to_13k import run, fmt, scaled, PLAN, SP

RAMP = [1, 1, 1.25, 1.5, 1.5, 1.75]


def real_max(lab, plan, fmax=1.0, stage=None):
    names, b = lab._base(plan)
    traded = np.stack([(lab.C[k] != 0) | (lab.W[k].min(1) != 0) for k in names])
    m = 1.0 if stage is None else max(stage)
    tot = (np.floor(b * fmax * m + 1e-9) * traded).sum(0)
    return int(tot.max()), float(np.percentile(tot[tot > 0], 99))


def time_to(lab, plan, targets=(3000, 5000, 7500, 10000, 13000), stage=None, ref=2000.0, fmax=1.0):
    """Median trading days until cumulative payouts reach each target (never = inf)."""
    names, b = lab._base(plan)
    W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names])
    st = np.arange(0, lab.D - 750)
    out = {}
    hs = list(range(25, 751, 25))
    paid = np.stack([F.simulate_sized(W, C, b, horizon=h, starts=st, fmin=0.5, fmax=fmax, ref=ref,
                                      stage=stage)["paid"] for h in hs])       # (len(hs), starts)
    for tg in targets:
        reach = paid >= tg - 1e-6
        first = np.where(reach.any(0), np.array(hs)[np.argmax(reach, 0)], np.inf)
        out[f"${tg:,}"] = np.median(first)
    return out


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
    atr = g.daily_atr(15)
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    lab.add("HSF", pd.read_pickle(SP + "hsf_trades.pkl"), slippage=False)
    lab.add("NFP", pd.read_pickle(SP + "nfp_mc_spec.pkl"), stop_pts=0.5 * atr, slippage=False)
    lab.add("VCS", A.vcs_trades(g, es, atr), stop_pts=0.25 * atr, slippage=False)
    NV = {**PLAN, "NFP": ("risk", 500), "VCS": 1}
    ALL = {**NV, "HSF": 1}
    cfg = {"current plan": (PLAN, None, 2000.0, 1.0),
           "plan + ramp": (PLAN, RAMP, 2000.0, 1.0),
           "plan + NFP + VCS": (NV, None, 2000.0, 1.0),
           "plan + NFP + VCS + ramp": (NV, RAMP, 2000.0, 1.0),
           "plan + all three": (ALL, None, 2000.0, 1.0),
           "plan + all three + ramp": (ALL, RAMP, 2000.0, 1.0),
           "plan, ref $1,500": (PLAN, None, 1500.0, 1.0),
           "plan + all three + ramp, ref $1,500": (ALL, RAMP, 1500.0, 1.0),
           "scale 1.25 (aggressive)": (scaled(PLAN, 1.25), None, 2000.0, 1.0)}
    rows, mx, tt = {}, {}, {}
    for nm, (p, stg, ref, fmax) in cfg.items():
        rows[nm] = run(lab, p, fmax=fmax, ref=ref, stage=stg)
        mx[nm] = real_max(lab, p, fmax, stg)
        rows[nm]["max_mnq"] = mx[nm][0]
        tt[nm] = time_to(lab, p, stage=stg, ref=ref, fmax=fmax)
    print(__doc__.split("\n")[0])
    print("\n1. Combined safe speed-ups (3-year horizon, starts 2018 to late 2023):")
    print(fmt(pd.DataFrame(rows).T))
    print("   real size: max MNQ / 99th percentile on days the strategies trade:",
          {k: f"{a} / {b:.0f}" for k, (a, b) in mx.items()})
    print("\n2. Median trading days until cumulative payouts reach each amount (one account):")
    T = pd.DataFrame(tt).T
    print(T.to_string(float_format=lambda v: ">750" if not np.isfinite(v) else f"{v:.0f}"))
    print("\n   Running N accounts with the same trades (started together): $13,000 in total needs")
    print("   $13,000 / N per account: 1 account = the $13,000 column, 2 accounts = $7,500 each (4 payouts),")
    print("   3 accounts = $5,000 each (3 payouts), 4-5 accounts = $3,000 each (2 payouts).")

    print("\n3. Without Headline Shock (no MultiCharts code yet): ramp + ref $1,500")
    rows = {}
    for nm, (p, stg, ref) in {"plan + ramp, ref $1,500": (PLAN, RAMP, 1500.0),
                              "plan + NFP + VCS + ramp, ref $1,500": (NV, RAMP, 1500.0),
                              "plan + NFP + VCS, ref $1,500": (NV, None, 1500.0)}.items():
        rows[nm] = run(lab, p, ref=ref, stage=stg); rows[nm]["max_mnq"] = real_max(lab, p, 1.0, stg)[0]
    print(fmt(pd.DataFrame(rows).T))
