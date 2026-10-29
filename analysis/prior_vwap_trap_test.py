"""Prior VWAP Trap (user's upload 2026-10-29, checks/candidates/prior_vwap_trap/): independent Python rebuild from the
PowerLanguage + PDF rules on our NQ 1-minute data (cash bars 08:31-15:00 CT), our costs ($7.25 + 1 tick per market /
stop fill). Roll jumps taken from the code's own list. Writes the trade list for the plan benches.
  python3 analysis/prior_vwap_trap_test.py
"""
import glob, re, sys, numpy as np, pandas as pd
sys.path.insert(0, "analysis")
src = open("checks/candidates/prior_vwap_trap/Prior_VWAP_Trap.txt").read()
rolls = [(int(d), int(t), float(j)) for d, t, j in re.findall(r"RollD\[\d+\] = (\d+); RollT\[\d+\] = (\d+); RollJ\[\d+\] = (-?[\d.]+)", src)]
d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/NQ_1min_20*.csv")) if "_ON_" not in f])
d = d[(d.time >= 831) & (d.time <= 1500)].sort_values(["date", "time"])
# session -> cumulative roll jump in force at its cash open (rolls at 17:01 count for the next date)
roll_sess = {}
for dd, t, j in rolls:
    D = pd.Timestamp(str(dd + 19000000))
    s = (D + pd.offsets.BDay(1)) if t >= 1700 else D
    roll_sess[int(s.strftime("%Y%m%d"))] = roll_sess.get(int(s.strftime("%Y%m%d")), 0) + j
days = sorted(d.date.unique()); cum, c = {}, 0.0
for x in days:
    c += roll_sess.get(x, 0.0); cum[x] = c
G = {k: g for k, g in d.groupby("date")}
info = []
for x in days:
    g = G[x]; v = g.volume.clip(lower=0)
    info.append(dict(date=x, n=len(g), hi=g.high.max(), lo=g.low.min(), close=g.close.iloc[-1],
                     vwap=(g.close * v).sum() / v.sum() if v.sum() > 0 else np.nan, last=g.time.iloc[-1]))
I = pd.DataFrame(info)
I["adj"] = I.date.map(cum)
I["close_a"] = I.close - I.adj; I["vwap_a"] = I.vwap - I.adj          # on one price scale
I["rng"] = I.hi - I.lo; I["adr"] = I.rng.shift(1).rolling(10).mean()
I["pm"] = (I.close_a.shift(1) - I.close_a.shift(2)) / I.adr
I["pv"] = I.vwap_a.shift(1) + I.adj                                     # yesterday's VWAP on today's contract
I["n1"] = I.n.shift(1)
def run(I, col="pv"):
  tr = []
  for r in I.itertuples():
      if np.isnan(r.adr) or np.isnan(r.pm) or np.isnan(getattr(r, col)) or r.n < 200 or r.n1 < 200: continue
      al, ash = r.pm <= 0.5, r.pm >= -0.5
      if not (al or ash): continue
      g = G[r.date]; o, h, l, cl, t = (g[k].to_numpy() for k in ("open", "high", "low", "close", "time"))
      last = r.last; lm = last // 100 * 60 + last % 100; end_m = lm - 180
      gab, gbe = o[0] > getattr(r, col), o[0] < getattr(r, col)
      below, above = not gab, not gbe
      sig, k = 0, None
      for i in range(len(g) - 1):
          m = t[i] // 100 * 60 + t[i] % 100
          if m > end_m or t[i] >= last: break
          if cl[i] <= getattr(r, col): below = True
          if cl[i] >= getattr(r, col): above = True
          if t[i] >= 835:
              if al and ((cl[i] > getattr(r, col) and below) or (gab and not below and t[i] >= 1000)): sig = 1
              elif ash and ((cl[i] < getattr(r, col) and above) or (gbe and not above and t[i] >= 1000)): sig = -1
          if sig: k = i + 1; break
      if not sig: continue
      ent = o[k]; dist = 0.5 * r.adr; best = ent; stop = ent - sig * dist; ex = None; kind = "time"
      for i in range(k, len(g)):
          if i > k:
              if t[i] >= 1500 and last >= 1500: ex = o[i]; break
              if (sig > 0 and l[i] <= stop) or (sig < 0 and h[i] >= stop):
                  ex = min(o[i], stop) if sig > 0 else max(o[i], stop); kind = "stop"; break
          best = max(best, h[i]) if sig > 0 else min(best, l[i])
          stop = max(stop, best - dist) if sig > 0 else min(stop, best + dist)
      if ex is None: ex = cl[-1]
      pts = (ex - ent) * sig - 0.5                                        # 1 tick entry + 1 tick exit
      tr.append(dict(date=r.date, side=sig, entry=ent, exit=ex, kind=kind, pnl=pts * 20 - 7.25))
  return pd.DataFrame(tr)


T = run(I)
T["yr"] = T.date // 10000
T.to_csv("checks/candidates/prior_vwap_trap/trades_python.csv", index=False)
import metrics as M
def line(x, name):
    tt = x.pnl.mean() / x.pnl.std() * np.sqrt(len(x))
    print(f"{name:<14} n {len(x):5d}  avg ${x.pnl.mean():6.0f}  PF {x.pnl[x.pnl>0].sum()/-x.pnl[x.pnl<0].sum():.2f}  t {tt:4.1f}  net ${x.pnl.sum()/1000:6.1f}k")
line(T, "all"); line(T[T.side > 0], "longs"); line(T[T.side < 0], "shorts")
line(T[T.yr <= 2022], "2018-22"); line(T[T.yr >= 2023], "2023+")
print("by year $k:", {int(y): round(g.pnl.sum() / 1000, 1) for y, g in T.groupby("yr")})
print("stop exits", round((T.kind == "stop").mean(), 2), "trades/yr", round(len(T) / (len(T.yr.unique()) - 0.2), 0))

# placebo levels: is it yesterday's VWAP, or any level near the open with a trailing stop?
I["pc"] = I.close_a.shift(1) + I.adj                                    # yesterday's close
I["pmid"] = (I.hi.shift(1) + I.lo.shift(1)) / 2 - I.adj.shift(1) + I.adj  # yesterday's cash midpoint
rng = np.random.default_rng(7)
for col in ("pc", "pmid"):
    x = run(I, col); x["yr"] = x.date // 10000; line(x, "level " + col)
for k in range(5):
    I["prnd"] = I.pv + rng.uniform(-0.3, 0.3, len(I)) * I.adr
    x = run(I, "prnd"); line(x, f"pv +-0.3ADR #{k}")
