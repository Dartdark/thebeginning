"""The Bridge's indicators as filters on the plan, round 2 (2026-10-14), after the user pasted the indicator code.
Fixes round 1's gamma feature: The Bridge publishes gamma levels in NDX INDEX points; the NQ level = level + basis
(the GEX study's PlotOn = 2). Round 1 compared NQ's price with the raw flip (basis 6 -> 233 pts, 2022 -> 2026).
New features (all from data strictly before the entry minute; directional ones signed by the trade side, + = agrees):
  gamma   NQ above flip + basis (unsigned)              groom  room to the major gamma level in the trade's direction
                                                               (long: maj_pos + basis - price; short: price - maj_neg - basis), / ATR
  gcen    (price - centroid - basis) / ATR              dep10 / dep20 / dep50  (bid - ask) / (bid + ask) resting size at
                                                               10 / 20 / 50 levels (LiquidityTracker slots 48-53), 5-min mean
  wallimb (largest bid wall - largest ask wall) / sum (Heatmap slots 54-61)
  wallroom distance to the largest opposing wall in the trade's direction / ATR
  vzmid / vzglx / vzwk  (price - VWAP) / VWAP sd, VWAP anchored at midnight ET (23:00 CT), Globex (17:00 CT the day before)
          and weekly (Sunday 17:00 CT); bar-based from NQ 1-min typical price x volume (The Bridge's are tape-exact)
Same test and null as round 1 (analysis/bridge_filter_scan.py).
  python3 analysis/bridge_filter_scan2.py [SCRATCH_DIR]
"""
import sys, glob, io, contextlib, runpy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import bridge_filter_scan as B1

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
FEATS = ["gamma", "groom", "gcen", "dep10", "dep20", "dep50", "wallimb", "wallroom", "vzmid", "vzglx", "vzwk"]
UNSIGNED = {"gamma", "groom", "wallroom"}

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/plan_agreement_test.py", run_name="__main__")
    T = ns["T"]; T = T[T.strat.isin(["VB", "ONB_ML", "MON", "EOS", "LDF"])].reset_index(drop=True)
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15)
    tp = ((g.h + g.l + g.c) / 3).ravel(); v = np.nan_to_num(g.v.ravel()); cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    tpv = np.where(np.isnan(tp), 0, tp * v); tp2v = np.where(np.isnan(tp), 0, tp * tp * v)
    cV, cPV, cP2V = np.cumsum(v), np.cumsum(tpv), np.cumsum(tp2v)
    def vz(a, b):   # VWAP over flat minutes [a, b), price at b-1
        V = cV[b - 1] - (cV[a - 1] if a > 0 else 0)
        if V <= 0: return np.nan
        m = (cPV[b - 1] - (cPV[a - 1] if a > 0 else 0)) / V; s2 = (cP2V[b - 1] - (cP2V[a - 1] if a > 0 else 0)) / V - m * m
        return (cf[b - 1] - m) / np.sqrt(s2) if s2 > 0 else np.nan
    OFc = ["date", "time", "close", "s48", "s49", "s50", "s51", "s52", "s53", "s54", "s55", "s56", "s57", "s58", "s59", "s60", "s61"]
    OF = pd.concat(pd.read_csv(f, usecols=OFc) for f in sorted(glob.glob("OF_1min_*.csv"))); OF["m"] = B1.ct_min(OF.time.to_numpy())
    byd = {d: x.sort_values("m") for d, x in OF.groupby("date")}
    G = pd.concat(pd.read_csv(f, usecols=["date", "time", "close", "flip", "centroid", "maj_pos", "maj_neg", "basis"])
                  for f in sorted(glob.glob("GEX_1min_20*.csv")))
    G = G[(G.date >= 20230328)]; G["m"] = B1.ct_min(G.time.to_numpy()); gb = {d: x.sort_values("m") for d, x in G.groupby("date")}
    rows = []
    for r in T.itertuples():
        f = dict.fromkeys(FEATS, np.nan); key = int(r.date.strftime("%Y%m%d")); A = atr[r.day] if not np.isnan(atr[r.day]) else np.nan
        x = byd.get(key)
        if x is not None:
            p = x[x.m < r.j0]
            if len(p):
                l5, last = p.tail(5), p.iloc[-1]
                for k, (bc, ac) in zip(("dep10", "dep20", "dep50"), (("s48", "s49"), ("s50", "s51"), ("s52", "s53"))):
                    b_, a_ = l5[bc].mean(), l5[ac].mean(); f[k] = (b_ - a_) / (b_ + a_) if b_ + a_ > 0 else np.nan
                bw, aw = max(last.s55, last.s57), max(last.s59, last.s61)
                f["wallimb"] = (bw - aw) / (bw + aw) if bw + aw > 0 else np.nan
                if A > 0:
                    if r.side > 0:
                        wp = last.s58 if last.s59 >= last.s61 else last.s60; f["wallroom"] = (wp - last.close) / A if wp > 0 else np.nan
                    else:
                        wp = last.s54 if last.s55 >= last.s57 else last.s56; f["wallroom"] = (last.close - wp) / A if wp > 0 else np.nan
        y = gb.get(key)
        if y is not None:
            q = y[(y.m < r.j0) & (y.flip > 0) & (y.basis > 0)]
            if len(q):
                L = q.iloc[-1]; px = L.close
                f["gamma"] = float(px > L.flip + L.basis)
                if A > 0:
                    if L.maj_pos > 0 and L.maj_neg > 0:
                        f["groom"] = ((L.maj_pos + L.basis - px) if r.side > 0 else (px - L.maj_neg - L.basis)) / A
                    if L.centroid > 0: f["gcen"] = (px - L.centroid - L.basis) / A
        e = int(r.day) * 1440 + int(r.j0)
        f["vzmid"] = vz((int(r.day) - 1) * 1440 + 23 * 60, e)
        f["vzglx"] = vz((int(r.day) - 1) * 1440 + 17 * 60, e)
        wd = pd.Timestamp(g.ts[int(r.day)]).dayofweek; sun = int(r.day) - (wd + 1)   # Sunday before
        f["vzwk"] = vz(sun * 1440 + 17 * 60, e)
        rows.append(f)
    F = pd.DataFrame(rows, index=T.index)
    for c in FEATS:
        if c not in UNSIGNED: F[c] = F[c] * T.side
    B1.FEATS, B1.UNSIGNED = FEATS, UNSIGNED
    print("feature coverage (%):"); print((F.notna().groupby(T.strat).mean() * 100).round(0).astype(int).to_string())
    R = B1.scan(T, F, T.net.to_numpy()); pd.set_option("display.width", 220)
    print(f"\n{len(R)} strategy x feature tests; PASS: {int(R.PASS.sum())}")
    print(R.sort_values("t_design", key=abs, ascending=False).head(12).round(2).to_string(index=False))
    rng = np.random.default_rng(1); null = []
    for _ in range(200):
        yv = T.net.to_numpy().copy()
        for s in T.strat.unique():
            m = (T.strat == s).to_numpy(); yv[m] = rng.permutation(yv[m])
        null.append(int(B1.scan(T, F, yv).PASS.sum()))
    print(f"\nnull (200 shuffles): passes mean {np.mean(null):.2f}, 95th pct {np.percentile(null, 95):.0f}, P(>= real) {np.mean(np.array(null) >= R.PASS.sum()):.2f}")
    if R.PASS.any(): print("\nPASSING:"); print(R[R.PASS].round(2).to_string(index=False))
    F.assign(strat=T.strat, date=T.date, net=T.net, side=T.side, day=T.day, j0=T.j0).to_pickle(SP + "bridge_features2.pkl")
