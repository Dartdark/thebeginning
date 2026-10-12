"""Rebuild the cached test data in a fresh session (2026-10-12).

  python3 analysis/build_lab.py [SCRATCH_DIR]

Writes to SCRATCH_DIR (default: ./scratch_data, git-ignored size ~2 GB, not committed):
  g24.pkl   NQ 1-minute 24-hour grid (analysis/grid24.Grid24 from NQ_1min_*.csv)
  ge.pkl    ES 1-minute grid (data/ES_1min_*.csv)
  lab.pkl   funded lab (analysis/funded_lab.Lab) with the current funded set, all from the
            MultiCharts trade lists in the repo root, +1 tick slippage per non-limit fill:
              VB (VB v1), ONB_ML2_MC (+ _L/_S), MON_MC, EOS, LDF_MC (+ _L/_S), OND_MC (backup)
Older test scripts load these from the first session's scratchpad path (SP = ...); point SP
at SCRATCH_DIR to rerun them. Check: the current plan should score about $7,676 (1 year) and
$12,012 (2 years) with cushion sizing (see the end of this script).
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np
from grid24 import Grid24
from portfolio import load_mc
from funded_lab import Lab

OUT = sys.argv[1] if len(sys.argv) > 1 else "scratch_data"
os.makedirs(OUT, exist_ok=True)
REPORTS = {   # name: (report file, stop in ATR for risk sizing)
    "VB": ("Backtesting Strategy Performance Report VB v1.xlsx", 0.30),
    "ONB_ML2_MC": ("Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx", 0.30),
    "EOS": ("Backtesting Strategy Performance Report EOS v1.xlsx", 0.30),
    "OND_MC": ("Backtesting Strategy Performance Report OND v1.xlsx", 0.30),
    "MON_MC": ("Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx", 0.50),
    "LDF_MC": ("Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx", 0.25),
}

if __name__ == "__main__":
    g = Grid24(); pickle.dump(g, open(f"{OUT}/g24.pkl", "wb"), protocol=4); print("g24 done")
    es = Grid24("data/ES_1min_20*.csv", night_pattern=""); pickle.dump(es, open(f"{OUT}/ge.pkl", "wb"), protocol=4); print("ge done")
    atr = g.daily_atr(15); lab = Lab(g)
    for k, (f, sa) in REPORTS.items():
        t = load_mc(g, f)
        if k == "OND_MC": t = t[t.j0 <= 30].reset_index(drop=True)   # MaxEntryDelay fix: entries by 00:30
        lab.add(k, t, stop_pts=sa * atr)
        if k in ("ONB_ML2_MC", "LDF_MC"):
            base = k.replace("_MC", "") if k == "ONB_ML2_MC" else k
            for s, nm in ((1, "L"), (-1, "S")):
                lab.add(f"{base}_{nm}", t[t.side == s].reset_index(drop=True), stop_pts=sa * atr)
        print(k, len(t), "trades")
    pickle.dump(lab, open(f"{OUT}/lab.pkl", "wb"), protocol=4)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2}
    for h in (250, 500):
        r = lab.score(plan, h, fmin=0.5, fmax=1.0, ref=2000.0)
        print(f"current plan, cushion sizing, {h // 250}y: ${r['expected']:,.0f} blown {r['blown']:.0%}")
