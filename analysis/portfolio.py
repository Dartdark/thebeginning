"""Apex 50K challenges for one strategy or a book of several, on real days,
with the strategies' trades overlapping minute by minute.

Each strategy's trades become per-day equity paths on the 1-minute grid
(analysis/grid.py): `worst` marks open trades at each minute's adverse
extreme, `real` is closed P&L. A book is the sum of its strategies' paths,
each scaled by its size in MNQ, so trades that are open at the same time
draw down together, as they would in one account. Costs: $7.25 per NQ round
trip ($0.725 per MNQ).

Apex 50K EOD rules as in prop_sim.py: $3,000 target on closed P&L, $2,000
drawdown trailing the end-of-day balance and locking at start + $100, open
equity breaching the floor fails the challenge, $1,000 daily loss limit
liquidates and ends the day, 21 trading days. A breach and the target in the
same minute count as a breach.

Two ways to run challenges:
  real_days(): start on every chosen day and walk the real days that follow
               (the realistic one; see start_timing.py)
  random_days(): days drawn at random with replacement (the notebook's method)
"""
import numpy as np
import pandas as pd
from grid import Grid, j_of, NMIN, POINT_VALUE, COST

RULES = dict(start=50_000.0, target=3_000.0, mll=2_000.0, dll=1_000.0,
             lock_above_start=100.0, max_days=21)


def load_mc(g, path):
    """A MultiCharts 'List of Trades' export as grid trades (any strategy on a
    5-minute chart with Bar Magnifier). Entry fills at the open of the
    5-minute bar it is stamped with; the exit minute is the first 1-minute bar
    inside the exit stamp's 5-minute bar that trades the exit price (the
    stamp's close for market/EOD exits)."""
    raw = pd.read_excel(path, sheet_name="List of Trades", header=2)
    ent = raw[raw["Type"].astype(str).str.startswith("Entry")].reset_index(drop=True)
    ex = raw[raw["Type"].astype(str).str.startswith("Exit")].reset_index(drop=True)
    et, xt = pd.to_datetime(ent["Date"]), pd.to_datetime(ex["Date"])
    dates = et.dt.strftime("%Y%m%d").astype(int).to_numpy()
    day = np.searchsorted(g.dates, dates)
    keep = (day < g.D) & (g.dates[np.minimum(day, g.D - 1)] == dates)
    j0 = j_of((et.dt.hour * 100 + et.dt.minute).to_numpy()) - 4
    xs = j_of((xt.dt.hour * 100 + xt.dt.minute).to_numpy())
    side = np.where(ent["Type"].astype(str).str.contains("Long"), 1, -1)
    px = ex["Price"].to_numpy(float)
    contracts = ent["Contracts"].to_numpy(float)
    j1 = xs.copy()
    sig = ex["Signal"].astype(str).to_numpy()
    for i in np.nonzero(keep)[0]:
        if "EOD" in sig[i] or "Time" in sig[i]:
            continue
        for j in range(max(xs[i] - 4, j0[i]), xs[i] + 1):
            if g.l[day[i], j] <= px[i] <= g.h[day[i], j]:
                j1[i] = j
                break
    t = pd.DataFrame(dict(day=day, j0=j0, j1=j1, side=side, entry=ent["Price"].to_numpy(float),
                          exit=px, kind=np.where([("Stop" in s) for s in sig], 0, 1),
                          pnl=ent["Profit ($)"].to_numpy(float) / contracts))[keep]
    t["kind"] = np.where([("EOD" in s) or ("Time" in s) for s in sig[keep]], 2, t["kind"])
    t["date"] = g.ts[t["day"].to_numpy()]
    t["net"] = t["pnl"] - COST
    return t.reset_index(drop=True)


def paths(g, t):
    """Per-day equity paths of a trade list, $ per 1 NQ after costs (times the
    trade's qty column, if any), relative to the day's start. Returns (worst, real), each (days, NMIN)."""
    worst = np.zeros((g.D, NMIN)); real = np.zeros((g.D, NMIN))
    qty = t["qty"] if "qty" in t else np.ones(len(t))
    for day, j0, j1, side, entry, px, kind, q in zip(t["day"], t["j0"], t["j1"], t["side"],
                                                     t["entry"], t["exit"], t["kind"], qty):
        net = ((px - entry) * side * POINT_VALUE - COST) * q
        seg = slice(j0, j1 + 1)
        adverse = g.l[day, seg] if side > 0 else g.h[day, seg]
        adv = ((np.nan_to_num(adverse, nan=entry) - entry) * side * POINT_VALUE - COST) * q
        adv[-1] = net if kind == 0 else min(adv[-1], net)
        worst[day, seg] += adv
        worst[day, j1 + 1:] += net
        real[day, j1:] += net
    return worst, real


class Book:
    """Strategies with their paths; combine() scales and sums them."""
    def __init__(self, g):
        self.g = g
        self.p = {}

    def add(self, name, trades):
        self.p[name] = paths(self.g, trades)
        return self

    def combine(self, mnq):
        """mnq: {name: size in MNQ}. Returns (worst, real) in $."""
        w = np.zeros((self.g.D, NMIN)); r = np.zeros((self.g.D, NMIN))
        for name, s in mnq.items():
            if s:
                w += self.p[name][0] * s / 10.0
                r += self.p[name][1] * s / 10.0
        return w, r


def _day(w, r, bal, floor, rules):
    """One day. Returns (status, new_balance): status 'pass', 'fail' or None."""
    start = rules["start"]
    dll_lvl = bal - rules["dll"] if rules["dll"] else -np.inf
    lim = max(floor, dll_lvl)
    hit = np.nonzero(bal + w <= lim)[0]
    win = np.nonzero(bal + r - start >= rules["target"])[0]
    jb = hit[0] if len(hit) else NMIN
    jp = win[0] if len(win) else NMIN
    if jp < jb:
        return "pass", bal + r[jp]
    if jb < NMIN:
        if floor >= dll_lvl:
            return "fail", floor
        return None, dll_lvl
    return None, bal + r[-1]


def challenge(w, r, day_index, rules=RULES):
    """One challenge over the given sequence of day indices. Returns
    (outcome, trading days used) or None if the days run out first."""
    bal = rules["start"]; floor = bal - rules["mll"]
    for n, d in enumerate(day_index[:rules["max_days"]], 1):
        st, bal = _day(w[d], r[d], bal, floor, rules)
        if st == "pass":
            return "pass", n
        if st == "fail":
            return "fail_mll", n
        floor = max(floor, min(bal - rules["mll"], rules["start"] + rules["lock_above_start"]))
    if len(day_index) < rules["max_days"]:
        return None
    return "fail_time", rules["max_days"]


def real_days(w, r, starts, rules=RULES):
    """Start a challenge on each day in `starts`, walking the real days after it."""
    D = w.shape[0]
    res = [challenge(w, r, np.arange(s, min(s + rules["max_days"], D)), rules) for s in starts]
    return summarize([x for x in res if x is not None])


def random_days(w, r, n=4000, seed=42, days=None, rules=RULES):
    rng = np.random.default_rng(seed)
    pool = np.arange(w.shape[0]) if days is None else np.asarray(days)
    res = [challenge(w, r, rng.choice(pool, rules["max_days"]), rules) for _ in range(n)]
    return summarize(res)


def summarize(res):
    o = pd.Series([x[0] for x in res])
    d = pd.Series([x[1] for x in res])[o.values == "pass"]
    return dict(n=len(res), p=(o == "pass").mean(), mll=(o == "fail_mll").mean(),
                time=(o == "fail_time").mean(), med_days=d.median() if len(d) else np.nan)


def daily_pnl(w, r):
    return r[:, -1]
