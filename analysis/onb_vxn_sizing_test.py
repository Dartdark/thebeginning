"""Overnight Bias sized by implied vol (user's request after the VIX / VXN resources, 2026-10-15). Pre-registered, one change:
the TRADES and their stops stay exactly as in the MultiCharts lists; only the size input changes. Now: MNQ = floor(risk /
(0.30 x 15-day ATR x $2)) (funded ONB ML, risk $400) and floor($1,100 / (0.25 x ATR x $2)) (combine ONB ADX30). Variant:
the ATR in that formula is replaced by k x implied daily sigma in points, sigma = yesterday's VXN close / 100 / sqrt(252) x
yesterday's NQ price, with k set so the 2018-26 median day gets the same size (pure re-timing of size, same average risk).
Checks: (1) how steady the dollar loss of a stopped trade is under each sizing (the point of vol sizing); (2) funded bench
(plan with single-print VB, CL fade; cushion $1,500, 1 / 2 years); (3) combine pass rate.
  python3 analysis/onb_vxn_sizing_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc, paths, challenge
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
ONB_ML = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx"
ONB30 = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx"

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; atr = g.daily_atr(15)
    px = pd.Series(pd.Series(g.c.ravel()).ffill().to_numpy().reshape(g.c.shape)[:, jof(1500)], index=pd.DatetimeIndex(g.ts))
    vxn = pd.read_csv("data/VXN_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE.reindex(px.index, method="ffill")
    sig = (px.shift(1).ffill() * vxn.shift(1) / 100 / np.sqrt(252)).to_numpy()          # known before the session
    tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]).year >= 2018]
    k = np.nanmedian(atr[tr]) / np.nanmedian(sig[tr]); sig_atr = k * sig
    print(f"median ATR {np.nanmedian(atr[tr]):.0f} pts, median implied sigma {np.nanmedian(sig[tr]):.0f} pts -> k {k:.2f}")
    # (1) dollar loss per stopped trade, per sizing (ONB ML, $400 risk)
    t = with_slippage(load_mc(g, ONB_ML)); pts = (t.exit - t.entry) * t.side
    for nm, a in (("ATR sizing", atr), ("VXN sizing", sig_atr)):
        q = np.floor(400 / (0.30 * a[t.day.to_numpy()] * 2.0))
        loss = (pts * 2.0 * q)[t.kind.to_numpy() == 0]
        print(f"   {nm}: MNQ median {np.nanmedian(q):.0f}; stopped trades {len(loss)}: loss $ mean {loss.mean():,.0f}, sd {loss.std():,.0f}, "
              f"worst {loss.min():,.0f}; all trades $ sd {np.nanstd(pts * 2.0 * q):,.0f}, total ${np.nansum(pts * 2.0 * q) - 0:,.0f}")
    # (2) funded bench: same trades, sizing input swapped
    dates = pd.DatetimeIndex(g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    lab.W["ONB_IV"] = lab.W["ONB_ML2_MC"]; lab.C["ONB_IV"] = lab.C["ONB_ML2_MC"]
    lab.stop["ONB_IV"] = np.nan_to_num(0.30 * sig_atr[lab.tr], nan=1e12)
    base = {"VB_N": 3, "VB_F": 1, "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    print("\nFunded bench (cushion $1,500):")
    for nm, p in (("plan, ONB ML ATR-sized $400", {**base, "ONB_ML2_MC": ("risk", 400)}), ("plan, ONB ML VXN-sized $400", {**base, "ONB_IV": ("risk", 400)}),
                  ("plan, ONB ML VXN-sized $500", {**base, "ONB_IV": ("risk", 500)})):
        r = (lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0))
        print(f"   {nm:<30} ${r[0]['expected']:,.0f} / ${r[1]['expected']:,.0f}  blown {r[0]['blown']:.0%} / {r[1]['blown']:.0%}  paid {r[0]['any_payout']:.0%}"
              f"  all 6 in 2y {r[1]['all_6']:.0%} | 1y 2018-22 ${r[0]['s2018_22']:,.0f} 2023+ ${r[0]['s2023_on']:,.0f}", flush=True)
    # (3) combine
    trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year; P = {}
    def add(nm, t_): w, r_ = paths(g, t_); P[nm] = (w[trr] / 10, r_[trr] / 10)
    add("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))); add("ONB30", with_slippage(load_mc(g, ONB30)))
    add("MON_BR", load_bridge_mc(g)); add("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))
    risk = lambda dollars, m, a: np.floor(dollars / (np.nan_to_num(m * a[trr], nan=1e12) * 2))[:, None]
    q_eos = risk(500, REPORTS["EOS"][1], atr)
    print("\nCombine (VB 8 + ONB ADX30 $1,100 + Bridge Monday 2 + EOS $500):")
    for nm, a in (("ONB30 ATR-sized", atr), ("ONB30 VXN-sized", sig_atr)):
        q = risk(1100, 0.25, a)
        W = P["VB"][0] * 8 + P["ONB30"][0] * q + P["MON_BR"][0] * 2 + P["EOS"][0] * q_eos
        Rr = P["VB"][1] * 8 + P["ONB30"][1] * q + P["MON_BR"][1] * 2 + P["EOS"][1] * q_eos
        res = [challenge(W, Rr, np.arange(s, min(s + 21, D))) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018)
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        fm = np.array([np.nan if x is None else float(x[0] == "fail_mll") for x in res])
        print(f"   {nm:<18} pass {np.nanmean(o[ok]):.1%} (2023-26 {np.nanmean(o[ok & (yr >= 2023)]):.1%}), blown {np.nanmean(fm[ok]):.1%}")
