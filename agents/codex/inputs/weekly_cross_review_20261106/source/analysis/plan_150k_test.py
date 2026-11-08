"""The plan scaled up on an Apex 150K account (user, 2026-10-15). 150K rules as in analysis/twin_150k_test.py (evaluation
+$9,000 in 21 trading days, $4,000 EOD trailing drawdown locking at $150,100, $2,000 daily loss pause; funded: request at
safety net $154,100 + the payout's cap, 5 days >= $350 since the last payout, 50% consistency, 6 payouts $20,500 with the
ladder 2,500 / 3,000 / 3,000 / 3,000 / 4,000 / 5,000 (Apex, user's screenshots)). Same simulator also run with the 50K rules on the 50K plan
as a check against the funded bench ($10,184 / $12,450, blown 3% / 3%).
  A  evaluation: the 50K combine set x 1.5 / 2 / 2.5 / 3; + Twin cap1 4-8 MNQ; the funded plan x 2-4
  B  funded PA: the current funded plan (VB_N 3 / VB_F 1, ONB ML $400, Monday 1, EOS $700, LDF 2, NFP $500, Bridge Monday 1,
     CL fade 2 MCL) x 1.5 / 2 / 2.5 / 3, cushion sizing (full size from a 1,500 x scale cushion, half below), +/- Twin cap1
Every start day (evaluation 2018-26; funded 1y 2018-25, 2y 2018-24). Payout policy: full-cap payouts (request when the
balance is at safety net + that payout's cap), as in the 50K bench.
  python3 analysis/plan_150k_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import twin_continuation_test as tc
from twin_continuation_bench import grids

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
ONB30 = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx"
R150 = dict(st=150_000.0, dd=4_000.0, dll=2_000.0, lock=150_100.0, tgt=9_000.0, safe=154_100.0, qday=350.0,
            caps=[2500.0, 3000.0, 3000.0, 3000.0, 4000.0, 5000.0])
R50 = dict(st=50_000.0, dd=2_000.0, dll=1_000.0, lock=50_100.0, tgt=3_000.0, safe=52_100.0, qday=250.0,
           caps=[1500.0, 1500.0, 2000.0, 2500.0, 2500.0, 3000.0])


def evaluation(W, R, s, D, r):
    bal = r["st"]; floor = r["st"] - r["dd"]
    for n, d in enumerate(range(s, min(s + 21, D)), 1):
        w, rr = W[d], R[d]; lim = max(floor, bal - r["dll"])
        hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
        win = np.nonzero(bal + rr - r["st"] >= r["tgt"])[0]; jp = win[0] if len(win) else len(w)
        if jp < jb: return "pass", n
        if jb < len(w):
            if lim == floor: return "fail", n
            bal = lim
        else: bal += rr[-1]
        floor = max(floor, min(bal - r["dd"], r["lock"]))
    return ("time", 21) if s + 21 <= D else None


def funded(low, close, s, h, r, ref):
    """low / close: the plan's daily lowest open P&L and close at scale 1; size f = cushion / ref in [0.5, 1]."""
    bal = r["st"]; floor = r["st"] - r["dd"]; n = 0; paid = 0.0; qual = 0; since = 0.0; best = 0.0
    for d in range(s, min(s + h, len(close))):
        f = min(1.0, max(0.5, (bal - floor) / ref)); lo, cl = low[d] * f, close[d] * f
        if bal + lo <= floor: return paid, n, True
        dll = r["dll"] if r["st"] > 60_000 else (1000.0 if bal - r["st"] < 3000 else 2000.0 if bal - r["st"] < 6000 else 3000.0)
        day = -dll if lo <= -dll else cl
        bal += day; since += day; best = max(best, day); qual += day >= r["qday"]
        floor = max(floor, min(bal - r["dd"], r["lock"]))
        if n < 6 and bal >= r["safe"] + r["caps"][n] and qual >= 5 and since > 0 and best < 0.5 * since:
            bal -= r["caps"][n]; paid += r["caps"][n]; n += 1; qual = 0; since = 0.0; best = 0.0
            if n == 6: return paid, n, False
    return paid, n, False


def show_funded(low, close, nm, r, ref, yr, D):
    out = []
    for h in (252, 504):
        st = [s for s in range(D - h) if yr[s] >= 2018]; rr = [funded(low, close, s, h, r, ref) for s in st]
        paid = np.array([x[0] for x in rr]); bl = np.array([x[2] for x in rr]); n6 = np.array([x[1] == 6 for x in rr])
        out.append((paid.mean(), bl.mean(), np.mean(paid > 0), n6.mean()))
    print(f"   {nm:<52} 1y ${out[0][0]:>7,.0f} blown {out[0][1]:>4.0%} paid {out[0][2]:>4.0%} | 2y ${out[1][0]:>7,.0f} blown {out[1][1]:>4.0%} all 6 {out[1][3]:>4.0%}", flush=True)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; atr = g.daily_atr(15); tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year
    # ---- funded plan, combined per-day paths at scale 1 (lab.W: (D, minutes) per MNQ; lab._base gives each day's MNQ)
    dates = pd.DatetimeIndex(g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    PLAN = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    names, b = lab._base(PLAN)
    Wp = sum(b[i][:, None] * lab.W[k] for i, k in enumerate(names)); Cp = sum(b[i] * lab.C[k] for i, k in enumerate(names))
    low_p, close_p = Wp.min(1), Cp
    # Twin cap1 per MNQ on the lab's day index
    B = tc.flatten(g); T = tc.simulate(B, max_stop_mult=1.0); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
    Wt, Rt = grids(g, B, T); Wt, Rt = Wt[lab.tr] / 10, Rt[lab.tr] / 10
    yl = pd.DatetimeIndex(g.ts[lab.tr]).year; Dl = len(lab.tr)

    import funded_sim as F50, funded_sim150 as F150
    lab.W["TWIN"] = Wt; lab.C["TWIN"] = Rt[:, -1]
    def bench(F, plan, ref, nm):
        names, b = lab._base(plan)
        W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names]); out = []
        for h in (250, 500):
            st = np.arange(0, lab.D - h)
            r = F.simulate_sized(W, C, b, horizon=h, starts=st, fmin=0.5, fmax=1.0, ref=ref)
            out.append((r["paid"].mean(), r["blown"].mean(), np.mean(r["paid"] > 0), np.mean(r["payouts"] == 6)))
        print(f"   {nm:<52} 1y ${out[0][0]:>7,.0f} blown {out[0][1]:>4.0%} paid {out[0][2]:>4.0%} | 2y ${out[1][0]:>7,.0f} blown {out[1][1]:>4.0%} all 6 {out[1][3]:>4.0%}", flush=True)
    scale = lambda plan, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in plan.items()}
    print("\nCheck: the exact funded simulator (integer MNQ per strategy) with the 50K rules = the funded bench ($10,184 / $12,450, blown 3% / 3%):")
    bench(F50, PLAN, 1500.0, "50K plan, full size from a $1,500 cushion")
    print("\nB. Funded 150K PA (funded_sim150: same simulator, 150K numbers):")
    for k in (1.5, 2.0, 2.5, 3.0):
        for ref in (1500.0 * k, 3000.0):
            bench(F150, scale(PLAN, k), ref, f"funded plan x {k}, full size from ${ref:,.0f} cushion")
    for k, q in ((2.0, 2), (2.0, 4), (2.5, 2)):
        bench(F150, {**scale(PLAN, k), "TWIN": q}, 1500.0 * k, f"funded plan x {k} + Twin cap1 {q} MNQ")

    print("\nA. 150K evaluation (every start day 2018-26):")
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
        w, r_ = paths(g, t); P[nm] = (w[tr] / 10, r_[tr] / 10)
    rk = lambda dl_, m: np.floor(dl_ / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": rk(1100, 0.25), "MON_BR": 2.0, "EOS": rk(500, REPORTS["EOS"][1])}
    Wc = sum(P[k][0] * q[k] for k in P); Rc = sum(P[k][1] * q[k] for k in P)
    Wt2, Rt2 = grids(g, B, T); Wt2, Rt2 = Wt2[tr] / 10, Rt2[tr] / 10
    def ev(W, R, nm):
        res = [evaluation(W, R, s, D, R150) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
        dd = np.array([x[1] if x else 0 for x in res])
        print(f"   {nm:<52} pass {ps[ok].mean():5.1%} (2018-22 {ps[ok & (yr < 2023)].mean():5.1%}, 2023-26 {ps[ok & (yr >= 2023)].mean():5.1%}) "
              f"blown {(o[ok] == 'fail').mean():5.1%} time {(o[ok] == 'time').mean():5.1%} median days {np.median(dd[ok & ps]) if ps[ok].any() else np.nan:.0f}", flush=True)
    for k in (1.5, 2.0, 2.5, 3.0):
        ev(Wc * k, Rc * k, f"combine set x {k}")
    for k, tq in ((2.0, 4), (2.0, 8), (2.5, 4)):
        ev(Wc * k + Wt2 * tq, Rc * k + Rt2 * tq, f"combine set x {k} + Twin cap1 {tq} MNQ")
