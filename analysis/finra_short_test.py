"""FINRA off-exchange short volume -> NQ next day (user 2026-11-08: new data). PRE-REGISTERED (header committed before the first run;
1 variant). Data: FINRA Reg SHO daily consolidated short-sale volume (cdn.finra.org CNMSshvol, from 2018-08; published the same evening),
filtered to QQQ + 10 Nasdaq-100 mega-caps (AAPL MSFT NVDA AMZN META GOOGL AVGO TSLA COST NFLX) -> data/finra/short_volume.csv.
Mechanism (DIX logic, SqueezeMetrics; tested before on S&P names as 'DIX-high long', C, t 2.1): most off-exchange 'short volume' is
market makers selling short to fill customer BUY orders, so a high short-volume ratio = heavy customer buying absorbed by dealers,
who then buy back -> upward pressure the next day; a low ratio = customer selling. New here: the Nasdaq version, traded on NQ.
Rule: ratio_s = ShortVolume / TotalVolume per symbol and day; R = equal-weight mean over the 11 symbols; Z = (R - mean of the previous
60 days) / sd of the previous 60; Z >= 1 -> long NQ the next trading day, Z <= -1 -> short; enter at the 08:31 open, stop 0.5 x ATR15,
out at the 14:55 close; CME early-close days skipped. NQ, $7.25 + 1 tick per market / stop fill.
Checks: $ a trade by period / year, longs / shorts; random side (200 runs); control = the same days with side = sign of the day's
QQQ-proxy move (NQ 08:30 -> 15:00 the signal day: is it just next-day momentum or reversal?); daily corr with the plan and with DIX
(data/DIX.csv); checker checks/candidates/finra_short/; 150K evaluation + 2 MNQ; funded 150K x 1.5 + Twin 2 + 2 MNQ; personal + 1 MNQ.
  tools/run_stamped.sh analysis/finra_short_test.py > analysis/outputs/finra_short_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import letf_flow_test as LF
from new_sources_150k import daypaths
import bench150 as BB

SYMS = ["QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "AVGO", "TSLA", "COST", "NFLX"]

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    F = pd.read_csv("data/finra/short_volume.csv", sep="|", parse_dates=["Date"])
    F = F[F.Symbol.isin(SYMS) & (F.TotalVolume > 0)]; F["r"] = F.ShortVolume / F.TotalVolume
    W = F.pivot_table(index="Date", columns="Symbol", values="r"); R = W.mean(axis=1)
    print(f"   FINRA days {len(R)} ({R.index.min().date()} -> {R.index.max().date()}); mean ratio {R.mean():.3f}; symbols per day min {W.notna().sum(axis=1).min()}")
    Z = (R - R.rolling(60).mean().shift(1)) / R.rolling(60).std().shift(1)
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); days = pd.DatetimeIndex(g.ts[g.trading])
    sig = {}
    for d, z in Z.dropna().items():
        later = days[days > d]
        if len(later) and abs(z) >= 1.0: sig.setdefault(later[0], z)
    sig = pd.Series(sig).sort_index(); print(f"   signal days {len(sig)}")
    kw = dict(t0=830, t1=1455, stop=0.5)
    T = LF.trades(g, sig, lambda d, z: int(np.sign(z)), **kw)
    print(LF.line(T.net, T.date, "rule: high short ratio -> long next day")); print(LF.line(T[T.side > 0].net, T[T.side > 0].date, "   longs")); print(LF.line(T[T.side < 0].net, T[T.side < 0].date, "   shorts"))
    print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    To = LF.trades(g, sig, lambda d, z: -int(np.sign(z)), **kw); print(LF.line(To.net, To.date, "opposite (informed-shorting reading)"))
    rth = pd.Series(g.c[g.trading, jof(1500)] - g.o[g.trading, jof(831)], index=days).shift(1).fillna(0.0)
    Tc = LF.trades(g, sig, lambda d, z: int(np.sign(rth.get(d, 0.0))), **kw); print(LF.line(Tc.net, Tc.date, "control: follow the signal day's NQ move"))
    agree = np.mean([np.sign(z) == np.sign(rth.get(d, 0.0)) for d, z in sig.items()]); print(f"   rule side = signal-day move side on {agree:.0%} of days")
    rng = np.random.default_rng(17); pl = []
    for run in range(200):
        sides = {d: int(rng.choice([-1, 1])) for d in sig.index}; Tp = LF.trades(g, sig, lambda d, z: sides[d], **kw); pl += [(run, x) for x in Tp.net]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
    print(f"   random side (200 runs): ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}", flush=True)
    dix = pd.read_csv("data/DIX.csv"); dc = [c for c in dix.columns if c.lower() in ("date",)][0]; dix[dc] = pd.to_datetime(dix[dc]); dix = dix.set_index(dc)
    dcol = [c for c in dix.columns if c.lower() == "dix"]
    if dcol: print(f"   corr of R with DIX (same day): {pd.concat([R, dix[dcol[0]]], axis=1).dropna().corr().iloc[0, 1]:.2f}")
    cd = "checks/candidates/finra_short"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# FINRA short volume (Nasdaq DIX) -> NQ next day (2026-11-08)\n" + __doc__.split("PRE-REGISTERED")[1].split("Checks:")[0] + "\n")
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts)
    W1, R1 = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(T.date, T.adv, T.net)])
    lab = ctx["lab"]; dd = pd.Series(R1[:, -1], index=dts); span = dts >= "2018-08-01"
    C = pd.DataFrame({k: lab.C[k] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "TWIN")}, index=dts)
    print("   daily corr:", C[span].corrwith(dd[span]).round(2).to_dict(), "\n")
    BB.eval_bench(ctx, {"+ FINRA short 2 MNQ": (2 * W1, 2 * R1)})
    print()
    BB.funded_bench(ctx, {"+ FINRA short 2 MNQ": {**BB.BASE_FUNDED, "FSV": 2}}, extra={"FSV": (W1, R1[:, -1])})
    print("\n   Personal book 1-year MC return / DD p95 (+ 1 MNQ):")
    BB.personal({"+ FINRA short 1 MNQ": (T.net / 10 - 0.55).groupby(T.date).sum()})
