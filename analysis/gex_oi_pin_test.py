"""NDX 0DTE open interest on NQ: expiry pinning, call / put walls, put-call OI (user's GEXOI export, 2026-10-15).

Data: data/GEXOI_<year>.csv from multi_strategy/OFB_GexOI_Exporter.txt (The Bridge's NDX 0DTE chain, 128 strikes nearest the
forward, snapshots 9:31 / 12:00 / 15:30 ET). 751 sessions 2022-09-01 .. 2026-07-07, Tue-Fri only (no Monday chain in the
export). OI is only used from the 9:31 ET snapshot: by 15:30 The Bridge zeroes far out-of-the-money strikes (puts below,
calls above the forward), so later snapshots are not the prior-close OI. NQ level of a strike = strike + basis (9:31).
gex (GexWalls slot 1) is used only from 2023-03-28, from the 12:00 ET snapshot (= 11:00 CT bar close), for trades after it.
Levels, from the 9:31 ET (8:31 CT) snapshot unless noted:
  pin    strike with the largest call + put OI       maxpain  strike minimising option holders' payoff at expiry
  cwall  largest call-OI strike above the 8:31 NQ    pwall    largest put-OI strike below
  gpin   largest |gex| strike at 12:00 ET (2023-03-28+)   near   largest call + put OI strike within 150 NQ points of 8:31
Pre-specified trades (1 NQ, $7.25 + 1 tick a market / stop fill, limit fills need a 1-tick trade-through):
  A  toward the level: at 12:00 / 13:00 / 14:00 CT, if NQ is >= 10 points from it, trade toward it, out 15:00 CT
     (NDX 0DTE options expire at the 15:00 CT cash close); also the change in distance (entry -> 15:00) in points
  B  wall fade: first touch of cwall (short) / pwall (long) between 8:35 and 14:00 CT, limit at the wall, stop 20, target 40,
     out 15:00
  C  put / call OI ratio (log) at 9:31 vs the 8:31 -> 15:00 CT NQ move (rank correlation, quintiles)
Placebo for A / B: each day's level offset from the 8:31 price replaced by another day's offset (200 / 100 shuffles) -> the
share of shuffles with an average P&L at least as high as the real one (p).
  D  filters on the plan's NQ trades (MultiCharts lists, entries after 8:31 CT): side x sign(level - entry) for pin / near /
     maxpain, room to the wall in the trade's direction (points), side x put/call; design-median split as in
     bridge_filter_scan.py (PASS = design |t| >= 2 and holdout kept - skipped > 0 with t >= 1.5), null = P&L shuffled 200x
Split: design 2022-09 .. 2024-06, holdout 2024-07 .. 2026-07 (only ~4 years of data).
  python3 analysis/gex_oi_pin_test.py [SCRATCH_DIR]
"""
import sys, glob, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import load
import metrics as M, resampling as R

PV, TICK, COMM = 20.0, 0.25, 7.25
C_MKT = COMM + 2 * TICK * PV          # market in, market out
C_LIM = COMM + TICK * PV              # limit in, market / stop out
SPLIT = pd.Timestamp("2024-07-01")


def levels():
    D = pd.concat(pd.read_csv(f) for f in sorted(glob.glob("data/GEXOI_*.csv")))
    out = {}
    for d, g in D[D.time == 931].groupby("date"):
        oi = g.call_oi + g.put_oi
        if oi.sum() <= 0: continue
        k = g.strike.to_numpy(); c = g.call_oi.to_numpy(float); p = g.put_oi.to_numpy(float)
        pain = [(np.clip(s - k, 0, None) * c).sum() + (np.clip(k - s, 0, None) * p).sum() for s in k]
        out[d] = dict(basis=g.basis.iloc[0], pin=k[np.argmax(oi.to_numpy())], maxpain=k[int(np.argmin(pain))],
                      k=k, c=c, p=p, pcr=np.log((p.sum() + 1) / (c.sum() + 1)))
    G = D[(D.time == 1200) & (D.date >= 20230328)]
    for d, g in G.groupby("date"):
        if d in out and (g.gex != 0).any():
            out[d]["gpin"] = g.strike.to_numpy()[np.argmax(np.abs(g.gex.to_numpy()))]
            out[d]["basis12"] = g.basis.iloc[0]
    return out


def frame():
    g = load("NQ"); L = levels()
    row = {d: i for i, d in enumerate(g.dates)}
    rows = []
    for d, v in L.items():
        r = row.get(d)
        if r is None or np.isnan(g.c[r, jof(831)]) or np.isnan(g.c[r, jof(1500)]): continue
        p0 = g.c[r, jof(831)]; b = v["basis"]; spot = p0 - b
        above, below = v["k"] > spot, v["k"] < spot
        cw = v["k"][above][np.argmax(v["c"][above])] + b if above.any() and v["c"][above].max() > 0 else np.nan
        pw = v["k"][below][np.argmax(v["p"][below])] + b if below.any() and v["p"][below].max() > 0 else np.nan
        rows.append(dict(date=pd.Timestamp(str(d)), r=r, p0=p0, pin=v["pin"] + b, maxpain=v["maxpain"] + b, cwall=cw,
                         pwall=pw, gpin=v.get("gpin", np.nan) + v.get("basis12", np.nan), pcr=v["pcr"],
                         inwin=v["k"].min() < spot < v["k"].max(),
                         near=(lambda m: v["k"][m][np.argmax((v["c"] + v["p"])[m])] + b if m.any() else np.nan)(np.abs(v["k"] - spot) <= 150)))
    return g, pd.DataFrame(rows).set_index("date").sort_index()


def toward(g, F, lvl, hhmm, min_dist=10.0):
    """A: P&L (net) and distance change, trading toward `lvl` (absolute NQ price, Series) at hhmm CT, out 15:00."""
    r = F.r.to_numpy(); pe = g.c[r, jof(hhmm)]; px = g.c[r, jof(1500)]
    L = lvl.to_numpy(); dist = L - pe; side = np.sign(dist)
    ok = (np.abs(dist) >= min_dist) & ~np.isnan(pe) & ~np.isnan(L)
    pnl = pd.Series(np.where(ok, side * (px - pe) * PV - C_MKT, np.nan), index=F.index)
    closer = pd.Series(np.where(ok, np.abs(dist) - np.abs(L - px), np.nan), index=F.index)
    return pnl.dropna(), closer.dropna()


def wall_fade(g, F, lvl, side, start=835, end=1400, stop=20.0, tgt=40.0):
    """B: first touch (1-tick trade-through) of lvl between start and end; side -1 short at a level above, +1 long below."""
    out = {}
    for dt, rr, L in zip(F.index, F.r, lvl):
        if np.isnan(L): continue
        h, l, c = g.h[rr], g.l[rr], g.c[rr]
        j1, j2, jx = jof(start), jof(end), jof(1500)
        if side < 0 and np.nanmax(h[jof(831):j1]) >= L: continue          # already there before the window
        if side > 0 and np.nanmin(l[jof(831):j1]) <= L: continue
        hit = np.where((h[j1:j2 + 1] >= L + TICK) if side < 0 else (l[j1:j2 + 1] <= L - TICK))[0]
        if not len(hit): continue
        j = j1 + hit[0]; sp = L - side * stop; tp = L + side * tgt; res = None
        for k in range(j + 1, jx + 1):
            if np.isnan(c[k]): continue
            if (side < 0 and h[k] >= sp) or (side > 0 and l[k] <= sp):
                res = (sp - L) * side * PV - TICK * PV; break
            if (side < 0 and l[k] <= tp - TICK) or (side > 0 and h[k] >= tp + TICK):
                res = (tp - L) * side * PV; break
        if res is None:
            px = c[jx] if not np.isnan(c[jx]) else c[:jx + 1][~np.isnan(c[:jx + 1])][-1]
            res = (px - L) * side * PV - TICK * PV
        out[dt] = res - C_LIM
    return pd.Series(out, dtype=float)


def line(x, nm, w=46):
    x = pd.Series(x).dropna()
    if len(x) < 5: return f"   {nm:<{w}} n={len(x)}"
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum()); t = x.mean() / x.std() * np.sqrt(len(x))
    by = x.groupby(x.index.year).sum(); a, b = x[x.index < SPLIT], x[x.index >= SPLIT]
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.1f} PF {pf:4.2f} t {t:4.1f} win {np.mean(x > 0):.0%} "
            f"yrs+ {(by > 0).sum()}/{len(by)} | design ${a.mean():6.1f} (n {len(a)}) holdout ${b.mean():6.1f} (n {len(b)})")


def placebo(F, nm, fn, n=500, seed=7):
    """p = share of shuffled-offset runs with avg P&L >= the real one."""
    real = fn(F[nm]).mean(); off = (F[nm] - F.p0).to_numpy(); rng = np.random.default_rng(seed); sims = []
    for _ in range(n):
        sims.append(fn(pd.Series(F.p0.to_numpy() + rng.permutation(off), index=F.index)).mean())
    sims = np.array(sims); return real, np.nanmean(sims), np.nanmean(sims >= real)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g, F = frame()
    print(f"\n{len(F)} sessions {F.index[0].date()} .. {F.index[-1].date()}; NQ at 8:31 inside the strike window: {F.inwin.mean():.0%}")
    print("level distance from the 8:31 NQ price (points, median |d|):",
          {c: round(float((F[c] - F.p0).abs().median()), 1) for c in ("pin", "near", "maxpain", "cwall", "pwall", "gpin")})

    print("\nA. Toward the level, out 15:00 CT (net, 1 NQ; 'closer' = points the distance shrank, entry -> 15:00)")
    keep = {}
    for nm in ("pin", "near", "maxpain", "gpin"):
        for hh in (1200, 1300, 1400):
            if nm == "gpin" and hh < 1200: continue
            x, cl = toward(g, F, F[nm], hh)
            print(line(x, f"{nm} @ {hh} CT") + f" | closer {cl.mean():+5.1f} pts")
            keep[(nm, hh)] = x
    print("   placebo (each day's level offset shuffled across days, 200 runs): real avg, placebo avg, p")
    for nm in ("pin", "near", "maxpain", "gpin"):
        for hh in (1200, 1300, 1400):
            Fn = F.dropna(subset=[nm])
            r_, s_, p_ = placebo(Fn, nm, lambda L, hh=hh, Fn=Fn: toward(g, Fn, L, hh)[0], n=200)
            print(f"   {nm:>8} @ {hh}: real ${r_:6.1f}  placebo ${s_:6.1f}  p {p_:.2f}")

    print("\nB. Wall fades (limit at the wall, stop 20, target 40, out 15:00; net)")
    cw = wall_fade(g, F, F.cwall, -1); pw = wall_fade(g, F, F.pwall, +1)
    print(line(cw, "call wall short")); print(line(pw, "put wall long")); both = pd.concat([cw, pw]).sort_index()
    print(line(both, "both"))
    for nm, side, x in (("cwall", -1, cw), ("pwall", +1, pw)):
        Fn = F.dropna(subset=[nm]); off = (Fn[nm] - Fn.p0).to_numpy(); rng = np.random.default_rng(3); sims = []
        for _ in range(100):
            # shuffled offsets kept on the same side of the 8:31 price
            o = np.abs(rng.permutation(off)) * (1 if side < 0 else -1)
            sims.append(wall_fade(g, Fn, pd.Series(Fn.p0.to_numpy() + o, index=Fn.index), side).mean())
        sims = np.array(sims)
        print(f"   placebo {nm}: real ${x.mean():6.1f}  placebo ${np.nanmean(sims):6.1f}  p {np.nanmean(sims >= x.mean()):.2f}")

    print("\nC. Put / call OI ratio at 9:31 vs the NQ move 8:31 -> 15:00 CT")
    mv = pd.Series(g.c[F.r, jof(1500)] - F.p0.to_numpy(), index=F.index)
    for nm, m in (("all", slice(None)), ("design", F.index < SPLIT), ("holdout", F.index >= SPLIT)):
        print(f"   {nm:<8} rank corr {F.pcr[m].rank().corr(mv[m].rank()):+.3f}  n {int(np.sum(np.ones(len(F))[m]))}")
    q = pd.qcut(F.pcr, 5, labels=False)
    print("   NQ move (pts) by put/call quintile (0 = most calls):", mv.groupby(q).mean().round(1).to_dict())

    print("\nD. Filters on the plan's NQ trades")
    import io, contextlib, runpy
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        T = runpy.run_path("analysis/plan_agreement_test.py", run_name="__main__")["T"]
    T = T[T.date.isin(F.index) & (T.j0 > jof(831))].reset_index(drop=True)
    rr = F.r.reindex(T.date).to_numpy(); pe = g.c[rr, T.j0.to_numpy() - 1]; Fd = F.reindex(T.date).reset_index(drop=True)
    sd = T.side.to_numpy()
    X = pd.DataFrame({"pin": sd * np.sign(Fd.pin - pe), "near": sd * np.sign(Fd.near - pe), "maxpain": sd * np.sign(Fd.maxpain - pe),
                      "room": np.where(sd > 0, Fd.cwall - pe, pe - Fd.pwall), "pcr": -sd * Fd.pcr})
    print("   trades by strategy:", T.strat.value_counts().to_dict())

    def scan(y):
        out = []
        for s_ in sorted(T.strat.unique()):
            ms = (T.strat == s_).to_numpy(); hol_ = (T.date >= SPLIT).to_numpy()
            for c_ in X:
                x_ = X[c_].to_numpy(); ok = ms & ~np.isnan(x_); des = ok & ~hol_; hol = ok & hol_
                if des.sum() < 20 or hol.sum() < 20: continue
                hi = x_ >= np.median(x_[des]) if c_ in ("room", "pcr") else x_ > 0
                a_, b_ = y[des & hi], y[des & ~hi]
                if len(a_) < 8 or len(b_) < 8: continue
                td = (a_.mean() - b_.mean()) / np.sqrt(a_.var() / len(a_) + b_.var() / len(b_)); kp = hi if td > 0 else ~hi
                k_, sk = y[hol & kp], y[hol & ~kp]
                if len(k_) < 5 or len(sk) < 5: continue
                th = (k_.mean() - sk.mean()) / np.sqrt(k_.var() / len(k_) + sk.var() / len(sk))
                out.append(dict(strat=s_, feat=c_, n=int(ok.sum()), t_design=td, kept_hold=k_.mean(), skipped_hold=sk.mean(),
                                t_hold=th, PASS=abs(td) >= 2 and th >= 1.5))
        return pd.DataFrame(out)
    Rs = scan(T.net.to_numpy()); print(f"   {len(Rs)} tests, PASS {int(Rs.PASS.sum())}")
    print(Rs.sort_values("t_design", key=abs, ascending=False).head(10).round(2).to_string(index=False))
    rng = np.random.default_rng(1); nul = []
    for _ in range(200):
        y = T.net.to_numpy().copy()
        for s_ in T.strat.unique():
            m = (T.strat == s_).to_numpy(); y[m] = rng.permutation(y[m])
        nul.append(int(scan(y).PASS.sum()))
    print(f"   null: passes mean {np.mean(nul):.2f}, 95th pct {np.percentile(nul, 95):.0f}, P(>= real) {np.mean(np.array(nul) >= Rs.PASS.sum()):.2f}")

    best = max(keep, key=lambda k: keep[k][keep[k].index < SPLIT].mean())
    x = keep[best]; print(f"\nStandard metrics, A's best on design ({best}), net; longs / shorts = trades toward a level above / below:")
    r = F.r.reindex(x.index).to_numpy(); side = np.sign(F[best[0]].reindex(x.index).to_numpy() - g.c[r, jof(best[1])])
    days = pd.Series(0.0, index=F.index); rows = {}
    for nm, m in (("all", side != 0), ("longs", side > 0), ("shorts", side < 0)):
        rows[nm] = (days.add(x[m], fill_value=0), x[m])
    print(M.table(rows))
    h = {k: v[0][v[0].index >= SPLIT] for k, v in rows.items()}
    b, p = R.report(h, n=2000); print("\nholdout bootstrap:\n" + b + "\n\nholdout drawdown permutation:\n" + p)
    F.to_pickle("scratch_data/gex_oi_levels.pkl")
