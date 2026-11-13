"""Live vs backtest replay, 2026-10-20 -> 2026-11-04 (user, 2026-11-04, after #2 and #4 failed): would the backtest have taken
the same trades at the same prices? Data: data/NQ_1min_*.csv extended with the VPS daily bar feed (data/live_bars/, identical
where they overlap); backtest = the Python ports (candidates24.vault_break24 + grid.execute; overnight_bias24 ADX 30 / 0.25 ATR),
the same ports used for every plan bench. Live = CLOSE rows of the VPS trade log (live/trades/*.csv), the 50K '-2' charts
(the 150 charts trade the same signals at 2.5x). Per MNQ, gross (no commissions), points x $2.
  python3 analysis/live_replay_1020_1104.py > analysis/outputs/live_replay_1020_1104_output.txt
"""
import sys, glob, pickle, os, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24, jof
from candidates24 import vault_break24, overnight_bias24
from grid import execute

PK = "scratch_data/g24_ext.pkl"
if os.path.exists(PK): g = pickle.load(open(PK, "rb"))
else:
    g = Grid24("scratch_data/ext/NQ_1min_20*.csv", "scratch_data/ext/NQ_1min_ON_*.csv"); pickle.dump(g, open(PK, "wb"), protocol=4)
A, B = pd.Timestamp("2026-10-20"), pd.Timestamp("2026-11-04")
hm = lambda j: int(j // 60 * 100 + j % 60)

s, kw = vault_break24(g); vb = execute(g, s, **kw)
onb = overnight_bias24(g, adx_min=30, stop_atr=0.25)
bt = []
for nm, t in (("VB", vb), ("ONB", onb)):
    t = t.copy(); t["date"] = pd.to_datetime(g.ts[t.day.to_numpy()])
    t = t[(t.date >= A) & (t.date <= B)]
    for r in t.itertuples():
        bt.append(dict(strat=nm, date=r.date.normalize(), side=int(r.side), t_in=hm(r.j0), t_out=hm(r.j1), entry=r.entry, exit=r.exit,
                       pts=(r.exit - r.entry) * r.side))
bt = pd.DataFrame(bt)

rows = []
for f in sorted(glob.glob("live/trades/2026*.csv")):
    for line in open(f):
        p = line.strip().split(",")
        if p[0] != "CLOSE" or not p[1].endswith("-2"): continue
        rows.append(dict(strat=p[1][:-2].replace("MON_BR", "BR"), date=pd.Timestamp(p[5]), side=1 if p[3] == "long" else -1, t_in=int(p[6]),
                         t_out=int(p[9]), entry=float(p[7]), exit=float(p[10]), qty=int(p[4])))
lv = pd.DataFrame(rows).drop_duplicates(["strat", "date", "t_in", "entry", "exit"])
lv = lv[(lv.date >= A) & (lv.date <= B)].copy(); lv["pts"] = (lv.exit - lv.entry) * lv.side

print(__doc__.split("\n")[0])
days = sorted(set(pd.DatetimeIndex(g.ts[g.trading])[(pd.DatetimeIndex(g.ts[g.trading]) >= A) & (pd.DatetimeIndex(g.ts[g.trading]) <= B)]))
print(f"\nTrading days {len(days)} ({days[0].date()} -> {days[-1].date()}); data last bar {pd.Timestamp(str(g.dates[g.last_j >= 0][-1])).date()}")
for nm in ("VB", "ONB"):
    L, T = lv[lv.strat == nm], bt[bt.strat == nm]
    print(f"\n=== {nm}: live {len(L)} trades {L.pts.sum():+.2f} pts (${L.pts.sum() * 2:+,.0f} per MNQ gross) | backtest {len(T)} trades "
          f"{T.pts.sum():+.2f} pts (${T.pts.sum() * 2:+,.0f} per MNQ)")
    print(f"   {'date':<11}{'live':<46}{'backtest':<46}match")
    for d in days:
        l, t = L[L.date == d], T[T.date == d]
        n = max(len(l), len(t))
        for i in range(n):
            a = l.iloc[i] if i < len(l) else None; b = t.iloc[i] if i < len(t) else None
            fa = f"{'L' if a.side > 0 else 'S'} {a.t_in:04d} {a.entry:.2f} -> {a.t_out:04d} {a.exit:.2f} {a.pts:+7.2f}" if a is not None else "-"
            fb = f"{'L' if b.side > 0 else 'S'} {b.t_in:04d} {b.entry:.2f} -> {b.t_out:04d} {b.exit:.2f} {b.pts:+7.2f}" if b is not None else "-"
            m = ("SAME" if abs(a.entry - b.entry) <= 1.0 and a.side == b.side and abs(a.pts - b.pts) <= 2.0 else
                 ("entry same, exit differs" if abs(a.entry - b.entry) <= 1.0 and a.side == b.side else "DIFFERENT")) if a is not None and b is not None \
                else ("LIVE ONLY" if a is not None else "BACKTEST ONLY (missed live?)")
            print(f"   {str(d.date()) if i == 0 else '':<11}{fa:<46}{fb:<46}{m}")
lt = lv[lv.strat.isin(["VB", "ONB"])].pts.sum(); btt = bt.pts.sum()
print(f"\nTotal VB + ONB per MNQ gross: live ${lt * 2:+,.0f} vs backtest ${btt * 2:+,.0f} (difference ${(lt - btt) * 2:+,.0f})")
other = lv[~lv.strat.isin(["VB", "ONB"])]
if len(other): print("Other live trades (not replayed):", other[["strat", "date", "side", "t_in", "entry", "exit", "pts"]].to_dict("records"))
