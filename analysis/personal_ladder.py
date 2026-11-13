"""Personal-account ladder rebuilt on the current 19-piece book (2026-10-31, Codex portfolio audit step 3: the old ladder's
'16-piece core' predates Swing Target and PAPERTREND). Daily $ per 1 micro from analysis/personal_portfolio.py (2018-01 ->
2026-10). Greedy: start from the single best piece, each step adds the piece that keeps the 1-year Monte Carlo return / DD p95
highest (20-day blocks, 2,000 runs, no trailing limit). Capital = DD p95 / 0.20 (the 20% rule). Pieces still on the forward log
(FC 2B, Kusho v9, S47 v2, S30 IBS) are not cleared to trade: they come only after every cleared piece, in a second tier.
  python3 analysis/personal_ladder.py > analysis/outputs/personal_ladder_output.txt
"""
import sys, io, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np
import montecarlo as MC

FWD = ["FC2B", "Kusho", "S47", "S30"]


def mc(x):
    d = MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1)
    return d["pnl_p50"], d["pnl_p5"], d["dd_p95"]


def ladder(P, pool, start=()):
    chosen, rows = list(start), []
    while pool:
        best = None
        for k in pool:
            p50, p5, dd = mc(P[chosen + [k]].sum(axis=1))
            if best is None or p50 / dd > best[1]: best = (k, p50 / dd, p50, p5, dd)
        k, rd, p50, p5, dd = best; chosen.append(k); pool = [x for x in pool if x != k]
        rows.append((k, len(chosen), p50, p5, dd, rd))
    return chosen, rows


def holdout(P):
    """Codex 2026-10-31: the ladder picks subsets on the same history it reports. Pick the order on 2018-22 only, then score
    that order on 2023+ (never seen) next to the full-history order, and the 2023+ capital line of each row."""
    A, B = P[P.index.year <= 2022], P[P.index.year >= 2023]
    cleared = [c for c in P.columns if c not in FWD]
    chA, _ = ladder(A, cleared); chF, _ = ladder(P, cleared)
    print("\nHoldout: order chosen on 2018-22, scored on 2023+ (vs the full-history order, also scored on 2023+)")
    print(f"{'n':>3}  {'2018-22 pick':<22}{'2023+ $ p50':>11} {'ret/DD':>6} {'capital':>9}   {'full-history pick':<22}{'2023+ $ p50':>11} {'ret/DD':>6} {'capital':>9}")
    for n in range(1, len(cleared) + 1):
        a = mc(B[chA[:n]].sum(axis=1)); f = mc(B[chF[:n]].sum(axis=1))
        print(f"{n:>3}  {chA[n - 1]:<22}${a[0]:>10,.0f} {a[0] / a[2]:>6.2f} ${a[2] / 0.2:>8,.0f}   {chF[n - 1]:<22}${f[0]:>10,.0f} {f[0] / f[2]:>6.2f} ${f[2] / 0.2:>8,.0f}")
    print(f"   same first 12 pieces (any order): {sorted(chA[:12]) == sorted(chF[:12])}; "
          f"shared in the first 4: {sorted(set(chA[:4]) & set(chF[:4]))}; first 12: {len(set(chA[:12]) & set(chF[:12]))} of 12")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        P = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")["P"]
    cleared = [c for c in P.columns if c not in FWD]
    ch, r1 = ladder(P, cleared)
    _, r2 = ladder(P, FWD, start=ch)
    print(f"\n{'step':>4}  {'+ piece':<22}{'pieces':>6}  {'$ a year p50':>12}  {'bad year p5':>11}  {'DD p95':>8}  {'ret/DD':>6}  {'capital (20%)':>13}")
    for tier, rows in (("cleared", r1), ("forward log (not cleared)", r2)):
        print(f"-- {tier}")
        for i, (k, n, p50, p5, dd, rd) in enumerate(rows, 1):
            print(f"{i:>4}  {k:<22}{n:>6}  ${p50:>11,.0f}  ${p5:>10,.0f}  ${dd:>7,.0f}  {rd:>6.2f}  ${dd / 0.2:>12,.0f}")
    holdout(P)

