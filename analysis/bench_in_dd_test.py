"""'A strategy in heavy drawdown stays on the bench; failures cluster, and so do passes' (The Bridge, 'Propfirms as a business',
live 005, 2026). Tested on our plan's MultiCharts trade lists (per contract, $7.25 + 1 tick a market / stop fill), 2018-2026.
  A  trade level, per strategy: the next trade's P&L (in the strategy's own sd units, z) when the strategy's running equity is
     (1) below its 20-trade moving average, (2) in a drawdown >= 3 average-loss sizes from its peak, (3) after 3+ losses in a row;
     vs the other trades. Pooled and per strategy, design 2018-22 / holdout 2023-26. Also lag-1 autocorrelation of trade P&L.
  B  combine level (current combine set: VB 8 + ONB ADX30 $1,100 + Bridge Monday 2 + EOS $500, Apex rules as in
     analysis/combine_addons_test.py): back-to-back evaluations (the next starts the trading day after the previous ends), from
     every start day of the first 60; P(pass | previous passed) vs P(pass | previous failed)
  C  the bench rule on the combine: skip VB / ONB while their own shadow equity is below its 20-trade average
  python3 analysis/bench_in_dd_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths, challenge
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def states(x):
    """per trade, known before it: below 20-trade equity MA, deep drawdown, 3+ losses in a row."""
    eq = x.cumsum().shift(1).fillna(0); ma = eq.rolling(20, min_periods=20).mean()
    dd = eq.cummax() - eq; avl = (-x[x < 0]).expanding().mean().reindex(x.index).ffill().shift(1)
    l = (x < 0).astype(int); streak = l.groupby((l != l.shift()).cumsum()).cumsum().where(l == 1, 0).shift(1).fillna(0)
    return pd.DataFrame({"below_ma": eq < ma, "deep_dd": dd >= 3 * avl, "streak3": streak >= 3}, index=x.index)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        T = runpy.run_path("analysis/plan_agreement_test.py", run_name="__main__")["T"]
    T = T.sort_values(["strat", "date", "j0"]).reset_index(drop=True)
    print("\nA. Next trade (z = P&L / strategy sd) in each state vs not")
    St = pd.concat([states(g.net) for _, g in T.groupby("strat")]).reindex(T.index)
    rows = []
    for c in St:
        for s_, g in [("POOLED", T)] + list(T.groupby("strat")):
            m = St.loc[g.index, c].astype(bool); a, b = g.z[m], g.z[~m]
            if len(a) < 10: continue
            t = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b)); y = g.date.dt.year
            dz = lambda k: g.z[m & k].mean() - g.z[~m & k].mean()
            rows.append(dict(state=c, strat=s_, n_in=len(a), z_in=a.mean(), z_out=b.mean(), t=t, design=dz(y < 2023), holdout=dz(y >= 2023)))
    R = pd.DataFrame(rows); print(R.round(3).to_string(index=False))
    ac = {s_: round(g.net.autocorr(1), 3) for s_, g in T.groupby("strat")}; print("   lag-1 autocorrelation of trade P&L:", ac)

    print("\nB/C. Combine: back-to-back evaluations, and the bench rule")
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year
    P = {}
    def add(nm, t):
        w, r = paths(g, t); P[nm] = (w[tr] / 10, r[tr] / 10); return t
    tv = add("VB", with_slippage(load_mc(g, REPORTS["VB"][0])))
    to = add("ONB30", with_slippage(load_mc(g, "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx")))
    add("MON_BR", load_bridge_mc(g)); add("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    q_onb = risk(1100, 0.25); q_eos = risk(500, REPORTS["EOS"][1])

    def bench_mask(t):
        """per trading row: 1 = trade, 0 = benched (shadow equity below its 20-trade MA before the day)."""
        x = pd.Series((t.exit - t.entry).to_numpy() * t.side.to_numpy(), index=t.day.to_numpy())
        st = states(x.reset_index(drop=True)); on = pd.Series(~st.below_ma.to_numpy(), index=x.index)
        on = on.groupby(level=0).first(); row = pd.Series(1.0, index=np.arange(len(g.ts)))
        row.loc[on.index] = on.astype(float).to_numpy(); return row.to_numpy()[tr][:, None]

    def combo(mv=1.0, mo=1.0):
        W = P["VB"][0] * 8 * mv + P["ONB30"][0] * q_onb * mo + P["MON_BR"][0] * 2 + P["EOS"][0] * q_eos
        Rr = P["VB"][1] * 8 * mv + P["ONB30"][1] * q_onb * mo + P["MON_BR"][1] * 2 + P["EOS"][1] * q_eos
        return W, Rr

    def every_start(W, Rr):
        res = [challenge(W, Rr, np.arange(s, min(s + 21, D))) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018)
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        return np.nanmean(o[ok]), np.nanmean(o[ok & (yr >= 2023)]), res

    W, Rr = combo(); base, base23, res = every_start(W, Rr)
    prev, cur = [], []
    s0 = int(np.argmax(yr >= 2018))
    for off in range(60):
        s = s0 + off; last = None
        while s < D - 21:
            x = res[s]
            if x is None: s += 1; continue
            p = x[0] == "pass"; L = int(x[1]) if x[1] is not None else 21
            if last is not None: prev.append(last); cur.append(p)
            last = p; s += max(L, 1) + 1
    prev, cur = np.array(prev), np.array(cur)
    print(f"   back-to-back: P(pass | prev pass) {cur[prev].mean():.1%} (n {prev.sum()}), P(pass | prev fail) {cur[~prev].mean():.1%} "
          f"(n {(~prev).sum()}), unconditional {base:.1%}")
    for nm, mv, mo in (("current combine", 1, 1), ("bench VB below its 20-trade MA", bench_mask(tv), 1),
                       ("bench ONB below its 20-trade MA", 1, bench_mask(to)), ("bench both", bench_mask(tv), bench_mask(to))):
        a, b, _ = every_start(*combo(mv, mo))
        print(f"   {nm:<34} pass 2018-26 {a:.1%}  2023-26 {b:.1%}")
