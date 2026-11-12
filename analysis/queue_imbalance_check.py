"""Queue imbalance (Gould & Bonart 2015, arXiv 1512.03492) at OUR time scale (user 2026-11-12, combination 2 ingredient; information only,
no strategy). NQ data/OF_1min_* (RTH 08:30-15:15 CT, to 2026-07-07): size_imb = top-of-book (bid - ask) / (bid + ask) size at each
minute's close. Does it predict the next 1 / 5 / 15 minutes' NQ move, and is the move bigger than the cost of a round trip?
  tools/run_stamped.sh analysis/queue_imbalance_check.py > analysis/outputs/queue_imbalance_check_output.txt
"""
import glob, numpy as np, pandas as pd
print(__doc__.split("\n")[0])
d = pd.concat([pd.read_csv(f, usecols=["date", "time", "close", "size_imb", "bid_sz_top", "ask_sz_top"]) for f in sorted(glob.glob("data/OF_1min_20*.csv"))])
d = d.sort_values(["date", "time"]).reset_index(drop=True); g = d.groupby("date").close
for h in (1, 5, 15): d[f"f{h}"] = g.shift(-h) - d.close
d = d[(d.time >= 935) & (d.time <= 1600)].dropna(); y = d.date // 10000
q = pd.qcut(d.size_imb, 10, labels=False, duplicates="drop")
print(f"{len(d):,} minutes, {d.date.nunique()} days; cost of a round trip per NQ: $7.25 + 2 ticks = $17.25 = 0.86 points")
for h in (1, 5, 15):
    c = np.corrcoef(d.size_imb, d[f"f{h}"])[0, 1]; c1 = np.corrcoef(d.size_imb[y <= 2022], d[f"f{h}"][y <= 2022])[0, 1]; c2 = np.corrcoef(d.size_imb[y >= 2023], d[f"f{h}"][y >= 2023])[0, 1]
    m = d.groupby(q)[f"f{h}"].mean()
    print(f"next {h:2d} min: corr {c:+.4f} (2018-22 {c1:+.4f}, 2023+ {c2:+.4f}); mean move by imbalance decile (points): " + " ".join(f"{v:+.2f}" for v in m)
          + f" | top - bottom decile {m.iloc[-1] - m.iloc[0]:+.2f} pts = ${(m.iloc[-1] - m.iloc[0]) * 20:+.0f} per NQ (long top, short bottom, before costs)")
    s = np.sign(d.size_imb); hit = np.mean(np.sign(d[f"f{h}"])[s != 0] == s[s != 0]); print(f"            sign hit rate {hit:.1%}")
