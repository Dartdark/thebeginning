"""Checker replica of FVB from spec.md alone (2026-10-24). Writes trades_replica.csv, placebo.csv (random side,
mirrored stop, same entry bars) and opposite.csv (every entry reversed).
  python3 checks/candidates/fvb/replica.py
"""
import sys, os, pickle, gc
sys.path.insert(0, "/home/user/thebeginning/analysis")
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TICK, PV, COST = 0.25, 20.0, 17.25
RTH0, RTH1, PM0, PM1, ENTRY_END, FC = 511, 915, 181, 510, 631, 911


def rt(x): return round(round(x / TICK) * TICK, 10)


def main():
    os.chdir("/home/user/thebeginning")
    g = pickle.load(open("scratch_data/g24.pkl", "rb"))
    from s_rank_gap_round2_test import Sym, rolls_index
    S = Sym("NQ", g); rb, _ = rolls_index(S); S.set_rolls(rb)
    TS = pd.DatetimeIndex(g.ts)
    O, H, L, C = g.o, g.h, g.l, g.c
    rows = np.where((~np.isnan(C[:, RTH0:RTH1 + 1])).any(1))[0]          # days with any RTH bar
    st = {}
    for r in rows:
        m = ~np.isnan(C[r, RTH0:RTH1 + 1]); js = np.where(m)[0] + RTH0
        hi, lo = np.nanmax(H[r, js]), np.nanmin(L[r, js]); o, c = O[r, js[0]], C[r, js[-1]]
        rng = hi - lo
        st[r] = dict(js=js, hi=hi, lo=lo, rng=rng, br=abs(c - o) / rng if rng > 0 else np.nan)
    rngs = pd.Series([st[r]["rng"] for r in rows]); atr = rngs.rolling(14, min_periods=14).mean().to_numpy()
    sig = []                     # (row, date, side, level name, j_signal) per trade + sims
    out = []
    for k in range(1, len(rows)):
        r, p = rows[k], rows[k - 1]
        if TS[r] < pd.Timestamp("2018-01-02"): continue
        js = st[r]["js"]
        if len(js) < 10: continue
        pmj = np.where(~np.isnan(C[r, PM0:PM1 + 1]))[0] + PM0
        if not len(pmj): continue
        a = atr[k - 1]
        if not np.isfinite(a) or a <= 0: continue
        pmh, pml = np.nanmax(H[r, pmj]), np.nanmin(L[r, pmj])
        if st[p]["rng"] > 1.5 * a or (pmh - pml) > 1.0 * a or pmh <= pml: continue
        if S.has_roll([p * 1440 + RTH1], [r * 1440 + RTH1])[0]: continue
        pdh, pdl, pbr = st[p]["hi"], st[p]["lo"], st[p]["br"]
        strong = np.isfinite(pbr) and pbr >= 0.6
        if pdh < pml or pdl > pmh:
            lv = [("pm_high", pmh, 1), ("pm_low", pml, -1)]
        else:
            lv = [("pdh", pdh, 1), ("pdl", pdl, -1)]
            if pmh != pdh: lv.append(("pm_high", pmh, 1))
            if pml != pdl: lv.append(("pm_low", pml, -1))
        sd = rt(0.18 * a)
        o, h, l, c = O[r, js], H[r, js], L[r, js], C[r, js]
        nb = len(js); scan = 0; ntr = 0; active = list(lv)
        while ntr < 2:
            hit = None
            for i in range(scan, nb - 1):
                if js[i] >= ENTRY_END: break
                for nm, x, d in active:
                    if d == -1 and strong: continue
                    if (d == 1 and c[i] > x) or (d == -1 and c[i] < x): hit = (i, nm, x, d); break
                if hit: break
            if not hit: break
            i, nm, x, d = hit
            res = walk(o, h, l, c, js, i, d, sd)
            ep, xp, sp, kind, xi = res
            pts = (xp - ep) * d
            out.append(dict(date=TS[r].date(), side=d, level=nm, n=ntr + 1, entry=ep, exit=xp, stop=sp, kind=kind,
                            sd=sd, atr=a, pts=pts, net=pts * PV - COST, j0=js[i + 1], j1=js[xi], row=r))
            sig.append((r, i, d, sd))
            ntr += 1
            if kind == "stop" and ntr < 2:
                scan = xi + 1; active = [z for z in active if z[1] != x]
            else: break
    T = pd.DataFrame(out); T.to_csv(os.path.join(HERE, "trades_replica.csv"), index=False)
    # placebos on the same entry bars: reversed side with mirrored stop; random side 500 runs
    base = []
    for (r, i, d, sd) in sig:
        js = st[r]["js"]; o, h, l, c = O[r, js], H[r, js], L[r, js], C[r, js]
        rr = {}
        for dd in (1, -1):
            ep, xp, sp, kind, xi = walk(o, h, l, c, js, i, dd, sd); rr[dd] = (xp - ep) * dd * PV - COST
        base.append((rr[1], rr[-1], d))
    B = np.array(base)
    opp = np.where(B[:, 2] == 1, B[:, 1], B[:, 0])
    pd.DataFrame(dict(date=T.date, side=-T.side, net=opp)).to_csv(os.path.join(HERE, "opposite.csv"), index=False)
    rng = np.random.default_rng(7); pl = []
    for run in range(500):
        s = rng.integers(0, 2, len(B)); pl.append(pd.DataFrame(dict(run=run, net=np.where(s == 1, B[:, 0], B[:, 1]))))
    pd.concat(pl).to_csv(os.path.join(HERE, "placebo.csv"), index=False)
    print("replica trades", len(T), "net", T.net.sum(), "mean", T.net.mean(), "| opposite mean", opp.mean())


def walk(o, h, l, c, js, i, d, sd):
    ep = rt(o[i + 1]); sp = rt(ep - sd) if d == 1 else rt(ep + sd)
    for k in range(i + 1, len(js)):
        if d == 1 and l[k] <= sp: return ep, sp, sp, "stop", k
        if d == -1 and h[k] >= sp: return ep, sp, sp, "stop", k
        if js[k] >= FC: return ep, c[k], sp, "eod", k
    return ep, c[-1], sp, "eod", len(js) - 1


if __name__ == "__main__":
    main()
