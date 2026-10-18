"""Rough independent Python Vault Break (from apex_strategies/NQ_Vault_Break.txt), to test whether the NR7 effect
survives on a trade list that is not the maker's MultiCharts export. Midnight open, midnight VWAP (30-min bars),
noise = open + 0.30 x 15-day ATR (grid24.daily_atr), decisions on 30-min closes 10:00..<14:30 (early close: <11:00,
flat 11:30), next-bar-open market entry, 40 pt target / 75 pt stop checked on 1-min bars (stop first if both in a minute),
flat at the 14:30 close. Costs: $7.25 round turn + 1 tick ($5) per market/stop fill."""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/thebeginning/analysis"); import grid24
sys.path.insert(0, "/home/user/thebeginning/checks/candidates/vb_nr7_sizing")
from replica import sessions, flags, CDIR
G = pickle.load(open("/home/user/thebeginning/scratch_data/g24.pkl", "rb"))
B = G.bars(30); vw = G.vwap_rows(B, start_j=30); atr = G.daily_atr(15)
S = sessions(); F = flags(S); early = set(S.index[S["last"] < 1400])
TICK = 0.25; rows = []
for r in G.trading:
    d = pd.Timestamp(str(G.dates[r]))
    if d < pd.Timestamp("2018-01-01") or np.isnan(atr[r]): continue
    o1 = G.o[r][~np.isnan(G.o[r])]
    if not len(o1): continue
    noise = o1[0] + 0.30 * atr[r]
    last_e, flat = (1100, 1130) if d in early else (1430, 1430)
    pos = None; ntr = 0; i = 20                       # bar index i closes at i*30 min; 20 -> 10:00
    while i < 48:
        t = (i * 30 // 60) * 100 + (i * 30) % 60
        if t > flat: break
        if pos is None:
            if t < last_e and ntr < 3 and B["c"][r, i] > noise and B["c"][r, i] > vw[r, i] and i + 1 < 48:
                j0 = i * 30                            # first minute of the next bar = column j0 + 1
                op = G.o[r, j0 + 1]
                if np.isnan(op): i += 1; continue
                ep = op + TICK; pos = (ep, j0 + 1, t); ntr += 1
            i += 1; continue
        # in position: walk minutes of bar i (columns (i-1)*30+1 .. i*30)
        ep, jent, tdec = pos; done = False
        for j in range(max(jent, (i - 1) * 30 + 1), i * 30 + 1):
            if np.isnan(G.c[r, j]): continue
            lo, hi = G.l[r, j], G.h[r, j]
            if lo <= ep - 75:
                px = min(G.o[r, j], ep - 75) - TICK; ex = "stop"; done = True
            elif hi >= ep + 40:
                px = ep + 40; ex = "target"; done = True
            if done: break
        if not done and t >= flat:
            px = B["c"][r, i] - TICK; ex = "time"; done = True
        if done:
            rows.append(dict(date=d, side=1, exit=ex, gross=(px - ep) * 20))
            pos = None; continue                       # flat at this bar's close: it can trigger a new entry
        i += 1
R = pd.DataFrame(rows)
R["net"] = R.gross - 7.25                              # slippage already inside px (entry +1 tick, stop/time -1 tick)
R["kept"] = R.date.map(F).fillna(False).astype(int)
R[["date", "side", "net", "kept"]].to_csv(CDIR + "_replica/trades_vb_python.csv", index=False)
M = pd.read_csv(CDIR + "/trades.csv", parse_dates=["date"])
md, rd = set(M.date), set(R.date)
print(f"python VB trades {len(R)} on {len(rd)} days (MC {len(M)} on {len(md)}); day overlap {len(md & rd)} "
      f"({len(md & rd) / len(md | rd):.2%} of union); avg ${R.net.mean():.1f} vs MC ${M.net.mean():.1f}")
dm = M.groupby("date").net.sum(); dr = R.groupby("date").net.sum(); j = dm.to_frame("mc").join(dr.rename("py"), how="inner")
print("daily P&L correlation on common days: %.3f" % j.corr().iloc[0, 1])
def welch(a, b): return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
k = R.kept == 1
print(f"NR7 on python VB: flagged ${R.net[k].mean():.1f} (n {k.sum()}) vs ${R.net[~k].mean():.1f} (n {(~k).sum()}), t {welch(R.net[k], R.net[~k]):.2f}")
for lab, m in (("2018-22", R.date.dt.year <= 2022), ("2023-26", R.date.dt.year >= 2023)):
    print(f"  {lab}: ${R.net[m & k].mean():.1f} vs ${R.net[m & ~k].mean():.1f}, t {welch(R.net[m & k], R.net[m & ~k]):.2f}")
