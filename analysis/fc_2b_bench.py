"""FC 2B v2 (user's MultiCharts strategy, 2026-10-23) in the Apex plans: add or replace.
Trades = the user's MultiCharts v2 report (holiday flatten 11:30, entry-bar stop), loaded with portfolio.load_mc, our costs
($7.25 + 1 tick per market / stop fill), sized in MNQ.
  A. 50K funded, bootstrapped bench (funded_bootstrap, 1,000 paired 2-year histories, 20-day blocks): current plan
     (VB 2 / 1, ONB ML $400, MON 1, EOS $700, LDF 2, NFP $500, Bridge 1, CL Sunday 2 MCL, ES MOC 2 MES, RS longs 1)
     + FC 2B 1 / 2 MNQ, longs only; and FC 2B in place of RS longs (next to that slot left empty).
  B. 50K evaluation: combine set (VB 8, ONB ADX30 $1,100, Bridge Monday 2, EOS $500) + FC 2B 1-3 MNQ
     (combine_levers_test.challenge: +$3,000 target, $2,000 EOD trail, $1,000 daily limit).
  python3 analysis/fc_2b_bench.py [SCRATCH_DIR]     (needs single_print_sessions.pkl, rs_trades.csv, s_rank_gap2.pkl)
"""
import sys, time, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import funded_bootstrap as FB, combine_levers_test as CL
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
KIND = {"stop": 0, "target": 1, "flat": 2}
REP = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute FC 2B v2.xlsx"


def fast_plan_lab(sp):
    """FB.plan_lab without the CL bench's own scoring runs (which take hours): lab.pkl + Bridge Monday + the CL Sunday fade
    (same construction as analysis/cl_sunday_fade_bench.py) + VB split by the single-print flag."""
    from cl_forced_flows_test import load
    from bridge_monday_confirm import load_bridge_mc
    PVc, TK, CM, STOP, EXIT_CT, ENTRY_T = 1000.0, 0.01, 7.25, 0.75, 900, 1706
    cl = load("CL"); fr = pickle.load(open(sp + "s_rank_gap2.pkl", "rb"))["frames"]["CL"]
    O, H, C = cl.o.ravel(), cl.h.ravel(), pd.Series(cl.c.ravel()).ffill().to_numpy(); rows = []
    for r in fr.itertuples():
        if not r.ok or not (r.gA >= 0.1): continue
        e_i = int(r.sun) * 1440 + jof(ENTRY_T); x_i = int(r.mon) * 1440 + jof(EXIT_CT)
        if np.isnan(O[e_i]): continue
        e = O[e_i] - TK; px = C[x_i] + TK; spx = e + STOP * r.atr; jx = x_i
        hit = np.where(H[e_i:x_i + 1] >= spx)[0]
        if len(hit): jx = e_i + hit[0]; px = (spx if jx == e_i or np.isnan(O[jx]) else max(O[jx], spx)) + TK
        rows.append(dict(date=pd.Timestamp(cl.ts[int(r.mon)]), net=(e - px) * PVc - CM, adv=min((e - np.nanmax(H[e_i:jx + 1])) * PVc - CM, (e - px) * PVc - CM)))
    t = pd.DataFrame(rows).set_index("date")
    lab = pickle.load(open(sp + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(lab.g), slippage=False)
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); pos = pd.Series(np.arange(len(dates)), index=dates)
    Wd = np.zeros(len(dates)); Cd = np.zeros(len(dates))
    for d, r in t.iterrows():
        if d in pos.index: i = pos[d]; Wd[i] = min(r.adv, r.net); Cd[i] = r.net
    lab.W["CLS"] = Wd[:, None] / 10 * np.ones((1, lab.W["VB"].shape[1])); lab.C["CLS"] = Cd / 10
    S = pd.read_pickle(sp + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    print(f"[CL fade trades {len(t)}, avg ${t.net.mean():.0f} per CL]")
    return lab

if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    lab = fast_plan_lab(SP); print(f"[plan lab {time.time() - T0:.0f}s]"); FB.add_moc_mes(lab, SP)
    rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map(KIND)
    lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
    fc = load_mc(lab.g, REP); fc = fc[pd.DatetimeIndex(lab.g.ts[fc.day]) >= "2018-01-01"].reset_index(drop=True)
    print(f"FC 2B trades loaded: {len(fc)}")
    lab.add("FC", fc); lab.add("FC_L", fc[fc.side > 0].reset_index(drop=True))
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    plans = {"plan": CUR, "+ FC 2B 1 MNQ": {**CUR, "FC": 1}, "+ FC 2B 2 MNQ": {**CUR, "FC": 2},
             "+ FC 2B longs 1 MNQ": {**CUR, "FC_L": 1},
             "RS longs -> FC 2B 1": {**drop("RS_L"), "FC": 1}, "RS longs -> FC 2B longs 1": {**drop("RS_L"), "FC_L": 1},
             "  RS longs slot empty": drop("RS_L")}
    print("\nA. 50K funded, bootstrapped (1,000 paired histories, 20-day blocks, 2 years; single-history bench skipped):")
    B = FB.Boot(lab); df, s, _ = B.compare(plans, n=1000, L=20); print(s); print(f"[bootstrap {time.time() - T0:.0f}s]")
    print("\n   Daily correlation of FC 2B with the plan pieces:")
    print(lab.corr(["FC"] + list(CUR)).loc["FC"].round(2).to_string())

    print("\nB. 50K evaluation (combine set + FC 2B):")
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))),
                  ("FC", with_slippage(load_mc(g, REP)))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    one = lambda p, c, n: 1.0
    for k in (0, 1, 2, 3):
        qq = {**q, "FC": float(k)}
        W = sum(P[x][0] * qq[x] for x in qq); Rr = sum(P[x][1] * qq[x] for x in qq)
        res = [CL.challenge(W, Rr, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
        print(f"   combine set + FC 2B {k} MNQ: pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, "
              f"23-26 {ps[ok & (yr >= 2023)].mean():5.1%})")
