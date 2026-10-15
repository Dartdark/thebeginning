"""Twin Continuation on an Apex 150K account (user, 2026-10-15: 'would Twin work in a bigger 150k account with 4k max
drawdown and 2k DLL?'). On the 50K Twin alone peaked at ~$3k / $7k (1y / 2y) at 3 MNQ: 4 MNQ blew 38-41% and the 50%
consistency rule bit (analysis/twin_apex_test.py). The 150K doubles the drawdown room, so Twin can run about twice the size.
150K rules used (user: $4,000 drawdown, $2,000 DLL; the rest from 2026 third-party guides, CONFIRM in the dashboard):
  evaluation  +$9,000 target, $4,000 drawdown trailing the end-of-day balance (locks at $150,100), $2,000 daily loss
              limit (pauses the day), 30 calendar days = 21 trading days
  funded PA   same drawdown / lock / DLL; payout when the balance >= $154,600 (safety net $154,100 + $500), 5 days of
              >= $350 since the last payout, best day < 50% of the profit since the last payout; 6 payouts, $20,500 in
              all (assumed ladder 2,400 / 2,400 / 3,100 / 3,900 / 3,900 / 4,800, the 50K ladder scaled), then it closes
Twin as MultiCharts-confirmed (v2.1 defaults) and with the breakout stop capped at 1 ATR ('cap1'); fixed MNQ sizes; costs
as always; a day = its lowest open-equity P&L and its close (paths from twin_continuation_bench.grids). Every start day
2018-2025 (1 year) / 2018-2024 (2 years); evaluation every start day 2018-2026. Funded also with cushion sizing.
  python3 analysis/twin_150k_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc
from twin_continuation_bench import grids

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
ST, DD, DLL, LOCK, TGT = 150_000.0, 4_000.0, 2_000.0, 150_100.0, 9_000.0
SAFE, MINREQ, QDAY, CAPS = 154_100.0, 154_600.0, 350.0, [2400.0, 2400.0, 3100.0, 3900.0, 3900.0, 4800.0]


def evaluation(W, R, s, q, D):
    bal = ST; floor = ST - DD
    for n, d in enumerate(range(s, min(s + 21, D)), 1):
        w, r = W[d] * q, R[d] * q; lim = max(floor, bal - DLL)
        hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
        win = np.nonzero(bal + r - ST >= TGT)[0]; jp = win[0] if len(win) else len(w)
        if jp < jb: return "pass", n
        if jb < len(w):
            if lim == floor: return "fail", n
            bal = lim
        else: bal += r[-1]
        floor = max(floor, min(bal - DD, LOCK))
    return ("time", 21) if s + 21 <= D else None


def funded(low, close, s, h, q, ref=None):
    bal = ST; floor = ST - DD; n = 0; paid = 0.0; first = -1; qual = 0; since = 0.0; best = 0.0
    for d in range(s, min(s + h, len(close))):
        k = q if ref is None else q * min(1.0, max(0.5, (bal - floor) / ref))
        lo, cl = low[d] * k, close[d] * k
        if bal + lo <= floor: return paid, n, True, first
        day = -DLL if lo <= -DLL else cl
        bal += day; since += day; best = max(best, day); qual += day >= QDAY
        floor = max(floor, min(bal - DD, LOCK))
        if n < 6 and bal >= MINREQ and qual >= 5 and since > 0 and best < 0.5 * since:
            amt = min(CAPS[n], bal - SAFE)
            if amt >= 500:
                bal -= amt; paid += amt; n += 1; qual = 0; since = 0.0; best = 0.0
                if first < 0: first = d - s
                if n == 6: return paid, n, False, first
    return paid, n, False, first


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); B = tc.flatten(g); tr = g.trading; yr = pd.DatetimeIndex(g.ts[tr]).year; D = len(tr)
    for nm, kw in (("Twin v2.1 (MC-confirmed)", {}), ("Twin cap1 (stop <= 1 ATR)", dict(max_stop_mult=1.0))):
        T = tc.simulate(B, **kw); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
        W, Rr = grids(g, B, T); W, Rr = W[tr] / 10, Rr[tr] / 10                 # per MNQ
        low, close = W.min(1), Rr[:, -1]
        x = pd.Series(close, index=pd.DatetimeIndex(g.ts[tr]))[yr >= 2018]
        print(f"\n== {nm}: {len(T)} trades, ${T.net.mean():.0f} a trade per NQ; per MNQ: worst day ${low[yr >= 2018].min():,.0f}, "
              f"worst 20-day drawdown ${(x.cumsum() - x.cumsum().cummax()).min():,.0f}")
        print("   Evaluation (150K, every start day 2018-26):")
        for q in (6, 8, 10, 12, 15, 20):
            res = [evaluation(W, Rr, s, q, D) for s in range(D)]
            ok = np.array([r is not None for r in res]) & (yr >= 2018); o = np.array([r[0] if r else "" for r in res]); ps = o == "pass"
            dd = np.array([r[1] if r else 0 for r in res])
            print(f"      {q:2d} MNQ: pass {ps[ok].mean():5.1%} (2018-22 {ps[ok & (yr < 2023)].mean():5.1%}, 2023-26 {ps[ok & (yr >= 2023)].mean():5.1%}), "
                  f"blown {(o[ok] == 'fail').mean():5.1%}, out of time {(o[ok] == 'time').mean():5.1%}, median days {np.median(dd[ok & ps]) if ps[ok].any() else np.nan:.0f}")
        print("   Funded PA (150K):")
        for q in (4, 6, 8, 10, 12):
            for h, lbl in ((252, "1y"), (504, "2y")):
                st = [s for s in range(D - h) if yr[s] >= 2018]
                rr = [funded(low, close, s, h, q) for s in st]
                paid = np.array([r[0] for r in rr]); bl = np.array([r[2] for r in rr]); n6 = np.array([r[1] == 6 for r in rr])
                fst = np.array([r[3] for r in rr]); fst = fst[fst >= 0]
                if lbl == "1y": line = f"      {q:2d} MNQ: 1y ${paid.mean():,.0f} (blown {bl.mean():.0%}, paid {np.mean(paid > 0):.0%}, median days to 1st {np.median(fst) if len(fst) else np.nan:.0f})"
                else: print(line + f" | 2y ${paid.mean():,.0f} (blown {bl.mean():.0%}, all 6 {n6.mean():.0%})", flush=True)
        print("   Funded PA (150K), cushion sizing as in our funded plan: full size from a $3,000 cushion, half size below $1,500:")
        for q in (6, 8, 10):
            out = []
            for h in (252, 504):
                st = [s for s in range(D - h) if yr[s] >= 2018]; rr = [funded(low, close, s, h, q, ref=3000.0) for s in st]
                paid = np.array([r[0] for r in rr]); bl = np.array([r[2] for r in rr]); n6 = np.array([r[1] == 6 for r in rr])
                out.append(f"${paid.mean():,.0f} (blown {bl.mean():.0%}, paid {np.mean(paid > 0):.0%}, all 6 {n6.mean():.0%})")
            print(f"      {q:2d} MNQ full size: 1y {out[0]} | 2y {out[1]}", flush=True)
