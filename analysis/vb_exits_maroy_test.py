"""Exits from Maroy 2025 ("Improvements to Intraday Momentum Strategies", SSRN 5095349) on Vault Break v1, walk-forward.

Paper: QQQ noise-band momentum (Zarattini, Aziz & Barbon) with ~11 parameters tuned by Optuna on the same 2014-24 data it
reports (Sharpe 2.1-3.4, no out-of-sample period). Its new parts are exits: (a) VWAP touch, (b) an exit band narrower than the
entry band, (c) a 2-step ladder: stop -1r / target a*r (sell half), then stop at k*r / target b*r on the rest.
Here: Vault Break v1's own entries (vault_break_v8_test.run(g, 'v1'), validated against MultiCharts), an entry is skipped if the
earlier trade is still open under the new exit; exits simulated on 1-minute bars, flat at the 14:30 close as v1.
Each family is tuned on 2018-22 (best total net), judged on 2023-26. 1 NQ, $7.25 + 1 tick per market / stop fill.
  python3 analysis/vb_exits_maroy_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from vault_break_v8_test import run, boundary, line, PV, TICK, COST
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def vwap_min(g, d):
    tp = (g.h[d] + g.l[d] + g.c[d]) / 3; v = np.nan_to_num(g.v[d]); tp = np.nan_to_num(tp)
    cv = np.cumsum(v); return np.where(cv > 0, np.cumsum(tp * v) / np.maximum(cv, 1e-9), np.nan)


def sim(g, ent, B, rule):
    """rule: dict(kind='base'|'vwap'|'band'|'ladder', ...). Returns trades with net."""
    out = []; busy = {}
    flat = jof(1430)
    for r in ent.itertuples():
        d, m0, e = r.day, r.j0, r.entry
        if busy.get(d, -1) >= m0: continue
        ef = e - TICK; Bd = B[d]
        okm = np.flatnonzero(~np.isnan(g.o[d]))
        so = g.o[d, okm[0]]
        vw = vwap_min(g, d) if rule["kind"] == "vwap" else None
        k = rule["kind"]
        if k == "ladder":
            R_ = rule["r"] * Bd; stop = ef - R_; tgt = ef + rule["a"] * R_; step = 0; qty = 1.0; pnl = 0.0; slips = 0
        else:
            sl_ = rule.get("sl", 75.0); tp_ = rule.get("tp", 1e9)
            sl_ = sl_[d] if hasattr(sl_, "__len__") else sl_; tp_ = tp_[d] if hasattr(tp_, "__len__") else tp_   # per-day arrays allowed
            stop = ef - sl_; tgt = ef + tp_
            if k == "band": stop = max(stop, so + rule["kx"] * Bd)
        j_end = flat; done = False
        for m in range(m0, flat + 1):
            if np.isnan(g.h[d, m]): continue
            first = m == m0
            lo, hi, op = g.l[d, m], g.h[d, m], g.o[d, m]
            if k == "vwap" and not first and lo <= max(stop, vw[m - 1] if not np.isnan(vw[m - 1]) else -1e9):
                lvl = max(stop, vw[m - 1]); px = min(op, lvl) - TICK
                out.append((d, m0, m, (px - e) * PV - COST)); j_end = m; done = True; break
            if k == "ladder":
                if lo <= stop:
                    px = (min(op, stop) if not first else stop) - TICK
                    pnl += qty * (px - e) * PV; out.append((d, m0, m, pnl - COST - (0 if step == 0 else 0))); j_end = m; done = True; break
                if hi >= tgt:
                    px = max(op, tgt) if not first else tgt
                    if step == 0:
                        pnl += 0.5 * (px - e) * PV; qty = 0.5; step = 1
                        stop = ef + rule["k"] * R_; tgt = ef + rule["b"] * R_
                        continue
                    pnl += qty * (px - e) * PV; out.append((d, m0, m, pnl - COST)); j_end = m; done = True; break
                continue
            if lo <= stop:
                px = (min(op, stop) if not first else stop) - TICK
                out.append((d, m0, m, (px - e) * PV - COST)); j_end = m; done = True; break
            if hi >= tgt:
                px = max(op, tgt) if not first else tgt
                out.append((d, m0, m, (px - e) * PV - COST)); j_end = m; done = True; break
        if not done:
            cf = g.c[d, :flat + 1]; mm = np.flatnonzero(~np.isnan(cf)); m = mm[-1]; px = cf[m] - TICK
            pn = (px - e) * PV
            if k == "ladder": pn = pnl + qty * (px - e) * PV
            out.append((d, m0, m, pn - COST)); j_end = m
        busy[d] = j_end
    t = pd.DataFrame(out, columns=["day", "j0", "j1", "net"]); t["date"] = pd.DatetimeIndex(g.ts[t.day.values]); return t


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    ent = run(g, "v1"); B = boundary(g, "tr")
    print(line(ent, "Vault Break v1 (engine, tp 40 / sl 75)"))
    base = sim(g, ent, B, dict(kind="base", sl=75.0, tp=40.0)); print(line(base, "re-simulated v1 (check)"))
    fams = {
        "vwap touch (+ sl, tp)": [dict(kind="vwap", sl=sl, tp=tp) for sl in (50, 75, 100) for tp in (40, 60, 1e9)],
        "exit band (+ tp)": [dict(kind="band", kx=kx, sl=1e9, tp=tp) for kx in (-0.2, -0.1, 0.0, 0.1, 0.2) for tp in (40, 60, 1e9)],
        "ladder 2-step": [dict(kind="ladder", r=r, a=a, k=k, b=b) for r in (0.15, 0.25, 0.35) for a in (0.5, 1, 2)
                          for k in (-0.5, 0.0) for b in (2, 3, 5)],
    }
    yr = lambda t: t.date.dt.year
    for nm, grid in fams.items():
        res = []
        for rule in grid:
            t = sim(g, ent, B, rule); a = t[yr(t) < 2023].net; b_ = t[yr(t) >= 2023].net
            res.append((a.sum(), b_.sum(), rule, t))
        res.sort(key=lambda x: -x[0])
        ranks = pd.Series([x[1] for x in res]); ins = pd.Series([x[0] for x in res])
        print(f"\n{nm}: {len(grid)} settings; in-sample rank vs 2023-26 total, Spearman {ins.rank().corr(ranks.rank()):+.2f}")
        for a_, b_, rule, t in res[:3]:
            print(line(t, f"  {', '.join(f'{k}={v:g}' for k, v in rule.items() if k != 'kind')}", 50))
        print(f"   best-in-sample 2023-26 total ${res[0][1]:,.0f} vs v1 ${base[yr(base) >= 2023].net.sum():,.0f}; median of all settings ${np.median([x[1] for x in res]):,.0f}")
