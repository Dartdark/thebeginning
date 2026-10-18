"""Checker robustness checks on the NR7 flag (uses replica.py session ranges)."""
import numpy as np, pandas as pd
from replica import sessions, CDIR
g = sessions(); T = pd.read_csv(CDIR + "/trades.csv", parse_dates=["date"])
def welch(a, b): return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
# 1) day-clustered t (trades on one day share the flag)
D = T.groupby("date").agg(net=("net", "sum"), f=("flagged", "max"), n=("net", "size"))
print("per-day sum: flagged $%.0f (n %d) vs other $%.0f (n %d), t %.2f" % (D.net[D.f == 1].mean(), (D.f == 1).sum(), D.net[D.f == 0].mean(), (D.f == 0).sum(), welch(D.net[D.f == 1], D.net[D.f == 0])))
print("trades/day: flagged %.2f vs other %.2f" % (D.n[D.f == 1].mean(), D.n[D.f == 0].mean()))
# 2) NR7 caused by a short (early-close) session
g["short"] = g["last"] < 1500
prevshort = g.short.shift(1).fillna(False)
T["after_short"] = T.date.map(prevshort).fillna(False)
print("flagged trades after an early-close session:", int((T.flagged & T.after_short).sum()),
      "mean $%.1f" % T.net[(T.flagged == 1) & T.after_short].mean())
m = ~T.after_short
print("excluding them: flagged $%.1f (n %d) vs other $%.1f, t %.2f" % (T.net[m & (T.flagged == 1)].mean(), (m & (T.flagged == 1)).sum(), T.net[m & (T.flagged == 0)].mean(), welch(T.net[m & (T.flagged == 1)], T.net[m & (T.flagged == 0)])))
# 3) concentration: drop best flagged days
fd = D[D.f == 1].net.sort_values(ascending=False)
for k in (5, 10, 20):
    keep = ~T.date.isin(fd.index[:k])
    a, b = T.net[keep & (T.flagged == 1)], T.net[keep & (T.flagged == 0)]
    print(f"drop best {k} flagged days: flagged ${a.mean():.1f} vs ${b.mean():.1f}, t {welch(a, b):.2f}")
# 4) neighbours: NRn for n = 4..10 and range ranks
for n in range(4, 11):
    f = (g.rng <= g.rng.shift(1).rolling(n - 1).min()).shift(1).fillna(False)
    k = T.date.map(f).fillna(False).astype(bool)
    print(f"NR{n}: n {k.sum()}, ${T.net[k].mean():.1f} vs ${T.net[~k].mean():.1f}, t {welch(T.net[k], T.net[~k]):.2f}")
# 5) continuous: previous range / 20-session median range, quintiles
r = (g.rng / g.rng.shift(1).rolling(20).median()).shift(1)
T["q"] = pd.qcut(T.date.map(r), 5, labels=False)
print("prev-range/median quintile means:", T.groupby("q").net.mean().round(0).to_dict())
# 6) exits mix
T["res"] = np.where(T.net > 700, "target", np.where(T.net < -1400, "stop", "time"))
print(pd.crosstab(T.flagged, T.res, normalize="index").round(3))
# 7) entry-time sanity
et = pd.to_datetime(T.entry_time); hm = et.dt.hour * 100 + et.dt.minute
print("entry times:", sorted(hm.unique())[:3], "...", sorted(hm.unique())[-3:], "| not on :00/:30:", int((et.dt.minute % 30 != 0).sum()))
# 8) flagged-only sizing effect: P&L of 1/3 sizing vs 1 contract
w = np.where(T.flagged == 1, 3, 1)
print("total 1x: $%.0f, 1/3x: $%.0f; extra from flagged 2x: $%.0f" % (T.net.sum(), (T.net * w).sum(), 2 * T.net[T.flagged == 1].sum()))
