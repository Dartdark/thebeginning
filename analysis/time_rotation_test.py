"""The Institutional Protocol's Intraday Bias Check + Time Rotation Strategy (user's MultiCharts code, 2026-10-14), ES and NQ
2018-2026, 60-min bars in exchange time (CT). A bar stamped H closes at H; 'next bar at market' = the open at H.
  1. bias check: long H -> H+1 for every hour; net $ per trade by hour, design 2018-22 vs holdout 2023-26
  2. rotation with the code's defaults: long 21:00 -> 05:00, short 06:00 -> 09:00, stop $1,000 / target $5,000 per contract
  3. rotation picked on 2018-22 only: best contiguous long block and best short block (2-10 hours, no overlap), holdout 2023-26
Costs a round trip: ES $5 + 1 tick a fill = $30; NQ $7.25 + 1 tick = $17.25. Stops on 1-min bars (+1 tick), target a limit.
  python3 analysis/time_rotation_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from co_oc_reversal_test import line
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPEC = {"ES": ("ge.pkl", 50.0, 0.25, 5.0), "NQ": ("g24.pkl", 20.0, 0.25, 7.25)}


def trades(g, pv, tick, comm, h0, h1, side, sl=None, tp=None):
    """side trade from the open at h0:00 to the open at h1:00 (crosses midnight if h1 <= h0), every weekday session."""
    ts = pd.DatetimeIndex(g.ts); O, H, L, C = (getattr(g, k).ravel() for k in "ohlc")
    cf = pd.Series(C).ffill().to_numpy(); out = []
    for d in range(1, g.D):
        day = ts[d]
        if day < pd.Timestamp("2018-01-02"): continue
        a = (d - (1 if h1 <= h0 else 0)) * 1440 + h0 * 60; b = d * 1440 + h1 * 60
        if day.dayofweek >= 5: continue
        if h1 <= h0 and ts[d - 1].dayofweek == 5: continue                        # no Saturday evening session
        if np.isnan(O[a]) or not np.isfinite(C[a:b]).any() or np.isnan(cf[b - 1]): continue
        e = O[a] + side * tick; px = None
        if sl is not None or tp is not None:
            sp = e - side * sl / pv if sl else None; tg = e + side * tp / pv if tp else None
            for m in range(a, b):
                if np.isnan(H[m]): continue
                if sp is not None and ((side > 0 and L[m] <= sp) or (side < 0 and H[m] >= sp)):
                    px = (min(O[m], sp) - tick) if side > 0 else (max(O[m], sp) + tick); break
                if tg is not None and ((side > 0 and H[m] >= tg) or (side < 0 and L[m] <= tg)): px = tg; break
        if px is None: px = cf[b - 1] - side * tick                              # out at the open at h1 ~ close of h1-1:59
        out.append((day, (px - e) * side * pv - comm))
    return pd.Series([v for _, v in out], index=pd.DatetimeIndex([d for d, _ in out]))


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for s, (f, pv, tick, comm) in SPEC.items():
        g = pickle.load(open(SP + f, "rb")); print(f"\n===== {s} =====\n1. bias check, net $ per 1-hour long (design 2018-22 | holdout 2023-26):")
        hr = {}
        for h in range(24):
            x = trades(g, pv, tick, comm, h, (h + 1) % 24, 1); hr[h] = x
        tab = pd.DataFrame({h: dict(des=x[x.index.year < 2023].mean(), t_des=x[x.index.year < 2023].mean() / x[x.index.year < 2023].std() * np.sqrt((x.index.year < 2023).sum()),
                                    hold=x[x.index.year >= 2023].mean()) for h, x in hr.items() if len(x) > 50}).T
        tab["same_sign"] = np.sign(tab.des) == np.sign(tab.hold)
        print(tab.round(1).to_string())
        print(f"   hours with design |t| >= 2: {int((tab.t_des.abs() >= 2).sum())}; of those same sign in holdout: {int(((tab.t_des.abs() >= 2) & tab.same_sign).sum())}"
              f"; corr(design, holdout) across hours {tab.des.corr(tab.hold):+.2f}")
        print("2. rotation, code defaults (long 21->05, short 06->09, SL $1,000, TP $5,000):")
        L_ = trades(g, pv, tick, comm, 21, 5, 1, 1000, 5000); S_ = trades(g, pv, tick, comm, 6, 9, -1, 1000, 5000)
        print(line(L_, "long 21:00 -> 05:00", 30)); print(line(S_, "short 06:00 -> 09:00", 30))
        both = pd.concat([L_, S_]); print(line(both, "both legs", 30))
        print("3. rotation picked on 2018-22 (best block by design total, 2-10 hours; then holdout):")
        g1 = {h: hr[h] for h in hr}
        best = {}
        for side in (1, -1):
            cands = []
            for h0 in range(24):
                for n in range(2, 11):
                    hs = [(h0 + k) % 24 for k in range(n)]
                    if 16 in hs: continue                                            # the 16:00-17:00 maintenance break
                    tot = sum(side * hr[h][hr[h].index.year < 2023].sum() for h in hs if h in hr)
                    cands.append((tot, h0, (h0 + n) % 24))
            cands.sort(reverse=True); best[side] = cands[0]
        for side, (tot, h0, h1) in best.items():
            x = trades(g, pv, tick, comm, h0, h1, side)
            print(line(x, f"{'long' if side > 0 else 'short'} {h0:02d}:00 -> {h1:02d}:00 (picked)", 30))
