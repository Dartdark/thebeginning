"""One-sided versions where one side carries 2023+ (user 2026-11-09: 'key in on the sides that are working for each strategy and see
if it improves performance'). PRE-REGISTERED (header committed before the first run). POST HOC in origin: the sides were picked
from the 2023+ splits of ingredient rounds 5, 9 and 10, so a gain here only earns a forward log, not a plan change.
Items (4): ES MOC Follow longs only (2023+ longs $212 vs shorts $34 per ES); S47 v2 shorts only ($494 vs $183); FC 2B longs only
($325 vs $100); Swing Target v3 shorts only ($486 vs $168; benched 2026-11-08 as a book tie, rerun on the same footing).
Method: each piece's own daily series in the benches, with the other side's days set to 0 (one trade a day at most; the side of
each day from the rebuilds: ingredient_ablation9.moc, s47_test, fc_2b_test, ingredient_ablation5.swing), so both versions come
from the same trades.
  Personal book (scratch_data/personal_P.pkl, every piece at 1 micro, data to 2026-10-09): 1-year block bootstrap median year /
    p95 drawdown / return-to-DD, 2018-26, 2018-22, 2023+, for the full book and the core book (without the forward-log pieces
    FC2B / Kusho / S47 / S30), replacing the piece by its one-sided version.
  Funded 150K (ES MOC only; 600 paired 2-year histories, plan x 1.5 + Twin 2 + MOC 3 MES): both sides vs longs only.
Decision rule: one-sided version better in both periods of the book -> forward log (WATCHLIST); else no change.
  tools/run_stamped.sh analysis/side_focus_test.py > analysis/outputs/side_focus_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
import ingredient_ablation9 as IA9
import ingredient_ablation5 as IA5
import s47_test as S4
import fc_2b_test as FC
import funded_bootstrap as FB
import bench150 as BB


def mcs(x):
    r = MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1); return r["pnl_p50"], r["dd_p95"], r["pnl_p50"] / r["dd_p95"]


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); ge = pickle.load(open("scratch_data/ge.pkl", "rb"))
    sides = {}
    t = IA9.moc(ge, 50.0, 0.25, 5.0); sides["ESMOCFollow_perMES"] = (pd.Series(t.side.values, index=pd.DatetimeIndex(t.date).normalize()), 1)
    T = S4.build(g); t = S4.run(g, T); sides["S47"] = (pd.Series(t.side.values, index=pd.DatetimeIndex(t.date).normalize()), -1)
    days = FC.load(); t = FC.run(days, FC.signals(days)); sides["FC2B"] = (pd.Series(t.side.values, index=pd.DatetimeIndex(t.date).normalize()), 1)
    t = IA5.swing(g); sides["SwingTarget"] = (pd.Series(t.side.values, index=pd.DatetimeIndex(t.date).normalize()), -1)
    P = pd.read_pickle("scratch_data/personal_P.pkl"); idx = P.index
    print("\n   piece: day coverage (rebuild side known for the piece's trading days in the book)")
    one = {}
    for col, (sd, keep) in sides.items():
        sd = sd[~sd.index.duplicated()]; s = sd.reindex(idx); active = P[col] != 0
        cov = s[active].notna().mean(); one[col] = P[col].where(s == keep, 0.0)
        y = lambda x, m: x[m].sum() / (m.sum() / 252)
        a, b = idx.year <= 2022, idx.year >= 2023
        print(f"   {col:<20} coverage {cov:.0%} | $ a year both sides {y(P[col], a):,.0f} / {y(P[col], b):,.0f} | {'longs' if keep > 0 else 'shorts'} only {y(one[col], a):,.0f} / {y(one[col], b):,.0f} (2018-22 / 2023+)")
    for lab, cols in (("FULL book", list(P.columns)), ("CORE book (no forward-log pieces)", [c for c in P.columns if c not in ("FC2B", "Kusho", "S47", "S30")])):
        print(f"\n   {lab}: median year / DD p95 / return-DD")
        base = P[cols].sum(axis=1)
        for per, m in (("2018-26", np.ones(len(idx), bool)), ("2018-22", idx.year <= 2022), ("2023+", idx.year >= 2023)):
            b0 = mcs(base[m]); parts = [f"book ${b0[0]:,.0f} / ${b0[1]:,.0f} / {b0[2]:.2f}"]
            for col in one:
                if col not in cols: continue
                x = mcs((base - P[col] + one[col])[m]); parts.append(f"{col.split('_')[0]} one-side {x[2]:.2f} ({x[2] - b0[2]:+.2f}; ${x[0] - b0[0]:+,.0f} / DD ${x[1] - b0[1]:+,.0f})")
            print(f"      {per}: " + " | ".join(parts), flush=True)
    print("\n   Funded 150K, ES MOC 3 MES both sides vs longs only:")
    ctx = BB.setup(); lab_ = ctx["lab"]; FB.add_moc_mes(lab_)
    ld = pd.DatetimeIndex(lab_.g.ts[lab_.tr]).normalize(); sd = sides["ESMOCFollow_perMES"][0]; sd = sd[~sd.index.duplicated()]
    keepL = (sd.reindex(ld) == 1).fillna(False).to_numpy()
    BB.funded_bench(ctx, {"+ MOC 3 MES both sides": {**BB.BASE_FUNDED, "MOC_MES": 3}, "+ MOC 3 MES longs only": {**BB.BASE_FUNDED, "MOC_L": 3}},
                    extra={"MOC_L": (lab_.W["MOC_MES"] * keepL[:, None], lab_.C["MOC_MES"] * keepL)})
