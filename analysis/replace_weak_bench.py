"""Replace a weaker plan strategy with a stronger new one? (user, 2026-10-23: 'ok with more correlation if it makes more money')
Weakest funded-plan pieces by profit and return / drawdown (analysis/personal_portfolio.py): ES MOC (MOC_MES), NFP (NFP_MC),
EOS, Late-Day Flow (LDF_MC). Candidates: FC 2B v2 (MC report), S47 v2 (rebuild), Kusho v9 flat 15:45 (rebuild), 1 MNQ each.
  A. 50K funded bootstrap, 1,000 paired 2-year histories (seeds 1-4 x 250, the same histories as the FC 2B / S47 / Kusho
     benches, so 'plan' matches): each replacement and each slot left empty. Two batches (each < 2 h on 4 cores).
  B. 50K evaluation: combine set with EOS or Bridge Monday replaced by each candidate at 1-3 MNQ.
  python3 analysis/replace_weak_bench.py SCRATCH_DIR worker BATCH SEED N | merge | combine
"""
import sys, time, pickle, glob, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import funded_bootstrap as FB, combine_levers_test as CL

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"
FCREP = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute FC 2B v2.xlsx"
WEAK = {"ES MOC": "MOC_MES", "NFP": "NFP_MC", "EOS": "EOS", "LDF": "LDF_MC"}
CANDS = {"FC 2B": "FC", "S47 v2": "S47", "Kusho v9 15:45": "K9"}


def candidates(g):
    s47 = runpy.run_path("analysis/s47_bench.py", run_name="lib")["s47_trades"](g)
    k9 = runpy.run_path("analysis/kusho_bench.py", run_name="lib")["trades"]("v9_RTH", g)
    fc = with_slippage(load_mc(g, FCREP)); fc = fc[pd.DatetimeIndex(g.ts[fc.day]) >= "2018-01-01"].reset_index(drop=True)
    return {"FC": fc, "S47": s47, "K9": k9}


def plans_for(batch, CUR):
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    p = {"plan": CUR}
    if batch == 1:
        for wn, wk in WEAK.items(): p[f"  {wn} slot empty"] = drop(wk)
        for wn, wk in WEAK.items(): p[f"{wn} -> FC 2B 1"] = {**drop(wk), "FC": 1}
    else:
        for cn in ("S47 v2", "Kusho v9 15:45"):
            for wn, wk in WEAK.items(): p[f"{wn} -> {cn} 1"] = {**drop(wk), CANDS[cn]: 1}
    return p


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    if MODE in ("worker", "merge"):
        fast_plan_lab = runpy.run_path("analysis/fc_2b_bench.py", run_name="lib")["fast_plan_lab"]
        lab = fast_plan_lab(SP); FB.add_moc_mes(lab, SP)
        rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map({"stop": 0, "target": 1, "flat": 2})
        lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
        for k, t in candidates(lab.g).items(): lab.add(k, t, slippage=False)
        CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
    if MODE == "worker":
        batch, seed, n = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
        res, y1, _ = FB.Boot(lab).run(plans_for(batch, CUR), n=n, L=20, seed=seed)
        pickle.dump((res, y1), open(SP + f"rw_boot_{batch}_{seed}.pkl", "wb")); print(f"[worker {batch}/{seed} done {time.time() - T0:.0f}s]"); sys.exit()
    if MODE == "merge":
        res, y1 = {}, {}
        for batch in (1, 2):
            parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + f"rw_boot_{batch}_*.pkl"))]
            if not parts: continue
            for k in plans_for(batch, CUR):
                res[k] = np.concatenate([p[0][k] for p in parts]); y1[k] = np.concatenate([p[1][k] for p in parts])
        B = FB.Boot(lab); B.run = lambda *a, **k: (res, y1, 0)
        print(f"\nA. 50K funded, bootstrapped ({len(res['plan'])} paired histories, 2 years):")
        df, s_, _ = B.compare({k: None for k in res}); print(s_)
        sys.exit()
    print("\nB. 50K evaluation: replace EOS or Bridge Monday in the combine set")
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))), *candidates(g).items()):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    one = lambda p, c, n: 1.0
    cases = [("combine set", q)] + [(f"  {w} slot empty", {a: b for a, b in q.items() if a != w}) for w in ("EOS", "MON_BR")]
    for w, wn in (("EOS", "EOS"), ("MON_BR", "Bridge")):
        for cn, ck in CANDS.items():
            for k in (1, 2, 3): cases.append((f"{wn} -> {cn} {k}", {**{a: b for a, b in q.items() if a != w}, ck: float(k)}))
    for nm, qq in cases:
        W = sum(P[x][0] * qq[x] for x in qq); Rr = sum(P[x][1] * qq[x] for x in qq)
        res = [CL.challenge(W, Rr, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); n = np.array([x[1] if x else 0 for x in res])
        ps = ok & (o == "pass")
        print(f"   {nm:<28} pass {ps.sum() / ok.sum():5.1%} (18-22 {ps[ok & (yr < 2023)].sum() / (ok & (yr < 2023)).sum():5.1%}, "
              f"23-26 {ps[ok & (yr >= 2023)].sum() / (ok & (yr >= 2023)).sum():5.1%}) | median days {np.median(n[ps]):.0f}", flush=True)
