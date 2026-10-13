"""VWAP Pullback + ADX gate, risk-sizing v4 ("C.S." profile; the Bridge's OFB_VwapPullbackADX, user's paste), 2026-10-13.

Core = the VWAP pullback already tested (analysis/vwap_orb_pullback_test.py, F): 8:31-9:00 CT opening range, a
close beyond it latches the side, VWAP from 8:31 (H+L+C)/3 x volume, touch then reclaim close -> next bar at
market; stop = last confirmed 20-bar swing pivot, target = last confirmed 5-bar swing pivot; 1 trade a day,
day reset 23:00. New in this profile: the ADX gate on the signal bar, ADX(14) of the 1-minute bars >= 20 AND
ADX <= its previous bar (falling); the gate delays, it doesn't cancel. Long only. Entries 9:01-17:00, flat at the
15:55 bar (market). Per NQ after $7.25 + 1 tick per market / stop fill (target = limit).
  python3 analysis/vwap_pullback_adx_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import vwap_orb_pullback_test as V
from candidates import adx
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    s = V.series(g)
    sh, sl = V.pivots(s["h"], s["l"], 20); th, tl = V.pivots(s["h"], s["l"], 5)
    A = adx(s["h"], s["l"], s["c"], 14); Ap = np.r_[np.nan, A[:-1]]
    gates = {"ADX >= 20 and falling (C.S. profile)": (A >= 20) & (A <= Ap), "ADX >= 20 only": A >= 20,
             "ADX falling only": A <= Ap, "no gate": None, "ADX >= 25 and falling": (A >= 25) & (A <= Ap),
             "ADX < 20 (gate inverted)": A < 20}
    print(__doc__.split("\n")[0])
    run = lambda gate, **kw: V.run(g, s, sh, sl, th, tl, apex=True, end_entry=1700, gate=gate, **{"shorts": False, **kw})
    base = run(gates["ADX >= 20 and falling (C.S. profile)"])
    print("\n1. The C.S. profile (long only, ADX >= 20 and falling, flat 15:55):")
    print(V.line(base, "C.S. profile"))
    print("   by year:", base.groupby(base.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print(f"   exits: target {np.mean(base.kind == 1):.0%}; trades a year {len(base) / base.date.dt.year.nunique():.0f}")
    pl = [run(gates["ADX >= 20 and falling (C.S. profile)"], rand=r).net.mean() for r in range(10)]
    print(f"   placebo (same entry bars, random side, mirrored stop / target, 10 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f})")

    print("\n2. Gate variants (long only) and the short side:")
    R_ = {}
    for nm, gt in gates.items():
        R_[nm] = run(gt); print(V.line(R_[nm], nm))
    sho = run(gates["ADX >= 20 and falling (C.S. profile)"], longs=False, shorts=True)
    print(V.line(sho, "shorts with the C.S. gate"))
    print(V.line(run(gates["ADX >= 20 and falling (C.S. profile)"], minrr=1.0), "C.S. + MinRR 1"))
    print(V.line(run(gates["ADX >= 20 and falling (C.S. profile)"], stopmode=2), "C.S. + StopMode 2 (pullback low)"))

    # the gate as a placebo: random gates that pass the same share of bars
    share = np.nanmean(gates["ADX >= 20 and falling (C.S. profile)"])
    rg = [run(np.random.default_rng(r).random(len(A)) < share).net.mean() for r in range(10)]
    print(f"   random gate passing the same {share:.0%} of bars (10 runs): ${np.mean(rg):.0f} ({min(rg):.0f}..{max(rg):.0f}) vs ${base.net.mean():.0f}")

    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print("\n3. Standard metrics per NQ:")
    rows = {"C.S. longs": (dl(base), base.net), "no gate longs": (dl(R_["no gate"]), R_["no gate"].net), "shorts (gated)": (dl(sho), sho.net)}
    print(M.table(rows))
    bt, pm = R.report({f"{k} 2023+": v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}, n=3000); print(bt); print(pm)

    print("\n4. Funded bench (8-strategy plan):")
    from bridge_monday_confirm import load_bridge_mc
    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    b2 = base[base.j1 >= base.j0].copy(); lab.add("VPA", b2, slippage=False)
    dts = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts.year >= 2018
    C = pd.DataFrame({k: lab.daily(k) for k in ("VPA", "VB", "ONB_ML2_MC", "MON_MC", "LDF_MC")}, index=dts)[mk]
    print("   correlation:", C.corr().round(2).loc["VPA"].drop("VPA").to_dict())
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500),
            "VCS_MC": 1, "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    for nm, p in (("current plan", plan), ("+ VWAP Pullback ADX 1 MNQ", {**plan, "VPA": 1}), ("+ 2 MNQ", {**plan, "VPA": 2})):
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<28} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
