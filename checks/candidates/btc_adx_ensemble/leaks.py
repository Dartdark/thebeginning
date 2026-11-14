import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replica as RP
D = RP.get_data(); T = RP.run(D); m15 = D["m15"]; m1 = D["m1"]
T[["t", "tx", "side", "entry", "exit"]].rename(columns={"t": "entry_time", "tx": "exit_time"}).to_csv("fills_replica.csv", index=False)
# L1: entry / exit price inside the 15m candle (UTC open-time clock)
ok = []
for r in T.itertuples():
    for tm, px in ((r.t, r.entry), (r.tx, r.exit)):
        b = m15.loc[tm]; ok.append(b.low - 1e-9 <= px <= b.high + 1e-9)
print(f"L1 fills inside their 15m candle: {np.mean(ok):.2%} of {len(ok)}")
# entry close == the 1h candle close (the decision bar)
h1 = D["h1"]; e = T.t - pd.Timedelta(minutes=45)
print("entry price == close of the 1h decision candle:", np.mean(np.isclose(T.entry.to_numpy(), h1.close.reindex(e).to_numpy())))
# guard gaps: 15m candle opened beyond the guard -> 'filled at its price' is optimistic
g = T[T.why == "guard"]; gap = []
for r in g.itertuples():
    b = m15.loc[r.tx]; gap.append((b.open - r.exit) * r.side < 0)
print(f"guard exits {len(g)}; candle OPENED beyond the guard (fill at guard price impossible): {int(np.sum(gap))}")
# stop exits: how far the 15m close is beyond / back inside the stop
s = T[T.why == "stop"].copy(); s["stop"] = s.entry * (1 - s.side * s.R)
s["slip_R"] = (s.exit - s.stop) * s.side / (s.entry * s.R)
print(f"stop exits {len(s)}: close vs stop, in R: mean {s.slip_R.mean():+.3f}, median {s.slip_R.median():+.3f}, share closed back inside {np.mean(s.slip_R > 0):.0%}")
# weekend entry dates (checker daily() keeps business days only)
for f in ("trades.csv",):
    M = pd.read_csv(f, parse_dates=["date"]); w = M.date.dt.dayofweek >= 5
    print(f"{f}: {w.sum()} of {len(M)} rows dated Sat/Sun ({w.mean():.0%}), their R {M.net[w].sum():.1f} of {M.net.sum():.1f}")
# minute-level: within the stop candle, did the target/half get touched first? (order ambiguity inside a 15m candle)
both = 0
for r in T.itertuples():
    b = m15.loc[r.tx]; tp = r.entry * (1 + r.side * r.R * 8 / 2.5); st = r.entry * (1 - r.side * r.R)
    if r.side == 1 and b.low <= st and b.high >= tp: both += 1
    if r.side == -1 and b.high >= st and b.low <= tp: both += 1
print("exit candles touching both stop and target:", both)
# data gaps
idx = m15.index; gaps = (idx[1:] - idx[:-1]) > pd.Timedelta(minutes=15)
print("15m candles missing (gaps):", int(((idx[1:] - idx[:-1])[gaps] / pd.Timedelta(minutes=15) - 1).sum()), "of", len(idx))
