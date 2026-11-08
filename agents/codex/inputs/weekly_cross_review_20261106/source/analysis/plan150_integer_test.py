"""150K funded: whole-number chart inputs (Codex portfolio audit 2026-10-31). The 150K benches used 'plan x 1.5', so three
1-lot pieces had a base of 1.5 (VB flagged, Monday Long, Bridge Monday). The simulator trades floor(base x f) MNQ each day,
so 1.5 traded 1 at f = 1 and 1 at f = 0.75 (1.125), while a chart input of 1 trades 0 at f = 0.75. Risk-sized pieces
(ONB ML, EOS, NFP) are already in dollars, and the others are whole numbers at x 1.5 (VB 3, LDF 3, CL 3, MOC 3).
Plans (bootstrapped funded bench, 500 paired 2-year histories, full size from a $3,000 cushion):
  old x 1.5 (fractional reference) | all 1.5 -> 1 | all 1.5 -> 2 | VB flagged 2, Monday Long / Bridge 1 | + DT 2 -> ST 2 on the best.
  python3 analysis/plan150_integer_test.py SCRATCH_DIR [worker SEED N | merge]
"""
import sys, glob, time, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"
import funded_bootstrap as FB, funded_sim150 as F150, overnight_tick_bench as OTB, swing_target_bench as STB

HALF = ("VB_F", "MON_MC", "MON_BR_MC")


def plans():
    old = STB.plans150()["150K plan"]
    assert {k for k, v in old.items() if not isinstance(v, tuple) and v % 1} == set(HALF), old
    to = lambda **kw: {**old, **kw}
    P = {"old x 1.5 (fractional)": old,
         "all 1.5 -> 1": to(VB_F=1, MON_MC=1, MON_BR_MC=1),
         "all 1.5 -> 2": to(VB_F=2, MON_MC=2, MON_BR_MC=2),
         "VB flagged 2, Mon/Bridge 1": to(VB_F=2, MON_MC=1, MON_BR_MC=1),
         "Mon/Bridge 2, VB flagged 1": to(VB_F=1, MON_MC=2, MON_BR_MC=2)}
    for k, p in P.items():
        assert all(isinstance(v, tuple) or v % 1 == 0 for v in p.values()) or k.startswith("old"), k
    return P


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    if MODE == "worker":
        seed, n = int(sys.argv[3]), int(sys.argv[4])
        lab = OTB.lab_for(150); lab.add("ST", STB.pt_trades(lab.g)); FB.F = F150
        res, y1, _ = FB.Boot(lab).run(plans(), n=n, L=20, seed=seed, ref=3000.0)
        pickle.dump((res, y1), open(SP + f"p150int_boot_{seed}.pkl", "wb")); print(f"[worker {seed} done {time.time() - T0:.0f}s]"); sys.exit()
    pl = plans(); parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + "p150int_boot_*.pkl"))]
    res = {k: np.concatenate([p[0][k] for p in parts]) for k in pl}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in pl}
    B = FB.Boot.__new__(FB.Boot); B.run = lambda *a, **k: (res, y1, 0)
    print(f"\n150K funded, bootstrapped ({len(res[next(iter(pl))])} paired 2-year histories):")
    print(B.compare(pl)[1])
