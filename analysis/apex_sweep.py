"""Data sweep for the Apex books (user 2026-11-10: 'run the same sweep process for the funded and evaluation books'). POST HOC screen,
information only (out-of-sample: the 2009-2017 export in TODO / the forward log).
1. Screen: every piece of the funded 150K plan (lab daily P&L: VB, ONB ML, Monday, EOS, LDF, NFP, Bridge Monday, CL fade, Twin) and of
   the 150K evaluation set (VB 15, ONB ADX30 $2,750, Bridge Monday 5, EOS $1,250, Twin 2, Dual Thrust 2) x the 21 series x 3 regimes of
   analysis/data_sweep.py (last close before the day); gap t on active days, same sign in 2018-22 and 2023+; bar t_threshold(all).
2. For each piece, its strongest same-sign condition -> a version that SKIPS the unfavourable days (no size-ups: extra size hurt both
   Apex books today), benched one at a time and all together: funded 150K (600 paired 2-year histories) and the 150K evaluation
   (every start 2018 -> 2026-09, paired band).
  tools/run_stamped.sh analysis/apex_sweep.py > analysis/outputs/apex_sweep_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from metrics import t_threshold
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30
from new_data_screen import RULES, prior
from data_sweep import series
import dual_thrust_bench as DTB, bench150 as BB


def screen(pieces, dts, S):
    rows = []
    for nm, s in S.items():
        for rule, fn in RULES.items():
            on_all = prior(s, dts, fn) == 1
            for p, x in pieces.items():
                act = x != 0; h = on_all[act]; v = x[act]; d = dts[act]
                if h.sum() < 15 or (~h).sum() < 15: continue
                a, b = v[h], v[~h]; t = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b)); e = d.year <= 2022
                g1, g2 = v[e & h].mean() - v[e & ~h].mean(), v[~e & h].mean() - v[~e & ~h].mean()
                rows.append(dict(piece=p, series=nm, rule=rule, t=t, same=np.sign(g1) == np.sign(g2), on=a.mean(), off=b.mean(), share=h.mean()))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(); g, trr, D, dts, lab = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"], ctx["lab"]; S = series()
    ld = pd.DatetimeIndex(lab.g.ts[lab.tr]).normalize()
    # ---------- pieces
    fk = {"VB": "VB", "ONB ML": "ONB_ML2_MC", "Monday Long": "MON_MC", "EOS": "EOS", "LDF": "LDF_MC", "NFP": "NFP_MC", "Bridge Monday": "MON_BR_MC", "CL fade": "CLS", "Twin": "TWIN"}
    funded = {p: np.asarray(lab.C[k], float) for p, k in fk.items()}
    atr = g.daily_atr(15); rk = lambda d_, m: np.floor(d_ / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    EP = {}
    for nm, t, q in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0])), 15.0), ("ONB ADX30", with_slippage(load_mc(g, ONB30)), rk(2750, 0.25)),
                     ("Bridge Monday", load_bridge_mc(g), 5.0), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])), rk(1250, REPORTS["EOS"][1])),
                     ("Dual Thrust", DTB.dt_trades(g), 2.0)):
        w, r = paths(g, t); EP[nm] = (w[trr] / 10 * q, r[trr] / 10 * q)
    EP["Twin"] = (ctx["Wt"] * 2, ctx["Rt"] * 2)
    evalp = {p: EP[p][1][:, -1] for p in EP}
    # ---------- 1. screen
    Rf = screen(funded, ld, S); Re = screen(evalp, dts, S); n = len(Rf) + len(Re); bar = t_threshold(n)
    print(f"\n1. Screen: funded {len(Rf)} + evaluation {len(Re)} = {n} comparisons; bar |t| >= {bar:.2f} (same sign both periods)")
    pick = {}
    for lab_, R in (("FUNDED", Rf), ("EVALUATION", Re)):
        R = R[R.same]; print(f"\n   {lab_}: at the bar {int((R.t.abs() >= bar).sum())}; |t| >= 3: {int((R.t.abs() >= 3).sum())}")
        for p in R.piece.unique():
            r = R[R.piece == p].reindex(R[R.piece == p].t.abs().sort_values(ascending=False).index).iloc[0]; pick[(lab_, p)] = r
            print(f"   {p:<15} best: {r.series:<26} {r.rule:<13} t {r.t:5.2f} | on ${r.on:6.0f} off ${r.off:6.0f} (on {r.share:.0%}) -> skip the {'off' if r.t > 0 else 'on'} days")
    def keep_mask(r, dates):
        on = prior(S[r.series], dates, RULES[r.rule]) == 1; return on if r.t > 0 else ~on
    # ---------- 2a. funded bench
    print("\n2a. Funded 150K, skip the unfavourable days (one piece at a time, then all):")
    ext, var, allp = {}, {}, {k: v for k, v in BB.BASE_FUNDED.items()}
    for p, k in fk.items():
        if ("FUNDED", p) not in pick: continue
        m = keep_mask(pick[("FUNDED", p)], ld).astype(float); keys = ["VB_N", "VB_F"] if k == "VB" else [k]
        plan = dict(BB.BASE_FUNDED)
        for kk in keys:
            if kk not in plan: continue
            ext[kk + "_S"] = (lab.W[kk] * m[:, None], lab.C[kk] * m); plan[kk + "_S"] = plan.pop(kk); allp[kk + "_S"] = allp.pop(kk)
            if kk in lab.stop: lab.stop[kk + "_S"] = lab.stop[kk]          # risk-sized pieces need their stop distance
        var[f"{p} skip"] = plan
    var["ALL skips together"] = allp
    BB.funded_bench(ctx, var, extra=ext)
    # ---------- 2b. evaluation bench
    print("\n2b. 150K evaluation (current set), skip the unfavourable days:")
    Wb = sum(EP[p][0] for p in EP); Rb = sum(EP[p][1] for p in EP); ctx["Wb"], ctx["Rb"] = Wb, Rb
    cands, aw, ar = {}, 0, 0
    for p in EP:
        if ("EVALUATION", p) not in pick: continue
        m = keep_mask(pick[("EVALUATION", p)], dts).astype(float); dw, dr = EP[p][0] * (m - 1)[:, None], EP[p][1] * (m - 1)[:, None]
        cands[f"{p} skip"] = (dw, dr); aw = aw + dw; ar = ar + dr
    cands["ALL skips together"] = (aw, ar)
    BB.eval_bench(ctx, cands, label="150K evaluation (current set, rebuilt)")
