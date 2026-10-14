"""Funded bench for the CL shorts-only Sunday-gap fade (S-rank round 2's best non-NQ line), 2026-10-14.

Rule (analysis/s_rank_gap_round2_test.py): when CL's Sunday 17:01 open is >= 0.1 x 15-day ATR above the last price
before the weekend close, short at the 17:05 bar open - 1 tick, out at the Monday 9:00 CT close + 1 tick (MultiCharts-confirmed spec; the
original Python test used 10:00 CT: $602 a trade, bench +2 MCL $9,839 / $12,630), stop 0.75 x ATR (fills at max(open, stop) + 1 tick);
(no stop: $642 a trade, PF 3.17, but one open loss of -$16.6k per CL on 2026-03-08, crude $98 -> $119 on Sunday night;
stops 0.5 / 0.75 / 1.0 / 1.5 / 2.0 ATR: t 2.8 / 3.2 / 2.9 / 2.7 / 2.6, 2018-22 $350 / $507 / $509 / $509 / $509);
roll weekends skipped. $7.25 + 1 tick per fill, 1 CL; the bench trades it in MCL (1/10) next to the NQ funded plan,
booked on the Monday (the Apex trading day starts Sunday 17:00), worst open loss from CL's own highs.
  python3 analysis/cl_sunday_fade_bench.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from cl_forced_flows_test import load
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 1000.0, 0.01, 7.25
STOP = 0.75
# MultiCharts-confirmed spec (analysis/cl_sunday_fade_confirm.py: 96/97 trades identical): the chart ran on Eastern time, so
# the exit is 10:00 ET = 9:00 CT, the entry the 17:05 CT 5-minute bar open, and roll weekends are not skipped.
EXIT_CT, ENTRY_T, ROLL_SKIP = 900, 1706, False

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    cl = load("CL"); fr = pickle.load(open(SP + "s_rank_gap2.pkl", "rb"))["frames"]["CL"]
    O, H, C = cl.o.ravel(), cl.h.ravel(), pd.Series(cl.c.ravel()).ffill().to_numpy()
    rows = []
    for r in fr.itertuples():
        if not r.ok or (ROLL_SKIP and r.roll) or not (r.gA >= 0.1): continue
        e_i = int(r.sun) * 1440 + jof(ENTRY_T); x_i = int(r.mon) * 1440 + jof(EXIT_CT)
        if np.isnan(O[e_i]): continue
        e = O[e_i] - TICK; px = C[x_i] + TICK; sp = e + STOP * r.atr; jx = x_i
        hit = np.where(H[e_i:x_i + 1] >= sp)[0]
        if len(hit): jx = e_i + hit[0]; px = (sp if jx == e_i or np.isnan(O[jx]) else max(O[jx], sp)) + TICK
        rows.append(dict(date=pd.Timestamp(cl.ts[int(r.mon)]), net=(e - px) * PV - COMM, adv=min((e - np.nanmax(H[e_i:jx + 1])) * PV - COMM, (e - px) * PV - COMM)))
    t = pd.DataFrame(rows).set_index("date")
    y = t.index.year; x = t.net
    print(f"trades {len(t)}, avg ${x.mean():.0f}, PF {x[x > 0].sum() / -x[x < 0].sum():.2f}, t {x.mean() / x.std() * np.sqrt(len(x)):.1f}, "
          f"2018-22 ${x[y < 2023].mean():.0f}, 2023-26 ${x[y >= 2023].mean():.0f}; worst open loss per CL ${t.adv.min():,.0f}")
    days = pd.DatetimeIndex(cl.ts[cl.trading]); days = days[days >= "2018-01-01"]
    dl = x.groupby(x.index.normalize()).sum().reindex(days, fill_value=0.0)
    print("   by year: " + " | ".join(f"{yy} ${v:,.0f}" for yy, v in x.groupby(y).sum().items()))
    print(M.table({"CL Sunday up-gap fade (shorts)": (dl, x), "  2023+": (dl[days >= "2023-01-01"], x[y >= 2023])}))
    b_, p_ = R.report({"CL Sunday fade, 2023+": dl[days >= "2023-01-01"]}, n=3000); print(b_); print(p_)
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    from bridge_monday_confirm import load_bridge_mc
    lab.add("MON_BR_MC", load_bridge_mc(lab.g), slippage=False)
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); pos = pd.Series(np.arange(len(dates)), index=dates)
    Wd = np.zeros(len(dates)); Cd = np.zeros(len(dates))
    for d, r in t.iterrows():
        if d in pos.index: i = pos[d]; Wd[i] = min(r.adv, r.net); Cd[i] = r.net
    lab.W["CLS"] = Wd[:, None] / 10 * np.ones((1, lab.W["VB"].shape[1])); lab.C["CLS"] = Cd / 10
    print("daily correlation with the plan:", {k: round(float(np.corrcoef(lab.C["CLS"], lab.C[k])[0, 1]), 2) for k in ("VB", "ONB_ML2_MC", "EOS", "LDF_MC", "MON_MC", "MON_BR_MC")})
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}
    from speed_to_13k import run as speed, fmt
    out = {}
    for ref in (1500.0, 1000.0):
        for q in (0, 1, 2, 3, 5):
            p = {**plan, "CLS": q} if q else plan
            a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=ref), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=ref)
            nm = f"cushion ${ref:,.0f}: plan" + (f" + {q} MCL" if q else "")
            print(f"   {nm:<32} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
            out[nm] = speed(lab, p, fmin=0.5, fmax=1.0, ref=ref)
    print(fmt(pd.DataFrame(out).T))
