"""How to collect the full $13,000 (all 6 payouts) of an Apex 50K PA faster (2026-10-13).

Every start day 2018 to late 2023 with a 3-year (750 trading day) horizon, real day order, the
same simulator as the funded bench (analysis/funded_sim.py). Measures:
  full 6m / 1y / 2y  share of accounts with all 6 payouts within 125 / 250 / 500 trading days
  median             median trading days to the 6th payout over ALL accounts (blown or slower
                     than 750 days count as never), so it is a real "typical time to $13k"
  if done            median days among accounts that got all 6
  blown              share of accounts closed by the drawdown within 3 years
  $/month (recycle)  payouts per 21 trading days when every blown or finished account is replaced
                     at once by a new one that needs PASS_DAYS trading days to pass the challenge:
                     E[paid] / E[days + PASS_DAYS] x 21 (one account at a time)
  max MNQ            the largest total size any day at the top of the sizing curve (Apex cap: 20)
Levers: size scale of the whole plan, cushion-sizing curve (ref = cushion that gives full size,
fmax = size cap above it), stage sizing (bigger size for the bigger later caps), add-ons.
  python3 analysis/speed_to_13k.py [SCRATCH_DIR]
"""
import sys, warnings, pickle, itertools; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import funded_sim as F
import addon_combo_test as A

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
H = 750
PASS_DAYS = 25          # trading days to the next funded account (HANDOFF: ~12 days a try, ~2.3 tries)
PLAN = A.PLAN


def scaled(plan, s):
    out = {}
    for k, v in plan.items():
        out[k] = ("risk", v[1] * s) if isinstance(v, tuple) else v * s
    return out


def run(lab, plan, fmin=0.5, fmax=1.0, ref=2000.0, stage=None):
    names, b = lab._base(plan)
    W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names])
    st = np.arange(0, lab.D - H)
    r = F.simulate_sized(W, C, b, horizon=H, starts=st, fmin=fmin, fmax=fmax, ref=ref, stage=stage)
    done = r["payouts"] == 6
    t = np.where(done, r["days"], np.inf)
    smax = 1.0 if stage is None else max(stage)
    return dict(full6m=np.mean(t <= 125), full1y=np.mean(t <= 250), full2y=np.mean(t <= 500),
                median=np.median(t), if_done=np.median(r["days"][done]) if done.any() else np.nan,
                blown=r["blown"].mean(), paid1y=np.nan, per_month=r["paid"].mean() / (r["days"].mean() + PASS_DAYS) * 21,
                exp3y=r["paid"].mean(), max_mnq=np.max(np.floor(b * fmax * smax + 1e-9).sum(0)))


def fmt(df):
    f = {c: "{:.0%}".format for c in ("full6m", "full1y", "full2y", "blown")}
    f.update({"median": lambda v: ">750" if not np.isfinite(v) else f"{v:.0f}", "if_done": "{:.0f}".format,
              "per_month": "${:,.0f}".format, "exp3y": "${:,.0f}".format, "max_mnq": "{:.0f}".format})
    return df.drop(columns=["paid1y"]).to_string(formatters=f)


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
    atr = g.daily_atr(15)
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    lab.add("HSF", pd.read_pickle(SP + "hsf_trades.pkl"), slippage=False)
    lab.add("NFP", pd.read_pickle(SP + "nfp_mc_spec.pkl"), stop_pts=0.5 * atr, slippage=False)
    lab.add("VCS", A.vcs_trades(g, es, atr), stop_pts=0.25 * atr, slippage=False)
    print(__doc__.split("\n")[0])

    rows = {}
    print("\n1. Current plan and size scale (cushion sizing as now: full size at $2,000 cushion, 0.5-1x):")
    for s in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0):
        rows[f"scale {s}"] = run(lab, scaled(PLAN, s))
    print(fmt(pd.DataFrame(rows).T))

    print("\n2. Cushion-sizing curve x scale (fmin 0.5): ref = cushion for full size, fmax = cap above it")
    rows = {}
    for s, ref, fmax in itertools.product((1.0, 1.25, 1.5), (2000.0, 1500.0, 1000.0), (1.0, 1.5, 2.0)):
        rows[f"scale {s}, ref ${ref:,.0f}, fmax {fmax}"] = run(lab, scaled(PLAN, s), fmax=fmax, ref=ref)
    R2 = pd.DataFrame(rows).T
    print(fmt(R2.sort_values("median")))

    print("\n3. Stage sizing (multiplier while n payouts have been made), scale 1:")
    rows = {}
    for nm, stg in (("flat", None), ("after 2 payouts x1.25", [1, 1, 1.25, 1.25, 1.25, 1.25]),
                    ("after 2 payouts x1.5", [1, 1, 1.5, 1.5, 1.5, 1.5]),
                    ("ramp 1 / 1 / 1.25 / 1.5 / 1.5 / 1.75", [1, 1, 1.25, 1.5, 1.5, 1.75]),
                    ("after the 1st payout x1.5", [1, 1.5, 1.5, 1.5, 1.5, 1.5]),
                    ("x2 from payout 3", [1, 1, 2, 2, 2, 2])):
        rows[nm] = run(lab, PLAN, stage=stg)
    print(fmt(pd.DataFrame(rows).T))

    print("\n4. Add-ons (MultiCharts-spec NFP Fade, VCS, Headline Shock), scale 1 and 1.25:")
    rows = {}
    for s in (1.0, 1.25):
        P = scaled(PLAN, s)
        rows[f"scale {s}"] = run(lab, P)
        rows[f"scale {s} + NFP $500 + VCS 1"] = run(lab, {**P, "NFP": ("risk", 500 * s), "VCS": s})
        rows[f"scale {s} + HSF 1"] = run(lab, {**P, "HSF": s})
        rows[f"scale {s} + all three"] = run(lab, {**P, "HSF": s, "NFP": ("risk", 500 * s), "VCS": s})
    print(fmt(pd.DataFrame(rows).T))
