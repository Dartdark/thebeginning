"""Ingredient ablation, round 5 (user 2026-11-08): Monday Long and Swing Target v3 (ONB ML: Codex already ran a frozen ablation the same day,
agents/codex/results/ingredients_fc_onb_t_20261108.md; summarised, not rerun). Information only. Rebuilt from the MultiCharts inputs and
checked (Monday Long: research 452 trades $413; Swing Target v3: MultiCharts list mc_trades_v3.csv), then ONE part changed at a time; per NQ
after $7.25 + 1 tick per market / stop fill (targets = limits, no slip); 2018-26 and both periods, total $ and max DD.
  Monday Long (Mondays, buy the 08:30 open, stop 0.5 ATR15, out at the 15:00 close; early-close days skipped): Tuesday / Wednesday /
    Thursday / Friday instead / short instead / no stop / out 10:00 / out 12:00 / enter 10:00 / after an up Friday / after a down Friday
  Swing Target v3 (RTH open inside the prior 2 days' RTH high / low; skip if a level broke 08:31-08:45; stop orders at both levels from
    08:45 to 14:29; target 0.35 / stop 0.7 x 20-day avg RTH range; break-even at 0.30 x range (bar close); out at the 14:59 close):
    1-day levels / 5-day levels / no early-break skip / start 08:31 / no target / no stop (target kept) / no break-even / target 0.7 /
    fade the break instead / longs only / shorts only
  tools/run_stamped.sh analysis/ingredient_ablation5.py > analysis/outputs/ingredient_ablation5_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close
from ingredient_ablation3 import line
from ingredient_ablation4 import walk

PV, TICK, COMM = 20.0, 0.25, 7.25


def swing(g, look=2, skip_early=True, start=845, tgt=0.35, stp=0.7, be=0.30, fade=False, side_only=0):
    tr = [r for r in g.trading]; J0, JC = jof(831), jof(1500); rows = []
    hi = np.array([np.nanmax(g.h[r, J0:JC + 1]) if np.isfinite(g.h[r, J0:JC + 1]).any() else np.nan for r in tr])
    lo = np.array([np.nanmin(g.l[r, J0:JC + 1]) if np.isfinite(g.l[r, J0:JC + 1]).any() else np.nan for r in tr])
    for i, r in enumerate(tr):
        d = pd.Timestamp(g.ts[r])
        if i < max(look, 20) or d < pd.Timestamp("2018-01-01") or is_early_close(d): continue
        H, L = np.nanmax(hi[i - look:i]), np.nanmin(lo[i - look:i]); avg = np.nanmean((hi - lo)[i - 20:i]); o = g.o[r, J0]
        if not (np.isfinite(H) and np.isfinite(L) and np.isfinite(o) and L < o < H): continue
        if skip_early and (np.nanmax(g.h[r, J0:jof(845) + 1]) >= H or np.nanmin(g.l[r, J0:jof(845) + 1]) <= L): continue
        pos = 0
        for j in range(jof(start) + 1, jof(1429) + 1):
            if np.isnan(g.c[r, j]): continue
            up, dn = g.h[r, j] >= H, g.l[r, j] <= L
            if up and dn: up, dn = (abs(g.o[r, j] - H) <= abs(g.o[r, j] - L)), (abs(g.o[r, j] - H) > abs(g.o[r, j] - L))
            if up: s, e = 1, max(g.o[r, j], H)
            elif dn: s, e = -1, min(g.o[r, j], L)
            else: continue
            if fade: s = -s
            if side_only and s != side_only: break
            pos, j_in = s, j; break
        if pos == 0: continue
        e = e + pos * TICK; sp = e - pos * stp * avg if stp else None; tp = e + pos * tgt * avg if tgt else None; px = None; slip = 1
        for j in range(j_in + 1, jof(1459) + 1):
            if np.isnan(g.c[r, j]): continue
            if sp is not None and ((g.l[r, j] <= sp) if pos > 0 else (g.h[r, j] >= sp)): px = (min(g.o[r, j], sp) if pos > 0 else max(g.o[r, j], sp)) - pos * TICK; break
            if tp is not None and ((g.h[r, j] >= tp) if pos > 0 else (g.l[r, j] <= tp)): px = tp; slip = 0; break
            if be and (g.c[r, j] - e) * pos >= be * avg: sp = e if sp is None else (max(sp, e) if pos > 0 else min(sp, e))
        if px is None:
            cc = g.c[r, j_in:jof(1459) + 1]; px = cc[np.isfinite(cc)][-1] - pos * TICK
        rows.append((d, pos, (px - e) * pos * PV - COMM))
    return pd.DataFrame(rows, columns=["date", "side", "net"])


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); ts = pd.DatetimeIndex(g.ts); trs = set(g.trading.tolist())
    print("\n0. ONB ML (Codex, same day, per NQ, design 2018-22 / recent 2023-26; see its report): original $631 (t 4.51) / $711 (t 3.13);"
          "\n   no ML score $233 / $312 (t 3.13 / 2.51); no calendar terms $463 / $556 (t 2.20 / 1.72); no price terms $442 / $784; no vol terms $413 / $368."
          "\n   ONB ADX30 core: no ADX $182 / $316; no overnight-bias direction $156 / $173 (DD x3-4); no target ~same.")
    def mon(wd=0, side=1, stop=0.5, t0=830, t1=1500, cond=None):
        rows = []
        for r in g.trading:
            d = ts[r]
            if d < pd.Timestamp("2018-01-01") or d.dayofweek != wd or is_early_close(d) or np.isnan(atr[r]): continue
            if cond is not None and not cond(r): continue
            x = walk(g, r * 1440 + jof(t0) + 1, r * 1440 + jof(t1), side, None if stop is None else stop * atr[r], PV, TICK)
            if x is not None: rows.append((d, side, x))
        return pd.DataFrame(rows, columns=["date", "side", "net"])
    sh = lambda nm, T: print(line(T.net, T.date, nm), flush=True)
    print("\n1. Monday Long (check: research 452 trades, $413):")
    sh("as is", mon())
    for wd, nm in ((1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday")): sh(f"{nm} instead", mon(wd=wd))
    sh("short instead", mon(side=-1)); sh("no stop", mon(stop=None)); sh("out 10:00", mon(t1=1000)); sh("out 12:00", mon(t1=1200)); sh("enter 10:00", mon(t0=1000))
    fri = lambda r, up: (lambda p: p is not None and ((g.c[p, jof(1500)] > g.o[p, jof(831)]) == up))(next((q for q in range(r - 1, r - 5, -1) if q in trs), None))
    sh("after an up Friday", mon(cond=lambda r: fri(r, True))); sh("after a down Friday", mon(cond=lambda r: fri(r, False)))
    print("\n2. Swing Target v3 (check: MultiCharts list):")
    mc = pd.read_csv("checks/candidates/swing_target/mc_trades_v3.csv", parse_dates=["date"]); mc = mc[mc.date >= "2018-01-01"]
    print(line(mc.net, mc.date, "MultiCharts v3 (its own costs)"))
    T0 = swing(g); sh("as is (rebuild)", T0)
    j = T0.merge(mc[["date", "side", "net"]], on="date", suffixes=("", "_mc")); print(f"   rebuild vs MC: same days {len(j)} of {len(mc)} MC / {len(T0)} rebuild; same side {np.mean(j.side == j.side_mc):.0%}; P&L corr {np.corrcoef(j.net, j.net_mc)[0, 1]:.2f}")
    for nm, kw in (("1-day levels", dict(look=1)), ("5-day levels", dict(look=5)), ("no early-break skip", dict(skip_early=False)), ("start 08:31", dict(start=830)),
                   ("no target", dict(tgt=0)), ("no stop (target kept)", dict(stp=0)), ("no break-even", dict(be=0)), ("target 0.7", dict(tgt=0.7)),
                   ("fade the break instead", dict(fade=True)), ("longs only", dict(side_only=1)), ("shorts only", dict(side_only=-1))):
        sh(nm, swing(g, **kw))
