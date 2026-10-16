"""Forced flows on ES and gold, round 5 (user, 2026-10-16: 'find strategies on ES, gold or oil based on forced flows' +
Monte Carlo). Two flows not tested before (TIER_LIST: unconditional month-end fades / turn-of-month already F/C):
  E1  Pension / balanced-fund rebalancing, CONDITIONAL on stocks vs bonds. Funds with fixed equity / bond weights must
      sell what outperformed into the month-end (and harder at quarter-ends). Signal at the close 4 trading days before
      month-end: S = ES % change since the previous month-end close minus ZN % change (both 15:00 CT closes). Trade the
      last 3 trading days, ES day session 8:30 -> 15:00 CT, side = -sign(S) (sell equities when they outperformed).
      Pre-registered variants: all month-ends / quarter-ends only / 'strong' (|S| above the median of all earlier |S|).
      Controls: the same rule mid-month (trading days 9-11) and random sides. NQ shown as a robustness check.
  G1  Gold first-notice-day long liquidation. Speculative longs in the active COMEX gold month (Feb / Apr / Jun / Aug /
      Oct / Dec) must roll or sell before first notice day (the last business day of the month before delivery).
      Short GC in the COMEX day session 7:20 -> 12:30 CT on the 3 trading days before FND. Control: the same days before
      the last business day of the other months (no delivery pressure), random sides.
  O1  CL holiday-reopen up-gap fade. Our CL Sunday up-gap fade (A, in the plan) shorts the 17:00 CT reopen after a
      weekend when it opens >= 0.1 ATR above the last price: weekend hedgers / short-covering push the reopen, then it
      reverts. Holiday breaks (Monday holidays, July 4, Thanksgiving, Christmas, New Year) are the same forced re-pricing
      after a long close. Rule copied unchanged: short 17:05 CT reopen after a >= 20-hour non-Sunday break if the open is
      >= 0.1 ATR above the last price, out 10:00 CT next day, stop 0.75 ATR; roll-crossing breaks skipped. Down-gaps and
      ordinary weekday reopens as controls; the Sunday fade itself for reference.
Costs: ES $5 + 1 tick a fill ($30 round trip), NQ $7.25 + 1 tick ($17.25), GC $7.25 + 1 tick ($27.25), CL $7.25 + 1 tick ($27.25), 1 contract,
2018-2026. Monte Carlo (analysis/montecarlo.py) on each pre-registered main variant.
  python3 analysis/forced_flows_round5_test.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import load, SPEC
import metrics as M, montecarlo as MC

COST = {"ES": 5.0 + 2 * 12.5, "NQ": 7.25 + 2 * 5.0, "GC": 7.25 + 2 * 10.0}


def session(sym, t0, t1):
    g = load(sym); tr = g.trading; ts = pd.DatetimeIndex(g.ts[tr])
    C = pd.DataFrame(g.c[tr]).ffill(axis=1).to_numpy()
    o = g.o[tr, jof(t0) + 1]; o = np.where(np.isnan(o), C[:, jof(t0)], o)
    df = pd.DataFrame({"o": o, "c": C[:, jof(t1)], "c15": C[:, jof(1500)]}, index=ts)
    has = ~np.isnan(g.c[tr, jof(t0) + 1:jof(t1) + 1]).all(1)
    return df[has & (ts.year >= 2017)]


def line(x, nm, w=46):
    x = pd.Series(x).dropna()
    if len(x) < 5: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():6.0f} PF {pf:4.2f} t {x.mean() / x.std() * np.sqrt(len(x)):+4.1f} "
            f"yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${x[y < 2023].mean():6.0f} 23-26 ${x[y >= 2023].mean():6.0f}")


def placebo(pnl_abs, n=200, seed=1):
    rng = np.random.default_rng(seed); a = np.asarray(pnl_abs)
    return np.array([np.mean(a * rng.choice([-1, 1], len(a))) for _ in range(n)])


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    zn = session("ZN", 830, 1400)
    print("\n=== E1: rebalancing flow, conditional on stocks vs bonds")
    for sym in ("ES", "NQ"):
        pv = SPEC[sym][0]; s = session(sym, 830, 1500); s = s[s.index >= "2017-06-01"]
        z = zn.c.reindex(s.index).ffill()
        months = s.groupby(s.index.to_period("M"))
        rows = []; prev_close = None; prev_z = None; past_abs = []
        for per, m in months:
            if prev_close is not None and len(m) >= 8:
                sig_day = m.index[-4]
                S = (m.c15[sig_day] / prev_close - 1) - (z[sig_day] / prev_z - 1)
                strong = bool(np.isfinite(S)) and len(past_abs) >= 12 and abs(S) >= np.median(past_abs)
                for d in m.index[-3:]:
                    rows.append(dict(date=d, kind="end", S=S, strong=strong, q=per.month in (3, 6, 9, 12),
                                     move=(m.c15[d] - m.o[d]) * pv))
                mid_sig = m.index[7]; Sm = (m.c15[mid_sig] / prev_close - 1) - (z[mid_sig] / prev_z - 1)
                for d in m.index[8:11]:
                    rows.append(dict(date=d, kind="mid", S=Sm, strong=False, q=False, move=(m.c15[d] - m.o[d]) * pv))
                if np.isfinite(S): past_abs.append(abs(S))     # ZN starts 2017-12: skip NaN signals
            prev_close = m.c15.iloc[-1]; prev_z = z[m.index[-1]]
        R = pd.DataFrame(rows).set_index("date"); R = R[R.index >= "2018-01-01"]
        R = R[np.isfinite(R.S)]; R["net"] = -np.sign(R.S) * R.move - COST[sym]
        e = R[R.kind == "end"]
        print(f"\n  {sym}:")
        print(line(e.net, "month-ends, all (last 3 days)"))
        print(line(e[e.q].net, "quarter-ends only"))
        print(line(e[e.strong].net, "strong |S| (above past median)"))
        print(line(e[e.strong & e.q].net, "strong quarter-ends"))
        for k, lbl in ((0, "T-2"), (1, "T-1"), (2, "T (last day)")):
            sub = e.groupby(e.index.to_period("M")).nth(k)
            print(line(sub.net, f"  day {lbl} only"))
        print(line(R[R.kind == "mid"].net, "control: same rule mid-month (days 9-11)"))
        pl = placebo(e.move.abs()) - COST[sym]
        print(f"   control: random sides on the same days: avg ${pl.mean():.0f} (5-95% {np.percentile(pl, 5):.0f}..{np.percentile(pl, 95):.0f})")
        if sym == "ES":
            days = pd.DatetimeIndex(s.index[s.index >= "2018-01-01"])
            dl = e.net.groupby(level=0).sum().reindex(days, fill_value=0.0)
            print(M.table({"ES month-ends, all": (dl, e.net), "  longs": (e.net[np.sign(e.S) < 0].groupby(level=0).sum().reindex(days, fill_value=0.0), e.net[np.sign(e.S) < 0]),
                           "  shorts": (e.net[np.sign(e.S) > 0].groupby(level=0).sum().reindex(days, fill_value=0.0), e.net[np.sign(e.S) > 0])}))
            print(MC.report(e.net.to_numpy(), dl.to_numpy(), size=0.1, label="ES month-ends as 1 MES", trail=2000))

    print("\n=== G1: gold first-notice-day liquidation (short 7:20 -> 12:30 CT, 3 days before FND)")
    pv = SPEC["GC"][0]; s = session("GC", 720, 1230); s = s[s.index >= "2018-01-01"]
    rows = []
    for per, m in s.groupby(s.index.to_period("M")):
        if len(m) < 6: continue
        fnd_month = per.month in (1, 3, 5, 7, 9, 11)          # last business day = FND of the next (active) month
        for k, d in enumerate(m.index[-4:-1]):                 # the 3 trading days before the last business day
            rows.append(dict(date=d, fnd=fnd_month, k=k, move=(m.c[d] - m.o[d]) * pv))
        rows.append(dict(date=m.index[-1], fnd=fnd_month, k=3, move=(m.c[m.index[-1]] - m.o[m.index[-1]]) * pv))
    G = pd.DataFrame(rows).set_index("date"); G["short"] = -G.move - COST["GC"]; G["long"] = G.move - COST["GC"]
    f = G[G.fnd & (G.k < 3)]; o = G[~G.fnd & (G.k < 3)]
    print(line(f.short, "short, 3 days before FND (active months)"))
    for k in range(3): print(line(G[G.fnd & (G.k == k)].short, f"  day FND-{3 - k} only"))
    print(line(G[G.fnd & (G.k == 3)].long, "info: long on FND day itself (rebound)"))
    print(line(o.short, "control: same days, non-delivery months"))
    pl = placebo(f.move.abs()) - COST["GC"]
    print(f"   control: random sides on the FND days: avg ${pl.mean():.0f} (5-95% {np.percentile(pl, 5):.0f}..{np.percentile(pl, 95):.0f})")
    days = pd.DatetimeIndex(s.index)
    dl = f.short.groupby(level=0).sum().reindex(days, fill_value=0.0)
    print(M.table({"GC FND short": (dl, f.short)}))
    print(MC.report(f.short.to_numpy(), dl.to_numpy(), size=0.1, label="GC FND short as 1 MGC", trail=2000))

    print("\n=== O1: CL holiday-reopen up-gap fade (Sunday fade rule on non-Sunday breaks >= 20 h)")
    import s_rank_gap_round2_test as G
    S = G.Sym("CL"); bars, _ = G.rolls_cl(S); S.set_rolls(bars)
    F = G.sunday_frame(S); W = G.weekday_frame(S)
    # holiday reopens: trading day n (full session), reopen on calendar row n-1 (not a Sunday) after a break >= 20 hours
    dow = S.TS[S.tr].dayofweek; n_ = S.tr[S.full[S.tr]]; r = n_ - 1
    r_ok = (S.TS[r].dayofweek != 6)
    o_i = S.first_open(r * 1440 + G.jof(1701)); ok = (o_i >= 0) & (o_i // 1440 == r)
    ref_i = S.prevv[r * 1440 + G.jof(1700)]; brk = (r * 1440 + G.jof(1700) - ref_i) / 60
    m = r_ok & ok & (brk >= 20); r, n_, o_i, ref_i = r[m], n_[m], o_i[m], ref_i[m]
    ref = S.CF[r * 1440 + G.jof(1700)]; gap = S.O[o_i] - ref; a = S.atr[n_]
    Hf = pd.DataFrame(dict(sun=r, mon=n_, o_i=o_i, ref=ref, ref_i=ref_i, gap=gap, atr=a, gA=gap / a, ok=np.isfinite(gap / a) & (gap != 0)), index=S.TS[n_])
    Hf["roll"] = S.has_roll(ref_i + 1, n_ * 1440 + G.jof(1329))
    print(f"   holiday reopens 2018-26: {len(Hf)} ({int((Hf.ok & ~Hf.roll).sum())} usable); dates: " + ", ".join(d.strftime('%Y-%m-%d') for d in Hf.index[:12]) + " ...")
    def stopped(F_, th=0.1, side=-1, stop=0.75):
        """short (side -1) / long (+1) at the 17:05 reopen, out 10:00 next day, stop `stop` ATR (first touch, gap-through filled at the open)."""
        out = []
        for row in F_[F_.ok & ~F_.roll & (side * -1 * F_.gA >= th)].itertuples():
            e_i = int(row.sun) * 1440 + G.jof(1705); e_i = S.first_open([e_i])[0]
            if e_i < 0 or e_i // 1440 != row.sun: continue
            x_i = int(row.mon) * 1440 + G.jof(1000); e = S.O[e_i] - side * S.tick; sp = e - side * stop * row.atr
            seg = S.H[e_i:x_i + 1] if side < 0 else S.L[e_i:x_i + 1]
            hit = np.where(seg >= sp)[0] if side < 0 else np.where(seg <= sp)[0]
            if len(hit):
                j = e_i + hit[0]; px = (sp if np.isnan(S.O[j]) or j == e_i else (max(S.O[j], sp) if side < 0 else min(S.O[j], sp))) + side * -1 * S.tick
            else: px = S.CF[x_i] + side * -1 * S.tick
            out.append((row.Index, (px - e) * side * S.pv - S.comm))
        return pd.Series(dict(out), dtype=float).sort_index()
    hol = stopped(Hf); print(line(hol, "short holiday up-gaps >= 0.1 ATR (the rule)"))
    print(line(stopped(Hf, 0.25), "  >= 0.25 ATR"))
    print(line(stopped(Hf, side=1), "control: long holiday down-gaps >= 0.1 ATR (fade)"))
    print(line(stopped(W), "control: ordinary weekday reopen up-gap short"))
    sun = stopped(F); print(line(sun, "reference: Sunday up-gap fade (in the plan)"))
    both = pd.concat([sun, hol]).sort_index(); print(line(both, "Sunday + holiday reopens together"))
    days = S.days; dl = both.groupby(level=0).sum().reindex(days, fill_value=0.0); dls = sun.groupby(level=0).sum().reindex(days, fill_value=0.0)
    print(M.table({"CL Sunday fade": (dls, sun), "CL Sunday + holiday": (dl, both)}))
    print(MC.report(sun.to_numpy(), dls.to_numpy(), size=0.2, label="CL Sunday fade as 2 MCL (the plan)", trail=2000))
    print(MC.report(both.to_numpy(), dl.to_numpy(), size=0.2, label="CL Sunday + holiday as 2 MCL", trail=2000))
