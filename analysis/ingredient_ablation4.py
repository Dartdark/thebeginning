"""Ingredient ablation, round 4 (user 2026-11-08): Expiration Open Short (EOS), NFP Fade, CL Sunday Gap Fade. Information only (historical
component evidence, no promotion). Each rebuilt here from its MultiCharts file's inputs (checked against the research numbers: EOS 105
trades $474, NFP 76 $319, CL 93 $602 per contract), then ONE part changed at a time; per contract after $7.25 + 1 tick per market / stop
fill; 2018-26 and both periods, with total $ and max DD.
  EOS (third-Friday options expiry, Thursday when the Friday is closed; short at the 08:30 open, out at the 10:00 close, stop 0.3 ATR):
    other Fridays (the expiry mechanism) / long instead / no stop / out 09:00 / out 11:00 / out 14:55 / enter 09:00 /
    quarterly expiries only (Mar Jun Sep Dec) / monthly-only expiries
  NFP (Friday, day <= 10, the 07:31-07:35 range > 3 x its median of the previous 20 weekdays; fade the 07:30 -> 07:45 reaction at the
    07:46 open, stop 0.5 ATR, out at the 09:00 close): no spike condition / follow instead of fade / no stop / out 08:30 / out 10:00 /
    reaction 07:30 -> 07:35 / reaction 07:30 -> 08:00
  CL Sunday Gap Fade (Sunday 17:00 reopen: the 17:05 close >= Friday's last price + 0.1 x ATR15 -> short at the 17:06 open, out at
    Monday's 09:00 CT close, stop 0.75 ATR; roll weekends and holiday Mondays out): no gap threshold (every up-gap) / gap >= 0.3 ATR /
    down-gaps faded too / down-gaps only (long) / follow instead / no stop / out Sunday 23:59 / out Monday 07:00 / out Monday 13:30 /
    the same fade on Monday-Thursday 17:00 reopens
  tools/run_stamped.sh analysis/ingredient_ablation4.py > analysis/outputs/ingredient_ablation4_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close
from overnight_round import roll_minutes
from ingredient_ablation3 import line

COMM = 7.25


def walk(g, f0, f1, side, stop_pts, pv, tick):
    """Trade from the open of flat minute f0 to the close of flat minute f1 (row * 1440 + j), stop in points (None = none)."""
    O, H, L, C = g.o.ravel(), g.h.ravel(), g.l.ravel(), g.c.ravel()
    k0 = f0 + np.flatnonzero(np.isfinite(O[f0:f1 + 1]))[:1]
    if not len(k0): return None
    k0 = int(k0[0]); e = O[k0] + side * tick; px = None
    if stop_pts is not None:
        sp = e - side * stop_pts; seg = slice(k0, f1 + 1)
        hit = np.flatnonzero((L[seg] <= sp) if side > 0 else (H[seg] >= sp))
        if len(hit): b = k0 + hit[0]; px = (min(O[b], sp) if side > 0 else max(O[b], sp)) - side * tick
    if px is None:
        cl = C[k0:f1 + 1]; ok = np.flatnonzero(np.isfinite(cl))
        if not len(ok): return None
        px = cl[ok[-1]] - side * tick
    return (px - e) * side * pv - COMM


def third_fridays(start, end):
    closed = {pd.Timestamp(x) for x in ("2019-04-19", "2022-04-15", "2025-04-18", "2026-06-19")}
    out = []
    for m in pd.date_range(start, end, freq="MS"):
        fr = [d for d in pd.date_range(m, m + pd.offsets.MonthEnd(0)) if d.dayofweek == 4][2]
        out.append(fr - pd.Timedelta(days=1) if fr in closed else fr)
    return out


def run(g, events, pv, tick):
    rows = []
    for d, f0, f1, side, stop in events:
        x = walk(g, f0, f1, side, stop, pv, tick)
        if x is not None: rows.append((d, side, x))
    return pd.DataFrame(rows, columns=["date", "side", "net"])


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); ts = pd.DatetimeIndex(g.ts); pos = pd.Series(np.arange(len(ts)), index=ts)
    tr = set(g.trading.tolist())
    def show(nm, ev, pv=20.0, tick=0.25):
        T = run(g_cur[0], ev, pv, tick); print(line(T.net, T.date, nm), flush=True); return T
    # ---------------- EOS
    g_cur = [g]; print("\n1. Expiration Open Short (check: 105 trades, $474):")
    exp = [d for d in third_fridays("2018-01-01", "2026-11-01") if d in pos.index and int(pos[d]) in tr]
    others = [d for d in ts[ts >= "2018-01-01"] if d.dayofweek == 4 and d not in set(exp) and int(pos[d]) in tr and not is_early_close(d)]
    def eos(days, side=-1, t0=830, t1=1000, stop=0.3, months=None):
        ev = []
        for d in days:
            r = int(pos[d])
            if np.isnan(atr[r]) or (months and d.month not in months) or is_early_close(d): continue
            ev.append((d, r * 1440 + jof(t0) + 1, r * 1440 + jof(t1), side, None if stop is None else stop * atr[r]))
        return ev
    show("as is", eos(exp)); show("other Fridays (no expiry)", eos(others)); show("long instead", eos(exp, side=1)); show("no stop", eos(exp, stop=None))
    show("out 09:00", eos(exp, t1=900)); show("out 11:00", eos(exp, t1=1100)); show("out 14:55", eos(exp, t1=1455)); show("enter 09:00", eos(exp, t0=900))
    show("quarterly expiries only", eos(exp, months={3, 6, 9, 12})); show("monthly-only expiries", eos(exp, months={1, 2, 4, 5, 7, 8, 10, 11}))
    # ---------------- NFP
    print("\n2. NFP Fade (check: 76 trades, $319):")
    rng_ = g.h[:, jof(731):jof(735) + 1].max(1) - g.l[:, jof(731):jof(735) + 1].min(1)
    wk = [r for r in range(g.D) if ts[r].dayofweek < 5 and np.isfinite(rng_[r])]; med = {}
    for i, r in enumerate(wk):
        if i >= 20: med[r] = np.median([rng_[q] for q in wk[i - 20:i]])
    cand = [r for r in med if ts[r] >= pd.Timestamp("2018-01-01") and ts[r].dayofweek == 4 and ts[r].day <= 10]
    def nfp(spike=3.0, fade=True, stop=0.5, t1=900, react=745):
        ev = []
        for r in cand:
            if spike and not rng_[r] > spike * med[r]: continue
            ref, rc = g.c[r, jof(730)], g.c[r, jof(react)]
            if not (np.isfinite(ref) and np.isfinite(rc)) or rc == ref or np.isnan(atr[r]): continue
            side = int(-np.sign(rc - ref)) if fade else int(np.sign(rc - ref))
            ev.append((ts[r], r * 1440 + jof(react) + 1, r * 1440 + jof(t1), side, None if stop is None else stop * atr[r]))
        return ev
    show("as is", nfp()); show("no spike condition (any first-10-day Friday)", nfp(spike=0)); show("follow instead of fade", nfp(fade=False))
    show("no stop", nfp(stop=None)); show("out 08:30", nfp(t1=830)); show("out 10:00", nfp(t1=1000)); show("reaction 07:30 -> 07:35", nfp(react=735)); show("reaction 07:30 -> 08:00", nfp(react=800))
    # ---------------- CL Sunday
    print("\n3. CL Sunday Gap Fade (check: MultiCharts spec 97 trades, $653 per CL after $27.25):")
    gc = pickle.load(open("scratch_data/cl.pkl", "rb")); g_cur[0] = gc; atc = gc.daily_atr(15); tsc = pd.DatetimeIndex(gc.ts)
    rolls = np.sort(roll_minutes(gc, "CL")); Cf = gc.c.ravel()
    fr_ = pickle.load(open("scratch_data/s_rank_gap2.pkl", "rb"))["frames"]["CL"]          # the confirmed bench's Sunday events
    # FIX 2026-11-08 (before reading any variant): gap = Sunday 17:01 OPEN vs Friday's last price (bench / MultiCharts spec), entry at
    # the open of the 17:06 bar (= 17:05 price), roll weekends kept; the first draft measured the gap at the 17:05 close.
    def reopen_events(weekdays, k=0.1, mode="fade_up", t1=(1, 900), stop=0.75):
        ev = []
        if weekdays == {6}:
            items = [(int(r.sun), int(r.mon), r.gA, r.atr) for r in fr_.itertuples() if r.ok and pd.Timestamp(gc.ts[int(r.sun)]) >= pd.Timestamp("2018-01-01")]
        else:
            items = []
            for r in range(1, gc.D - 2):
                d = tsc[r]
                if d < pd.Timestamp("2018-01-01") or d.dayofweek not in weekdays or np.isnan(atc[r]) or tsc[r + 1].dayofweek >= 5: continue
                o1 = gc.o[r, jof(1701)]; prev = Cf[r * 1440 + jof(1500):r * 1440 + jof(1659)]; ok = np.flatnonzero(np.isfinite(prev))
                if not np.isfinite(o1) or not len(ok): continue
                items.append((r, r + 1, (o1 - prev[ok[-1]]) / atc[r], atc[r]))
        for rs, rm, gA, a_ in items:
            if not np.isfinite(gA): continue
            rx = rm if t1[0] == 1 else rs; fx = rx * 1440 + jof(t1[1])
            up, dn = gA >= k, gA <= -k
            if mode == "fade_up" and up: side = -1
            elif mode == "fade_both" and (up or dn): side = -1 if up else 1
            elif mode == "fade_down" and dn: side = 1
            elif mode == "follow_up" and up: side = 1
            else: continue
            ev.append((pd.Timestamp(gc.ts[rm]), rs * 1440 + jof(1706), fx, side, None if stop is None else stop * a_))
        return ev
    cl = dict(pv=1000.0, tick=0.01)
    show("as is", reopen_events({6}), **cl); show("no gap threshold (every up-gap)", reopen_events({6}, k=0.0), **cl); show("gap >= 0.3 ATR", reopen_events({6}, k=0.3), **cl)
    show("down-gaps faded too", reopen_events({6}, mode="fade_both"), **cl); show("down-gaps only (long)", reopen_events({6}, mode="fade_down"), **cl)
    show("follow instead", reopen_events({6}, mode="follow_up"), **cl); show("no stop", reopen_events({6}, stop=None), **cl)
    show("out Sunday 23:59", reopen_events({6}, t1=(0, 2359)), **cl); show("out Monday 07:00", reopen_events({6}, t1=(1, 700)), **cl); show("out Monday 13:30", reopen_events({6}, t1=(1, 1330)), **cl)
    show("same fade on Mon-Thu 17:00 reopens", reopen_events({0, 1, 2, 3}), **cl)
