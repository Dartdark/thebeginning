"""Replacement sweep (user, 2026-10-18): can any tested candidate (watchlist, B / C tier, recent papers) REPLACE a plan
strategy, wholly or in part, and serve the funded plan better? Plan = current funded plan (VB 2 / 1, ES MOC 2 MES).
Stage 1 (screen, single-history funded bench, every start day, 2-year horizon, cushion sizing): for each plan piece P and
  candidate X at each size: plan − P + X, against plan − P with nothing in its place (the control: a swap only counts if
  X beats leaving the slot empty) and against the current plan.
Stage 2 (decision): the best swaps on the bootstrapped bench (1,000 paired 2-year histories, L 20) with their controls.
Candidates: trade lists harvested from their own scripts (analysis/replacement_harvest.py -> scratch_data/repl_*.pkl),
  plus noise-band (Chuk 2026), NQ MOC follow (WATCHLIST #10), Overnight Drift, Vol-Control Sell (already in the lab).
  python3 analysis/replacement_sweep.py [SCRATCH_DIR]
"""
import sys, glob, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import funded_bootstrap as FB
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
lab = FB.add_moc_mes(FB.plan_lab(SP), SP)
g = lab.g; dates = pd.DatetimeIndex(g.ts[lab.tr]); pos = pd.Series(np.arange(len(dates)), index=dates)

# --- noise-band (all / shorts) from its test script
import noise_band_chuk_test as NB
for key, sel in (("NB", NB.T.side != 0), ("NB_S", NB.T.side < 0)):
    W = np.zeros((len(dates), 1440)); Cd = np.zeros(len(dates))
    for d, grp in NB.T[sel].groupby("date"):
        if d not in pos.index: continue
        i = pos[d]; acc = 0.0; day = np.zeros(1440)
        for r in grp.itertuples():
            a, b = NB.J0 + r.j0, NB.J0 + r.j1
            day[a:b + 1] = acc + (NB.C[r.i, r.j0:r.j1 + 1] - r.e) * r.side * 2 - 0.5 - 1.45
            acc += r.side * (r.x - r.e) * 2 - 1.0 - 1.45; day[b + 1:] = acc
        W[i] = day; Cd[i] = acc
    lab.W[key] = W; lab.C[key] = Cd

# --- NQ MOC auction follow (>= 0.3 ATR 14:00 -> 14:50, follow 14:51 -> 15:00, stop 0.25 ATR)
import s_rank_es_round1_test as ER
atr = g.daily_atr(15); cf = pd.Series(g.c.ravel()).ffill().to_numpy(); tr = lab.tr
P = lambda t: cf[tr * 1440 + jof(t)]
mv = P(1450) - P(1400); m = (g.last_j[tr] >= jof(1500)) & (np.abs(mv) >= 0.3 * atr[tr]) & (mv != 0)
t = ER.trades(g, tr[m], np.sign(mv[m]).astype(int), jof(1451), jof(1500), 0.25 * atr[tr][m]).reset_index(drop=True)
t["slips"] = 0
lab.add("MOC_NQ", t[["day", "j0", "j1", "side", "entry", "exit", "kind", "slips"]], stop_pts=0.25 * atr, slippage=False)

# --- harvested candidates
for f in sorted(glob.glob(SP + "repl_*.pkl")):
    k = f.split("repl_")[1][:-4]; d = pickle.load(open(f, "rb"))
    src = pd.DatetimeIndex(d["dates"])
    if len(src) == len(dates) and (src == dates).all():
        lab.W[k], lab.C[k] = d["W"], d["C"]; st = d["stop"]
    else:
        ix = pd.Series(np.arange(len(src)), index=src).reindex(dates)
        ok = ix.notna().to_numpy(); ii = ix.fillna(0).astype(int).to_numpy()
        lab.W[k] = np.where(ok[:, None], d["W"][ii], 0.0); lab.C[k] = np.where(ok, d["C"][ii], 0.0)
        st = None if d["stop"] is None else np.where(ok, d["stop"][ii], 1e12)
    if st is not None: lab.stop[k] = st

CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2}
PIECES = {"Vault Break": ["VB_N", "VB_F"], "ONB ML": ["ONB_ML2_MC"], "Monday Long": ["MON_MC"], "EOS": ["EOS"],
          "Late-Day Flow": ["LDF_MC"], "NFP Fade": ["NFP_MC"], "Bridge Monday": ["MON_BR_MC"], "CL Sunday fade": ["CLS"],
          "ES MOC": ["MOC_MES"]}
PART = {"Vault Break": {"VB_N": 1, "VB_F": 1}, "Late-Day Flow": {"LDF_MC": 1}, "ES MOC": {"MOC_MES": 1}, "CL Sunday fade": {"CLS": 1}}
CANDS = [k for k in ["NB", "NB_S", "MOC_NQ", "OND_MC", "VCS_MC", "HSF", "HSF_L", "HSF_S", "DPB_S", "CRB", "BR_ORB", "MOT",
                     "MO_R", "RRF", "VWP", "OPB", "GLD", "NFP_845", "LDF_MC_L", "LDF_MC_S", "ONB_ML2_L", "ONB_ML2_S"] if k in lab.W]


def sizes(k):
    return [("risk", 400), ("risk", 700)] if k in lab.stop else [1, 2]


def drop(piece):
    return {k: v for k, v in CUR.items() if k not in PIECES[piece]}


def sc(plan):
    s = lab.score(plan, 500, fmin=0.5, fmax=1.0, ref=1500.0); return s["expected"], s["blown"], s["s2023_on"]


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); print("Candidates:", CANDS)
    base = sc(CUR); print(f"\nCurrent plan: 2y ${base[0]:,.0f}, blown {base[1]:.1%}, 2023+ starts ${base[2]:,.0f}")
    rows = []
    for piece in PIECES:
        variants = {"whole": drop(piece)}
        if piece in PART: variants["part"] = {**CUR, **PART[piece]}
        for how, p0 in variants.items():
            c0 = sc(p0); rows.append(dict(piece=piece, how=how, cand="(nothing)", size="", y2=c0[0], blown=c0[1], s23=c0[2]))
            for k in CANDS:
                if k.startswith(tuple(PIECES[piece])) or (piece == "Late-Day Flow" and k.startswith("LDF")) or \
                   (piece == "ONB ML" and k.startswith("ONB")): pass
                for s in sizes(k):
                    r = sc({**p0, k: s}); rows.append(dict(piece=piece, how=how, cand=k, size=str(s), y2=r[0], blown=r[1], s23=r[2]))
    R = pd.DataFrame(rows); R.to_pickle(SP + "replacement_stage1.pkl")
    ctl = R[R.cand == "(nothing)"].set_index(["piece", "how"])
    R["vs_plan"] = R.y2 - base[0]; R["vs_empty"] = R.y2 - [ctl.loc[(p, h), "y2"] for p, h in zip(R.piece, R.how)]
    R["blown_vs_plan"] = R.blown - base[1]
    print("\nStage 1: best replacement per plan piece (single-history bench, 2-year expected payouts)")
    for (piece, how), grp in R.groupby(["piece", "how"], sort=False):
        c = grp[grp.cand == "(nothing)"].iloc[0]; best = grp[grp.cand != "(nothing)"].sort_values("y2", ascending=False).head(3)
        print(f" {piece} ({how}): leave empty ${c.y2:,.0f} ({c.vs_plan:+,.0f} vs plan), blown {c.blown:.1%}")
        for b in best.itertuples():
            print(f"     {b.cand:<9} {b.size:<14} ${b.y2:,.0f}  vs plan {b.vs_plan:+,.0f}  vs empty {b.vs_empty:+,.0f}  "
                  f"blown {b.blown:.1%} ({b.blown_vs_plan:+.1%})  2023+ ${b.s23:,.0f}")
    win = R[(R.cand != "(nothing)") & (R.vs_plan > 0) & (R.vs_empty > 0) & (R.blown_vs_plan <= 0.005)].sort_values("vs_plan", ascending=False)
    print(f"\nStage 1 survivors (beat the plan AND the empty slot, blown not up > 0.5 pts): {len(win)}")
    print(win.head(15)[["piece", "how", "cand", "size", "y2", "vs_plan", "vs_empty", "blown", "s23"]].round(3).to_string(index=False))
    if len(win):
        top = win.drop_duplicates(["piece", "how", "cand"]).head(8)
        plans = {"current plan": CUR}
        for r in top.itertuples():
            p0 = drop(r.piece) if r.how == "whole" else {**CUR, **PART[r.piece]}
            sz = eval(r.size) if r.size.startswith("(") else int(r.size)
            plans[f"{r.piece} {r.how} -> {r.cand} {r.size}"] = {**p0, r.cand: sz}
            plans[f"{r.piece} {r.how} -> empty"] = p0
        B = FB.Boot(lab); df, s, _ = B.compare(plans, base="current plan", n=1000, L=20)
        print("\nStage 2: bootstrapped bench (1,000 paired 2-year histories)"); print(s)
