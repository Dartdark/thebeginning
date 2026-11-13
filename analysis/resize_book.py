"""Re-optimise contract sizes after ANY plan change (user rule 2026-11-12: 'every time a change is made to a plan, rerun contract size
to optimize for that change'). Reads the live book from bench150.LIVE_EVAL (so it can't run on an old plan), then:
  1. one at a time: each piece at 0 / 0.5x / 1x / 1.5x / 2x its live size (risk pieces in $, rounded to $250; fixed to whole micros)
  2. greedy coordinate search from the live sizes, ranked on fresh evaluations starting 2018-22 (design): each round tries every
     piece one step up / down, keeps the best move if it adds >= 0.3 pt, max 12 rounds
  3. the search result judged once on starts 2023 -> 2026-09 (holdout) and from the live account's state now; paired diffs vs the
     live sizes with 60-day block bands. RECOMMEND a change only if the holdout band AND the account-now band are above 0.
Account state: edit NOW below (balance, floor) when it changes.  Funded / personal plans: their own benches (bench150.funded_bench /
personal); this script is the evaluation book.
  tools/run_stamped.sh analysis/resize_book.py > analysis/outputs/resize_book_output.txt
"""
import sys; sys.path.insert(0, "analysis"); sys.argv = ["x"]
import numpy as np
NOW = dict(bal=147998.08, floor=146000.0, target=159000.0)          # account #5, 2026-11-12
src = open("analysis/eval_size_combo.py").read().split("rows = []")[0].replace("cache=True", "cache=False")
src = src.replace("now = lambda W, R: ev_all(W, R, 20, 147998.08, 146000.0, 159000.0, 4000.0, 2000.0, False)",
                  f"now = lambda W, R: ev_all(W, R, 20, {NOW['bal']}, {NOW['floor']}, {NOW['target']}, 4000.0, 2000.0, False)")
ns = {}; exec(compile(src, "eval_size_combo_head", "exec"), ns)
book, fresh, now, DES, HOL, NOWV, LIVE, RM = (ns[k] for k in ("book", "fresh", "now", "DES", "HOL", "NOWV", "LIVE", "RM"))
def band(d):
    rng = np.random.default_rng(1); n = len(d); nb_ = int(np.ceil(n / 60)); st = rng.integers(0, n, (1000, nb_))
    mm = d[((st[:, :, None] + np.arange(60)) % n).reshape(1000, -1)[:, :n]].mean(1); return np.percentile(mm, 5), np.percentile(mm, 95)
def step(k): return 250 if k in RM else 1
def rnd(k, v): return max(0, int(round(v / step(k))) * step(k))
W0, R0 = book(LIVE); f0 = fresh(W0, R0); n0 = now(W0, R0)
print(f"live {LIVE}: fresh 18-22 {f0[DES].mean():.1%} 23-26 {f0[HOL].mean():.1%} | account now {n0[NOWV].mean():.1%}")
print("\n== 1. one piece at a time (diff vs live: 18-22 / 23-26 [band] / account now [band])")
for k, v in LIVE.items():
    for m in (0, 0.5, 1.5, 2):
        nv = rnd(k, v * m)
        if nv == v: continue
        W, R = book({**LIVE, k: nv}); f = fresh(W, R); n = now(W, R)
        d1 = f[DES] - f0[DES]; d2 = f[HOL] - f0[HOL]; d3 = n[NOWV] - n0[NOWV]; b2 = band(d2); b3 = band(d3)
        print(f"   {k:<7} {nv:>5}: {d1.mean():+.1%} / {d2.mean():+.1%} [{b2[0]:+.1%},{b2[1]:+.1%}] / {d3.mean():+.1%} [{b3[0]:+.1%},{b3[1]:+.1%}]", flush=True)
print("\n== 2. greedy search on 2018-22 starts")
cur = dict(LIVE); best = f0[DES].mean()
for it in range(12):
    moves = []
    for k in cur:
        for s in (-1, 1):
            nv = cur[k] + s * (step(k) if k in RM else 1) * (2 if k in RM else 1)
            if nv < 0: continue
            W, R = book({**cur, k: nv}); moves.append((fresh(W, R)[DES].mean(), k, nv))
    sc, k, nv = max(moves)
    if sc < best + 0.003: break
    cur[k] = nv; best = sc; print(f"   round {it + 1}: {k} -> {nv}  (2018-22 {sc:.1%})", flush=True)
print(f"\n== 3. search result {cur}")
if cur == LIVE: print("   no move adds >= 0.3 pt on 2018-22: KEEP the live sizes")
else:
    W, R = book(cur); f = fresh(W, R); n = now(W, R); d2 = f[HOL] - f0[HOL]; d3 = n[NOWV] - n0[NOWV]; b2 = band(d2); b3 = band(d3)
    print(f"   18-22 {f[DES].mean():.1%} | 23-26 {f[HOL].mean():.1%} ({d2.mean():+.1%} [{b2[0]:+.1%},{b2[1]:+.1%}]) | account now {n[NOWV].mean():.1%} ({d3.mean():+.1%} [{b3[0]:+.1%},{b3[1]:+.1%}])")
    print("   RECOMMEND the change" if b2[0] > 0 and b3[0] > 0 else "   NOT recommended: a band includes 0 (keep the live sizes)")
