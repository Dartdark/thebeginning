"""Order-flow absorption, NQ (user 2026-11-08: 'build a strategy around its own mechanism'). PRE-REGISTERED (header committed before the
first run; 1 variant; new mechanism, not in TIER_LIST).
Mechanism: price normally moves with net aggressive flow (Kyle 1985; Cont, Kukanov & Stoikov 2014: price change ~ order-flow imbalance).
When the first two RTH hours' price move is much WEAKER than its aggressor delta implies, large passive orders are absorbing the
aggression (a seller working limit orders under buying, or the mirror); that inventory is still being worked, so the rest of the day
should follow the price, not the flow. Prediction: trade in the direction of the price-vs-flow residual.
Rule (The Bridge's NQ aggressor volume, data/OF_1min_*, RTH 9:30-16:15 ET = 8:30-15:15 CT, ends 2026-07-07):
  per day: P = NQ close of the 10:29 CT bar - open of the 8:30 bar (points); F = sum of (up - down aggressor volume) over 8:30-10:29 CT.
  past-only fit over the previous 60 trading days: P = a + b x F (OLS); residual sd s. Z = (P - a - b x F) / s.
  |Z| >= 1.0 -> enter at the 10:31 CT bar's open in the direction of sign(Z); stop 0.3 x ATR15 (daily, known that morning); no target;
  out at the 14:55 CT close. CME early-close days skipped. Costs $7.25 + 1 tick per NQ market / stop fill.
Checks: per trade by period / year, longs / shorts; the OPPOSITE side (the competing reading: follow the flow) shown; random side on the
same days (200 runs); a no-flow control (same days, side = sign of P alone: plain momentum); daily corr with the plan; checker
checks/candidates/absorption/; 150K evaluation (set + Twin 2 MNQ) + 2 MNQ; funded 150K x 1.5 + Twin 2 + 2 MNQ; personal book + 1 MNQ.
Live note: MultiCharts would use up / down ticks, which agree with this aggressor flow only partly (62% sign agreement in Overnight
Tick's window), so a live version needs its own check.
  tools/run_stamped.sh analysis/absorption_test.py > analysis/outputs/absorption_test_output.txt
"""
import sys, os, glob, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close
from new_sources_150k import daypaths
import bench150 as BB

PV, TICK, COMM = 20.0, 0.25, 7.25


def features():
    d = pd.concat([pd.read_csv(f, usecols=["date", "time", "open", "close", "upvol", "downvol"]) for f in sorted(glob.glob("data/OF_1min_20*.csv"))])
    d = d[(d.time >= 930) & (d.time <= 1129)].sort_values(["date", "time"])          # ET: 8:30-10:29 CT
    g_ = d.groupby("date")
    X = pd.DataFrame({"o": g_.open.first(), "c": g_.close.last(), "F": (g_.upvol.sum() - g_.downvol.sum()), "n": g_.size(), "t0": g_.time.first(), "t1": g_.time.last()})
    X = X[(X.n >= 110) & (X.t0 == 930) & (X.t1 == 1129)]
    X["P"] = X.c - X.o; X.index = pd.to_datetime(X.index.astype(str)); return X


def zscores(X, L=60):
    z = np.full(len(X), np.nan); P, F = X.P.to_numpy(), X.F.to_numpy().astype(float)
    for i in range(L, len(X)):
        p, f = P[i - L:i], F[i - L:i]; A = np.c_[np.ones(L), f]; coef, *_ = np.linalg.lstsq(A, p, rcond=None)
        r = p - A @ coef; s = r.std(ddof=2)
        if s > 0: z[i] = (P[i] - coef[0] - coef[1] * F[i]) / s
    return pd.Series(z, index=X.index)


def trades(g, Z, side_fn, zmin=1.0, stop=0.3):
    atr = g.daily_atr(15); pos = pd.Series(np.arange(len(g.ts)), index=pd.DatetimeIndex(g.ts)); rows = []
    j0, jx = jof(1031), jof(1455)
    for d, z in Z.items():
        if not np.isfinite(z) or abs(z) < zmin or d < pd.Timestamp("2018-01-01") or d not in pos.index or is_early_close(d): continue
        r = int(pos[d])
        if np.isnan(atr[r]) or np.isnan(g.o[r, j0]) or np.isnan(g.c[r, jx]): continue
        s = side_fn(d, z)
        if s == 0: continue
        e = g.o[r, j0] + s * TICK; sp = e - s * stop * atr[r]; px = None; worst = 0.0
        for j in range(j0, jx + 1):
            if np.isnan(g.c[r, j]): continue
            worst = min(worst, ((g.l[r, j] if s > 0 else g.h[r, j]) - e) * s)
            if (g.l[r, j] <= sp) if s > 0 else (g.h[r, j] >= sp):
                px = (min(g.o[r, j], sp) if s > 0 else max(g.o[r, j], sp)) - s * TICK; break
        if px is None: px = g.c[r, jx] - s * TICK
        net = (px - e) * s * PV - COMM
        rows.append(dict(date=d, side=s, z=z, net=net, adv=min(worst * PV - COMM, net), risk=stop * atr[r] * PV))
    return pd.DataFrame(rows)


def line(x, d, nm):
    x = pd.Series(np.asarray(x, float)); d = pd.DatetimeIndex(d); tt = lambda v: v.mean() / v.std(ddof=1) * np.sqrt(len(v)) if len(v) > 2 else np.nan
    a, b = x[(d < "2023").tolist()], x[(d >= "2023").tolist()]; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    cum = pd.Series(x.values, index=d).groupby(level=0).sum().cumsum(); mdd = (cum.cummax() - cum).max()
    return (f"   {nm:<40} n {len(x):5d} ${x.mean():5.0f} t {tt(x):5.2f} PF {pf:4.2f} total ${x.sum() / 1000:5.0f}k maxDD ${mdd / 1000:4.1f}k | 2018-22 ${a.mean():4.0f} (t {tt(a):4.1f})"
            f" 2023+ ${b.mean():4.0f} (t {tt(b):4.1f}) | worst ${x.min():,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    X = features(); Z = zscores(X); g = pickle.load(open("scratch_data/g24.pkl", "rb"))
    print(f"   days with flow data {len(X)} ({X.index.min().date()} -> {X.index.max().date()}); |Z| >= 1 on {np.mean(np.abs(Z.dropna()) >= 1):.0%} of days")
    T = trades(g, Z, lambda d, z: int(np.sign(z)))
    print(line(T.net, T.date, "rule: follow the price-vs-flow residual"))
    print(line(T[T.side > 0].net, T[T.side > 0].date, "   longs")); print(line(T[T.side < 0].net, T[T.side < 0].date, "   shorts"))
    print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    To = trades(g, Z, lambda d, z: -int(np.sign(z))); print(line(To.net, To.date, "opposite (follow the flow)"))
    Pm = X.P; Tm = trades(g, Z, lambda d, z: int(np.sign(Pm.get(d, 0.0)))); print(line(Tm.net, Tm.date, "no-flow control (sign of the price move)"))
    agree = np.mean([np.sign(z) == np.sign(Pm.get(d, 0.0)) for d, z in Z.items() if np.isfinite(z) and abs(z) >= 1])
    print(f"   rule side = price-move side on {agree:.0%} of trade days")
    rng = np.random.default_rng(11); pl = []
    for run in range(200):
        sides = {d: int(rng.choice([-1, 1])) for d in Z.index}
        Tp = trades(g, Z, lambda d, z: sides[d]); pl += [(run, x) for x in Tp.net]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
    print(f"   random side (200 runs, same days): ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}", flush=True)
    cd = "checks/candidates/absorption"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# Order-flow absorption, NQ (2026-11-08)\n" + __doc__.split("PRE-REGISTERED")[1].split("Checks:")[0] + "\n")
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts)
    W1, R1 = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(T.date, T.adv, T.net)])     # per MNQ
    lab = ctx["lab"]; dd = pd.Series(R1[:, -1], index=dts); span = (dts >= "2018-01-01") & (dts <= "2026-07-07")
    C = pd.DataFrame({k: lab.C[k] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "TWIN")}, index=dts)
    print("   daily corr:", C[span].corrwith(dd[span]).round(2).to_dict(), "\n")
    BB.eval_bench(ctx, {f"+ absorption {n} MNQ": (n * W1, n * R1) for n in (2,)}, end="2026-06-01")
    print()
    BB.funded_bench(ctx, {"+ absorption 2 MNQ": {**BB.BASE_FUNDED, "ABS": 2}}, extra={"ABS": (W1, R1[:, -1])}, end="2026-07-07")
    print("\n   Personal book 1-year MC return / DD p95 (+ 1 MNQ, to 2026-07-07):")
    BB.personal({"+ absorption 1 MNQ": (T.net / 10 - 0.55).groupby(T.date).sum()}, end="2026-07-07")
