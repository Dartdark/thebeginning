"""Cushion cap on the funded (Apex 50K PA) plan (user 2026-11-08; evaluation result in cushion_cap_bench_output.txt).
Plan = funded_bootstrap.PLAN without the CL Sunday fade (its MCL data chain was not rebuilt this session; small piece).
Same simulator as funded_sim.run_pa_sized (cushion sizing f = cushion / $1,500 in [0.5, 1], payout rules, DLL), plus:
each day, after f, piece k trades min(q, floor((cushion - buffer - used) / stop_k)) MNQ; stop_k = its stop per MNQ
(VB 75 pts = $150; risk-sized pieces their ATR stop; Bridge Monday Long has none: exempt).
  per-piece: used = 0 (each stop alone fits); combined: used += the stops already placed that day (plan order).
Bench: (1) every start day 2018+, one history; (2) 1,000 paired block-bootstrap histories (L 20), 2 years.
  tools/run_stamped.sh analysis/cushion_cap_funded.py > analysis/outputs/cushion_cap_funded_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from numba import njit
import funded_sim as F
from funded_bootstrap import PLAN

START, MLL, LOCK, SAFETY, CAPS, MIN_DAY, MIN_DAYS = F.START, F.MLL, F.LOCK, F.SAFETY, np.asarray(F.CAPS, float), F.MIN_DAY, F.MIN_DAYS
_dll = F._dll


@njit(cache=True)
def run_cap(W, C, base, S, s, horizon, fmin, fmax, ref, buf, mode):
    K, D, M = W.shape
    bal = START; floor = START - MLL; cyc = START; best = 0.0; qual = 0; paid = 0.0; n = 0; first = -1; capped = 0
    end = min(D, s + horizon); q = np.zeros(K)
    for d in range(s, end):
        f = min(max((bal - floor) / ref, fmin), fmax)
        room = bal - floor - buf; anyq = False
        for k in range(K):
            q[k] = np.floor(base[k, d] * f + 1e-9)
            if mode > 0 and q[k] > 0 and S[k, d] > 0:
                fit = np.floor(max(room, 0.0) / S[k, d])
                if fit < q[k]:
                    q[k] = fit; capped += 1
                if mode == 2: room -= q[k] * S[k, d]
            if q[k] > 0: anyq = True
        if not anyq: continue
        dll = _dll(bal); lim = max(floor, bal - dll); low = 0.0
        for j in range(M):
            x = 0.0
            for k in range(K):
                if q[k] > 0: x += q[k] * W[k, d, j]
            if x < low: low = x
        if bal + low <= lim:
            if floor >= bal - dll: return paid, n, d - s + 1, 1, first, capped
            pnl = -dll
        else:
            pnl = 0.0
            for k in range(K): pnl += q[k] * C[k, d]
        bal += pnl
        if pnl >= MIN_DAY: qual += 1
        if pnl > best: best = pnl
        if floor < LOCK: floor = max(floor, min(bal - MLL, LOCK))
        prof = bal - cyc; cap = CAPS[n]
        if qual >= MIN_DAYS and bal - SAFETY >= cap and prof > 0 and best < 0.5 * prof:
            bal -= cap; paid += cap; n += 1
            if first < 0: first = d - s + 1
            if n == 6: return paid, n, d - s + 1, 0, first, capped
            cyc = bal; best = 0.0; qual = 0
    return paid, n, end - s, 0, first, capped


def sim(W, C, base, S, starts, H, buf, mode):
    return np.array([run_cap(W, C, base, S, int(s), H, 0.5, 1.0, 1500.0, buf, mode) for s in starts])


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    lab = pickle.load(open("scratch_data/lab.pkl", "rb"))
    S_ = pd.read_pickle("scratch_data/single_print_sessions.pkl"); dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    flag = S_.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    plan = {k: v for k, v in PLAN.items() if k != "CLS"}
    if len(sys.argv) > 1: plan["VB_N"] = int(sys.argv[1])   # FUNDED_PLAN: NumContracts 2 since 2026-10-17 (PLAN in funded_bootstrap still says 3)
    order = ["ONB_ML2_MC", "VB_N", "VB_F", "EOS", "NFP_MC", "LDF_MC", "MON_MC", "MON_BR_MC"]
    names, b = lab._base(plan); ix = [names.index(k) for k in order]; names = [names[i] for i in ix]; base = b[ix]
    W = np.ascontiguousarray(np.stack([lab.W[k] for k in names])); C = np.ascontiguousarray(np.stack([lab.C[k] for k in names]))
    S = np.zeros_like(base)
    for i, k in enumerate(names):
        if k in ("VB_N", "VB_F"): S[i] = 150.0
        elif k in lab.stop: S[i] = lab.stop[k] * 2.0
    print("   plan (without CLS):", plan)
    V = (("plan (no cap)", 0, 0.0), ("per-piece cap, buffer $0", 1, 0.0), ("per-piece cap, buffer $200", 1, 200.0),
         ("combined cap, buffer $0", 2, 0.0), ("combined cap, buffer $200", 2, 200.0))
    yr = lab.yr
    for H, lab_h in ((250, "1 year"), (500, "2 years")):
        st = np.arange(np.searchsorted(dates, pd.Timestamp("2018-01-01")), lab.D - H)
        print(f"\n1. Every start day 2018+, {lab_h}:")
        for nm, mode, buf in V:
            r = sim(W, C, base, S, st, H, buf, mode)
            print(f"   {nm:<30} payouts ${r[:, 0].mean():7,.0f} (2018-22 ${r[yr[st] < 2023, 0].mean():6,.0f} / 2023+ ${r[yr[st] >= 2023, 0].mean():6,.0f})"
                  f"  blown {r[:, 3].mean():5.1%}  all 6 {np.mean(r[:, 1] == 6):5.1%}  capped days/acct {r[:, 5].mean():4.1f}", flush=True)
    print("\n2. 1,000 paired bootstrap histories (blocks of 20 days, 2 years):")
    days = np.where(dates >= "2018-01-01")[0]; rng = np.random.default_rng(1); n, H, L = 1000, 500, 20
    stb = rng.integers(0, len(days), (n, H // L)); hist = days[((stb[:, :, None] + np.arange(L)) % len(days)).reshape(n, -1)]
    R = {nm: np.zeros((n, 6)) for nm, _, _ in V}
    for h in range(n):
        ixh = hist[h]; Wh = np.ascontiguousarray(W[:, ixh]); Ch = np.ascontiguousarray(C[:, ixh])
        bh = np.ascontiguousarray(base[:, ixh]); Sh = np.ascontiguousarray(S[:, ixh])
        for nm, mode, buf in V: R[nm][h] = run_cap(Wh, Ch, bh, Sh, 0, H, 0.5, 1.0, 1500.0, buf, mode)
    b0 = R["plan (no cap)"][:, 0]
    for nm, _, _ in V:
        r = R[nm]
        print(f"   {nm:<30} 2y payouts ${r[:, 0].mean():7,.0f} (p5 ${np.percentile(r[:, 0], 5):6,.0f})  blown {r[:, 3].mean():5.1%}"
              f"  all 6 {np.mean(r[:, 1] == 6):5.1%}  beats plan {np.mean(r[:, 0] > b0) + 0.5 * np.mean(r[:, 0] == b0):5.1%}"
              f"  diff ${(r[:, 0] - b0).mean():+6,.0f}")
