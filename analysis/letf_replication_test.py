"""Replication of the LETF-flow fade on ES and YM (user 2026-11-08). PRE-REGISTERED (header committed before the first run; rules frozen
from analysis/letf_fade_test.py, nothing re-tuned; data downloaded 2026-11-08 from ProShares, never looked at for returns before).
  ES: S&P 500 funds UPRO +3, SPXU -3, SSO +2, SDS -2; ES $50 a point, tick 0.25, $5 + 1 tick per fill (MES = 1/10)
  YM: Dow 30 funds UDOW +3, SDOW -3, DDM +2, DXD -2; YM $5 a point, tick 1, $5 + 1 tick per fill (MYM = 1/10)
Rule (same as NQ): exposure flow X_D = sum of L x (AUM_D - AUM_{D-1} x NAV_D / NAV_{D-1}); Z = X_{D-1} / past-60-day sd; |Z| >= 1 ->
trade AGAINST sign(Z) at the 14:31 CT open, stop 0.25 x ATR15, out at the 15:00 close; CME early-close days skipped; 2018-26.
Also shown: the follow side (expected negative if the effect is the same); random side (200 runs); assets by year; daily corr with the
NQ fade. Success = the fade positive with t >= 2 in at least one market AND the same sign in the other. No books unless it replicates.
  tools/run_stamped.sh analysis/letf_replication_test.py > analysis/outputs/letf_replication_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import letf_flow_test as LF

MK = {"ES": dict(grid="scratch_data/ge.pkl", funds={"UPRO": 3, "SPXU": -3, "SSO": 2, "SDS": -2}, cost=(50.0, 0.25, 5.0)),
      "YM": dict(grid="scratch_data/gy.pkl", funds={"UDOW": 3, "SDOW": -3, "DDM": 2, "DXD": -2}, cost=(5.0, 1.0, 5.0))}


def flow(funds):
    out = {}
    for f, L in funds.items():
        d = pd.read_csv(f"data/letf/{f}.csv"); d["Date"] = pd.to_datetime(d.Date, format="%m/%d/%Y"); d = d.sort_values("Date").set_index("Date")
        aum, nav = d["Assets Under Management"].astype(float), d.NAV.astype(float); out[f] = L * (aum - aum.shift(1) * nav / nav.shift(1))
    return pd.DataFrame(out).dropna().sum(axis=1)


def signal(X, days):
    Zf = (X / X.rolling(60).std().shift(1)).dropna(); out = {}
    for d, z in Zf.items():
        later = days[days > d]
        if len(later) and abs(z) >= 1.0: out.setdefault(later[0], z)
    return pd.Series(out).sort_index()


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    gq = pickle.load(open("scratch_data/g24.pkl", "rb")); dq = pd.DatetimeIndex(gq.ts[gq.trading])
    nq = LF.trades(gq, signal(LF.exposure_flow(), dq), lambda d, z: -int(np.sign(z))); nqd = nq.groupby("date").net.sum()
    for m, it in MK.items():
        LF.PV, LF.TICK, LF.COMM = it["cost"]; g = pickle.load(open(it["grid"], "rb")); days = pd.DatetimeIndex(g.ts[g.trading])
        X = flow(it["funds"]); S = signal(X, days)
        f0 = list(it["funds"])[0]; d0 = pd.read_csv(f"data/letf/{f0}.csv"); d0["Date"] = pd.to_datetime(d0.Date, format="%m/%d/%Y")
        a = d0.set_index("Date")["Assets Under Management"]; print(f"\n{m}: {f0} median assets $bn by year", {y: round(a[a.index.year == y].median() / 1e9, 1) for y in range(2018, 2027)})
        T = LF.trades(g, S, lambda d, z: -int(np.sign(z))); Tf = LF.trades(g, S, lambda d, z: int(np.sign(z)))
        print(LF.line(T.net, T.date, f"{m} fade (frozen rule)")); print(LF.line(T[T.side > 0].net, T[T.side > 0].date, "   longs")); print(LF.line(T[T.side < 0].net, T[T.side < 0].date, "   shorts"))
        print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
        print(LF.line(Tf.net, Tf.date, f"{m} follow (should be negative)"))
        rng = np.random.default_rng(13); pl = []
        for run in range(200):
            sides = {d: int(rng.choice([-1, 1])) for d in S.index}; Tp = LF.trades(g, S, lambda d, z: sides[d]); pl += [(run, x) for x in Tp.net]
        pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
        print(f"   random side ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}")
        dd = T.groupby("date").net.sum(); j = pd.concat([dd, nqd], axis=1).fillna(0.0); print(f"   daily corr with the NQ fade {j.corr().iloc[0, 1]:.2f}; same-day signals {len(set(T.date) & set(nq.date))} of {len(T)}")
        cd = f"checks/candidates/letf_fade_{m.lower()}"; os.makedirs(cd, exist_ok=True)
        T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
        pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
        json.dump({"kind": "strategy", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
        open(f"{cd}/spec.md", "w").write(f"# LETF-flow fade on {m} (frozen NQ rule, 2026-11-08)\n" + __doc__.split("PRE-REGISTERED")[1].split("Also shown")[0] + "\n")
