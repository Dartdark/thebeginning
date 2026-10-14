"""Gold and bitcoin next steps after the CL Sunday fade joined the plan (2026-10-14, user: "how about gold or btc").

1. Gold Asian-range breakout (best gold item, C; parked 2026-10-14) re-benched with the CL Sunday fade in the plan:
   filter B (fill before 02:00 CT), exit 12:00 CT, stop 1x range (analysis/gold_breakout_exit_test.py). Does a second
   uncorrelated market change its funded verdict (it was about neutral next to the NQ plan alone)?
2. FOMC (13:00 CT statement) on gold and bitcoin — not tested before on either: pre-announcement drift (long 8:31 ->
   12:59), the 13:00 -> 13:15 reaction, and follow / fade of that reaction 13:16 -> 15:00. Placebo: the same windows on
   non-FOMC Wednesdays. GC per contract $100/pt, $7.25 + 1 tick ($10) a fill; BTC per 1 BTC $1/pt, $25 + 1 tick ($5).
  python3 analysis/gold_btc_next_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from cl_forced_flows_test import load
from event_days import FOMC_DATES
import asian_breakout_test as AB
import gold_asian_breakout_gc_test as GT
from gold_breakout_exit_test import manage
from s_rank_cl_round1_test import tstat

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def line(x, nm, w=60):
    x = pd.Series(x).dropna(); y = x.index.year
    if len(x) < 8: return f"   {nm:<{w}} n={len(x)}"
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():7.0f} PF {pf:4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(x.groupby(y).sum() > 0).sum()}/{len(set(y))}"
            f" | 18-22 ${x[y < 2023].mean():6.0f} 23-26 ${x[y >= 2023].mean():6.0f}")


def cl_fade_into(lab):
    """The MultiCharts-confirmed CL Sunday up-gap fade (analysis/cl_sunday_fade_bench.py spec) as lab rows, per MCL."""
    cl = load("CL"); fr = pickle.load(open(SP + "s_rank_gap2.pkl", "rb"))["frames"]["CL"]
    O, H = cl.o.ravel(), cl.h.ravel(); C = pd.Series(cl.c.ravel()).ffill().to_numpy()
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); pos = pd.Series(np.arange(len(dates)), index=dates)
    Wd = np.zeros(len(dates)); Cd = np.zeros(len(dates))
    for r in fr.itertuples():
        if not r.ok or not (r.gA >= 0.1): continue
        e_i = int(r.sun) * 1440 + jof(1706); x_i = int(r.mon) * 1440 + jof(900)
        if np.isnan(O[e_i]): continue
        e = O[e_i] - 0.01; px = C[x_i] + 0.01; sp = e + 0.75 * r.atr; jx = x_i
        hit = np.where(H[e_i:x_i + 1] >= sp)[0]
        if len(hit): jx = e_i + hit[0]; px = (sp if jx == e_i or np.isnan(O[jx]) else max(O[jx], sp)) + 0.01
        net = (e - px) * 1000 - 7.25; adv = min((e - np.nanmax(H[e_i:jx + 1])) * 1000 - 7.25, net)
        d = pd.Timestamp(cl.ts[int(r.mon)])
        if d in pos.index: Wd[pos[d]] = adv; Cd[pos[d]] = net
    lab.W["CLS"] = Wd[:, None] / 10 * np.ones((1, lab.W["VB"].shape[1])); lab.C["CLS"] = Cd / 10


def fomc(G, sym, pv, cost):
    tr = G.trading[pd.DatetimeIndex(G.ts[G.trading]) >= "2018-01-01"]; idx = pd.DatetimeIndex(G.ts[tr])
    cf = pd.Series(G.c.ravel()).ffill().to_numpy(); P = lambda t: pd.Series(cf[tr * 1440 + jof(t)], index=idx)
    o831 = pd.Series(G.o[tr, jof(831)], index=idx)
    fd = idx.normalize().isin(pd.DatetimeIndex(FOMC_DATES)); wed = (idx.dayofweek == 2) & ~fd
    pre = (P(1259) - o831) * pv; react = (P(1315) - P(1300)) * pv; after = (P(1500) - P(1315)) * pv
    print(f"\n{sym}: FOMC days {fd.sum()}")
    print(line(pre[fd] - cost, f"{sym} pre-FOMC drift: long 8:31 -> 12:59"))
    print(line(pre[wed] - cost, f"   placebo: other Wednesdays"))
    print(f"   |13:00 -> 13:15| median ${react[fd].abs().median():,.0f} on FOMC days vs ${react[wed].abs().median():,.0f} other Wednesdays")
    for nm, sgn in (("follow", 1), ("fade", -1)):
        x = sgn * np.sign(react) * after - cost
        print(line(x[fd], f"{sym} {nm} the 13:00 -> 13:15 reaction, 13:16 -> 15:00"))
        print(line(x[wed], f"   placebo: other Wednesdays"))


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    print(__doc__.split("\n")[0])
    gc = GT.load_gc()
    base = AB.run(gc, "GC", exit_t=1200); base = base[(base.date >= pd.Timestamp("2018-01-01")) & ((base.t0 % 1440) // 60 < 2)].reset_index(drop=True)
    t = manage(gc, base, 1200, False, None)
    print("\n1. Gold Asian-range breakout (filter B, out 12:00) with the CL Sunday fade in the plan")
    print(line(t.set_index("date").net, "gold breakout, per GC"))
    lab = pickle.load(open(SP + "lab.pkl", "rb")); g = lab.g
    from bridge_monday_confirm import load_bridge_mc
    lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    cl_fade_into(lab); GT.add_to_lab(lab, "GXB", t, gc)
    dpos = pd.Series(np.arange(lab.D), index=pd.DatetimeIndex(g.ts[lab.tr])); st_arr = np.full(lab.D, 1e12)
    for r in t.itertuples():
        if r.date in dpos.index: st_arr[dpos[r.date]] = r.width * 5.0
    lab.stop["GXB"] = st_arr
    print("   daily correlation gold breakout vs CL fade:", round(float(np.corrcoef(lab.C["GXB"], lab.C["CLS"])[0, 1]), 2),
          "| vs plan:", {k: round(float(np.corrcoef(lab.C["GXB"], lab.C[k])[0, 1]), 2) for k in ("VB", "ONB_ML2_MC", "LDF_MC")})
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    from speed_to_13k import run as speed, fmt
    sp = {}
    for nm, p in (("plan with CL fade 2 MCL", plan), ("+ gold breakout 1 MGC", {**plan, "GXB": 1}), ("+ gold breakout 2 MGC", {**plan, "GXB": 2}),
                  ("+ gold breakout risk $75", {**plan, "GXB": ("risk", 75)}), ("+ gold breakout risk $150", {**plan, "GXB": ("risk", 150)})):
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<30} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
        sp[nm] = speed(lab, p, **CS)
    print(fmt(pd.DataFrame(sp).T))

    print("\n2. FOMC on gold and bitcoin")
    fomc(gc, "GC", 100.0, 7.25 + 2 * 10.0)
    bt = pickle.load(open(SP + "btc.pkl", "rb"))
    fomc(bt, "BTC", 1.0, 25.0 + 2 * 5.0)
