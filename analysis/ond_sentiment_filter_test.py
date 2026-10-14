"""Overnight Drift (OND, MultiCharts trades) with the sentiment filters of Vojtko & Hanicova (Quantpedia, SSRN 3829582),
2018-2026. Paper: SPY close -> open (no costs) Sharpe 0.84; only when SPY > 20-day MA 1.92, VIX < 20-day MA 1.80.
Pre-specified: OND trades (entries by 00:30 as in build_lab.py, $7.25 + 1 tick a non-limit fill) taken only when, at the previous
session's close, (a) NQ 15:00 close > its 20-day MA, (b) VIX close < its 20-day MA, (c) both; then the funded bench: the current
plan (+ CL fade 2 MCL) + filtered OND at risk $500 (its old size) vs unfiltered.
  python3 analysis/ond_sentiment_filter_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
from funded_lab import with_slippage
from co_oc_reversal_test import line
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")
    lab = ns["lab"]; g = lab.g
    t0 = load_mc(g, "Backtesting Strategy Performance Report OND v1.xlsx"); t0 = t0[t0.j0 <= 30].reset_index(drop=True)
    t = with_slippage(t0.copy()); t["net"] = (t.exit - t.entry) * t.side * 20 - 7.25
    t["date"] = pd.DatetimeIndex(g.ts[t.day.values])
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); tr = g.trading; days = pd.DatetimeIndex(g.ts[tr])
    nq = pd.Series(cf[tr * 1440 + 900], index=days); ma = nq.rolling(20).mean()
    vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE; vma = vix.rolling(20).mean()
    prev = lambda s, d: s[s.index < d].iloc[-1] if (s.index < d).any() else np.nan
    t["nq_up"] = [prev(nq > ma, d) for d in t.date]; t["vix_low"] = [prev(vix < vma, d) for d in t.date]
    t = t[t.date >= "2018-01-01"]
    print(f"OND trades {len(t)}, longs {np.mean(t.side > 0):.0%}")
    for nm, m in (("OND all", np.ones(len(t), bool)), ("(a) NQ > 20-day MA", t.nq_up == True), ("    NQ < MA", t.nq_up == False),
                  ("(b) VIX < 20-day MA", t.vix_low == True), ("    VIX > MA", t.vix_low == False),
                  ("(c) both", (t.nq_up == True) & (t.vix_low == True)), ("    neither", (t.nq_up == False) & (t.vix_low == False))):
        x = t.net[m].set_axis(t.date[m]); print(line(x, nm, 26))
    atr = g.daily_atr(15)
    keep = {"a": (t.nq_up == True), "b": (t.vix_low == True), "c": (t.nq_up == True) & (t.vix_low == True)}
    t0 = t0.loc[t.index]
    for k, m in keep.items(): lab.add(f"OND_{k}", t0[m.values].reset_index(drop=True), stop_pts=0.30 * atr)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500),
            "MON_BR_MC": 1, "CLS": 2}
    print("\nfunded bench, cushion $1,500 (1 year / 2 years, blown):")
    for nm, p in (("plan", plan), ("+ OND unfiltered $500", {**plan, "OND_MC": ("risk", 500)}),
                  ("+ OND (a) NQ > MA $500", {**plan, "OND_a": ("risk", 500)}), ("+ OND (b) VIX < MA $500", {**plan, "OND_b": ("risk", 500)}),
                  ("+ OND (c) both $500", {**plan, "OND_c": ("risk", 500)})):
        a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
        print(f"   {nm:<26} ${a['expected']:,.0f} / ${c['expected']:,.0f}  blown {a['blown']:.0%} / {c['blown']:.0%}")

    # post-hoc (2026-10-14, after seeing the paper's filters backfire): the inverse = OND only after 'fear'
    inv = {"nqdn": (t.nq_up == False), "vixhi": (t.vix_low == False), "neither": (t.nq_up == False) & (t.vix_low == False)}
    for k, m in inv.items(): lab.add(f"OND_{k}", t0[m.values].reset_index(drop=True), stop_pts=0.30 * atr)
    print("\npost-hoc inverse (OND only after fear), cushion $1,500:")
    for nm, k in (("NQ < MA", "nqdn"), ("VIX > MA", "vixhi"), ("both (neither good)", "neither")):
        for risk in (250, 500):
            p = {**plan, f"OND_{k}": ("risk", risk)}
            a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
            print(f"   + OND {nm:<20} ${risk:<4} ${a['expected']:,.0f} / ${c['expected']:,.0f}  blown {a['blown']:.0%} / {c['blown']:.0%}")
