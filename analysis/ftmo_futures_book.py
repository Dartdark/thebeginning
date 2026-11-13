"""Our live #5 book (bench150.LIVE_EVAL) under FTMO FUTURES evaluation rules vs the Apex 150K evaluation (user 2026-11-13: FTMO has
a futures product; ftmo_vs_apex_book.py used the CFD 2-Step rules, whose fixed floor does NOT apply to futures).
FTMO Futures Growth, as read on ftmo.com/en/futures (pricing + trading-objectives pages, 2026-11-13):
  150K: target $9,000 (pass at balance $159,000); max drawdown $4,500 END-OF-DAY TRAILING (floor = highest closing balance - $4,500,
  equity incl. open P&L must never touch it intraday); daily loss limit 'soft, Sim-Funded only' (not modelled in the evaluation);
  CONSISTENCY 40% (evaluation only): best closing day <= 40% of total profit, else keep trading until it is; no time limit, billed
  $229 / month (capped here at 120 trading days; 'time' = still going). 'Drawdown trailing lock': assumed the floor stops at the
  start balance (as Apex); 100K ($6,000 / $3,000) shown as well. Max contracts not modelled (150K cap not read; book max 25 MNQ).
Same NQ trade paths and costs as the Apex engine (eval_size_combo). Starts 2018 -> 2026-01.
  tools/run_stamped.sh analysis/ftmo_futures_book.py > analysis/outputs/ftmo_futures_book_output.txt
"""
import sys; sys.path.insert(0, "analysis"); sys.argv = ["x"]
import numpy as np, numba as nb
src = open("analysis/eval_size_combo.py").read().split("rows = []")[0].replace("cache=True", "cache=False")
ns = {}; exec(compile(src, "eval_size_combo_head", "exec"), ns)
book, fresh, LIVE, dts, D = (ns[k] for k in ("book", "fresh", "LIVE", "dts", "D"))
print(__doc__.split("\n")[0])


@nb.njit
def ftmo_fut(W, R, start, tgt, dd, cons, H=120):
    """per start day: result 1 pass / -1 fail / 0 time; trading days used; 1 if the target was reached but consistency delayed it"""
    n_ = W.shape[0]; res = np.full(n_, -9.0); days = np.zeros(n_); held = np.zeros(n_)
    for s in range(n_ - H):
        bal = start; hi = start; best = 0.0; r = 0.0; n = 0; reached = 0
        for d in range(s, s + H):
            n += 1; floor = min(hi - dd, start)
            failed = False
            for j in range(1440):
                if bal + W[d, j] <= floor: failed = True; break
            if failed: r = -1.0; break
            pnl = R[d, 1439]; bal += pnl; hi = max(hi, bal); best = max(best, pnl)
            tot = bal - start
            if tot >= tgt:
                if best <= cons * tot: r = 1.0; break
                reached = 1
        res[s] = r; days[s] = n; held[s] = reached
    return res, days, held


yr = dts.year; ok = (yr >= 2018) & (dts <= "2026-01-31")
W0, R0 = book(LIVE)
fa = fresh(W0, R0); okA = ok & (fa >= 0)
print(f"book {LIVE}")
print(f"Apex 150K evaluation (21 days, EOD trail $4,000): pass {fa[okA].mean():.1%}  (2018-22 {fa[okA & (yr <= 2022)].mean():.1%}, 2023+ {fa[okA & (yr >= 2023)].mean():.1%})")
for nm, start, tgt, dd, k in (("FTMO Fut 150K, live sizes", 150000.0, 9000.0, 4500.0, 1.0),
                              ("FTMO Fut 150K, sizes x0.75", 150000.0, 9000.0, 4500.0, 0.75),
                              ("FTMO Fut 150K, no consistency", 150000.0, 9000.0, 4500.0, 1.0),
                              ("FTMO Fut 100K, sizes x0.67", 100000.0, 6000.0, 3000.0, 0.67)):
    cons = 1.0 if "no consistency" in nm else 0.40
    r, dd_, h = ftmo_fut(W0 * k, R0 * k, start, tgt, dd, cons); m = ok & (r > -9)
    p = r[m] == 1
    med = np.median(dd_[m][p]) if p.any() else np.nan
    months = np.ceil(dd_[m] / 21.0)
    print(f"{nm:<30} pass {p.mean():5.1%} fail {(r[m] == -1).mean():5.1%} still going {(r[m] == 0).mean():5.1%} | median days to pass {med:.0f} "
          f"| pass within 21 days {np.mean((r[m] == 1) & (dd_[m] <= 21)):.1%} | consistency delayed {h[m].mean():.1%} of starts "
          f"| mean months billed {months.mean():.1f} | 2018-22 {np.mean(r[m & (yr <= 2022)] == 1):.1%} 2023+ {np.mean(r[m & (yr >= 2023)] == 1):.1%}")
