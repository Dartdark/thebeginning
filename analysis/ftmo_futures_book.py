"""Our live #5 book on FTMO FUTURES 150K (user 2026-11-13: 'ftmo has a futures version'). Rules from fundedtrading.com/propfirm/ftmo-futures
(third-party page, 'checked 7 Sep 2026 against FTMO's own rules pages'; NOT verified on ftmo.com):
  Growth 150K: target $9,000, max drawdown $5,000 trailing on end-of-day balance, locks at the start balance; NO daily loss limit in
               the evaluation; consistency: best day <= 40% of total profit (blocks the pass, not a breach)
  Pro 150K:    target $9,000, max drawdown $6,000 trailing EOD (locks at the start); HARD daily loss $2,000 (ends the evaluation);
               consistency 50%
  Both: intraday equity checked against the floor; time limit unclear on the page (30 days vs none): both shown (21 and 60 trading days);
  flat by 15:10 CT (our pieces are flat by 15:00 except check Twin); contract cap 15 minis = 150 micros (book max ~60).
Apex 150K for reference (eval_size_combo engine: $4,000 EOD trail, $2,000 daily PAUSE, 21 days, no consistency rule). Pass checked at the
end of a day for FTMO (consistency needs the day's close); same NQ paths, costs in.
  tools/run_stamped.sh analysis/ftmo_futures_book.py > analysis/outputs/ftmo_futures_book_output.txt
"""
import sys; sys.path.insert(0, "analysis"); sys.argv = ["x"]
import numpy as np, numba as nb
src = open("analysis/eval_size_combo.py").read().split("rows = []")[0].replace("cache=True", "cache=False")
ns = {}; exec(compile(src, "eval_size_combo_head", "exec"), ns)
book, fresh, LIVE, dts, D = (ns[k] for k in ("book", "fresh", "LIVE", "dts", "D"))
print(__doc__.split("\n")[0])


@nb.njit
def ftmo_fut(W, R, H, start, tgt, trail, daily, consist):
    D = W.shape[0]; res = np.full(D, -9.0); days = np.zeros(D)
    for s in range(D - H):
        bal = start; floor = start - trail; best = 0.0; r = 0.0; n = 0
        for d in range(s, s + H):
            n += 1; day0 = bal; dead = False
            for j in range(1440):
                eq = bal + W[d, j]
                if eq <= floor or (daily > 0 and eq <= day0 - daily): dead = True; break
            if dead: r = -1.0; break
            bal += R[d, 1439]; best = max(best, bal - day0)
            if bal - start >= tgt and best <= consist * (bal - start): r = 1.0; break
            floor = max(floor, min(bal - trail, start))
        res[s] = r; days[s] = n
    return res, days


yr = dts.year; ok = (yr >= 2018) & (dts <= "2026-06-30")
W0, R0 = book(LIVE)
fa = fresh(W0, R0); m = ok & (fa >= 0)
print(f"book {LIVE}\nApex 150K (21 days): pass {fa[m].mean():.1%} (2018-22 {fa[m & (yr <= 2022)].mean():.1%}, 2023+ {fa[m & (yr >= 2023)].mean():.1%})")
for plan, trail, daily, cons in (("Growth 150K", 5000.0, 0.0, 0.40), ("Pro 150K", 6000.0, 2000.0, 0.50)):
    for H in (21, 60):
        for k in (1.0, 0.75):
            r, dd = ftmo_fut(W0 * k, R0 * k, H, 150000.0, 9000.0, trail, daily, cons); mm = ok & (r > -9)
            p = r[mm] == 1
            print(f"FTMO Futures {plan:<12} {H:>2} days, sizes x{k:<4}: pass {p.mean():5.1%} fail {np.mean(r[mm] == -1):5.1%} open {np.mean(r[mm] == 0):5.1%} | "
                  f"median days to pass {np.median(dd[mm][p]):.0f} | 2018-22 {np.mean(r[mm & (yr <= 2022)] == 1):.1%} 2023+ {np.mean(r[mm & (yr >= 2023)] == 1):.1%}")
# how often the consistency rule is what blocks (at H 60, live sizes): rerun without it
for plan, trail, daily, cons in (("Growth 150K", 5000.0, 0.0, 0.40), ("Pro 150K", 6000.0, 2000.0, 0.50)):
    r1, _ = ftmo_fut(W0, R0, 60, 150000.0, 9000.0, trail, daily, cons); r0, _ = ftmo_fut(W0, R0, 60, 150000.0, 9000.0, trail, daily, 1e9); mm = ok & (r1 > -9)
    print(f"{plan}: without the consistency rule {np.mean(r0[mm] == 1):.1%} vs with {np.mean(r1[mm] == 1):.1%} (60 days)")
print(f"book days with an intraday low below -$2,000: {(W0.min(axis=1) < -2000).sum()} of {(yr >= 2018).sum()} trading days (Pro's hard daily limit)")
