"""Codex weekly review 2026-11-06 #1: our evaluation engines locked the trailing floor at start + $100 (a funded-PA rule);
Apex evaluations keep trailing until the target (Codex eval audit 2026-11-04, Apex floor page). This reruns the plan and the
recent evaluation variants with cushion_cap_bench.run(evalrule=True) next to the old engine. 21 sessions kept (~30 calendar
days); the audit's other items (DLL fill at the limit, 30-calendar-day clock) are NOT fixed here.
  tools/run_stamped.sh analysis/eval_rule_fix_check.py > analysis/outputs/eval_rule_fix_check_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL
from eval_sizing_bench import build
from cushion_cap_bench import run, summary, R50, R150

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year
    P = build(g, with_slippage(load_mc(g, REPORTS["VB"][0])), with_slippage(load_mc(g, CL.ONB30)), load_bridge_mc(g),
              with_slippage(load_mc(g, REPORTS["EOS"][0])))
    A = np.nan_to_num(atr[trr], nan=1e12); risk = lambda dollars, m: np.floor(dollars / (m * A * 2))
    stop = {"VB": np.full(D, 150.0), "ONB30": 0.25 * A * 2, "EOS": REPORTS["EOS"][1] * A * 2}
    for lab, r, sets in (("50K", R50, (("plan: VB 8, ONB $1,100", 8, 1100), ("VB 6", 6, 1100), ("ONB $550", 8, 550), ("VB 4, ONB $550", 4, 550))),
                         ("150K", R150, (("plan: VB 20, ONB $2,750", 20, 2750), ("VB 15", 15, 2750), ("ONB $1,400", 20, 1400), ("VB 10, ONB $1,400", 10, 1400)))):
        k = 1 if lab == "50K" else 2.5
        print(f"\n{lab} evaluation, every start day 2018+:")
        for nm, vb, onb in sets:
            q = {"VB": float(vb), "ONB30": risk(onb, 0.25), "MON_BR": 2.0 * k, "EOS": risk(500 * k, REPORTS["EOS"][1])}
            for eng in (False, True):
                print(summary([run(P, q, stop, s, D, r, "none", 0, evalrule=eng) for s in range(D)], yr,
                              f"{nm} [{'eval rule' if eng else 'old lock'}]"), flush=True)
        q = {"VB": 8.0 if lab == "50K" else 20.0, "ONB30": risk(1100 * k, 0.25), "MON_BR": 2.0 * k, "EOS": risk(500 * k, REPORTS["EOS"][1])}
        print(summary([run(P, q, stop, s, D, r, "piece", 0, evalrule=True) for s in range(D)], yr, "plan + cushion cap [eval rule]"), flush=True)
