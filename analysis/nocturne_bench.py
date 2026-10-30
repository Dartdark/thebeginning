"""Nocturne (analysis/nocturne_test.py, N0 = the rule as given, no stop) on the bootstrapped funded benches (user 2026-10-30):
added at 1-2 MNQ and in place of Overnight Tick (our overnight long). 50K = t_oneside_bench2 'RS longs -> T 1';
150K = swing_target_bench 'DT 2 -> ST 2'. Nights booked on the exit day, worst point = the night's lowest open P&L (as OT).
  python3 analysis/nocturne_bench.py SCRATCH_DIR [worker50 SEED N | worker150 SEED N | merge]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"


def add_noc(lab):
    t = pd.read_csv("checks/candidates/nocturne/python_nights.csv", parse_dates=["date"])
    t = t[t["var"] == "N0"].set_index("date")
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); pos = pd.Series(np.arange(len(dates)), index=dates)
    Wd = np.zeros(len(dates)); Cd = np.zeros(len(dates))
    for d, r in t.iterrows():
        if d in pos.index: i = pos[d]; Wd[i] = r.adv; Cd[i] = r.net
    lab.W["NOC"] = Wd[:, None] / 10 * np.ones((1, lab.W["VB"].shape[1])); lab.C["NOC"] = Cd / 10


def plans50():
    import t_oneside_bench2 as TB2
    CUR = TB2.plans50()["RS longs -> T 1"]
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    return {"50K plan (now)": CUR, "+ NOC 1": {**CUR, "NOC": 1}, "+ NOC 2": {**CUR, "NOC": 2}, "OT 1 -> NOC 1": {**drop("OT"), "NOC": 1}}


def plans150():
    import swing_target_bench as STB
    CUR = STB.plans150()["DT 2 -> ST 2"]
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    return {"150K plan (now)": CUR, "+ NOC 1": {**CUR, "NOC": 1}, "+ NOC 2": {**CUR, "NOC": 2}, "OT 2 -> NOC 2": {**drop("OT"), "NOC": 2}}


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    if True:
        import time, glob
        import funded_bootstrap as FB, funded_sim150 as F150, funded_sim as F50
        import overnight_tick_bench as OTB, swing_target_bench as STB, t_oneside_bench2 as TB2
        if MODE != "merge":
            which = 50 if MODE == "worker50" else 150; seed, n = int(sys.argv[3]), int(sys.argv[4]); T0 = time.time()
            lab = OTB.lab_for(which); lab.add("ST", STB.pt_trades(lab.g)); add_noc(lab)
            if which == 50: lab.add("T", TB2.tos_t())
            FB.F = F50 if which == 50 else F150
            pl = plans50() if which == 50 else plans150(); kw = {} if which == 50 else dict(ref=3000.0)
            res, y1, _ = FB.Boot(lab).run(pl, n=n, L=20, seed=seed, **kw)
            pickle.dump((res, y1), open(SP + f"noc{which}_boot_{seed}.pkl", "wb")); print(f"[{MODE} {seed} done {time.time() - T0:.0f}s]")
            if seed == 1:
                ks = [k for k in pl[next(iter(pl))]] + ["NOC"]; print(lab.corr(ks).loc["NOC"].round(2).to_string())
            sys.exit()
        for which, pl in ((50, plans50()), (150, plans150())):
            parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + f"noc{which}_boot_*.pkl"))]
            if not parts: continue
            res = {k: np.concatenate([p[0][k] for p in parts]) for k in pl}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in pl}
            B = FB.Boot.__new__(FB.Boot); B.run = lambda *a, **k: (res, y1, 0)
            print(f"\n{which}K funded, bootstrapped ({len(res[next(iter(pl))])} paired 2-year histories):")
            df, s_, _ = B.compare(pl); print(s_)
        sys.exit()
