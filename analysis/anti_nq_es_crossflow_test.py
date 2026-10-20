"""Antigravity's NQESCrossFlow (antigravity/jesse 2026-10-20, 'sister strategy' to Relative Strength): rebuild with the RS
machinery. At 10:00 CT: residual = (NQ % 9:30 -> 10:00) - 1.25 x (ES %); |residual| >= 0.25% with ES the same sign -> follow
at the 10:01 open; stop 0.6 x / target 1.2 x the 20-day RTH range (its report: 0.6 / 1.2 x daily ATR; its code: fixed 65 / 130
pts); flat 15:00. Then: RS alone vs RS + CrossFlow at equal size (daily P&L), and CrossFlow on RS days vs other days.
  python3 analysis/anti_nq_es_crossflow_test.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import relative_strength_test as RS, metrics as M

if __name__ == "__main__":
    days, N, E = RS.load(); idx = pd.DatetimeIndex([pd.Timestamp(str(x)) for x in days.date])
    j0, j1 = 60, 90                                                    # 9:30 and 10:00 bar closes (col 0 = 8:30)
    rn = N["c"][:, j1] / N["c"][:, j0] - 1; re = E[:, j1] / E[:, j0] - 1; res = rn - 1.25 * re
    sig = np.where((res >= 0.0025) & (re > 0), 9.0, np.where((res <= -0.0025) & (re < 0), -9.0, np.nan))
    X = RS.trades(days, N, sig, decide=1000, tgt_f=1.2); RS.line("CrossFlow rebuild (range exits)", X)
    th = pd.read_csv(RS.SP + "anti/xflow_trades.csv"); th["date"] = pd.to_datetime(th.date.astype(str))
    mg = th.merge(X, on="date"); print(f"   its trades.csv {len(th)} (${th.pnl.mean():.0f}); shared days {len(mg)}, same side {np.mean(mg.side_x == mg.side_y):.0%}")
    T = RS.trades(days, N, RS.signals(days, N, E))
    d = lambda t: t.groupby("date").pnl.sum().reindex(idx, fill_value=0.0)
    a, c = d(T), d(T) + d(X)
    for nm, s in (("RS alone", a), ("RS + CrossFlow", c), ("CrossFlow alone", d(X))):
        p = M.perf(s); h = M.perf(s[s.index >= "2023"])
        print(f"   {nm:<16} ${s.sum():>9,.0f}  Sharpe {p['sharpe']:.2f} (2023+ {h['sharpe']:.2f})  max DD ${p['max_dd']:,.0f}  Calmar {p['calmar']:.2f}")
    print(f"   daily corr RS vs CrossFlow: {a.corr(d(X)):.2f}; CrossFlow days that are RS days {X.date.isin(T.date).mean():.0%}")
    on = X.date.isin(T.date); RS.line("   CrossFlow on RS days", X[on]); RS.line("   CrossFlow on non-RS days", X[~on])

    # its own trades (its report's Z rule; its code's 0.25% threshold gives only ~60 trades on our data, above)
    print("\nIts trades.csv (298, its Z version), with Relative Strength:")
    s2 = th.groupby("date").pnl.sum().reindex(idx, fill_value=0.0); A2 = th.assign(pnl=th.pnl)
    RS.line("   its CrossFlow trades", A2)
    for nm, s in (("RS alone", a), ("RS + its CrossFlow", a + s2)):
        p = M.perf(s); h = M.perf(s[s.index >= "2023"]); dsg = M.perf(s[s.index < "2023"])
        print(f"   {nm:<20} ${s.sum():>9,.0f}  Sharpe {p['sharpe']:.2f} (2018-22 {dsg['sharpe']:.2f}, 2023+ {h['sharpe']:.2f})  max DD ${p['max_dd']:,.0f}")
    print(f"   daily corr: {a.corr(s2):.2f}")
