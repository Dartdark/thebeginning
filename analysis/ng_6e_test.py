"""NG / 6E program, round 1 (user 2026-11-10: focus on other markets, low correlation with the book). PRE-REGISTERED (header committed
before the first run). The strategy lab already tested NG / 6E ideas on 2018-22 with the 2023-26 holdout SEALED (lab/ledger.json); two
showed something there, so their holdout is a genuine out-of-sample test now:
H1 NG weekend gap FOLLOW (lab Q021 found the CL-style fade losing on both sides, t -2.2: 'NG weekend gaps continue'). Frame, entry,
   stop and exit exactly as lab Q021 (analysis/lab_Q021.py: Sunday 17:01 gap vs Friday's last price in daily ATR15 units, |gA| >= 0.1,
   entry at the 17:05 bar's open, stop 0.75 ATR, out Monday 09:00 close, roll weekends dropped, 1 NG $10 / tick, $5 a round trip
   + 1 tick per fill) with the side FLIPPED: long up-gaps, short down-gaps.
H2 6E month-end follow into the London 4 pm fix (lab Q003 V1: follow the move from fix-30 to fix-5 minutes, enter fix-4, out at the fix
   close; month-end sessions; gross $32 a trade, placebo p 0.000, but t 0.85 on 58 trades), rules unchanged.
   Gate for H1 / H2 (the lab's stage 3): holdout 2023-26 mean > 0 with t >= 1.5 and PF >= 1.1; 2018-22 shown for reference only.
E1 NEW: 6E London-open breakout: range = high / low of the bars closing 07:01-08:00 London time (the hour before the London open);
   from 08:01 to 11:00 London, a 1-minute close beyond the range -> enter at the next bar's open in that direction, stop at the
   opposite side of the range, out at the close of the bar ending 12:00 London; one trade a day; 6E $125,000 x price, tick 0.00005,
   $5 a round trip + 1 tick per fill. Gate: 2018-26 t >= 1.65 (one pre-registered item), positive in 2018-22 and 2023+, random-side
   placebo p < 0.05 (500 runs). Per contract; 1 M6E = 1/10.
Survivors get the book benches (low correlation is their advantage) and the standing data sweep.
  tools/run_stamped.sh analysis/ng_6e_test.py > analysis/outputs/ng_6e_test_output.txt
"""
import sys, datetime as dt, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
import lab_Q021 as NG
import lab_Q003 as FX

LON, CT = ZoneInfo("Europe/London"), ZoneInfo("America/Chicago")
tt = lambda x: x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
pf = lambda x: x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def show(x, nm):
    if len(x) < 3: print(f"   {nm:<44} n={len(x)}"); return
    by = x.groupby(x.index.year).sum()
    print(f"   {nm:<44} n {len(x):4d} ${x.mean():7.1f} t {tt(x):5.2f} PF {pf(x):4.2f} yrs+ {(by > 0).sum()}/{len(by)} | " + " ".join(f"{y}:{v:+.0f}" for y, v in by.items()))


def lon_col(d, hh, mm):
    t = dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=LON).astimezone(CT)
    return t.hour * 60 + t.minute, t.date() == d


def london_breakout(g, rng=None):
    out = {}
    for r in g.trading:
        d = pd.Timestamp(g.ts[r]).date()
        if d < dt.date(2018, 1, 1) or pd.Timestamp(d).dayofweek > 4: continue
        a, ok1 = lon_col(d, 7, 1); b, ok2 = lon_col(d, 8, 0); x1, ok3 = lon_col(d, 11, 0); xe, ok4 = lon_col(d, 12, 0)
        if not (ok1 and ok2 and ok3 and ok4): continue
        hi, lo = np.nanmax(g.h[r, a:b + 1]), np.nanmin(g.l[r, a:b + 1])
        if not (np.isfinite(hi) and np.isfinite(lo)) or hi <= lo: continue
        side = 0
        for j in range(b + 1, x1 + 1):
            c = g.c[r, j]
            if not np.isfinite(c): continue
            if c > hi: side = 1
            elif c < lo: side = -1
            if side: break
        if not side or j + 1 > xe: continue
        if rng is not None: side = int(rng.choice([-1, 1]))
        e = g.o[r, j + 1]
        if not np.isfinite(e): continue
        e += side * FX.TICK; sp = lo if side > 0 else hi; px = None
        for k in range(j + 1, xe + 1):
            if not np.isfinite(g.c[r, k]): continue
            if (side > 0 and g.l[r, k] <= sp) or (side < 0 and g.h[r, k] >= sp):
                px = (min(g.o[r, k], sp) if side > 0 else max(g.o[r, k], sp)) - side * FX.TICK; break
        if px is None:
            cc = g.c[r, j + 1:xe + 1]; cc = cc[np.isfinite(cc)]
            if not len(cc): continue
            px = cc[-1] - side * FX.TICK
        out[pd.Timestamp(d)] = side * (px - e) * FX.PV - FX.COMM
    return pd.Series(out, dtype=float).sort_index()


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    # ---------------- H1
    print("\nH1. NG weekend gap FOLLOW (lab Q021 frame, side flipped), per NG:")
    S = NG.frame("sun"); out = {}
    for d, row in S.iterrows():
        s = 1 if row.gA >= 0.1 else (-1 if row.gA <= -0.1 else 0)
        if s:
            p = NG.trade(row, s)
            if np.isfinite(p): out[d] = (p, s)
    T = pd.DataFrame(out, index=["net", "side"]).T.astype(float).sort_index(); T = T[T.index.year >= 2018]
    dz, hz = T[T.index.year <= 2022], T[T.index.year >= 2023]
    show(dz.net, "2018-22 (where the idea came from)"); show(hz.net, "HOLDOUT 2023-26 (decides)")
    for sd, nm in ((1, "up-gaps (long)"), (-1, "down-gaps (short)")): show(hz[hz.side == sd].net, f"   holdout {nm}")
    h = hz.net; print(f"   gate: mean > 0, t >= 1.5, PF >= 1.1 -> {'PASS' if (h.mean() > 0 and tt(h) >= 1.5 and pf(h) >= 1.1) else 'FAIL'}")
    # ---------------- H2
    print("\nH2. 6E month-end follow into the London fix (lab Q003 V1), per 6E:")
    g = FX.load(); rows = g.trading; idx = pd.DatetimeIndex(g.ts[rows])
    me = pd.Series(idx, index=idx).groupby(idx.to_period("M")).transform("max").to_numpy() == idx.to_numpy()
    F = np.array([FX.fix_col(t) for t in g.ts[rows]]); yr = idx.year
    x2 = FX.run(g, rows[me & (yr >= 2018)], F[me & (yr >= 2018)], 1)
    show(x2[x2.index.year <= 2022], "2018-22 (where the idea came from)"); h2 = x2[x2.index.year >= 2023]; show(h2, "HOLDOUT 2023-26 (decides)")
    print(f"   gross a trade (holdout) ${h2.mean() + FX.COST:.1f}; gate: {'PASS' if (h2.mean() > 0 and tt(h2) >= 1.5 and pf(h2) >= 1.1) else 'FAIL'}")
    # ---------------- E1
    print("\nE1. 6E London-open breakout (new), per 6E:")
    x3 = london_breakout(g); show(x3, "2018-26"); show(x3[x3.index.year <= 2022], "2018-22"); show(x3[x3.index.year >= 2023], "2023-26")
    rng = np.random.default_rng(31); pm = np.array([london_breakout(g, rng).mean() for _ in range(100)])
    print(f"   random side (100 runs): 95th ${np.percentile(pm, 95):.1f}; real ${x3.mean():.1f}; p {np.mean(pm >= x3.mean()):.3f}")
    ok = tt(x3) >= 1.65 and x3[x3.index.year <= 2022].mean() > 0 and x3[x3.index.year >= 2023].mean() > 0 and np.mean(pm >= x3.mean()) < 0.05
    print(f"   gate -> {'PASS' if ok else 'FAIL'}")
