"""Post-settlement reversal with cheaper execution (pre-registered: checks/candidates/post_settlement/PREREG.md, 2026-10-25).
NQ (ES, YM as checks), 1-minute grids (CT, close-stamped). M = close(15:00) - close(14:00); fade it 15:01 -> the 15:15 close.
  V0 market entry at the 15:01 open; V1 limit at the 15:00 close, 15:01-15:05, filled when traded 1 tick through;
  V2 / V3 = V0 / V1 on |M| >= 0.3 ATR (and 0.2). Costs $7.25 + 1 tick per market fill per NQ (limit entries pay no tick);
  Apex micro fees $10.40 + $5 per fill per NQ-equivalent. Controls: random side, following.
  python3 analysis/post_settlement_test.py [SCRATCH_DIR] > analysis/outputs/post_settlement_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPEC = {"NQ": ("g24", 20.0, 0.25, 7.25), "ES": ("ge", 50.0, 0.25, 5.0), "YM": ("gy", 5.0, 1.0, 5.0)}


def build(sym):
    f, pv, tick, comm = SPEC[sym]
    g = pickle.load(open(SP + f + ".pkl", "rb")); atr = g.daily_atr(15)
    tr = g.trading; d = pd.DatetimeIndex(g.ts[tr])
    J14, J15, J1515 = jof(1400), jof(1500), jof(1515)
    c14, c15, c1515 = g.c[tr, J14], g.c[tr, J15], g.c[tr, J1515]
    o1501 = g.o[tr, J15 + 1]
    lo = np.nanmin(g.l[tr, J15 + 1:J15 + 6], axis=1); hi = np.nanmax(g.h[tr, J15 + 1:J15 + 6], axis=1)
    F = pd.DataFrame(dict(m=c15 - c14, set=c15, o1501=o1501, lo=lo, hi=hi, x=c1515, atr=atr[tr]), index=d)
    F = F[(F.index >= "2018-01-01") & F[["m", "set", "o1501", "x", "atr"]].notna().all(axis=1) & (F.m != 0)]
    F.attrs.update(pv=pv, tick=tick, comm=comm)
    return F


def trades(F, variant, k=0.3, fee=None, slip=None, side_mode="fade", seed=1):
    pv, tick = F.attrs["pv"], F.attrs["tick"]; comm = F.attrs["comm"] if fee is None else fee
    slip_d = tick * pv if slip is None else slip
    side = -np.sign(F.m) if side_mode == "fade" else np.sign(F.m)
    if side_mode == "random": side = np.random.default_rng(seed).choice([-1, 1], len(F))
    side = pd.Series(side, index=F.index)
    keep = pd.Series(True, index=F.index)
    if variant in ("V2", "V3"): keep &= F.m.abs() >= k * F.atr
    if variant in ("V0", "V2"):
        e = F.o1501; fills = 2
    else:
        lim = F.set; thr = tick
        filled = np.where(side > 0, F.lo <= lim - thr, F.hi >= lim + thr)
        keep &= pd.Series(filled, index=F.index); e = lim; fills = 1
    gross = (F.x - e) * side * pv
    net = gross - comm - fills * slip_d
    return net[keep]


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(x, nm, w=46):
    a, b = x[x.index.year <= 2022], x[x.index.year >= 2023]; by = x.groupby(x.index.year).sum()
    return (f"   {nm:<{w}} n={len(x):5d} ({len(x) / 8.8:4.0f}/yr) ${x.mean():6.2f} PF {pf(x):4.2f} t {tst(x):5.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():6.2f} t {tst(a):4.1f} | 23-26 ${b.mean():6.2f} t {tst(b):4.1f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for sym in ("NQ", "ES", "YM"):
        F = build(sym); print(f"\n{sym} ({len(F)} days with a 14:00 -> 15:00 move; per 1 {sym}):")
        print(line(trades(F, "V0", fee=0, slip=0), "gross (no costs), market entry"))
        for v in ("V0", "V1"): print(line(trades(F, v), f"{v} ours"))
        for k in (0.2, 0.3):
            for v in ("V2", "V3"): print(line(trades(F, v, k=k), f"{v} ours, |M| >= {k} ATR"))
        if sym == "NQ":
            for v in ("V0", "V1", "V3"): print(line(trades(F, v, fee=10.4, slip=5.0), f"{v} Apex micro fees (x10)"))
            print(line(trades(F, "V1", side_mode="follow"), "V1 following instead of fading"))
            r = [trades(F, "V1", side_mode="random", seed=s).mean() for s in range(200)]
            print(f"   V1 random side, 200 runs: mean ${np.mean(r):.2f}, 95th pct ${np.percentile(r, 95):.2f}")
            v1 = trades(F, "V1"); v0 = trades(F, "V0")
            print(f"   V1 fill rate {len(v1) / len(v0):.0%}; on the days V1 misses, V0 makes ${v0[~v0.index.isin(v1.index)].mean():.2f} a trade (adverse selection check)")
            print("   V1 by year:", v1.groupby(v1.index.year).sum().round(0).astype(int).to_dict())
            print(f"   pass bar: t >= 3.58 (N_items), holdout t >= 1.5 same sign, >= 300 trades a year; t_threshold(4 variants) {M.t_threshold(4):.2f}")
