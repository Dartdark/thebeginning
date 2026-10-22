"""Relative Strength NQ / ES in the funded plan (2026-10-20): add or replace, on the bootstrapped bench (funded_bootstrap).
Trades = the Python rebuild (analysis/relative_strength_test.py; run it first, it writes SCRATCH/rs_trades.csv), sized in
MNQ. Plan = the current funded plan (VB 2 / 1 + ES MOC 2 MES). Every replacement is shown next to the same slot left
EMPTY (LESSONS.md), so a 'gain' that only comes from removing risk is visible.
  python3 analysis/relative_strength_bench.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import pandas as pd
import funded_bootstrap as FB

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
KIND = {"stop": 0, "target": 1, "flat": 2}

if __name__ == "__main__":
    lab = FB.plan_lab(SP); FB.add_moc_mes(lab, SP)
    t = pd.read_csv(SP + "rs_trades.csv"); t["kind"] = t.kind.map(KIND)
    lab.add("RS", t); lab.add("RS_L", t[t.side > 0].reset_index(drop=True))
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2}
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    plans = {"plan": CUR, "+ RS 1 MNQ": {**CUR, "RS": 1}, "+ RS 2 MNQ": {**CUR, "RS": 2}, "+ RS longs 1 MNQ": {**CUR, "RS_L": 1},
             "ONB ML -> RS 1": {**drop("ONB_ML2_MC"), "RS": 1}, "  ONB ML slot empty": drop("ONB_ML2_MC"),
             "VB -> RS 1": {**drop("VB_N", "VB_F"), "RS": 1}, "  VB slot empty": drop("VB_N", "VB_F"),
             "NFP -> RS 1": {**drop("NFP_MC"), "RS": 1}, "  NFP slot empty": drop("NFP_MC"),
             "MON -> RS 1": {**drop("MON_MC"), "RS": 1}, "  MON slot empty": drop("MON_MC")}
    B = FB.Boot(lab)
    print("Single-history bench (1y / 2y payouts, blown):")
    for nm, p in plans.items():
        a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
        print(f"   {nm:<22} ${a['expected']:7,.0f} / ${c['expected']:7,.0f}  blown {a['blown']:.0%} / {c['blown']:.0%}")
    print("\nBootstrapped bench (1,000 paired histories, 20-day blocks, 2 years):")
    df, s, _ = B.compare(plans, n=1000, L=20); print(s)
    print("\nDaily correlation of RS with the plan pieces:")
    print(lab.corr(["RS"] + [k for k in CUR]).loc["RS"].round(2).to_string())
