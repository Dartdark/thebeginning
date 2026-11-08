"""Opposing-position overlap in the funded benches (Codex portfolio audit 2026-10-31; v2 same day after Codex's follow-up).
portfolio.paths marks each trade at its own adverse extreme per minute (longs at the low, shorts at the high) and the benches
sum them, so minutes with NQ longs AND shorts open count the smaller side's range twice: min(long, short) MNQ x range x $2.
v2: CURRENT rosters (50K: T fade 1 in place of RS longs since 10/28, VB 2/1; 150K: whole-number inputs, DT 2), VB flagged
contracts only on flagged days, and a corrected REPLAY: the double-counted amount goes back in as a credit piece (base 100,
W / 100, so it scales with floor(100 f) like the plan) and the bootstrapped bench reruns the plan with and without it.
Overnight Tick is excluded (stored as one whole-night worst on its exit day, also conservative).
  python3 analysis/opposing_overlap_check.py SCRATCH_DIR [worker 50|150 SEED N | merge]
"""
import sys, glob, pickle, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"
import funded_lab as FL
store = {}
_add = FL.Lab.add
def _rec(self, name, trades, *a, **k):
    store[name] = FL.with_slippage(trades) if k.get("slippage", True) else trades
    return _add(self, name, trades, *a, **k)
FL.Lab.add = _rec
import funded_bootstrap as FB, funded_sim as F50, funded_sim150 as F150
import overnight_tick_bench as OTB, swing_target_bench as STB, plan150_integer_test as P150I, t_oneside_bench2 as TOS
from build_lab import REPORTS
from portfolio import load_mc

NQ = {"VB_N", "VB_F", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "MON_BR_MC", "RS", "RS_L", "DT", "T"}


def plan_for(which):
    if which == 50:
        p = {k: v for k, v in STB.plans50()["50K plan"].items() if k != "RS_L"}; p["T"] = 1; return p
    return P150I.plans()["all 1.5 -> 1"]


def build(which):
    store.clear(); lab = OTB.lab_for(which); lab.add("T", TOS.tos_t()); g = lab.g
    for k, (f, _) in REPORTS.items(): store.setdefault(k, FL.with_slippage(load_mc(g, f)))
    plan = plan_for(which); names, b = lab._base(plan)
    D, M = g.o.shape; lo = np.zeros((D, M)); sh = np.zeros((D, M)); pos = {d: i for i, d in enumerate(lab.tr)}
    flagged = np.abs(lab.W["VB_F"]).sum(axis=1) > 0
    for k, bk in zip(names, b):
        if k not in NQ: continue
        t = store["VB" if k in ("VB_N", "VB_F") else k]; q = t["qty"].to_numpy() if "qty" in t else np.ones(len(t))
        for (d, j0, j1, s), qq in zip(t[["day", "j0", "j1", "side"]].to_numpy(int), q):
            i = pos.get(d)
            if i is None or (k == "VB_F" and not flagged[i]): continue
            (lo if s > 0 else sh)[d, j0:j1 + 1] += qq * bk[i]
    both = (lo > 0) & (sh > 0); over = np.minimum(lo, sh) * np.nan_to_num(g.h - g.l) * 2.0
    lab.W["CREDIT"] = over[lab.tr] / 100.0; lab.C["CREDIT"] = np.zeros(len(lab.tr))
    days = both[lab.tr].any(1)
    line = (f"{which}K plan {sorted(plan)}:\n  long+short NQ open together: {both[lab.tr].sum():,} minutes on {days.sum()} of {len(lab.tr)} days; "
            f"double-counted per such minute avg ${over[both].mean():.0f}, worst ${over.max():,.0f}")
    return lab, plan, line


if __name__ == "__main__":
    T0 = time.time()
    if MODE == "worker":
        which, seed, n = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
        lab, plan, line = build(which); FB.F = F50 if which == 50 else F150
        pl = {"bench as run": plan, "overlap corrected": {**plan, "CREDIT": 100}}
        res, y1, _ = FB.Boot(lab).run(pl, n=n, L=20, seed=seed, **({} if which == 50 else dict(ref=3000.0)))
        pickle.dump((res, y1, line), open(SP + f"overlap{which}_boot_{seed}.pkl", "wb")); print(f"[worker {which} {seed} {time.time() - T0:.0f}s]"); sys.exit()
    print(__doc__.split("\n")[0])
    for which in (50, 150):
        parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + f"overlap{which}_boot_*.pkl"))]
        if not parts: continue
        pl = ["bench as run", "overlap corrected"]; print("\n" + parts[0][2])
        res = {k: np.concatenate([p[0][k] for p in parts]) for k in pl}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in pl}
        B = FB.Boot.__new__(FB.Boot); B.run = lambda *a, **k: (res, y1, 0)
        print(B.compare({k: {} for k in pl})[1])
