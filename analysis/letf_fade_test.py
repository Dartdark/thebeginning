"""FADE leveraged-ETF flow into the close, NQ (user 2026-11-08). POST HOC in origin (letf_flow_test.py: following the flow lost $139 a
trade, t -3.58, while a fade-yesterday control was flat); header committed before this run; counts as a 2nd variant, so the bar is
t >= the multiple-testing threshold (~3.65) or DSR >= 0.95, not 2.0. Same days and rule as letf_flow_test with the side flipped:
Z = yesterday's Nasdaq exposure flow of TQQQ / SQQQ / QLD / QID (L x fund dollar flow) / its past-60-day sd; |Z| >= 1.0 -> at 14:30 CT
trade AGAINST sign(Z) at the 14:31 open, stop 0.25 x ATR15, out at the 15:00 close; early-close days skipped; $7.25 + 1 tick per fill.
Possible mechanism (to check, not assumed): ProShares' swap dealers pre-hedge creations before the close, or retail flows mark a
local extreme; whichever, the price into the next close goes the other way.
Checks: by period / year, longs / shorts, Z >= 2 subset (information); random side (200 runs); checker checks/candidates/letf_fade/
(pre_registered false, 2 variants); 150K evaluation + 2 MNQ; funded 150K x 1.5 + Twin 2 + 2 MNQ; personal book + 1 MNQ.
  tools/run_stamped.sh analysis/letf_fade_test.py > analysis/outputs/letf_fade_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import letf_flow_test as LF
from new_sources_150k import daypaths
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    X = LF.exposure_flow(); g = pickle.load(open("scratch_data/g24.pkl", "rb")); days = pd.DatetimeIndex(g.ts[g.trading])
    sd = X.rolling(60).std().shift(1); Zf = X / sd
    nxt = {d: days[days > d][0] for d in Zf.dropna().index if (days > d).any()}
    sig = pd.Series({nxt[d]: z for d, z in Zf.dropna().items() if d in nxt and abs(z) >= 1.0}).sort_index(); sig = sig[~sig.index.duplicated()]
    T = LF.trades(g, sig, lambda d, z: -int(np.sign(z)))
    print(LF.line(T.net, T.date, "fade yesterday's LETF flow 14:30-15:00"))
    print(LF.line(T[T.side > 0].net, T[T.side > 0].date, "   longs (after net bearish flow)")); print(LF.line(T[T.side < 0].net, T[T.side < 0].date, "   shorts (after net bullish flow)"))
    big = T[np.abs(T.z) >= 2.0]; print(LF.line(big.net, big.date, "   |Z| >= 2 only (info)"))
    print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    rng = np.random.default_rng(7); pl = []
    for run in range(200):
        sides = {d: int(rng.choice([-1, 1])) for d in sig.index}
        Tp = LF.trades(g, sig, lambda d, z: sides[d]); pl += [(run, x) for x in Tp.net]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
    print(f"   random side (200 runs): ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}", flush=True)
    cd = "checks/candidates/letf_fade"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": False, "variants": 2}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# Fade leveraged-ETF flow into the close, NQ (2026-11-08, post hoc in origin)\n" + __doc__.split("Same days and rule as letf_flow_test with the side flipped:")[1].split("Possible mechanism")[0] + "\n")
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts)
    W1, R1 = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(T.date, T.adv, T.net)])
    lab = ctx["lab"]; dd = pd.Series(R1[:, -1], index=dts); span = dts >= "2018-01-01"
    C = pd.DataFrame({k: lab.C[k] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "TWIN")}, index=dts)
    print("   daily corr:", C[span].corrwith(dd[span]).round(2).to_dict(), "\n")
    BB.eval_bench(ctx, {"+ LETF fade 2 MNQ": (2 * W1, 2 * R1)})
    print()
    BB.funded_bench(ctx, {"+ LETF fade 2 MNQ": {**BB.BASE_FUNDED, "LFD": 2}}, extra={"LFD": (W1, R1[:, -1])})
    print("\n   Personal book 1-year MC return / DD p95 (+ 1 MNQ):")
    BB.personal({"+ LETF fade 1 MNQ": (T.net / 10 - 0.55).groupby(T.date).sum()})
