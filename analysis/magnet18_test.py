"""MAGNET18 (user's upload 2026-10-24: Magnet18_proto.txt + research note, same author as T_ONESIDE; checks/candidates/magnet18/).
Rebuild of the frozen file (nLots 1, UseVolSize false, UseEarlyCls false) on the 24-hour grid, 2018-2026, 1-min bars, CT:
  gate at the 10:30 bar close: close > session VWAP + 2 pt OR close > the 08:30 bar's open (08:29:00) + 2 pt
  (VWAP from the 08:30 bar, typical price x volume) -> long at the 10:31 bar's open (10:30:00); out at the 14:30 bar's open
  (14:29:00). No stop. On CME early-close days (no 14:30 bar) the file holds through the 12:00 halt and sells at the
  first bar after the reopen: done the same here, and separately counted.
Costs $7.25 + 1 tick per fill per NQ ($17.25 a round trip). The note's research cost 0.5 pt ($10) shown for parity.
Controls: every day long (no gate); the complement days (gate false); each magnet alone; both (AND).
The author's open questions: (1) VWAP reclaim (the morning traded at / below VWAP or the open, then holds at 10:30) vs
never-left (it never did); (2) the same gate on ES (+0.5 pt = 2 ticks, the NQ 2 pt scaled by price).
  python3 analysis/magnet18_test.py SCRATCH_DIR
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import line
import metrics as M, resampling as R, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def build(g, pv, tick, comm, clear):
    O = g.o.ravel(); ok = np.flatnonzero(np.isfinite(O)); rows = []
    for r in g.trading:
        jj = np.arange(jof(830), jof(1030) + 1)
        h, l, c, v = g.h[r, jj], g.l[r, jj], g.c[r, jj], np.nan_to_num(g.v[r, jj])
        px = g.o[r, jof(830)]; c10 = c[-1]
        if not (np.isfinite(px) and np.isfinite(c10) and np.isfinite(g.o[r, jof(1031)])): continue
        tp = np.nan_to_num((h + l + c) / 3); cv = np.cumsum(v); vw = np.where(cv > 0, np.cumsum(tp * v) / np.maximum(cv, 1e-9), np.nan)
        e = g.o[r, jof(1031)]
        if np.isfinite(g.o[r, jof(1430)]): x = g.o[r, jof(1430)]; early = False
        else:
            k = ok[np.searchsorted(ok, r * 1440 + jof(1430))]; x = O[k]; early = True     # first bar after the halt
        touched = bool(np.any(np.nan_to_num(l[15:-1], nan=np.inf) <= np.minimum(vw[15:-1], px)))   # 08:45-10:29 at / below VWAP or the open
        gross = (x - e) * pv
        rows.append(dict(r=r, e=e, x=x, date=pd.Timestamp(g.ts[r]), up_vw=c10 > vw[-1] + clear, up_open=c10 > px + clear, touched=touched, early=early,
                         gross=gross, net=gross - 2 * tick * pv - comm, net_note=gross - (10.0 if pv == 20 else 0.5 * pv)))
    T = pd.DataFrame(rows); T["gate"] = T.up_vw | T.up_open
    return T[T.date >= "2018-01-01"].reset_index(drop=True)


def stats(x, nm, dd):
    p = M.perf(x.groupby(x.index).sum().reindex(dd, fill_value=0.0), x.values)
    return (f"   {nm:<30} Sharpe {p['sharpe']:5.2f} Sortino {p['sortino']:5.2f} PF {p['profit_factor']:4.2f} "
            f"Calmar {p['calmar']:5.2f} Ulcer {p['ulcer']:5.2f} maxDD ${p['max_dd']:,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); T = build(g, 20.0, 0.25, 7.25, 2.0)
    s = lambda m, col="net", t=T: t[col][m].set_axis(pd.DatetimeIndex(t.date[m]))
    dd = pd.DatetimeIndex(T.date); G = T.gate
    w = T[(T.date <= "2026-08-17")]; x = w.net_note[w.gate]
    print(f"days {len(T)}, gated {G.sum()} ({G.mean():.0%}; {G.sum() / (len(T) / 252) / 52:.1f} a week), early-close holds {(G & T.early).sum()}")
    print(f"parity (note's 0.5 pt cost): ${x.mean():.0f} a trade, win {np.mean(x > 0):.1%}, PF {x[x > 0].sum() / -x[x < 0].sum():.2f} "
          f"| note MultiCharts 2016-26 2,288 trades 58.3% $165 PF 1.30 (UseVolSize true, $5 slip), research IS +7.07 pt 60.8%")
    print("\nper NQ at our costs, 2018-2026, long 10:30 -> 14:29 CT:")
    for nm, m in (("MAGNET18 (union gate)", G), ("   without early-close days", G & ~T.early), ("every day long (no gate)", T.net.notna()),
                  ("complement (gate false)", ~G), ("VWAP + 2 only", T.up_vw), ("open + 2 only", T.up_open), ("both (AND)", T.up_vw & T.up_open),
                  ("open only, not VWAP", T.up_open & ~T.up_vw), ("VWAP only, not open", T.up_vw & ~T.up_open),
                  ("(1) reclaim: gate, AM touched", G & T.touched), ("(1) never-left: gate, untouched", G & ~T.touched),
                  ("after their split 2023-09-08", G & (T.date >= "2023-09-08"))):
        print(line(s(m), nm, 40))
    print(f"   early-close holds through the halt: {(G & T.early).sum()} trades, ${s(G & T.early).mean():.0f} avg")
    d_ = s(G).mean() - s(~G).mean(); se = np.sqrt(s(G).var() / G.sum() + s(~G).var() / (~G).sum())
    print(f"   gate minus complement ${d_:.0f} (t {d_ / se:.2f}); gate minus every day ${s(G).mean() - T.net.mean():.0f}")
    print("\nby year (sum per NQ): gate / every day")
    print(pd.DataFrame({"gate": s(G).groupby(lambda d: d.year).sum(), "every day": s(T.net.notna()).groupby(lambda d: d.year).sum()}).round(0).to_string())
    print("\nmetrics (daily, per NQ; long only):")
    for nm, m in (("MAGNET18", G), ("every day long", T.net.notna()), ("MAGNET18 2023+", G & (T.date >= "2023-01-01"))):
        print(stats(s(m), nm, dd if "2023" not in nm else dd[dd >= "2023-01-01"]))
    x = s(G & (T.date >= "2023-01-01")); d23 = dd[dd >= "2023-01-01"]
    print("\nresampling MAGNET18 2023+:"); print("\n".join(R.report({"MAGNET18": x.groupby(x.index).sum().reindex(d23, fill_value=0.0)})))
    y = s(G); dy = y.groupby(y.index).sum().reindex(dd, fill_value=0.0)
    print(MC.report(y.values, dy, size=0.1, label="MAGNET18 1 MNQ")); print(f"      t {y.mean() / y.std() * np.sqrt(len(y)):.2f}, DSR at 292 items {M.deflated_sharpe(dy, 292):.2f}")

    print("\n(2) ES, same gate (+0.5 pt), per ES $5 + 1 tick per fill:")
    ge = pickle.load(open(SP + "ge.pkl", "rb")); E = build(ge, 50.0, 0.25, 5.0, 0.5)
    se_ = lambda m: E.net[m].set_axis(pd.DatetimeIndex(E.date[m]))
    for nm, m in (("ES gate", E.gate), ("ES every day long", E.net.notna()), ("ES complement", ~E.gate),
                  ("ES reclaim", E.gate & E.touched), ("ES never-left", E.gate & ~E.touched)):
        print(line(se_(m), nm, 40))
    T.to_csv(SP + "magnet18_days.csv", index=False)
