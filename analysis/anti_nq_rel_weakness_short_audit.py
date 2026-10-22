"""Audit of Antigravity's NQRelWeaknessShort trade list (detailed_trades_audit.csv, antigravity/jesse 2026-10-20) against our
1-minute NQ data: where in its entry minute's range each short was filled, and the same trades re-filled at the next
minute's open (a real market fill) with its own stop / target distances and breakeven rule. Put the CSV at
SCRATCH/anti/rws_audit.csv (git show origin/antigravity/jesse:strategies/NQRelWeaknessShort/detailed_trades_audit.csv).
  python3 analysis/anti_nq_rel_weakness_short_audit.py [SCRATCH_DIR]
"""
import sys, pickle; sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
g = pickle.load(open(SP + "g24.pkl", "rb")); a = pd.read_csv(SP + "anti/rws_audit.csv"); pos = {int(d): k for k, d in enumerate(g.dates)}
loc, gap, out = [], [], []
for r in a.itertuples():
    d = pos[int(r.date)]; j0 = jof(r.entry_time); hi, lo = g.h[d, j0], g.l[d, j0]
    loc.append((r.entry_price - lo) / (hi - lo) if hi > lo else np.nan); gap.append(r.entry_price - g.c[d, j0])
    e = g.o[d, j0 + 1]; st, tg, on, x = e + r.stop_pts, e - r.target_pts, False, None
    for j in range(j0 + 1, jof(1515) + 1):
        if g.h[d, j] >= st: x = st; break
        if g.l[d, j] <= tg: x = tg; break
        if (j + 1) % 15 == 0 and not on and e - g.c[d, j] >= r.atr15m_at_entry: st, on = e - 1, True
    if x is None: x = g.c[d, jof(1515)]
    out.append(((e - x) * 20 - 17.25, r.net_full_nq, int(str(r.date)[:4])))
o = pd.DataFrame(out, columns=["real", "its", "yr"]); ts = lambda v: v.mean() / v.std() * np.sqrt(len(v))
print(f"entry location in its minute (0 = low, 1 = high): mean {np.nanmean(loc):.2f}, at the top 10%: {np.nanmean(np.array(loc) >= 0.9):.0%}")
print(f"its entry price minus that minute's close: median {np.median(gap):.2f} pts")
print(f"its fills: ${o.its.mean():.0f} per NQ, t {ts(o.its):.2f} | next-minute open, same exits: ${o.real.mean():.0f}, t {ts(o.real):.2f}, win {(o.real > 0).mean():.0%}")
print("by year (real fills):", o.groupby("yr").real.sum().round(0).to_dict())
