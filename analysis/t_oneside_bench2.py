"""T_ONESIDE fade (T only, the note's stop) re-benched against the CURRENT funded plans (2026-10-28; first bench
analysis/t_oneside_bench.py ran on the 10/24 plan, before Overnight Tick replaced the Monday Long and Swing Target came in).
Bootstrapped bench (funded_bootstrap, paired 2-year histories, 20-day blocks), MNQ = NQ / 10, our costs.
  50K funded now: VB 1/1, ONB ML $400, OT 1, EOS, LDF, NFP, Bridge 1, CL, ES MOC 2, RS longs 1, ST 1.
     + T 1 / 2 MNQ; T in place of OT (closest window: night -> morning), of ONB ML, of RS longs.
  150K funded now: plan x 1.5 + RS 1 + OT 2 + ST 2 (Dual Thrust out).  + T 1 / 2 / 3; OT 2 -> T 2.
  The evaluation set has not changed since the first bench (no gain there), so it is not rerun.
  python3 analysis/t_oneside_bench2.py SCRATCH_DIR [worker50 SEED N | worker150 SEED N | merge]
"""
import sys, glob, time, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"
import funded_bootstrap as FB, funded_sim150 as F150, funded_sim as F50
import overnight_tick_bench as OTB, swing_target_bench as STB


def tos_t():
    t = pd.read_csv(SP + "t_oneside_stop.csv", parse_dates=["date"])
    t = t[(t.date >= "2018-01-01") & (t.cell == "T")].reset_index(drop=True)
    return t[["day", "j0", "j1", "side", "entry", "exit", "kind"]]


def plans50():
    p = STB.plans50(); CUR = p["VB 2/1 -> 1/1 + ST 1"]
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    return {"50K plan (now)": CUR, "+ T 1 MNQ": {**CUR, "T": 1}, "+ T 2 MNQ": {**CUR, "T": 2},
            "OT 1 -> T 1": {**drop("OT"), "T": 1}, "ONB ML -> T 2": {**drop("ONB_ML2_MC"), "T": 2},
            "RS longs -> T 1": {**drop("RS_L"), "T": 1}}


def plans150():
    p = STB.plans150(); CUR = p["DT 2 -> ST 2"]
    nool = {k: v for k, v in CUR.items() if k != "OT"}
    return {"150K plan (now)": CUR, "+ T 1 MNQ": {**CUR, "T": 1}, "+ T 2 MNQ": {**CUR, "T": 2}, "+ T 3 MNQ": {**CUR, "T": 3},
            "OT 2 -> T 2": {**nool, "T": 2}}


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    if MODE in ("worker50", "worker150"):
        which = 50 if MODE == "worker50" else 150; seed, n = int(sys.argv[3]), int(sys.argv[4])
        lab = OTB.lab_for(which); lab.add("ST", STB.pt_trades(lab.g)); lab.add("T", tos_t())
        FB.F = F50 if which == 50 else F150
        pl = plans50() if which == 50 else plans150(); kw = {} if which == 50 else dict(ref=3000.0)
        res, y1, _ = FB.Boot(lab).run(pl, n=n, L=20, seed=seed, **kw)
        pickle.dump((res, y1), open(SP + f"tos2_{which}_boot_{seed}.pkl", "wb")); print(f"[{MODE} {seed} done {time.time() - T0:.0f}s]")
        if seed == 1:
            ks = [k for k in pl[next(iter(pl))]] + ["T"]
            print(lab.corr(ks).loc["T"].round(2).to_string())
        sys.exit()
    for which, pl in ((50, plans50()), (150, plans150())):
        parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + f"tos2_{which}_boot_*.pkl"))]
        if not parts: continue
        res = {k: np.concatenate([p[0][k] for p in parts]) for k in pl}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in pl}
        B = FB.Boot.__new__(FB.Boot); B.run = lambda *a, **k: (res, y1, 0)
        print(f"\n{which}K funded, bootstrapped ({len(res[next(iter(pl))])} paired 2-year histories):")
        df, s_, _ = B.compare(pl); print(s_)
