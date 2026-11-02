"""Exact generator of the adopted inverse-vol ladder in personal_strategies/PORTFOLIO.md (Codex review 2026-11-01 #7: the
table cited personal_invvol_confirm.py but was not its direct output). Two separate things per row:
  - DEPLOY vector (what to trade from 2026): micros per piece = round(capped 1/stdev weight from 2018-25 x size). It uses all
    history on purpose: it is a forward sizing rule, not a test.
  - SCORE (what to expect): the causal yearly walk-forward of personal_invvol_confirm.book() (each year sized from earlier
    years only), restricted to 2023+. This is the number the table reports. The static 2018-25 vector scored on 2023+ is
    printed too, labelled 'in-sample sizing' (its weights saw 2023-25): a check only, never the table's number.
Note (Codex): 2023+ was already seen when the method / cap / sizes were chosen, so it is not an untouched holdout.
  tools/run_stamped.sh analysis/personal_invvol_ladder.py > analysis/outputs/personal_invvol_ladder_output.txt
"""
import sys, io, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from personal_invvol_confirm import FWD, weights, score, book

ROWS = [("15 cleared, ~2 a piece", "cleared", 2), ("full 19, ~2 a piece", "full", 2), ("15 cleared, ~4 a piece", "cleared", 4),
        ("full 19, ~4 a piece", "full", 4), ("full 19, ~10 a piece", "full", 10)]

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        P = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")["P"]
    print(f"\n{'row':<26}{'causal 2023+ $ p50':>19}{'DD p95':>9}{'capital':>10} | {'in-sample sizing $ p50':>23}{'DD p95':>9}")
    vecs = []
    for name, which, m in ROWS:
        cols = [c for c in P.columns if c not in FWD] if which == "cleared" else list(P.columns)
        x = book(P, cols, m, "inv-vol cap 2x"); c = score(x[x.index.year >= 2023])
        past = P[(P.index.year >= 2018) & (P.index.year < 2026)][cols]
        n = pd.Series(np.round(weights(past.std().to_numpy(), cap=2.0) * m).astype(int), index=cols)
        s = score((P[P.index.year >= 2023][cols] * n.values).sum(axis=1))
        print(f"{name:<26}${c[0]:>18,.0f}${c[1]:>8,.0f}${c[1] / 0.2:>9,.0f} | ${s[0]:>22,.0f}${s[1]:>8,.0f}")
        vecs.append((name, n))
    print("\nDEPLOY vectors (micros per piece, 2018-25 capped weights; MCL for CL fade, MES for ES MOC):")
    for name, n in vecs: print(f"  {name}: " + ", ".join(f"{k} {v}" for k, v in n.items()))
