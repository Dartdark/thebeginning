"""Confirmation of the inverse-vol personal book (analysis/personal_invvol_test.py, 2026-11-01): (1) a yearly walk-forward
(each year Y's weights from daily stdev per micro in all earlier years since 2018, first test year 2020), and (2) a cap of
2x the equal weight per piece (weights scaled to average 1, capped, re-scaled, repeated). Books: the 15 cleared pieces and
the full 19; sizes ~2 and ~4 micros a piece (inverse vol is useless at ~1: rounding drops pieces). Scored on the
walk-forward years 2020-26 and on 2023+ alone; ret/DD = 1-year MC median $ / DD p95, capital = DD p95 / 0.20.
  python3 analysis/personal_invvol_confirm.py > analysis/outputs/personal_invvol_confirm_output.txt
"""
import sys, io, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC

FWD = ["FC2B", "Kusho", "S47", "S30"]


def weights(sig, cap=None):
    w = (1 / sig); w = w / w.mean()
    for _ in range(20):
        if cap is None: break
        w = np.minimum(w, cap); w = w / w.mean()
    return w


def score(x):
    d = MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1)
    return d["pnl_p50"], d["dd_p95"], x.mean() / x.std() * np.sqrt(252)


def book(P, cols, m, how):
    """Daily $ of the book, each year sized from earlier years only (walk-forward)."""
    out = []
    for y in range(2020, P.index.year.max() + 1):
        past, cur = P[(P.index.year >= 2018) & (P.index.year < y)][cols], P[P.index.year == y][cols]
        if how == "equal": n = np.full(len(cols), m)
        else: n = np.round(weights(past.std().to_numpy(), cap=2.0 if how == "inv-vol cap 2x" else None) * m).astype(int)
        out.append((cur * n).sum(axis=1))
    return pd.concat(out)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        P = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")["P"]
    for name, cols in (("15 cleared pieces", [c for c in P.columns if c not in FWD]), ("full 19", list(P.columns))):
        print(f"\n{name} (walk-forward weights, re-estimated each year)")
        print(f"   {'size':<8}{'book':<16}{'2020-26 ret/DD':>15}{'Sharpe':>8}{'2023+ $ p50':>13}{'DD p95':>9}{'ret/DD':>8}{'Sharpe':>8}{'capital':>10}")
        for m in (2, 4):
            for how in ("equal", "inv-vol", "inv-vol cap 2x"):
                x = book(P, cols, m, how); a = score(x); b = score(x[x.index.year >= 2023])
                print(f"   ~{m:<7}{how:<16}{a[0] / a[1]:>15.2f}{a[2]:>8.2f}${b[0]:>12,.0f}${b[1]:>8,.0f}{b[0] / b[1]:>8.2f}{b[2]:>8.2f}${b[1] / 0.2:>9,.0f}")
        past = P[(P.index.year >= 2018) & (P.index.year < 2026)][cols]
        w = pd.Series(weights(past.std().to_numpy(), cap=2.0), index=cols)
        print("   2026 weights, capped (x equal): " + ", ".join(f"{c} {v:.2f}" for c, v in w.sort_values().items()))
