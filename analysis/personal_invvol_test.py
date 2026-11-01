"""Personal book: equal 1-micro weights vs inverse-volatility weights (user 2026-11-01, after @RitOnchain's position-sizing
card, method 6). Weights are set on 2018-22 only (each piece's daily $ stdev per micro, w_i ~ 1/sigma_i) and scored on
2023+ (never seen). Same total micros as the equal book at each size m (m micros per piece on average), rounded to whole
micros (0 allowed: a piece can drop out at small sizes). Measures: 1-year MC median $ / DD p95 (ret/DD, as
analysis/personal_ladder.py), capital = DD p95 / 0.20, Sharpe of daily $. Books: the 15 cleared pieces and the full 19.
  python3 analysis/personal_invvol_test.py > analysis/outputs/personal_invvol_test_output.txt
"""
import sys, io, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np
import montecarlo as MC

FWD = ["FC2B", "Kusho", "S47", "S30"]


def score(x):
    d = MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1)
    return d["pnl_p50"], d["dd_p95"], x.mean() / x.std() * np.sqrt(252)


def sizes(sig, m):
    w = (1 / sig) / (1 / sig).sum()
    return np.round(w * m * len(sig)).astype(int)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        P = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")["P"]
    A, B = P[P.index.year <= 2022], P[P.index.year >= 2023]
    for name, cols in (("15 cleared pieces", [c for c in P.columns if c not in FWD]), ("full 19", list(P.columns))):
        sig = A[cols].std()
        print(f"\n{name}: 2018-22 daily stdev per micro, lowest {sig.idxmin()} ${sig.min():.0f}, highest {sig.idxmax()} ${sig.max():.0f}")
        print(f"   {'size':<26}{'book':<10}{'2023+ $ p50':>12}{'DD p95':>9}{'ret/DD':>8}{'Sharpe':>8}{'capital':>10}   micros")
        for m in (1, 2, 4, 10):
            eq = np.full(len(cols), m); iv = sizes(sig.to_numpy(), m)
            for lab, n in (("equal", eq), ("inv-vol", iv)):
                x = (B[cols] * n).sum(axis=1); p50, dd, sh = score(x)
                print(f"   {m:>2} micros/piece avg     {lab:<10}${p50:>11,.0f}${dd:>8,.0f}{p50 / dd:>8.2f}{sh:>8.2f}${dd / 0.2:>9,.0f}   {int(n.sum())}"
                      + ("" if lab == "equal" else f"  (dropped: {', '.join(c for c, k in zip(cols, n) if k == 0) or 'none'})"))
        w = (1 / sig) / (1 / sig).sum() * len(cols)
        print("   inv-vol weight vs equal (1.0 = same): " + ", ".join(f"{c} {v:.2f}" for c, v in w.sort_values().items()))
