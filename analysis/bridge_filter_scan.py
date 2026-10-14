"""The Bridge's exported indicators as filters on the current plan (user's request, 2026-10-14).
Data: OF_1min_*.csv (The Bridge MBO order flow, RTH 9:30-16:15 ET = 8:30-15:15 CT, 2018-2026) and GEX_1min_*.csv (2022+).
Trades: MultiCharts lists of the plan strategies that enter inside RTH (VB, ONB ML v2, Monday Long, EOS, LDF); NFP (7:46 CT),
Bridge Monday (Sunday) and the CL fade have no order-flow data at entry. Per NQ, $7.25 + 1 tick a non-limit fill.
Each feature uses only rows strictly BEFORE the entry minute (CT = ET - 1h), signed by the trade side (+ = agrees):
  cd cum delta | d30 30-min delta | simb size imbalance (5 min) | cimb count imbalance (5) | vz (close - VWAP) / VWAP sd |
  va (close - POC) / (VAH - VAL) | pocmig POC - prior POC | pull pulled bid - ask (5) | qd queue depletion bid - ask (5) |
  ice icebergs bid - ask (30) | big big prints (30) | lvl levels bid - ask (5) | rate trade rate vs the day's median (unsigned) |
  gamma NQ above the gamma flip (unsigned, 2022+)
Pre-specified test: design 2018-22: split at the design median, keep the better half (direction chosen on design);
PASS = design |t| >= 2 AND holdout 2023-26 kept - skipped > 0 with t >= 1.5. Null: the whole scan repeated with each
strategy's P&L shuffled across its trades (200 times) -> expected passes by chance.
  python3 analysis/bridge_filter_scan.py [SCRATCH_DIR]
"""
import sys, glob, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
COLS = ["date", "time", "close", "upvol", "downvol", "size_imb", "count_imb", "qdepl_bid", "qdepl_ask", "pulled_bid",
        "pulled_ask", "ice_bid", "ice_ask", "trade_rate", "cum_delta", "levels_bid", "levels_ask", "big_trade", "vwap",
        "vwap_sd", "poc", "poc_prev", "vah", "val"]
FEATS = ["cd", "d30", "simb", "cimb", "vz", "va", "pocmig", "pull", "qd", "ice", "big", "lvl", "rate", "gamma"]
UNSIGNED = {"rate", "gamma"}


def ct_min(t):  # ET hhmm -> CT minute of day
    return (t // 100) * 60 + t % 100 - 60


def features(T):
    OF = pd.concat(pd.read_csv(f, usecols=COLS) for f in sorted(glob.glob("OF_1min_*.csv")))
    for c in ("vwap", "vwap_sd", "poc", "poc_prev", "vah", "val"): OF.loc[OF[c] == 0, c] = np.nan
    OF["m"] = ct_min(OF.time.to_numpy()); OF["delta"] = OF.upvol - OF.downvol
    G = pd.concat(pd.read_csv(f, usecols=["date", "time", "close", "flip"]) for f in sorted(glob.glob("GEX_1min_20*.csv")))
    G = G[G.flip > 0]; G["m"] = ct_min(G.time.to_numpy()); gb = {d: g for d, g in G.groupby("date")}
    byd = {d: g.sort_values("m") for d, g in OF.groupby("date")}
    rows = []
    for r in T.itertuples():
        key = int(r.date.strftime("%Y%m%d")); f = dict.fromkeys(FEATS, np.nan); g = byd.get(key)
        if g is not None:
            p = g[g.m < r.j0]
            if len(p):
                l5, l30, last = p.tail(5), p.tail(30), p.iloc[-1]
                f.update(cd=last.cum_delta, d30=l30.delta.sum(), simb=l5.size_imb.mean(), cimb=l5.count_imb.mean(),
                         vz=(last.close - last.vwap) / last.vwap_sd if last.vwap_sd > 0 else np.nan,
                         va=(last.close - last.poc) / (last.vah - last.val) if last.vah > last.val else np.nan,
                         pocmig=last.poc - last.poc_prev, pull=(l5.pulled_bid - l5.pulled_ask).mean(),
                         qd=(l5.qdepl_bid - l5.qdepl_ask).mean(), ice=(l30.ice_bid - l30.ice_ask).sum(),
                         big=l30.big_trade.sum(), lvl=(l5.levels_bid - l5.levels_ask).mean(),
                         rate=l5.trade_rate.mean() / max(p.trade_rate.median(), 1e-9))
        gg = gb.get(key)
        if gg is not None:
            q = gg[gg.m < r.j0]
            if len(q): f["gamma"] = float(q.iloc[-1].close > q.iloc[-1].flip)
        rows.append(f)
    F = pd.DataFrame(rows, index=T.index)
    for c in FEATS:
        if c not in UNSIGNED: F[c] = F[c] * T.side
    return F


def scan(T, F, pnl):
    out = []
    for s in sorted(T.strat.unique()):
        ms = (T.strat == s).to_numpy()
        for c in FEATS:
            x = F[c].to_numpy()[ms]; y = pnl[ms]; yr = T.date.dt.year.to_numpy()[ms]
            ok = ~np.isnan(x); des = ok & (yr < 2023); hol = ok & (yr >= 2023)
            if des.sum() < 30 or hol.sum() < 20: continue
            med = np.median(x[des]); hi = x >= med
            a, b = y[des & hi], y[des & ~hi]
            if len(a) < 10 or len(b) < 10: continue
            td = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
            keep = hi if td > 0 else ~hi
            k, sk = y[hol & keep], y[hol & ~keep]
            if len(k) < 5 or len(sk) < 5: continue
            th = (k.mean() - sk.mean()) / np.sqrt(k.var() / len(k) + sk.var() / len(sk))
            out.append(dict(strat=s, feat=c, n=int(ok.sum()), keep="high" if td > 0 else "low", t_design=td,
                            kept_hold=k.mean(), skipped_hold=sk.mean(), t_hold=th, PASS=abs(td) >= 2 and th >= 1.5))
    return pd.DataFrame(out)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/plan_agreement_test.py", run_name="__main__")
    T = ns["T"]; T = T[T.strat.isin(["VB", "ONB_ML", "MON", "EOS", "LDF"])].reset_index(drop=True)
    F = features(T)
    print("feature coverage (share of trades with a value):"); print((F.notna().groupby(T.strat).mean() * 100).round(0).astype(int).to_string())
    R = scan(T, F, T.net.to_numpy())
    pd.set_option("display.width", 220)
    print(f"\n{len(R)} strategy x feature tests; PASS: {int(R.PASS.sum())}")
    print(R.sort_values("t_design", key=abs, ascending=False).head(15).round(2).to_string(index=False))
    rng = np.random.default_rng(1); null = []
    for _ in range(200):
        y = T.net.to_numpy().copy()
        for s in T.strat.unique():
            m = (T.strat == s).to_numpy(); y[m] = rng.permutation(y[m])
        null.append(int(scan(T, F, y).PASS.sum()))
    print(f"\nnull (shuffled P&L, 200 runs): passes mean {np.mean(null):.2f}, 95th pct {np.percentile(null, 95):.0f}, P(>= real) {np.mean(np.array(null) >= R.PASS.sum()):.2f}")
    if R.PASS.any(): print("\nPASSING:"); print(R[R.PASS].round(2).to_string(index=False))
    F.assign(strat=T.strat, date=T.date, net=T.net, side=T.side, day=T.day, j0=T.j0).to_pickle(SP + "bridge_features.pkl")
