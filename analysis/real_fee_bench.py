"""Real micro fees on the Apex benches (2026-10-24; cross-review 2026-10-23 open routine item, Codex's cost qualification).
The benches charge $7.25 per NQ scaled to micros = $0.725 per MNQ round trip (MES $0.50, MCL $0.725). The live Apex fills
cost more: 10/19 8 MNQ $8.66 ($1.08 per round trip), 10/21 2 x 8 MNQ $15.82 ($0.99) (live/orders_20261020_21.md, Apex
dashboard). Assumed real fee: $1.04 per micro round trip (MNQ / MES / MCL alike); sensitivity $1.24. Slippage unchanged
(1 tick per market / stop fill). Fewer-trade pieces lose less, so this can shift close add / replace calls.
  A. 50K evaluation (combine set VB 8, ONB ADX30 $1,100, Bridge Monday 2, EOS $500): pass rate at bench / real fees.
  B. 50K funded, bootstrapped (1,000 paired 2-year histories, seeds 1-4 x 250 = the replace-weak / FC 2B benches'
     histories, so 'plan @ bench' must match those outputs): the current plan and the past decisions that were within
     ~$60 of the plan (EOS -> FC 2B / Kusho / S47, + FC 2B, RS longs -> FC 2B, EOS / RS slots empty) at $1.04.
  python3 analysis/real_fee_bench.py SCRATCH_DIR combine | worker SEED N | merge
"""
import sys, time, pickle, glob, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import portfolio
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import funded_bootstrap as FB, combine_levers_test as CL

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"
BENCH = {"micro": 0.725, "MOC_MES": 0.50}
FEES = (1.04, 1.24)


def combine():
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year
    T = {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, CL.ONB30)),
         "MON_BR": load_bridge_mc(g), "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    one = lambda p, c, n: 1.0
    print("\nA. 50K evaluation, combine set, every start day 2018-2026")
    for fee in (BENCH["micro"],) + FEES:
        portfolio.COST = fee * 10                                  # paths() reads the module's COST ($ per NQ)
        P = {k: tuple(x[trr] / 10 for x in paths(g, t)) for k, t in T.items()}
        W = sum(P[k][0] * q[k] for k in q); R = sum(P[k][1] * q[k] for k in q)
        res = [CL.challenge(W, R, np.arange(s, min(s + CL.MAXD, D)), one) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res])
        n = np.array([x[1] if x else 0 for x in res]); ps = ok & (o == "pass")
        fr = lambda m: ps[ok & m].sum() / (ok & m).sum()
        print(f"   fee ${fee:.3f} per MNQ: pass {fr(yr > 0):5.1%} (18-22 {fr(yr < 2023):5.1%}, 23-26 {fr(yr >= 2023):5.1%}), "
              f"blown {(o[ok] == 'fail').mean():5.1%}, median days {np.median(n[ps]):.0f}")
    portfolio.COST = BENCH["micro"] * 10


def lab_with_fees():
    """The replace-weak bench's lab (plan + candidates), plus a '|f' copy of every piece at each real fee."""
    rw = runpy.run_path("analysis/replace_weak_bench.py", run_name="lib")
    lab = runpy.run_path("analysis/fc_2b_bench.py", run_name="lib")["fast_plan_lab"](SP); FB.add_moc_mes(lab, SP)
    rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map({"stop": 0, "target": 1, "flat": 2})
    lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
    for k, t in rw["candidates"](lab.g).items(): lab.add(k, t, slippage=False)
    S = pd.read_pickle(SP + "single_print_sessions.pkl")
    flag = S.flag.reindex(pd.DatetimeIndex(lab.g.ts[lab.tr])).fillna(False).to_numpy().astype(bool)
    for k, m in (("VB_F", flag), ("VB_N", ~flag)):                 # VB split keeps VB's trade counts
        lab.N[k] = lab.N["VB"] * m; lab.J0[k] = lab.J0["VB"]
    keys = ["VB_N", "VB_F", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "MON_BR_MC", "CLS", "MOC_MES", "RS_L", "FC", "S47", "K9"]
    total = {}
    for i, fee in enumerate(FEES):
        for k in keys:
            nk = f"{k}|{i}"; lab.W[nk] = lab.W[k].copy(); lab.C[nk] = lab.C[k].copy()
            if k in lab.N: lab.N[nk] = lab.N[k]; lab.J0[nk] = lab.J0[k]
            if k in lab.stop: lab.stop[nk] = lab.stop[k]
            total[nk] = lab.real_fees(fee - BENCH["MOC_MES" if k == "MOC_MES" else "micro"], [nk])[nk]
    return lab, total


def plans():
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
    drop = lambda p, *ks: {k: v for k, v in p.items() if k not in ks}
    base = {"plan": CUR, "EOS slot empty": drop(CUR, "EOS"), "RS longs slot empty": drop(CUR, "RS_L"), "EOS -> FC 2B 1": {**drop(CUR, "EOS"), "FC": 1},
            "EOS -> Kusho v9 1": {**drop(CUR, "EOS"), "K9": 1}, "EOS -> S47 v2 1": {**drop(CUR, "EOS"), "S47": 1},
            "+ FC 2B 1": {**CUR, "FC": 1},
            "RS longs -> FC 2B 1": {**drop(CUR, "RS_L"), "FC": 1}}
    out = {"plan @ bench fee": CUR}
    for i, fee in enumerate(FEES):
        for nm, p in base.items():
            if i == 1 and nm != "plan": continue                    # $1.24: the plan's absolute figures only
            out[f"{nm} @ ${fee:.2f}"] = {f"{k}|{i}": v for k, v in p.items()}
    return out


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    if MODE == "combine": combine(); sys.exit()
    lab, total = lab_with_fees()
    if MODE == "worker":
        seed, n = int(sys.argv[3]), int(sys.argv[4]); only = sys.argv[5].split(",") if len(sys.argv) > 5 else None
        pl = {k: v for k, v in plans().items() if only is None or any(o in k for o in only)}
        res, y1, _ = FB.Boot(lab).run(pl, n=n, L=20, seed=seed)       # a plan's result depends only on its own pieces
        pickle.dump((res, y1), open(SP + f"rf_boot_{seed}{'_redo' if only else ''}.pkl", "wb")); print(f"[worker {seed} done {time.time() - T0:.0f}s]"); sys.exit()
    yrs = len(lab.tr) / 252
    print("\nExtra fees at $1.04 per micro, $ per 1 micro per year (2018-2026):",
          {k.split("|")[0]: round(v / yrs) for k, v in total.items() if k.endswith("|0")})
    parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + "rf_boot_[0-9].pkl"))]
    for s_ in range(len(parts)):              # plans rerun after the 2026-10-24 S47 / Kusho grid-row fix replace the old rows
        f = SP + f"rf_boot_{s_ + 1}_redo.pkl"
        if glob.glob(f): r2 = pickle.load(open(f, "rb")); parts[s_][0].update(r2[0]); parts[s_][1].update(r2[1])
    res = {k: np.concatenate([p[0][k] for p in parts]) for k in plans()}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in plans()}
    B = FB.Boot(lab); B.run = lambda *a, **k: (res, y1, 0)
    for i, fee in enumerate(FEES):
        sub = {k: None for k in res if k.endswith(f"@ ${fee:.2f}")}
        print(f"\nB. 50K funded, bootstrapped ({len(res['plan @ bench fee'])} paired histories, 2 years), real fee ${fee:.2f} per micro:")
        df, s_, _ = B.compare(sub, base=f"plan @ ${fee:.2f}"); print(s_)
    print("\n   plan at bench vs real fees:")
    df, s_, _ = B.compare({k: None for k in res if k.startswith("plan")}, base="plan @ bench fee"); print(s_)
