"""Relative Strength NQ / ES: room for optimisation? (pre-registered 2026-10-20, written before any result).
Base = the user's RelStrength_v3 as rebuilt in analysis/relative_strength_test.py (decide 9:00, |Z| >= 1.25, stop 0.6 /
target 1.0 x 20-day avg RTH range, flat 15:00). Design 2018-2022 ONLY for every choice; 2023-26 is looked at once, at the end
of each stage, for the chosen setting vs the base. Method = DEVELOPMENT_PROCESS.md 'clusters, not the single best'.

Stage 1  Exits, both sides together. Grid: stop {0.4, 0.5, 0.6, 0.8, 1.0} x target {0.6, 0.8, 1.0, 1.5, none} x flat
         {15:00, 15:55} = 50. Score = design daily Sharpe. Pick = the setting with the best average Sharpe over itself and
         its grid neighbours (one step in stop / target, same flat): a plateau, not a peak. Also reported: breakeven stop
         (move the stop to entry at +0.5 x range) on the pick.
Stage 2  Sides. The same grid for longs and shorts separately, and a higher short threshold |Z| {1.5, 2.0}. A side gets its
         own setting only if it beats the shared pick on design by > 0.15 Sharpe AND holds on 2023+.
Stage 3  Filters, each pre-registered with its expected sign (keep the trades where...):
         F1 VXN above its own 252-day median (Gao et al.: intraday momentum is stronger on volatile days)       expect +
         F2 not an FOMC day (13:00 CT statement inside the hold adds noise)                                    expect +
         F3 not a 7:30 CT macro-release day (the open move is news, not NQ-specific flow)                      expect ?
         F4 NQ's overnight move (prev 15:00 -> 8:30) in the trade's direction                                   expect ?
         F5 size 2x when |Z| >= 2.0 (the note: larger Z = larger average)                                       expect +
         Adopt a filter only if design AND 2023+ both improve the per-day Sharpe, and the kept trades' average beats
         the skipped ones in both periods.
Trials: 50 + 2 x 50 + 2 + 1 + 5 = 158 variants; all go to TRIALS.csv. Expectation (in advance): exits matter little (the
note's sweep found a plateau), small gains at most; anything bigger than +0.2 Sharpe on design is suspect.
  python3 analysis/relative_strength_opt_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import relative_strength_test as RS
from grid24 import jof
import event_days as EV

STOPS, TGTS, FLATS = (0.4, 0.5, 0.6, 0.8, 1.0), (0.6, 0.8, 1.0, 1.5, 0), (1500, 1555)   # target 0 = none


def sharpe(t, idx, lo=None, hi=None, w=None):
    d = pd.Series(0.0, index=idx); x = t.pnl * (w if w is not None else 1.0)
    g = x.groupby(t.date).sum(); d.loc[g.index] = g.values
    if lo: d = d[d.index >= lo]
    if hi: d = d[d.index < hi]
    return d.mean() / d.std() * np.sqrt(252) if d.std() > 0 else np.nan


def grid(days, N, Z, idx, side=None, **kw):
    rows = []
    for fl in FLATS:
        for s in STOPS:
            for tg in TGTS:
                t = RS.trades(days, N, Z, stop_f=s, tgt_f=tg, flat=fl, **kw)
                if side: t = t[t.side == side]
                rows.append(dict(flat=fl, stop=s, tgt=tg, n=len(t[t.date < "2023"]), avg=t[t.date < "2023"].pnl.mean(),
                                 sh=sharpe(t, idx, hi="2023"), _t=t))
    return pd.DataFrame(rows)


def plateau(G):
    si = {s: k for k, s in enumerate(STOPS)}; ti = {t: k for k, t in enumerate(TGTS)}
    sc = []
    for _, r in G.iterrows():
        nb = G[(G.flat == r.flat) & (G.stop.map(si).sub(si[r.stop]).abs() <= 1) &
               (G.tgt.map(lambda v: ti[v]).sub(ti[r.tgt]).abs() <= 1)]
        sc.append(nb.sh.mean())
    G = G.copy(); G["plateau"] = sc; return G


def show(G, nm):
    tab = G.pivot_table(index=["flat", "stop"], columns="tgt", values="sh").round(2)
    tab.columns = ["none" if c == 0 else c for c in tab.columns]
    print(f"\n{nm}: design 2018-22 daily Sharpe (columns = target x range; 'none' = no target)\n{tab.to_string()}")


def summary(nm, t, idx, w=None):
    x = t.pnl * (w if w is not None else 1.0); a, b = t.date < "2023", t.date >= "2023"
    print(f"   {nm:<40} n {len(t):4d} ${x.mean():5.0f}  t {RS.tstat(x):4.1f} | design Sharpe {sharpe(t, idx, hi='2023', w=w):.2f} ${x[a].mean():.0f}"
          f" | 2023+ Sharpe {sharpe(t, idx, lo='2023', w=w):.2f} ${x[b].mean():.0f} | full {sharpe(t, idx, w=w):.2f}")


if __name__ == "__main__":
    days, N, E = RS.load(); idx = pd.DatetimeIndex([pd.Timestamp(str(x)) for x in days.date]); Z = RS.signals(days, N, E)
    base = RS.trades(days, N, Z); print("Base (user's settings):"); summary("base 0.6 / 1.0 / 15:00", base, idx)

    print("\n=== Stage 1: exits, both sides ===")
    G = plateau(grid(days, N, Z, idx)); show(G, "Both sides")
    pick = G.loc[G.plateau.idxmax()]; base_row = G[(G.stop == 0.6) & (G.tgt == 1.0) & (G.flat == 1500)].iloc[0]
    print(f"\n   plateau pick: stop {pick.stop}, target {pick.tgt}, flat {pick.flat} (design Sharpe {pick.sh:.2f}, plateau {pick.plateau:.2f});"
          f" base design {base_row.sh:.2f} (plateau {base_row.plateau:.2f}); single best cell {G.sh.max():.2f}")
    P = pick._t; summary("PICK", P, idx); summary("base", base, idx)
    be = RS.trades(days, N, Z, stop_f=pick.stop, tgt_f=pick.tgt, flat=int(pick.flat), be_f=0.5); summary("PICK + breakeven at +0.5 range", be, idx)
    kw = dict(stop_f=pick.stop, tgt_f=pick.tgt, flat=int(pick.flat))

    print("\n=== Stage 2: sides ===")
    for sd, nm in ((1, "Longs"), (-1, "Shorts")):
        Gs = plateau(grid(days, N, Z, idx, side=sd)); show(Gs, nm); ps = Gs.loc[Gs.plateau.idxmax()]
        shared = sharpe(P[P.side == sd], idx, hi="2023")
        print(f"   {nm} own pick: stop {ps.stop}, target {ps.tgt}, flat {ps.flat}: design {ps.sh:.2f} vs shared setting {shared:.2f}"
              f" -> {'candidate' if ps.sh - shared > 0.15 else 'keep shared'}")
        summary(f"{nm} own pick", ps._t, idx); summary(f"{nm} shared pick", P[P.side == sd], idx)
    for zs in (1.5, 2.0):
        t = RS.trades(days, N, Z, zmin_short=zs, **kw); summary(f"short |Z| >= {zs}", t, idx)

    print("\n=== Stage 3: filters on the pick ===")
    vxn = pd.read_csv("data/VXN_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE
    med = vxn.rolling(252).median(); prev = vxn.shift(1).reindex(P.date).to_numpy(); pmed = med.shift(1).reindex(P.date).to_numpy()
    f1 = prev > pmed
    fomc = set(pd.to_datetime(EV.FOMC_DATES)); f2 = ~P.date.isin(fomc).to_numpy()
    g = pickle.load(open(RS.SP + "g24.pkl", "rb")); rel = set(pd.DatetimeIndex(g.ts[EV.release_days(g)]).normalize())
    f3 = ~P.date.isin(rel).to_numpy()
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); dd = P.day.to_numpy()
    on = cf[dd * 1440 + jof(830)] - cf[(dd - 1) * 1440 + jof(1500)]
    prev_day = np.array([(pd.Timestamp(g.ts[d]) - pd.Timestamp(g.ts[d - 1])).days for d in dd])
    on = np.where(prev_day == 1, on, cf[dd * 1440 + jof(830)] - cf[(dd - 3) * 1440 + jof(1500)])   # Monday: from Friday
    f4 = np.sign(on) == P.side.to_numpy()
    for nm, m, exp in (("F1 VXN above its 1-year median", f1, "+"), ("F2 not FOMC day", f2, "+"),
                       ("F3 not a 7:30 release day", f3, "?"), ("F4 overnight move with the trade", f4, "?")):
        k, sk = P[m], P[~m]
        print(f"   {nm:<36} (expected {exp}) kept {len(k)}: design ${k[k.date < '2023'].pnl.mean():.0f} vs skipped ${sk[sk.date < '2023'].pnl.mean():.0f}"
              f" | 2023+ ${k[k.date >= '2023'].pnl.mean():.0f} vs ${sk[sk.date >= '2023'].pnl.mean():.0f}")
        summary(f"   pick with {nm[:2]}", k, idx)
    w = np.where(P.z.abs() >= 2.0, 2.0, 1.0); summary("F5 size 2x when |Z| >= 2", P, idx, w=w)
    print("   |Z| buckets (all years, $ a trade):", P.groupby(pd.cut(P.z.abs(), [1.25, 1.5, 2, 2.5, 3, 99])).pnl.agg(["count", "mean"]).round(0).to_dict("index"))
    P.to_csv(RS.SP + "rs_pick_trades.csv", index=False)
