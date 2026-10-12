"""Headline Shock Follow and NFP Fade: full checks (2026-10-12, from analysis/news_meanrev_test.py).

Headline Shock Follow: NQ has no headline feed here, so an unscheduled news headline is proxied
by a 5-minute move far above normal for that time of day: |close - close 5 min earlier| >
K x the mean of the same 5-minute slot's |move| over the last N trading days, at 8:40-14:15 CT,
not at scheduled minutes (7:30, 8:30-8:40, 9:00-9:10, 10:00, 15:00; 13:00-15:45 on FOMC days).
Enter in the jump's direction at the next minute, stop = the jump's size beyond the entry,
out after H minutes (no later than 14:55). One trade at a time. Jeon, McCurdy & Zhao (2022):
news-driven jumps continue; NQ intraday is momentum (big-move fades lose here).

NFP Fade: on payroll Fridays (7:30 CT range spike, Friday, day <= 10) fade the 7:29 -> 7:45
reaction at 7:46, out at the 9:00 close, stop 0.5 ATR.

Steps (DEVELOPMENT_PROCESS.md): design-period grid (2018-22) + clusters, holdout 2023-26, by
year, longs / shorts, random-time placebo, standard metrics, funded bench with the current plan,
bootstrap + permutation.  python3 analysis/headline_shock_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle, itertools; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import event_days as E, metrics as M, resampling as R, param_clusters as PC
from news_meanrev_test import row, summ, reaction_trades

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SCHED = ((730, 740), (830, 840), (900, 910), (1000, 1005), (1500, 1520))


def jumps(G, k=6.0, lookback=14, window=(840, 1415), step=5):
    """(row, column, signed 5-min move) for unscheduled jumps; normal size = mean |move| of the
    same slot over the previous `lookback` trading days."""
    tr = G.trading
    C = pd.DataFrame(G.c[tr]).ffill(axis=1).to_numpy()
    J = np.arange(jof(window[0]), jof(window[1]) + 1, step)
    mv = C[:, J] - C[:, J - step]
    mv[np.isnan(G.c[tr][:, J]) | np.isnan(G.c[tr][:, J - step])] = np.nan
    norm = pd.DataFrame(np.abs(mv)).rolling(lookback, min_periods=max(5, lookback // 2)).mean().shift(1).to_numpy()
    hhmm = (J // 60) * 100 + J % 60
    sched = np.zeros(len(J), bool)
    for a, b in SCHED: sched |= (hhmm > a) & (hhmm <= b)
    fom = set(E.rows_of(G, E.FOMC_DATES).tolist())
    with np.errstate(all="ignore"): z = np.abs(mv) / norm
    out = []
    for i, c in zip(*np.where(z > k)):
        d = tr[i]
        if sched[c] or (d in fom and 1300 < hhmm[c] <= 1545): continue
        out.append((d, J[c], mv[i, c]))
    return out


def trades(G, k=6.0, lookback=14, hold=90, rand=None, stop=True):
    js = jumps(G, k, lookback)
    if rand is not None:                       # placebo: same days, random slots, follow the last 5 min
        rng = np.random.default_rng(rand); C = pd.DataFrame(G.c).ffill(axis=1).to_numpy()
        jr = rng.choice(np.arange(jof(840), jof(1415) + 1, 5), len(js))
        js = sorted((d, j, C[d, j] - C[d, j - 5]) for (d, _, _), j in zip(js, jr))
    rows = []; ts = pd.DatetimeIndex(G.ts); last = (-1, -1)
    for d, j, m in js:
        if ts[d].year < 2018 or (d == last[0] and j <= last[1]) or m == 0: continue
        s = int(np.sign(m)); j0 = j + 1; j1 = min(j0 + hold, jof(1455))
        e = G.o[d, j0]
        if np.isnan(e): continue
        r = row(G, d, j0, s, j1, e - s * abs(m) if stop else None, None)
        if r: r["stop_pts"] = abs(m); rows.append(r); last = (d, r["j1"])
    return pd.DataFrame(rows)


def daily(t, days):
    return t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15)
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dz, hz = days[days.year <= 2022], days[days.year >= 2023]
    print(__doc__.split("\n")[0])

    # ---------------- 1. design-period grid and clusters
    grid = []
    for k, lb, h in itertools.product((5.0, 5.5, 6.0, 6.5, 7.0), (10, 14, 20, 30), (45, 60, 90, 120, 400)):
        t = trades(g, k, lb, h); y = t.date.dt.year
        a, b = t[y <= 2022], t[y >= 2023]
        pa, pb = M.perf(daily(a, dz), a.net), M.perf(daily(b, hz), b.net)
        grid.append(dict(k=k, lookback=lb, hold=h, n=len(t), design_calmar=pa["calmar"], design_pf=pa["profit_factor"],
                         design_t=a.net.mean() / a.net.std() * np.sqrt(len(a)), hold_calmar=pb["calmar"],
                         hold_pf=pb["profit_factor"], hold_avg=b.net.mean()))
    G_ = pd.DataFrame(grid)
    G_["hold_rank"] = G_.hold_calmar.rank(pct=True)
    print(f"\n1. Grid: {len(G_)} combinations (K 5-7, lookback 10-30 trading days, hold 45-120 min / to 14:55)")
    print(f"   design 2018-22 PF > 1 in {np.mean(G_.design_pf > 1):.0%}, holdout 2023-26 PF > 1 in {np.mean(G_.hold_pf > 1):.0%}")
    cl, sel = PC.cluster_top(G_, ["k", "lookback", "hold"], "design_calmar", top=0.2, k=4)
    print(cl[["size", "score_mean", "k_range", "lookback_range", "hold_range", "medoid_k", "medoid_lookback", "medoid_hold"]].to_string(index=False))
    for _, c in cl.iterrows():
        m = G_.loc[c.medoid_index]
        print(f"   medoid K {m.k} / {m.lookback:.0f} days / {m.hold:.0f} min: design Calmar {m.design_calmar:.2f} t {m.design_t:.1f}"
              f" | holdout Calmar {m.hold_calmar:.2f} PF {m.hold_pf:.2f} avg ${m.hold_avg:.0f} (rank {m.hold_rank:.0%})")
    best = G_.loc[cl.iloc[0].medoid_index]
    K, LB, H = best.k, int(best.lookback), int(best.hold)
    print(f"\n   Chosen (largest cluster's medoid): K {K}, lookback {LB} trading days, hold {H if H < 400 else 'to 14:55'}")
    print("   Sensitivity (one at a time, 2018-26 avg / PF):")
    for nm, vals in (("k", (5.0, 5.5, 6.0, 6.5, 7.0)), ("lookback", (10, 14, 20, 30)), ("hold", (45, 60, 90, 120, 400))):
        s = []
        for v in vals:
            p = dict(k=K, lookback=LB, hold=H); p[nm] = v
            r = G_[(G_.k == p["k"]) & (G_.lookback == p["lookback"]) & (G_.hold == p["hold"])].iloc[0]
            tt = trades(g, p["k"], p["lookback"], p["hold"])
            s.append(f"{v:g}: ${tt.net.mean():.0f}/{M.perf(daily(tt, days), tt.net)['profit_factor']:.2f}")
        print(f"     {nm}: " + "  ".join(s))

    # ---------------- 2. the chosen version
    t = trades(g, K, LB, H)
    print("\n2. Chosen version, per NQ after costs:")
    print(summ(t, "Headline Shock Follow"))
    print(summ(t[t.side > 0], "  longs")); print(summ(t[t.side < 0], "  shorts"))
    print("   by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   trades a year:", round(len(t) / (len(days) / 252), 1), "| jumps by hour:",
          t.groupby(t.j0 // 60).size().to_dict())
    pl = [trades(g, K, LB, H, rand=r).net.mean() for r in range(20)]
    print(f"   placebo (same days, random times, follow the last 5 min, 20 runs): real ${t.net.mean():.0f}"
          f" vs ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f})")
    tn = trades(g, K, LB, H, stop=False)
    print(summ(tn, "   no stop"))

    # ---------------- 3. NFP fade
    rel = E.release_days(g); tsr = pd.DatetimeIndex(g.ts[rel])
    nfp = rel[(tsr.dayofweek == 4) & (tsr.day <= 10)]
    tf = reaction_trades(g, nfp, 729, 745, 900, "fade", stop_k=0.5, atr=atr)
    print("\n3. NFP Fade (7:29 -> 7:45 reaction faded, 7:46 -> 9:00, stop 0.5 ATR), per NQ:")
    print(summ(tf, "NFP Fade")); print(summ(tf[tf.side > 0], "  longs")); print(summ(tf[tf.side < 0], "  shorts"))
    print("   by year:", tf.groupby(tf.date.dt.year).net.sum().round(0).astype(int).to_dict())
    rng = np.random.default_rng(3); plf = []
    for r in range(200):
        tt = tf.copy(); flip = rng.choice([-1, 1], len(tt))
        plf.append(((tt.exit - tt.entry) * tt.side * flip * 20 - 7.25).mean())
    print(f"   placebo (same days and times, random side, 200 runs, no stop): real ${tf.net.mean():.0f} vs "
          f"${np.mean(plf):.0f} (95% ${np.percentile(plf, 95):.0f})")

    # ---------------- 4. standard metrics, per NQ
    def sides(tt, nm):
        return {nm: (daily(tt, days), tt.net), f"{nm} longs": (daily(tt[tt.side > 0], days), tt.net[tt.side > 0]),
                f"{nm} shorts": (daily(tt[tt.side < 0], days), tt.net[tt.side < 0])}
    print("\n4. Standard metrics per NQ, 2018-2026:"); print(M.table({**sides(t, "HSF"), **sides(tf, "NFP")}))
    th, tfh = t[t.date.dt.year >= 2023], tf[tf.date.dt.year >= 2023]
    D2 = days[days.year >= 2023]
    print("   2023 onward:")
    print(M.table({"HSF": (daily(th, D2), th.net), "HSF longs": (daily(th[th.side > 0], D2), th.net[th.side > 0]),
                   "HSF shorts": (daily(th[th.side < 0], D2), th.net[th.side < 0]), "NFP": (daily(tfh, D2), tfh.net)}))

    # ---------------- 5. funded bench
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    lab.add("HSF", t, slippage=False)
    lab.add("HSF_L", t[t.side > 0].reset_index(drop=True), slippage=False)
    lab.add("HSF_S", t[t.side < 0].reset_index(drop=True), slippage=False)
    sp = np.full(g.D, np.nan); sp[tf.day.to_numpy()] = 0.5 * atr[tf.day.to_numpy()]
    lab.add("NFP", tf, stop_pts=0.5 * atr, slippage=False)
    CS = dict(fmin=0.5, fmax=1.0, ref=2000.0)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2}
    plans = {"Current plan": plan}
    for n in (1, 2, 3): plans[f"+ HSF {n} MNQ"] = {**plan, "HSF": n}
    plans["+ HSF longs 2 MNQ"] = {**plan, "HSF_L": 2}; plans["+ HSF shorts 2 MNQ"] = {**plan, "HSF_S": 2}
    for r in (300, 500): plans[f"+ NFP ${r}"] = {**plan, "NFP": ("risk", r)}
    plans["+ HSF 2 MNQ + NFP $500"] = {**plan, "HSF": 2, "NFP": ("risk", 500)}
    out = {}
    for nm, p in plans.items():
        a = lab.score(p, 250, **CS); b = lab.score(p, 500, **CS)
        out[nm] = {"1y": a["expected"], "1y 2023+": a["s2023_on"], "2y": b["expected"], "blown 1y": a["blown"],
                   "blown 2y": b["blown"], "days to 1st": a["days_to_1st"]}
    fm = {c: "${:,.0f}".format for c in ("1y", "1y 2023+", "2y")}
    fm.update({"blown 1y": "{:.0%}".format, "blown 2y": "{:.0%}".format, "days to 1st": "{:.0f}".format})
    print("\n5. Funded bench, cushion sizing:"); print(pd.DataFrame(out).T.to_string(formatters=fm))
    dts = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts.year >= 2018
    P = {k: pd.Series(lab.daily(k), index=dts)[mk] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "HSF", "NFP")}
    print("   daily P&L correlation with the plan:"); print(pd.DataFrame(P).corr().round(2).loc[["HSF", "NFP"]].to_string())
    names, base = lab._base({**plan, "HSF": 2}); base = np.floor(base + 1e-9)
    Q = {k: pd.Series(lab.C[k] * base[i], index=dts)[mk] for i, k in enumerate(names)}
    port = sum(Q.values()); port0 = sum(v for k, v in Q.items() if k != "HSF")
    print("\n   Portfolio at full size:"); print(M.table({"current plan": (port0, None), "+ HSF 2 MNQ": (port, None)}))

    # ---------------- 6. bootstrap + permutation (2023 onward holdout and 2018-26), per NQ
    rows = {"HSF 2023-26": daily(th, D2), "HSF longs 2023-26": daily(th[th.side > 0], D2),
            "HSF shorts 2023-26": daily(th[th.side < 0], D2), "HSF 2018-26": daily(t, days),
            "NFP 2023-26": daily(tfh, D2), "NFP 2018-26": daily(tf, days),
            "plan + HSF 2 2023-26": port[port.index.year >= 2023], "plan 2023-26": port0[port0.index.year >= 2023]}
    B, Pm = R.report(rows, n=5000)
    print("\n6. Bootstrap (10-day blocks, 5,000 runs):"); print(B); print("\n   Permutation:"); print(Pm)
    t.to_pickle(SP + "hsf_trades.pkl"); tf.to_pickle(SP + "nfp_trades.pkl")
