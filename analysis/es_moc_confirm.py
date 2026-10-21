"""ES MOC Follow: MultiCharts report vs the Python test (s_rank_es_round1_test.py section 5) and the Jesse port, trade by trade
(2026-10-17). Report: 5-minute @ES, NumContracts 1, no costs (user's run; Bar Magnifier was OFF in it).
  python3 analysis/es_moc_confirm.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.path.insert(0, "analysis/jesse")
import numpy as np, pandas as pd
from grid24 import jof
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"; sys.argv = sys.argv[:1]
import compare as C, s_rank_es_round1_test as ER, metrics as M, montecarlo as MC

REP = "mc_reports/Backtesting Strategy Performance Report _ @ES - 5 Minutes ES MOC Follow.xlsx"
PV, COMM, TICK = 50.0, 5.0, 0.25

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    m = C.mc_trades(REP); m["day"] = m.entry_time.dt.normalize()
    m["stop"] = (m.exit_time - m.entry_time) < pd.Timedelta(minutes=5)
    ge = pickle.load(open(SP + "ge.pkl", "rb")); tr = ge.trading[pd.DatetimeIndex(ge.ts[ge.trading]) >= "2018-01-01"]
    atr = ge.daily_atr(15)[tr]; cf = pd.Series(ge.c.ravel()).ffill().to_numpy(); P = lambda t: cf[tr * 1440 + jof(t)]
    full = ge.last_j[tr] >= jof(1500); mv = P(1450) - P(1400); k = full & (np.abs(mv) >= 0.3 * atr) & (mv != 0)
    t = ER.trades(ge, tr[k], np.sign(mv[k]).astype(int), jof(1451), jof(1500), 0.25 * atr[k]); t["day"] = pd.DatetimeIndex(t.date).normalize()
    t["gross_pts"] = (t.exit - t.entry) * t.side + 2 * TICK
    lo, hi = m.day.min(), m.day.max(); tp = t[(t.day >= lo) & (t.day <= hi)]
    j = pd.read_csv(SP + "jesse_ESMOCFollow.csv", parse_dates=["entry_time"]); j["day"] = j.entry_time.dt.normalize(); j = j[(j.day >= lo) & (j.day <= hi)]
    mm = m.merge(tp, on="day", how="outer", suffixes=("_mc", "_py"), indicator="src"); b = mm[mm.src == "both"]
    print(f"\nMultiCharts {len(m)} trades ({lo.date()} .. {hi.date()}) | Python {len(tp)} | Jesse {len(j)}; same days MC/Python {len(b)} "
          f"(only MC {int((mm.src == 'left_only').sum())}, only Python {int((mm.src == 'right_only').sum())}); same side {np.mean(b.side_mc == b.side_py):.1%}")
    de = (b.entry_mc - (b.entry_py - b.side_py * TICK)).abs(); dp = (b.points - b.gross_pts) * PV
    print(f"   entry price identical (Python before its 1-tick slippage) {np.mean(de < 1e-6):.1%}, within 1 tick {np.mean(de <= TICK + 1e-9):.1%}")
    print(f"   gross P&L within $25: {np.mean(dp.abs() <= 25):.1%} of matched trades; corr {np.corrcoef(b.points, b.gross_pts)[0, 1]:.3f}")
    big = b.assign(dp=dp).reindex(dp.abs().sort_values(ascending=False).index).head(5)
    for r in big.itertuples(): print(f"      {r.day.date()}: MC {r.entry_mc:.2f}->{r.exit_mc:.2f} ({'stop' if r.stop else 'close'}) | Python {r.entry_py:.2f}->{r.exit_py:.2f} kind {r.kind}  diff ${r.dp:,.0f}")
    print("   only MC:", [d.date() for d in mm[mm.src == 'left_only'].day][:10], "| only Python:", [d.date() for d in mm[mm.src == 'right_only'].day][:10])
    m["net"] = m.points * PV - COMM - (1 + m.stop.astype(int)) * TICK * PV
    x = m.set_index("entry_time").net
    y = x.index.year; pf = x[x > 0].sum() / -x[x < 0].sum()
    print(f"\nMultiCharts trades net of $5 + 1 tick per market / stop fill: n {len(x)}, ${x.mean():.0f} a trade, PF {pf:.2f}, t {x.mean() / x.std() * np.sqrt(len(x)):.1f}, "
          f"win {np.mean(x > 0):.0%}; 2018-22 ${x[y < 2023].mean():.0f}, 2023+ ${x[y >= 2023].mean():.0f}; years + {(x.groupby(y).sum() > 0).sum()}/{y.nunique()}")
    print("   by year: " + " | ".join(f"{a} ${v:,.0f}" for a, v in x.groupby(y).sum().items()))
    days = pd.bdate_range(x.index.min().normalize(), x.index.max().normalize()); dl = x.groupby(x.index.normalize()).sum().reindex(days, fill_value=0)
    L, S = x[m.set_index("entry_time").side > 0], x[m.set_index("entry_time").side < 0]
    gd = lambda z: z.groupby(z.index.normalize()).sum().reindex(days, fill_value=0)
    print(M.table({"ES MOC Follow (MC), per ES": (dl, x), "  longs": (gd(L), L), "  shorts": (gd(S), S)}))
    print(MC.report(x.to_numpy(), dl.to_numpy(), size=0.2, label="at 2 MES"))
