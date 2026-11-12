"""Morning jump fade (WATCHLIST #40, POST-HOC lead, analysis/jump_morning_fade.py) against the current books: add AND replace
(CLAUDE.md 'Add or replace'), user 2026-11-11 'what are its stats against the current books'.
Rule: 5-min bar with |J| > 3 closing 07:00-09:59 CT -> fade at the next minute, stop 1.5 x bar range, target 0.3 x stop, 240 min /
15:55. Trades per NQ after $7.25 + 1 tick per market / stop fill; MNQ = NQ / 10 - $0.55 extra micro fee a trade.
Benches (analysis/bench150.py): 150K evaluation (set + Twin 2 MNQ), funded 150K x 1.5 + Twin 2 (600 paired 2-year histories),
personal book (1-year block MC median year / p95 DD). Control: the same MNQ count's dollars spread over the base (x the base's
own scale) is NOT available on these engines, so the comparison is base vs base + lead and base - piece + lead.
  tools/run_stamped.sh analysis/jump_morning_fade_bench.py > analysis/outputs/jump_morning_fade_bench_output.txt
"""
import sys, io, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import jump_lib as L, jump_study as S, bench150 as BN, montecarlo as MC
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30

EXTRA = 0.55
NOVB = "novb" in sys.argv          # VB removed from the 150K evaluation 2026-11-11 (user); novb also drops it from funded / personal
print(__doc__.split("\n")[0])
b = L.bars(); M = S.Mkt(); yr = b.ts.dt.year.to_numpy(); sgn = np.sign(b.r).fillna(0).to_numpy(); aJ = b.J.abs().to_numpy()
hc = b.ts.dt.hour.to_numpy()
T = S.trades(b, M, (yr >= 2018) & (aJ > 3) & np.isin(hc, [7, 8, 9]), -sgn, "rng", 1.5, tp=0.3, hold=240)
ix = np.searchsorted(M.ts, T.ts.to_numpy())                                   # entry minute index in the 1-min frame
print(f"lead: {len(T)} trades, ${T.net.mean():.1f} per NQ, PF {T.net[T.net > 0].sum() / -T.net[T.net < 0].sum():.2f}, per MNQ ${T.net.mean() / 10 - EXTRA:.2f} a trade")

ctx = BN.setup(); g = ctx["g"]; trr = ctx["trr"]; dts = ctx["dts"]
row_of = pd.Series(np.arange(g.D), index=pd.DatetimeIndex(g.ts)); tpos = pd.Series(np.arange(len(trr)), index=dts)
W = np.zeros((ctx["D"], 1440)); R = np.zeros((ctx["D"], 1440)); hi, lo = M.arr[1], M.arr[2]; miss = 0
for t, e in zip(T.itertuples(), ix):
    day = pd.Timestamp(t.ts).normalize()
    if day not in tpos.index: miss += 1; continue
    r = tpos[day]; n = int(t.mins); mins = pd.DatetimeIndex(M.ts[e:e + n]); js = mins.hour * 60 + mins.minute
    if (mins.normalize() != day).any(): miss += 1; continue
    cost = t.gross - t.net; adv = ((lo[e:e + n] if t.side > 0 else hi[e:e + n]) - t.entry) * t.side * 20 - cost
    adv[-1] = t.net if t.why == "tgt" else min(adv[-1], t.net)
    W[r, js] += adv; W[r, js[-1] + 1:] += t.net; R[r, js[-1]:] += t.net
W, R = W / 10, R / 10                                                           # per MNQ
fee = np.zeros(ctx["D"]); np.add.at(fee, [tpos[pd.Timestamp(x).normalize()] for x in T.ts if pd.Timestamp(x).normalize() in tpos.index], EXTRA)
W -= fee[:, None]; R -= fee[:, None]
print(f"mapped to Apex trading days: {len(T) - miss} of {len(T)} (dropped {miss}: not a grid trading day)")
lead_d = pd.Series(R[:, -1], index=dts)

# correlation with each plan piece (daily, per unit)
lab = ctx["lab"]; corr = {k: float(np.corrcoef(lead_d.values, lab.C[k])[0, 1]) for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "MON_BR_MC", "CLS", "TWIN")}
print("daily correlation with the funded-plan pieces: " + ", ".join(f"{k} {v:+.2f}" for k, v in corr.items()))
both = (lead_d != 0) & (pd.Series(lab.C["ONB_ML2_MC"], index=dts) != 0); print(f"days both the lead and ONB trade: {int(both.sum())} of {int((lead_d != 0).sum())} lead days")

# the evaluation base pieces' paths (as in bench150.setup) for the replacement test
P = {}
for k, t_ in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, ONB30)), "MON_BR": load_bridge_mc(g),
              "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
    w, rr = paths(g, t_); P[k] = (w[trr] / 10, rr[trr] / 10)
ec = {k: float(np.corrcoef(lead_d.values, P[k][1][:, -1])[0, 1]) for k in P}
ec["TWIN"] = float(np.corrcoef(lead_d.values, ctx["Rt"][:, -1])[0, 1])
print("daily correlation with the 150K evaluation pieces: " + ", ".join(f"{k} {v:+.2f}" for k, v in ec.items()))
if NOVB:
    ctx["Wb"] = ctx["Wb"] - 20 * P["VB"][0]; ctx["Rb"] = ctx["Rb"] - 20 * P["VB"][1]
    print("BASE WITHOUT VB: evaluation base = ONB30 $2,750 risk, MON_BR 5, EOS $1,250 risk, Twin 2 MNQ; funded = plan x 1.5 + Twin 2 minus VB_N / VB_F; personal minus VaultBreak")
    BN.BASE_FUNDED = {k: v for k, v in BN.BASE_FUNDED.items() if k not in ("VB_N", "VB_F")}
else:
    print("BASE: evaluation VB 20, ONB30 $2,750 risk, MON_BR 5, EOS $1,250 risk, Twin 2 MNQ")
atr = g.daily_atr(15); onb_n = np.floor(2750 / (np.nan_to_num(0.25 * atr[trr], nan=1e12) * 2))[:, None]

print("\n== 150K evaluation (pass rate, paired diff and 5-95% block band)")
cands = {f"+ lead {k} MNQ": (W * k, R * k) for k in (1, 2, 3)}
cands["+ lead 2 MNQ, MON_BR 5 -> 3"] = (2 * W - 2 * P["MON_BR"][0], 2 * R - 2 * P["MON_BR"][1])
cands["MON_BR 5 -> 3 alone (control)"] = (-2 * P["MON_BR"][0], -2 * P["MON_BR"][1])
cands["+ lead 2 MNQ, Twin 2 -> 0"] = (2 * W - 2 * ctx["Wt"], 2 * R - 2 * ctx["Rt"])
cands["Twin 2 -> 0 alone (control)"] = (-2 * ctx["Wt"], -2 * ctx["Rt"])
BN.eval_bench(ctx, cands)

print("\n== Funded 150K x 1.5 + Twin 2 (600 paired 2-year histories)")
BN.funded_bench(ctx, {f"+ lead {k} MNQ": {**BN.BASE_FUNDED, "JMF": k} for k in (1, 2, 3)} |
                {"+ lead 2 MNQ, Twin 2 -> 0": {**{k: v for k, v in BN.BASE_FUNDED.items() if k != "TWIN"}, "JMF": 2},
                 "Twin 2 -> 0 alone (control)": {k: v for k, v in BN.BASE_FUNDED.items() if k != "TWIN"}},
                extra={"JMF": (W, R[:, -1])})

print("\n== Personal book (1-year block-bootstrap MC: median year / p95 drawdown), every piece 1 micro + OT 2 MNQ as in the plan")
with contextlib.redirect_stdout(io.StringIO()):
    Pp = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")["P"]
Pp = Pp[[c for c in Pp.columns if c not in ("FC2B", "Kusho", "S47", "S30") + (("VaultBreak",) if NOVB else ())]]
base = Pp.sum(axis=1) + Pp.OvernightTick; lp = lead_d.reindex(Pp.index, fill_value=0.0)
cpb = {c: float(np.corrcoef(lp, Pp[c])[0, 1]) for c in Pp}; top = max(cpb, key=lambda c: cpb[c])
print("   correlation with personal pieces: " + ", ".join(f"{c} {v:+.2f}" for c, v in sorted(cpb.items(), key=lambda x: -x[1])[:5]) + f"; most overlapped: {top}")
def mc(x):
    d = MC.daily_mc(x.values, horizon=252, n=3000, block=20, trail=1e12, seed=1); return d["pnl_p50"], d["dd_p95"], d["pnl_p50"] / d["dd_p95"]
V = {"book": base, "+ lead 1 MNQ": base + lp, "+ lead 2 MNQ": base + 2 * lp, f"- {top} + lead 1 MNQ": base - Pp[top] + lp, f"- {top} (control)": base - Pp[top]}
for per, m in (("2018-26", np.ones(len(Pp), bool)), ("2018-22", Pp.index.year <= 2022), ("2023+", Pp.index.year >= 2023)):
    r0 = mc(base[m]); print(f"   {per}: " + " | ".join(f"{nm} ${a:,.0f} / ${dd:,.0f} = {q:.2f}" + ("" if nm == "book" else f" ({q - r0[2]:+.2f})") for nm, x in V.items() for a, dd, q in [mc(x[m])]))
