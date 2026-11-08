"""Lab Q021: NG Sunday up-gap fade, the plan's CL rule unchanged (frame as analysis/s_rank_gap_round2_test.py).
Pre-registration: checks/candidates/lab_Q021/PREREG.md. Stages 1-2 on 2018-22; stage 3 only with --holdout.
  python3 analysis/lab_Q021.py [--holdout]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
from grid24 import jof
import metrics as M
from lab_Q007 import load

PV, TICK, COMM = 10000.0, 0.001, 5.0
HOLD = "--holdout" in sys.argv

g = load(); O, H, L, C = (getattr(g, k).ravel() for k in "ohlc"); CF = pd.Series(C).ffill().to_numpy(); N = len(O)
valid = ~np.isnan(C); prevv = np.maximum.accumulate(np.where(valid, np.arange(N), -1))
TS = pd.DatetimeIndex(g.ts); ATR = g.daily_atr(15)
tr = g.trading[TS[g.trading] >= "2018-01-01"]; full = g.last_j >= jof(1500)


def first_open(e, k=10):
    e = np.asarray(e, int); out = np.full(len(e), -1)
    for s in range(k):
        ee = np.clip(e + s, 0, N - 1); ok = (out < 0) & ~np.isnan(O[ee]); out[ok] = ee[ok]
    return out


def roll_bars():
    bd = CustomBusinessDay(calendar=USFederalHolidayCalendar()); out = []
    for y in range(2017, 2027):
        for m in range(1, 13):
            exp = pd.Timestamp(y, m, 1) - 3 * bd; r = TS.searchsorted(exp)
            for rr in range(r - 1, max(r - 5, 0), -1):                    # evening that opens the expiry-day session
                ev = np.where(valid[rr * 1440 + jof(1701): (rr + 1) * 1440])[0]
                if len(ev): out.append(rr * 1440 + jof(1701) + ev[0]); break
    return np.array(sorted(out))


RB = roll_bars(); cum = np.zeros(N + 1); cum[RB + 1] = 1; RC = np.cumsum(cum)
has_roll = lambda a, b: RC[np.clip(b, 0, N - 1) + 1] - RC[np.clip(a, 0, N - 1)] > 0


def frame(kind):
    """kind 'sun': Sunday reopen -> Monday; 'wk': Mon-Thu 17:00 reopen -> next day (placebo)."""
    dow = TS[tr].dayofweek
    if kind == "sun":
        nxt = tr[(dow == 0) & full[tr]]; ev = nxt - 1; keep = TS[ev].dayofweek == 6
    else:
        nxt = tr[(dow >= 1) & (dow <= 4) & full[tr]]; ev = nxt - 1; keep = (TS[ev].dayofweek <= 3) & np.isin(ev, tr)
    nxt, ev = nxt[keep], ev[keep]
    o_i = first_open(ev * 1440 + jof(1701)); ok = (o_i >= 0) & (o_i // 1440 == ev)
    ref_i = prevv[ev * 1440 + jof(1700)]; ref = CF[ev * 1440 + jof(1700)]
    gap = np.where(ok, O[np.clip(o_i, 0, None)] - ref, np.nan); a = ATR[nxt]
    F = pd.DataFrame(dict(ev=ev, nxt=nxt, gA=gap / a, atr=a), index=TS[nxt])
    F["ok"] = ok & np.isfinite(F.gA) & (gap != 0) & ~has_roll(ref_i + 1, nxt * 1440 + jof(900))
    return F[F.ok]


def trade(row, s):
    e_i = first_open([int(row.ev) * 1440 + jof(1706)])[0]; x_i = int(row.nxt) * 1440 + jof(900)
    if e_i < 0 or e_i // 1440 != row.ev: return np.nan
    raw = O[e_i]; ent = raw + s * TICK; sp = raw - s * 0.75 * row.atr; px = CF[x_i] - s * TICK
    hit = np.where((H[e_i:x_i + 1] >= sp) if s < 0 else (L[e_i:x_i + 1] <= sp))[0]
    if len(hit):
        j = e_i + hit[0]; o = O[j]
        px = ((max(o, sp) if s < 0 else min(o, sp)) if np.isfinite(o) and j != e_i else sp) - s * TICK
    return s * (px - ent) * PV - COMM


def run(F, v, th=None):
    th = th if th is not None else (0.3 if v == 3 else 0.1)
    out = {}
    for d, r in F.iterrows():
        if r.gA >= th: s = -1
        elif v == 2 and r.gA <= -th: s = 1
        else: continue
        p = trade(r, s)
        if np.isfinite(p): out[d] = (p, s)
    x = pd.DataFrame(out, index=["net", "side"]).T if out else pd.DataFrame(columns=["net", "side"])
    return x.astype(float).sort_index()


def tstat(x): return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def show(x, nm):
    by = x.groupby(x.index.year).sum()
    print(f"  {nm:<28} n={len(x):4d} avg ${x.mean():6.1f} PF {pf(x):4.2f} t {tstat(x):5.2f} win {np.mean(x > 0):.0%} "
          f"yrs+ {(by > 0).sum()}/{len(by)}  " + " ".join(f"{y}:{v:+.0f}" for y, v in by.items()))


if __name__ == "__main__":
    S = frame("sun"); W = frame("wk")
    print(f"roll bars marked {len(RB)}; Sunday weekends kept {len(S)} (2018-22 {((S.index.year >= 2018) & (S.index.year <= 2022)).sum()})")
    Sd = S[(S.index.year >= 2018) & (S.index.year <= 2022)]; Wd = W[(W.index.year >= 2018) & (W.index.year <= 2022)]
    print("\nStage 1 (2018-22), per NG")
    T = {v: run(Sd, v) for v in (1, 2, 3)}
    for v, nm in ((1, "V1 short gA >= +0.1 (CL rule)"), (2, "V2 both sides |gA| >= 0.1"), (3, "V3 short gA >= +0.3")): show(T[v].net, nm)
    best = max(T, key=lambda v: tstat(T[v].net)); x = T[best].net
    s1 = tstat(x) >= 2.0 and pf(x) >= 1.15 and len(x) >= 80
    print(f"  best V{best}: stage 1 {'PASS' if s1 else 'FAIL'}")
    th = 0.3 if best == 3 else 0.1
    share = np.mean(Sd.gA >= th) if best != 2 else np.mean(np.abs(Sd.gA) >= th)
    q = np.nanquantile(Wd.gA if best != 2 else np.abs(Wd.gA), 1 - share)
    P = run(Wd, best, th=q).net
    rng = np.random.default_rng(7)
    pm = np.array([P.iloc[rng.choice(len(P), min(len(x), len(P)), replace=False)].mean() for _ in range(500)])
    p = np.mean(pm >= x.mean()); by = x.groupby(x.index.year).sum(); s2 = p < 0.05 and (by > 0).sum() >= 4
    print(f"\nStage 2 placebo V{best} (weekday evenings, threshold {q:.3f} ATR = same share): n {len(P)} avg ${P.mean():.1f}, "
          f"p = {p:.3f}; stage 2 {'PASS' if s2 else 'FAIL'}")
    daily = x.groupby(x.index).sum().reindex(pd.date_range("2018-01-01", "2022-12-31", freq="B"), fill_value=0.0)
    m = M.perf(daily, x)
    print("  metrics V%d 2018-22: Sharpe %.2f Sortino %.2f PF %.2f Calmar %.2f Ulcer %.2f" %
          (best, m["sharpe"], m["sortino"], m["profit_factor"], m["calmar"], m["ulcer"]))
    for sd, nm in ((1, "longs"), (-1, "shorts")):
        xs = T[best][T[best].side == sd].net
        if len(xs) > 2: show(xs, f"  V{best} {nm}")
    if HOLD and s1 and s2:
        h = run(S[S.index.year >= 2023], best).net; print("\nStage 3 holdout (one look)"); show(h, f"V{best} 2023-onward")
        show(pd.concat([x, h]), f"V{best} full")
