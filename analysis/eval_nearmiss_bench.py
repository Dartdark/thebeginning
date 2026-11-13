"""150K evaluation bench of the three Apex-legal near misses from analysis/eval_profile_screen.py (2026-11-09). PRE-REGISTERED (header
committed before the run; 3 pieces x sizes). Current engine (floor keeps trailing), base = the 150K evaluation set + Twin 2 MNQ.
  noise-area longs (personal plan rule: Bridge RTH, longs only, early-close flat) 1 / 2 / 3 MNQ; Relative Strength (both sides) 1 / 2 MNQ;
  Dual Thrust v4 2 / 3 / 5 MNQ (benched in October on the old engine: worse at every size). Exact intraday paths (1-minute lows / highs).
  tools/run_stamped.sh analysis/eval_nearmiss_bench.py > analysis/outputs/eval_nearmiss_bench_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import paths
from funded_lab import with_slippage
import bench150 as BB
import bridge_noise_15m_test as BN
import dual_thrust_bench as DTB

if __name__ == "__main__" and "--replace" not in sys.argv:
    print(__doc__.split("\n")[0])
    ctx = BB.setup(); g, trr = ctx["g"], ctx["trr"]
    T = BN.run(BN.series("rth"), shorts=False, early_flat=True); T = T[T.date >= "2018-01-01"]
    nb = pd.DataFrame(dict(day=T.row.values, j0=T.j0.values, j1=T.j1.values, side=T.side.values, entry=T.entry.values - T.side.values * 0.25, exit=T.exit.values,
                           kind=np.where(T.kind == "target", 1, np.where(T.kind == "stop", 0, 2))))
    rs = pd.read_csv("scratch_data/rs_trades.csv"); rs = rs.assign(kind=rs.kind.map({"stop": 0, "target": 1, "flat": 2}))[["day", "j0", "j1", "side", "entry", "exit", "kind"]]
    P = {}
    for nm, t in (("noise-area longs", nb), ("Relative Strength", with_slippage(rs)), ("Dual Thrust", DTB.dt_trades(g))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    sizes = {"noise-area longs": (1, 2, 3), "Relative Strength": (1, 2), "Dual Thrust": (2, 3, 5)}
    BB.eval_bench(ctx, {f"+ {nm} {n} MNQ": (n * P[nm][0], n * P[nm][1]) for nm in P for n in sizes[nm]})


def replacements():
    """Added after the first run (repo rule 'add AND replace'): swap part of the piece each one overlaps most."""
    from portfolio import load_mc
    from build_lab import REPORTS
    from combine_levers_test import ONB30
    ctx = BB.setup(); g, trr = ctx["g"], ctx["trr"]; atr = g.daily_atr(15)
    P = {}
    T = BN.run(BN.series("rth"), shorts=False, early_flat=True); T = T[T.date >= "2018-01-01"]
    nb = pd.DataFrame(dict(day=T.row.values, j0=T.j0.values, j1=T.j1.values, side=T.side.values, entry=T.entry.values - T.side.values * 0.25, exit=T.exit.values,
                           kind=np.where(T.kind == "target", 1, np.where(T.kind == "stop", 0, 2))))
    rs = pd.read_csv("scratch_data/rs_trades.csv"); rs = rs.assign(kind=rs.kind.map({"stop": 0, "target": 1, "flat": 2}))[["day", "j0", "j1", "side", "entry", "exit", "kind"]]
    for nm, t in (("NB", nb), ("RS", with_slippage(rs)), ("DT", DTB.dt_trades(g)), ("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB", with_slippage(load_mc(g, ONB30)))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    q = lambda d: np.floor(d / (np.nan_to_num(0.25 * atr[trr], nan=1e12) * 2))[:, None]          # ONB contracts for $d risk
    C = {"VB 20 -> 15 + noise-area 2": (-5 * P["VB"][0] + 2 * P["NB"][0], -5 * P["VB"][1] + 2 * P["NB"][1]),
         "VB 20 -> 15 + Dual Thrust 2": (-5 * P["VB"][0] + 2 * P["DT"][0], -5 * P["VB"][1] + 2 * P["DT"][1]),
         "VB 20 -> 15 + noise-area 2 + Dual Thrust 2": (-5 * P["VB"][0] + 2 * P["NB"][0] + 2 * P["DT"][0], -5 * P["VB"][1] + 2 * P["NB"][1] + 2 * P["DT"][1]),
         "ONB $2,750 -> $2,000 + Relative Strength 2": ((q(2000) - q(2750)) * P["ONB"][0] + 2 * P["RS"][0], (q(2000) - q(2750)) * P["ONB"][1] + 2 * P["RS"][1])}
    BB.eval_bench(ctx, C, label="150K evaluation (set + Twin 2), replacements")


if __name__ == "__main__" and "--replace" in sys.argv:
    replacements()
