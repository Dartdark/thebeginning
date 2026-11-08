"""Leveraged-ETF fund flows -> closing hedge demand, NQ (user 2026-11-08: 'golden goose' hunt, new data). PRE-REGISTERED (header committed
before the first run; 1 variant; new mechanism and new use of data/letf).
Mechanism: creations / redemptions in the Nasdaq-100 leveraged and inverse ETFs force ProShares to add / cut Nasdaq exposure at the cash
close of the day they are processed. Retail flows into these funds come in waves (dip buying, hedging runs), so a big net flow yesterday
predicts more flow, and more closing hedge trades in the same direction, today.
Data: ProShares daily NAV / AUM (data/letf/: TQQQ +3, SQQQ -3, QLD +2, QID -2; to 2026-10-21). Fund dollar flow on day D (split-proof):
flow_D = AUM_D - AUM_{D-1} x NAV_D / NAV_{D-1}; Nasdaq exposure flow X_D = sum over funds of L x flow_D. Point in time: the row for D is
published the evening of D, so a trade on D uses X_{D-1}.
Rule: Z = X_{D-1} / sd of X over the previous 60 trading days (past only); |Z| >= 1.0 -> at 14:30 CT follow sign(Z) (net bullish exposure
created -> long) at the 14:31 open, stop 0.25 x ATR15, out at the 15:00 close (the cash close, where creations are hedged). CME early-
close days skipped. NQ, $7.25 + 1 tick per market / stop fill.
Checks: lag-1 autocorrelation of X (the persistence the mechanism needs); $ a trade by period / year, longs / shorts; random side on the
same days (200 runs); control = same days, side = -sign(yesterday's NQ cash-session return) (LETF flows are often dip buying: is this
just a fade of yesterday?); the same rule 14:00 -> 14:30 (Late-Day Flow's window; information); daily corr with Late-Day Flow and the
plan; checker checks/candidates/letf_flow/; 150K evaluation + 2 MNQ; funded 150K x 1.5 + Twin 2 + 2 MNQ; personal book + 1 MNQ.
  tools/run_stamped.sh analysis/letf_flow_test.py > analysis/outputs/letf_flow_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close
from new_sources_150k import daypaths
import bench150 as BB

PV, TICK, COMM = 20.0, 0.25, 7.25
FUNDS = {"TQQQ": 3, "SQQQ": -3, "QLD": 2, "QID": -2}


def exposure_flow():
    out = {}
    for f, L in FUNDS.items():
        d = pd.read_csv(f"data/letf/{f}.csv"); d["Date"] = pd.to_datetime(d.Date, format="%m/%d/%Y"); d = d.sort_values("Date").set_index("Date")
        aum, nav = d["Assets Under Management"].astype(float), d.NAV.astype(float)
        out[f] = L * (aum - aum.shift(1) * nav / nav.shift(1))
    return pd.DataFrame(out).dropna().sum(axis=1)


def trades(g, sig, side_fn, t0=1430, t1=1500, stop=0.25):
    atr = g.daily_atr(15); pos = pd.Series(np.arange(len(g.ts)), index=pd.DatetimeIndex(g.ts)); rows = []
    js, jx = jof(t0) + 1, jof(t1)
    for d, z in sig.items():
        if d < pd.Timestamp("2018-01-01") or d not in pos.index or is_early_close(d): continue
        r = int(pos[d])
        if np.isnan(atr[r]) or np.isnan(g.o[r, js]) or np.isnan(g.c[r, jx]): continue
        s = side_fn(d, z)
        if s == 0: continue
        e = g.o[r, js] + s * TICK; sp = e - s * stop * atr[r]; px = None; worst = 0.0
        for j in range(js, jx + 1):
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
    return (f"   {nm:<42} n {len(x):5d} ${x.mean():5.0f} t {tt(x):5.2f} PF {pf:4.2f} total ${x.sum() / 1000:5.0f}k maxDD ${mdd / 1000:4.1f}k | 2018-22 ${a.mean():4.0f} (t {tt(a):4.1f})"
            f" 2023+ ${b.mean():4.0f} (t {tt(b):4.1f}) | worst ${x.min():,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    X = exposure_flow(); print(f"   exposure flow days {len(X)} ({X.index.min().date()} -> {X.index.max().date()}); lag-1 autocorr 2018+ {X[X.index >= '2018'].autocorr(1):.2f} (rank {pd.Series(X[X.index >= '2018'].rank()).autocorr(1):.2f})")
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); days = pd.DatetimeIndex(g.ts[g.trading])
    sd = X.rolling(60).std().shift(1); Zf = (X / sd)                                          # Z on the flow day, past-only scale
    # trade day = the next NQ trading day after the flow day
    nxt = {d: days[days > d][0] for d in Zf.dropna().index if (days > d).any()}
    sig = pd.Series({nxt[d]: z for d, z in Zf.dropna().items() if d in nxt and abs(z) >= 1.0}).sort_index()
    sig = sig[~sig.index.duplicated()]
    print(f"   signal days {len(sig)} (|Z| >= 1 on {np.mean(np.abs(Zf.dropna()) >= 1):.0%} of flow days)")
    T = trades(g, sig, lambda d, z: int(np.sign(z)))
    print(line(T.net, T.date, "rule: follow yesterday's LETF flow 14:30-15:00"))
    print(line(T[T.side > 0].net, T[T.side > 0].date, "   longs")); print(line(T[T.side < 0].net, T[T.side < 0].date, "   shorts"))
    print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    rth = pd.Series(g.c[g.trading, jof(1500)] - g.o[g.trading, jof(831)], index=days); prev = rth.shift(1)
    Tc = trades(g, sig, lambda d, z: -int(np.sign(prev.get(d, 0.0)))); print(line(Tc.net, Tc.date, "control: fade yesterday's cash session"))
    agree = np.mean([np.sign(z) == -np.sign(prev.get(d, 0.0)) for d, z in sig.items()]); print(f"   rule side = fade-yesterday side on {agree:.0%} of signal days")
    Tw = trades(g, sig, lambda d, z: int(np.sign(z)), t0=1400, t1=1430); print(line(Tw.net, Tw.date, "same rule 14:00-14:30 (info)"))
    rng = np.random.default_rng(5); pl = []
    for run in range(200):
        sides = {d: int(rng.choice([-1, 1])) for d in sig.index}
        Tp = trades(g, sig, lambda d, z: sides[d]); pl += [(run, x) for x in Tp.net]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
    print(f"   random side (200 runs, same days): ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}", flush=True)
    cd = "checks/candidates/letf_flow"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# Leveraged-ETF flow -> closing hedge demand, NQ (2026-11-08)\n" + __doc__.split("PRE-REGISTERED")[1].split("Checks:")[0] + "\n")
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts)
    W1, R1 = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(T.date, T.adv, T.net)])
    lab = ctx["lab"]; dd = pd.Series(R1[:, -1], index=dts); span = dts >= "2018-01-01"
    C = pd.DataFrame({k: lab.C[k] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "TWIN")}, index=dts)
    print("   daily corr:", C[span].corrwith(dd[span]).round(2).to_dict(), "\n")
    BB.eval_bench(ctx, {"+ LETF flow 2 MNQ": (2 * W1, 2 * R1)})
    print()
    BB.funded_bench(ctx, {"+ LETF flow 2 MNQ": {**BB.BASE_FUNDED, "LFL": 2}}, extra={"LFL": (W1, R1[:, -1])})
    print("\n   Personal book 1-year MC return / DD p95 (+ 1 MNQ):")
    BB.personal({"+ LETF flow 1 MNQ": (T.net / 10 - 0.55).groupby(T.date).sum()})
