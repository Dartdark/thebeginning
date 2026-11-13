"""Ingredient combos: an engine from one plan piece + a proven filter from another (user 2026-11-09: 'combining ingredients from
different strategies to create completely new ones', 'yes' to all four). PRE-REGISTERED (header committed before the first run;
4 items, filters fixed here, no tuning).
  C1 Flow-confirmed Vault Break: VB (MultiCharts list, longs) kept only on days whose opening-range order-flow z (FC 2B's
     ratio, 08:31-09:00, vs the past 60 days) is > 0, i.e. the opening flow agrees with a long breakout.
  C2 Heavy-night London impulse: S47 v2 kept only after a HEAVY night (T fade's filter: night volume > 1.4 x the median of the
     prior 20 valid nights; known at 08:29, S47 enters 09:31).
  C3 Trend-gated Monday: Monday Long (MultiCharts list) kept only when the last regular session's DI+ > DI- (Bridge Monday's
     DI(7) bookkeeping; known Friday's close).
  C4 Auction-confirmed MOC: ES MOC Follow kept only when Late-Day Flow fired the same day in the SAME direction (NQ open ->
     14:00 move >= 0.4 x ATR15, sign = the MOC side).
Each vs its parent, per contract after our costs: $ a trade, t, both periods; kept vs skipped trades (t of the difference);
random-skip placebo: keep the same NUMBER of the parent's trades at random, 1,000 runs, p = share >= the combo's mean
(bar p < 0.0125 = 0.05 / 4 items; equivalently t >= metrics.t_threshold(4) = 2.24 on kept - skipped).
Books (replacement of the parent at its plan size): C1 150K evaluation (current set: VB 15 -> filtered VB 15); C2 personal full
book (S47 column); C3 funded 150K (MON_MC x 1.5) + personal full (MondayLong); C4 funded 150K (MOC 3 MES) + personal full
(ESMOCFollow). Adoption: placebo p < 0.0125 AND the book better in both periods -> forward log first (new rule = new strategy).
  tools/run_stamped.sh analysis/ingredient_combos_test.py > analysis/outputs/ingredient_combos_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from replica import is_early_close
from ingredient_ablation3 import line
import ingredient_ablation9 as IA9
import fc_2b_test as FC, s47_test as S4, t_oneside_test as TO, bridge_monday_long_test as BM
import dual_thrust_bench as DTB, funded_bootstrap as FB, montecarlo as MC, bench150 as BB


def judge(nm, T, keep):
    """T: parent trades (date, net); keep: bool per trade."""
    k, s = T[keep], T[~keep]
    tt = lambda v: v.mean() / v.std() * np.sqrt(len(v)) if len(v) > 2 else np.nan
    dif = (k.net.mean() - s.net.mean()) / np.sqrt(k.net.var() / max(len(k), 1) + s.net.var() / max(len(s), 1))
    rng = np.random.default_rng(7); pm = np.array([T.net.values[rng.choice(len(T), len(k), replace=False)].mean() for _ in range(1000)])
    print(line(T.net, T.date, f"{nm} PARENT"))
    print(line(k.net, k.date, f"{nm} COMBO (kept {len(k)} of {len(T)})"))
    print(line(s.net, s.date, f"{nm} skipped"))
    print(f"      kept - skipped t {dif:.2f} | random-skip placebo: mean ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}, combo ${k.net.mean():.0f}, p {np.mean(pm >= k.net.mean()):.3f}", flush=True)


def personal(col, mask_dates, label):
    P = pd.read_pickle("scratch_data/personal_P.pkl"); idx = P.index; m = pd.Series(idx.isin(mask_dates), index=idx)
    base = P.sum(axis=1); alt = base - P[col] + P[col].where(m, 0.0)
    f = lambda x: (lambda r: (r["pnl_p50"], r["dd_p95"], r["pnl_p50"] / r["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
    out = []
    for per, mm in (("2018-26", np.ones(len(idx), bool)), ("2018-22", idx.year <= 2022), ("2023+", idx.year >= 2023)):
        a, b = f(base[mm]), f(alt[mm]); out.append(f"{per} {a[2]:.2f} -> {b[2]:.2f} ({b[2] - a[2]:+.2f}; median ${b[0] - a[0]:+,.0f}, DD ${b[1] - a[1]:+,.0f})")
    print(f"   personal full book, {label}: " + " | ".join(out), flush=True)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(base="legacy"); g, trr, D, dts, lab = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"], ctx["lab"]; ts = pd.DatetimeIndex(g.ts)
    FB.add_moc_mes(lab); ld = pd.DatetimeIndex(lab.g.ts[lab.tr]).normalize()
    # ---------------- C1
    print("\nC1 Flow-confirmed Vault Break:")
    days = FC.load(); sig = FC.signals(days); z = pd.Series(sig.z.values, index=pd.DatetimeIndex(sig.date).normalize())
    vb = with_slippage(load_mc(g, REPORTS["VB"][0])); vb["date"] = ts[vb.day.values].normalize(); vb = vb[vb.date >= "2018-01-01"].reset_index(drop=True)
    keep1 = (z.reindex(vb.date).values > 0)
    judge("VB", vb, keep1)
    P = {}
    for nm, t in (("VB", vb), ("VBf", vb[keep1]), ("DT", DTB.dt_trades(g))): w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    ctx["Wb"] = ctx["Wb"] - 5 * P["VB"][0] + 2 * P["DT"][0]; ctx["Rb"] = ctx["Rb"] - 5 * P["VB"][1] + 2 * P["DT"][1]
    BB.eval_bench(ctx, {"VB 15 -> flow-confirmed VB 15": (15 * (P["VBf"][0] - P["VB"][0]), 15 * (P["VBf"][1] - P["VB"][1]))}, label="150K evaluation (current set)")
    # ---------------- C2
    print("\nC2 Heavy-night London impulse:")
    T = S4.build(g); s47 = S4.run(g, T); s47["date"] = pd.DatetimeIndex(s47.date).normalize()
    Dn = TO.days(g); heavy = Dn[Dn.valid & (Dn.med > 0) & (Dn.vol > 1.4 * Dn.med)]; hd = set(pd.DatetimeIndex(heavy.date).normalize())
    keep2 = s47.date.isin(hd).values
    judge("S47", s47, keep2); personal("S47", set(s47.date[keep2]) | set(), "S47 -> heavy-night S47")
    # ---------------- C3
    print("\nC3 Trend-gated Monday:")
    A7 = BM.bridge_adx(g, 7); mon = with_slippage(load_mc(g, REPORTS["MON_MC"][0])); mon["date"] = ts[mon.day.values].normalize(); mon = mon[mon.date >= "2018-01-01"].reset_index(drop=True)
    keep3 = np.array([A7[int(d) - 1][0] >= 0 and A7[int(d) - 1][1] > 0 for d in mon.day])
    judge("MON", mon, keep3)
    gm = set(mon.date[keep3]); m3 = np.array([d in gm for d in ld])
    BB.funded_bench(ctx, {"MON -> trend-gated MON": {**{k: v for k, v in BB.BASE_FUNDED.items() if k != "MON_MC"}, "MON_G": BB.BASE_FUNDED["MON_MC"]}},
                    extra={"MON_G": (lab.W["MON_MC"] * m3[:, None], lab.C["MON_MC"] * m3)})
    personal("MondayLong", gm, "Monday Long -> trend-gated")
    # ---------------- C4
    print("\nC4 Auction-confirmed MOC (per ES):")
    ge = pickle.load(open("scratch_data/ge.pkl", "rb")); moc = IA9.moc(ge, 50.0, 0.25, 5.0); moc["date"] = pd.DatetimeIndex(moc.date).normalize()
    import ingredient_ablation3 as IA3
    l = IA3.ldf(g); lside = pd.Series(l.side.values, index=pd.DatetimeIndex(l.date).normalize()); lside = lside[~lside.index.duplicated()]
    keep4 = (lside.reindex(moc.date).values == moc.side.values)
    judge("MOC", moc, keep4)
    ga = set(moc.date[keep4]); m4 = np.array([d in ga for d in ld])
    BB.funded_bench(ctx, {"+ MOC 3 MES (both, as plan)": {**BB.BASE_FUNDED, "MOC_MES": 3}, "+ MOC 3 MES auction-confirmed": {**BB.BASE_FUNDED, "MOC_A": 3}},
                    extra={"MOC_A": (lab.W["MOC_MES"] * m4[:, None], lab.C["MOC_MES"] * m4)})
    personal("ESMOCFollow_perMES", ga, "ES MOC -> auction-confirmed")
