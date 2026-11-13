"""Twin's Morning Momentum filtered by the previous session's closing order flow x VIX (user 2026-11-08, batch of 5, test 5).
PRE-REGISTERED (header committed before the first run; 1 variant, filter). Base: Twin cap1 v2.1 (twin_continuation_test.simulate,
max_stop_mult 1, v21), its MO trades. Overnight-flow direction for the morning of date d = Overnight Tick's order-flow x VIX cell of the
session before d (the night that ends on d, checks/candidates/overnight_tick/nights.csv, any day: cell = (flow < 0 and VIX > SMA25) or
(flow >= 0 and VIX <= SMA25) -> +1, else -1). Keep an MO trade when its side equals that direction; MO days with no signal (no
order-flow data, contract-switch nights, holidays) are kept and left out of the filter statistics. Breakout trades untouched.
Checks: kept vs skipped (longs and shorts separately), by period and year; checker (kind filter) checks/candidates/twin_mo_flow/;
as a REPLACEMENT of Twin cap1 2 MNQ in the 150K evaluation and the funded 150K x 1.5 (to 2026-07-07, the order-flow span), and of
Twin v2.1 (uncapped) 1 MNQ in the personal book.
  tools/run_stamped.sh analysis/twin_mo_flow_test.py > analysis/outputs/twin_mo_flow_test_output.txt
"""
import sys, os, json, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc
from twin_continuation_bench import grids
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(); g, B, Tn, dts = ctx["g"], ctx["B"], ctx["Tn"].reset_index(drop=True), ctx["dts"]
    N = pd.read_csv("checks/candidates/overnight_tick/nights.csv", parse_dates=["date", "sess"]); N = N[N.rsv.notna() & N.hi25.notna() & ~N.half]
    cell = ((N.rsv < 0) & N.hi25.astype(bool)) | ((N.rsv >= 0) & ~N.hi25.astype(bool)); dirn = pd.Series(np.where(cell, 1, -1), index=N.date).groupby(level=0).first()
    def tag(T):
        mo = T.setup == "MO"; d = T.date.map(dirn); has = mo & d.notna()
        keep = ~mo | d.isna() | (T.side == d); return keep.to_numpy(), has.to_numpy()
    keep, has = tag(Tn)
    X = Tn[has].copy(); X["kept"] = keep[has].astype(int)
    tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan
    print(f"   MO trades {int((Tn.setup == 'MO').sum())}, with a flow signal {len(X)} (to {X.date.max().date()})")
    for nm, m in (("all MO (with signal)", np.ones(len(X), bool)), ("kept: side = flow direction", X.kept == 1), ("skipped", X.kept == 0),
                  ("kept longs", (X.kept == 1) & (X.side > 0)), ("skipped longs", (X.kept == 0) & (X.side > 0)),
                  ("kept shorts", (X.kept == 1) & (X.side < 0)), ("skipped shorts", (X.kept == 0) & (X.side < 0))):
        x = X[m]; a, b = x[x.date < "2023"].net, x[x.date >= "2023"].net
        print(f"   {nm:<30} n {len(x):4d} ${x.net.mean():5.0f} t {tt(x.net):5.2f} | 2018-22 ${a.mean():.0f} (t {tt(a):.1f}) 2023+ ${b.mean():.0f} (t {tt(b):.1f}) | total ${x.net.sum():,.0f}")
    print("   $ a trade by year (0 skipped / 1 kept):", X.groupby([X.date.dt.year, "kept"]).net.mean().unstack().round(0).to_dict(orient="index"))
    cd = "checks/candidates/twin_mo_flow"; os.makedirs(cd, exist_ok=True)
    X.assign(date=X.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "kept"]].to_csv(f"{cd}/trades.csv", index=False)
    json.dump({"kind": "filter", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# Twin MO x closing order flow (2026-11-08)\nBase: Twin cap1 v2.1 Morning Momentum trades on NQ ($7.25 + 1 tick). Filter: keep an MO trade when its side equals the previous session's Overnight Tick cell direction (+1 when (flow 14:15-15:15 CT < 0 and VIX > SMA25) or (flow >= 0 and VIX <= SMA25), else -1). Order flow = The Bridge aggressor volume (NQ).\n")
    # replacement benches (to the order-flow end)
    Tf = Tn[keep]; Wf, Rf = grids(g, B, Tf); Wf, Rf = Wf[ctx["trr"]] / 10, Rf[ctx["trr"]] / 10; Wt, Rt = ctx["Wt"], ctx["Rt"]
    print()
    BB.eval_bench(ctx, {"Twin 2 MNQ -> MO-filtered Twin 2 MNQ": (2 * (Wf - Wt), 2 * (Rf - Rt))}, end="2026-06-01")
    print()
    base_no = {k: v for k, v in BB.BASE_FUNDED.items() if k != "TWIN"}
    BB.funded_bench(ctx, {"Twin -> MO-filtered Twin 2 MNQ": {**base_no, "TWINF": 2}}, extra={"TWINF": (Wf, Rf[:, -1])}, end="2026-07-07")
    Tu = tc.simulate(B, v21=True); Tu = Tu[Tu.date >= "2018-01-01"].reset_index(drop=True); ku, _ = tag(Tu)
    du = lambda T: T.groupby("date").net.sum() / 10 - 0.55 * T.groupby("date").size()
    print("\n   Personal book 1-year MC return / DD p95 (Twin column replaced by the v2.1 sim, as is vs MO-filtered; to 2026-07-07):")
    BB.personal({"Twin v2.1 sim": du(Tu), "MO-filtered": du(Tu[ku])}, drop=("TwinContinuation",), end="2026-07-07")
