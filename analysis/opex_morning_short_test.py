"""Zoom-in from the option-income ETF test: short NQ on the 3rd-Friday (monthly roll / expiry) morning (2026-10-14).

Finding (analysis/option_income_etf_test.py, A): on the 3rd Friday NQ fell 8:30 -> 10:30 CT by $487 per NQ (t -2.3,
7 of 9 years, 2018-21 -$335, 2022-26 -$615) while other Fridays were flat; the 10:30-11:00 BXN / QYLD sell window
itself showed no selling. Reading: dealers who will buy the covered-call funds' new calls at 10:30-11:00 CT pre-hedge
by selling futures in the morning (and expiring-option hedges unwind at the open settlement).
Trade: short at the 8:31 bar open - 1 tick on the roll day (3rd Friday; Thursday when Friday is a holiday);
exit 9:30 / 10:00 / 10:30 / 11:00 / 15:00; stop none / 0.5 / 1.0 x 15-day ATR; $7.25 + 1 tick a fill.
Pick by 2018-22 t, holdout 2023-26. Controls: the same trade on the Fridays one week before / after the roll and on
every other Friday; quarterly (futures expiry) vs other months; a long version (longs / shorts separately, per
DEVELOPMENT_PROCESS.md). Then the plan's trades on roll mornings (does a filter help?), full metrics, bootstrap /
permutation on 2023+, funded bench.
  python3 analysis/opex_morning_short_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from option_income_etf_test import roll_rows, tstat
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25
SPLIT = pd.Timestamp("2023-01-01")


def line(x, nm, w=58):
    x = pd.Series(x).dropna()
    if len(x) < 6: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.0f} PF {pf:4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${x[y < 2023].mean():6.0f} 23-26 ${x[y >= 2023].mean():6.0f}")


def trade(g, rows, side, exit_t, stop_atr, atr, t0=831):
    O, H, L, C = g.o, g.h, g.l, g.c; j0 = jof(t0); j1 = jof(exit_t); out = []
    for d in rows:
        if np.isnan(O[d, j0]): continue
        s = side; e = O[d, j0] + s * TICK; sp = e - s * stop_atr * atr[d] if stop_atr else None; px = None
        for j in range(j0, j1 + 1):
            if sp is None or np.isnan(H[d, j]): continue
            if (L[d, j] <= sp) if s > 0 else (H[d, j] >= sp):
                px = ((min(O[d, j], sp) if s > 0 else max(O[d, j], sp)) if j > j0 else sp) - s * TICK; jx = j; kind = 0; break
        if px is None:
            cc = C[d, j0:j1 + 1]; ok = np.where(~np.isnan(cc))[0]
            if not len(ok): continue
            px = cc[ok[-1]] - s * TICK; jx = j0 + ok[-1]; kind = 2
        out.append(dict(day=d, j0=j0, j1=jx, side=s, entry=e, exit=px, kind=kind, date=pd.Timestamp(g.ts[d]), net=(px - e) * s * PV - COMM))
    return pd.DataFrame(out).set_index("date", drop=False)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15)
    tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= "2018-01-01"]; idx = pd.DatetimeIndex(g.ts[tr])
    k = roll_rows(g, tr); roll = tr[k]
    fri = np.where(idx.dayofweek == 4)[0]
    pos_by_date = pd.Series(np.arange(len(tr)), index=idx)
    def shift_weeks(w):
        out = []
        for d in idx[k]:
            t_ = d + pd.Timedelta(days=7 * w)
            if t_ in pos_by_date.index: out.append(pos_by_date[t_])
        return tr[np.array(out)]
    other_fri = tr[np.setdiff1d(fri, k)]
    quarterly = roll[np.isin(pd.DatetimeIndex(g.ts[roll]).month, (3, 6, 9, 12))]; monthly_only = np.setdiff1d(roll, quarterly)

    res = {}
    for ex, st in itertools.product((930, 1000, 1030, 1100, 1500), (None, 0.5, 1.0)):
        res[(ex, st)] = trade(g, roll, -1, ex, st, atr)
    print("\n1. Short 8:31 on the roll day, exit x stop (pick by 2018-22 t)")
    for (ex, st), t in res.items(): print(line(t.net, f"out {ex}, stop {st if st else 'none'}"))
    sc = {kk: tstat(v.net[v.index < SPLIT]) for kk, v in res.items()}; pick = max(sc, key=sc.get); ex, st = pick
    t = res[pick]
    print(f"\n== pick: out {ex}, stop {st if st else 'none'} (2018-22 t {sc[pick]:.1f})")
    print(line(t.net, "picked")); print("   by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in t.net.groupby(t.index.year).sum().items()))
    print(f"   median ${t.net.median():.0f}; without the best 5 trades avg ${t.net.sort_values().iloc[:-5].mean():.0f}")

    print("\n2. Controls at the picked settings")
    for nm, rows, s in (("long version (same day, same exit)", roll, 1), ("Friday one week BEFORE the roll", shift_weeks(-1), -1),
                        ("Friday one week AFTER the roll", shift_weeks(1), -1), ("every other Friday", other_fri, -1),
                        ("quarterly rolls (futures expiry too)", quarterly, -1), ("non-quarterly months", monthly_only, -1),
                        ("Thursday before the roll", tr[np.clip(k - 1, 0, None)], -1)):
        print(line(trade(g, rows, s, ex, st, atr).net, nm))
    for w in (1, 2, 3):
        for ex2, st2 in ((1000, 0.5), (1100, None), (1100, 0.5), (1500, 0.5)):
            print(line(trade(g, shift_weeks(w), 1, ex2, st2, atr).net, f"LONG the Friday {w} week(s) after the roll, out {ex2}, stop {st2 if st2 else 'none'}"))
    rnd = np.random.default_rng(1); pm = []
    for _ in range(2000):
        rr = rnd.choice(other_fri, len(roll), replace=False); x = (g.c[rr, jof(ex)] - g.o[rr, jof(831)]) * -PV - COMM - 2 * TICK * PV
        pm.append(np.nanmean(x))
    print(f"   placebo: random sets of {len(roll)} other Fridays (no stop), avg ${np.mean(pm):.0f}, 95th pct ${np.percentile(pm, 95):.0f}; "
          f"share >= the roll days' no-stop result: {np.mean(np.array(pm) >= res[(ex, None)].net.mean()):.3f}")

    print("\n3. The plan's trades on roll days vs other days (net $ per NQ-equivalent trade; MultiCharts reports)")
    from time_clusters_test import trades as plan_trades
    T = plan_trades(g); rset = set(roll)
    for nm, x in T.items():
        on = x[x.day.isin(rset)]; off = x[~x.day.isin(rset) & (pd.DatetimeIndex(x.date).dayofweek == 4)]
        if len(on) >= 5: print(f"   {nm:<11} roll days n={len(on):3d} avg ${on.net.mean():6.0f} (longs ${on[on.side > 0].net.mean():6.0f}, shorts ${on[on.side < 0].net.mean():6.0f}) | other Fridays n={len(off):3d} avg ${off.net.mean():6.0f}")

    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days >= "2018-01-01"]
    dl = lambda x: x.net.groupby(x.index.normalize()).sum().reindex(days, fill_value=0.0)
    print("\n4. Metrics (short only; the long version is the control above)")
    print(M.table({"OPEX morning short": (dl(t), t.net), "  2023+": (dl(t)[days >= SPLIT], t.net[t.index >= SPLIT])}))
    b_, p_ = R.report({"OPEX morning short, 2023+": dl(t)[days >= SPLIT]}, n=3000); print(b_); print(p_)

    print("\n5. Funded bench (adds to the plan)")
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    from bridge_monday_confirm import load_bridge_mc
    lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    tt = t.reset_index(drop=True)[["day", "j0", "j1", "side", "entry", "exit", "kind"]].copy(); tt["slips"] = 0
    lab.add("OPX", tt, stop_pts=(st or 1.0) * atr, slippage=False)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    from speed_to_13k import run as speed, fmt
    sp = {}
    for nm, p in (("current plan", plan), ("+ OPEX short 1 MNQ", {**plan, "OPX": 1}), ("+ OPEX short 2 MNQ", {**plan, "OPX": 2}),
                  ("+ OPEX short 3 MNQ", {**plan, "OPX": 3}), ("+ OPEX short risk $300", {**plan, "OPX": ("risk", 300)}), ("+ OPEX short risk $500", {**plan, "OPX": ("risk", 500)})):
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<28} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
        sp[nm] = speed(lab, p, **CS)
    print(fmt(pd.DataFrame(sp).T))
    print("   daily correlation with the plan:", {kk: round(float(np.corrcoef(lab.C["OPX"], lab.C[kk])[0, 1]), 2) for kk in ("VB", "ONB_ML2_MC", "EOS", "LDF_MC")})
    pickle.dump(dict(res=res, pick=pick), open(SP + "opex_short.pkl", "wb"))
