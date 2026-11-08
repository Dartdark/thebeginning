"""WATCHLIST #30 combined (user 2026-11-08): 60-min double top (short) + double bottom (long) as ONE rule, exactly as in
chart_patterns_test.py (no parameter changes). POST HOC: chosen as the best of 33 pre-registered pattern tests, so the 2023+ split
is not a clean holdout and promotion needs t >= the multiple-testing bar. Writes checks/candidates/double_top_bottom_60m/ for the
checker (trades.csv, placebo.csv = 200 runs of random 60-min bars with the same side mix and count per year, meta.json).
  tools/run_stamped.sh analysis/double_top_bottom_60m.py > analysis/outputs/double_top_bottom_60m_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, montecarlo as MC
from candlestick_patterns_test import rth_bars
from chart_patterns_test import pivots_signals, trades

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); B = rth_bars(g, 60); d = pd.DatetimeIndex(g.ts[B.row.to_numpy()])
    S = pivots_signals(B); ALL = {s: trades(g, B, 60, s) for s in (1, -1)}; keep = d >= "2018-01-01"
    rows = []
    for nm, s in (("DTOP", -1), ("DBOT", 1)):
        m = S[nm][0] & keep & ~np.isnan(ALL[s])
        for i in np.nonzero(m)[0]: rows.append((d[i], s, ALL[s][i], nm))
    T = pd.DataFrame(rows, columns=["date", "side", "net", "kind"]).sort_values("date").reset_index(drop=True)
    x = T.net; tt = x.mean() / x.std(ddof=1) * np.sqrt(len(x))
    print(f"\ncombined: n {len(T)} ${x.mean():.0f} a trade, t {tt:.2f}, PF {x[x > 0].sum() / -x[x < 0].sum():.2f}, win {np.mean(x > 0):.0%}")
    print("   by year $:", T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   by year n:", T.groupby(T.date.dt.year).size().to_dict())
    for k_, v in (("2018-22", T[T.date < "2023"]), ("2023+", T[T.date >= "2023"])):
        print(f"   {k_}: n {len(v)} ${v.net.mean():.0f} t {v.net.mean() / v.net.std(ddof=1) * np.sqrt(len(v)):.2f}")
    print("   longs / shorts:", {nm: f"n {len(v)} ${v.net.mean():.0f}" for nm, v in T.groupby("kind")})
    # placebo: random 60-min bars, same side and count per year
    rng = np.random.default_rng(11); yrs = T.date.dt.year; pl = []
    pool = {(y, s): ALL[s][keep & (d.year == y) & ~np.isnan(ALL[s])] for y in yrs.unique() for s in (1, -1)}
    cnt = T.groupby([yrs, "side"]).size()
    for run in range(200):
        v = np.concatenate([rng.choice(pool[(y, s)], n, replace=False) for (y, s), n in cnt.items()]); pl.append((run, v))
    pm = np.array([v.mean() for _, v in pl]); print(f"   placebo (same side and count per year, 200 runs): mean ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; p {np.mean(pm >= x.mean()):.3f}")
    idx = pd.date_range("2018-01-01", T.date.max(), freq="B"); dl = T.groupby("date").net.sum().reindex(idx, fill_value=0.0)
    print(M.table({"combined": (dl, T.set_index("date").net), "2023+": (dl[dl.index >= "2023"], T[T.date >= "2023"].set_index("date").net)}))
    print(MC.report(T.net.values, daily=dl.values, size=0.1, label="double top / bottom 60-min, 1 MNQ"))
    pdp = pd.read_csv("agents/tasks/plan_daily_pnl.csv", index_col=0, parse_dates=True)
    print("   daily corr with plan pieces:", pdp.corrwith(dl.reindex(pdp.index, fill_value=0.0)).round(2).to_dict())
    nt = len([1 for l_ in open("TIER_LIST.md") if l_.startswith("| ") and "---" not in l_])
    print(f"   t needed (N = {nt}): {M.t_threshold(nt):.2f}; deflated Sharpe {M.deflated_sharpe(dl.values, nt):.2f}")
    cd = "checks/candidates/double_top_bottom_60m"; os.makedirs(cd, exist_ok=True)
    T[["date", "side", "net"]].assign(date=T.date.dt.strftime("%Y-%m-%d")).to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame([(r, v_) for r, v in pl for v_ in v], columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": False, "variants": 33}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("""# Double top / bottom, NQ 60-min RTH bars (WATCHLIST #30)
Bars: RTH 60-min (08:30-15:00 CT, last bar 14:30-15:00). ATR = 14-bar mean of high-low. Zigzag pivots: a swing high (low) is confirmed
when price falls (rises) 1.5 x ATR from the running extreme; signal on the confirmation bar.
Double top: last 3 pivots max-min-max with the two maxima within 0.75 x ATR -> short. Double bottom: min-max-min, minima within 0.75 ATR -> long.
Entry next bar open; stop 1 x ATR (of the signal bar); exit after 4 bars or at 14:59 CT; no entries from a signal bar ending 14:30 or later.
Costs: $7.25 per round trip + 1 tick per market / stop fill, per NQ. 2018-2026. Post hoc: best of 33 pre-registered pattern tests.
""")
    print(f"\n   wrote {cd}/ (trades {len(T)}, placebo 200 runs)")
