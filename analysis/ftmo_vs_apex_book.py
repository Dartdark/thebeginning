"""Our live #5 book (bench150.LIVE_EVAL) under FTMO 2-Step rules vs the Apex 150K evaluation (user upload 2026-11-13: the Bridge's
'Propfirms as a business, live 007', papers/bridge_propfirms_as_a_business_live007.pdf). Same NQ trade paths, costs in (NQ costs, NOT
the CFD spread: our strategies are untested on US100). FTMO 2-Step, published rules as in the deck:
  phase 1 target +10%, phase 2 target +5% (balance reset to the start), max loss 10% of the start, FIXED (equity incl. open trades);
  daily loss 5% of the start, measured from the day's starting balance incl. open P&L: touching it ENDS the account (Apex only stops the day);
  min 4 trading days per phase, no time limit (capped here at 120 trading days per phase; 'time' = still going).
Sizes: the book as live (sized for Apex 150K) on FTMO 100K and 200K, and scaled x0.67 / x1.33 on 100K. Apex 150K: the same engine as
eval_size_combo (21 days, $4,000 EOD trail, $2,000 daily pause). Starts 2018 -> 2026-01 (room for 120 + 120 days).
  tools/run_stamped.sh analysis/ftmo_vs_apex_book.py > analysis/outputs/ftmo_vs_apex_book_output.txt
"""
import sys; sys.path.insert(0, "analysis"); sys.argv = ["x"]
import numpy as np, numba as nb
src = open("analysis/eval_size_combo.py").read().split("rows = []")[0].replace("cache=True", "cache=False")
ns = {}; exec(compile(src, "eval_size_combo_head", "exec"), ns)
book, fresh, LIVE, dts, D = (ns[k] for k in ("book", "fresh", "LIVE", "dts", "D"))
print(__doc__.split("\n")[0])


@nb.njit
def phase(W, R, s, H, start, tgt, maxloss, daily, mindays):
    """returns (result 1 pass / -1 fail / 0 time, days used, end day index)"""
    bal = start; floor = start - maxloss; n = 0
    for d in range(s, min(s + H, W.shape[0])):
        n += 1; day0 = bal; dl = day0 - daily
        for j in range(1440):
            eq = bal + W[d, j]
            if eq <= floor or eq <= dl: return -1, n, d
        for j in range(1440):
            if bal + R[d, j] >= start + tgt and n >= mindays: return 1, n, d
        bal += R[d, 1439]
    return 0, n, s + H - 1


@nb.njit
def ftmo_all(W, R, size, H=120):
    D = W.shape[0]; res = np.full(D, -9.0); days = np.zeros(D)
    for s in range(D - 2 * H):
        r1, n1, e1 = phase(W, R, s, H, size, 0.10 * size, 0.10 * size, 0.05 * size, 4)
        if r1 != 1: res[s] = r1; days[s] = n1; continue
        r2, n2, e2 = phase(W, R, e1 + 1, H, size, 0.05 * size, 0.10 * size, 0.05 * size, 4)
        res[s] = 1.0 if r2 == 1 else r2; days[s] = n1 + n2
    return res, days


yr = dts.year; ok = (yr >= 2018) & (dts <= "2026-01-31")
W0, R0 = book(LIVE)
fa = fresh(W0, R0); okA = ok & (fa >= 0)
print(f"book {LIVE}")
print(f"Apex 150K evaluation (21 days, EOD trail $4,000): pass {fa[okA].mean():.1%}  (2018-22 {fa[okA & (yr <= 2022)].mean():.1%}, 2023+ {fa[okA & (yr >= 2023)].mean():.1%})")
for nm, size, k in (("FTMO 100K, live sizes", 100000.0, 1.0), ("FTMO 100K, sizes x0.67", 100000.0, 0.67), ("FTMO 100K, sizes x1.33", 100000.0, 1.33),
                    ("FTMO 200K, live sizes", 200000.0, 1.0), ("FTMO 200K, sizes x1.5", 200000.0, 1.5)):
    r, dd = ftmo_all(W0 * k, R0 * k, size); m = ok & (r > -9)
    p = r[m] == 1; f = r[m] == -1
    print(f"{nm:<24} pass {p.mean():5.1%} fail {f.mean():5.1%} still going {(r[m] == 0).mean():5.1%} | median trading days to pass {np.median(dd[m][p]):.0f} "
          f"| 2018-22 {np.mean(r[m & (yr <= 2022)] == 1):.1%} 2023+ {np.mean(r[m & (yr >= 2023)] == 1):.1%}")
# what ends FTMO accounts: the daily 5% or the 10% floor?
@nb.njit
def why(W, R, size, H=120):
    D = W.shape[0]; out = np.zeros((D, 2))
    for s in range(D - 2 * H):
        bal = size; floor = size * 0.9
        for d in range(s, s + H):
            dl = bal - 0.05 * size; hit = 0
            for j in range(1440):
                eq = bal + W[d, j]
                if eq <= floor: hit = 2; break
                if eq <= dl: hit = 1; break
            if hit: out[s, hit - 1] = 1; break
            if bal + R[d, 1439] - size >= 0.10 * size: break
            bal += R[d, 1439]
    return out
w = why(W0, R0, 100000.0); m = ok & (np.arange(D) < D - 240)
print(f"FTMO 100K live sizes, phase 1 failures by cause: daily 5% loss {w[m, 0].mean():.1%} of starts, 10% floor {w[m, 1].mean():.1%}")
print(f"worst single day of the book (intraday low): ${W0.min(axis=1).min():,.0f}; days with an intraday low below -$5,000: {(W0.min(axis=1) < -5000).sum()} of {(yr >= 2018).sum()}")
