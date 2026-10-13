"""The Bridge's L644NQ_MondayLong_NQ vs our Monday Long (funded_strategies/NQ_Monday_Long.txt), 2026-10-13.

Bridge rules (manual section 8.6; code not seen): buy the close of Sunday's 19:00 CT bar when the previous
daily bar's ADX(7) is between 10 and 50 and DI+ > DI-; target 100 points; no stop; out Monday 15:55 CT; skips
Monday closures and early closes. Daily bars here = CME sessions (17:00 CT -> 16:00 CT), Wilder ADX / DI(7);
"previous daily bar" before Sunday 19:00 = Friday's session.
Ours: Monday 8:30 CT open -> close of the 15:00 bar, stop 0.5 x 15-day ATR (MultiCharts trade list).
Per NQ after $7.25 + 1 tick per market fill (the target is a limit: no slippage). The Sunday 19:00 entry is
booked on Monday's row (Apex counts Sunday evening as Monday's trading day); the bench's worst-point path
starts at Monday 00:00, so Sunday 19:00-24:00 dips are not in it.
  python3 analysis/bridge_monday_long_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
from funded_lab import with_slippage
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25
MON_FILE = "Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx"


def sessions(g):
    """CME session bars for each trading row d: previous calendar row from 17:00 + row d up to 16:00."""
    out = []
    for d in g.trading:
        h = np.r_[g.h[d - 1, jof(1700):], g.h[d, :jof(1600) + 1]]
        l = np.r_[g.l[d - 1, jof(1700):], g.l[d, :jof(1600) + 1]]
        c = np.r_[g.c[d - 1, jof(1700):], g.c[d, :jof(1600) + 1]]
        ok = ~np.isnan(c)
        if ok.sum() < 30: out.append((d, np.nan, np.nan, np.nan)); continue
        out.append((d, np.nanmax(h), np.nanmin(l), c[ok][-1]))
    return pd.DataFrame(out, columns=["d", "h", "l", "c"]).dropna().reset_index(drop=True)


def adx(S, n=7):
    h, l, c = S.h.to_numpy(), S.l.to_numpy(), S.c.to_numpy()
    pc = np.r_[np.nan, c[:-1]]
    tr = np.nanmax(np.c_[h - l, np.abs(h - pc), np.abs(l - pc)], 1)
    up, dn = np.r_[np.nan, np.diff(h)], -np.r_[np.nan, np.diff(l)]
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    w = lambda x: pd.Series(x).ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    atr = w(tr); pdi = 100 * w(pdm) / atr; mdi = 100 * w(mdm) / atr
    dx = 100 * np.abs(pdi - mdi) / np.maximum(pdi + mdi, 1e-9)
    return pd.DataFrame({"d": S.d, "adx": w(dx), "pdi": pdi, "mdi": mdi})


def bridge(g, A, weekday=0, filt=True, target=100.0, entry_t=1900, exit_t=1555, rth_only=False):
    """Trades for a given weekday (0 = Monday): enter at the close of the previous evening's entry_t bar."""
    ts = pd.DatetimeIndex(g.ts); tr = set(g.trading); rows = []
    prev_ind = dict(zip(A.d, zip(A.adx, A.pdi, A.mdi)))
    trading = list(g.trading)
    for k, d in enumerate(trading):
        if ts[d].dayofweek != weekday or ts[d].year < 2018: continue
        if g.last_j[d] < jof(1500) or np.isnan(g.c[d, jof(1455)]): continue      # early close / missing
        # the last completed session before the previous evening = the trading row before d
        p = trading[k - 1]
        if p not in prev_ind: continue
        a, pdi, mdi = prev_ind[p]
        sig = (10 <= a <= 50) and pdi > mdi
        if filt and not sig: continue
        if rth_only:
            e_row, e_j = d, jof(830)
        else:
            e_row, e_j = d - 1, jof(entry_t)
        e = g.c[e_row, e_j]
        if np.isnan(e): continue
        e += TICK
        tgt = e + target if target else None
        # walk: rest of the entry row, then row d up to exit_t
        px, kind, j1 = None, 2, jof(exit_t)
        segs = ([(e_row, e_j + 1, 1439)] if e_row != d else []) + [(d, (e_j + 1 if e_row == d else 0), jof(exit_t))]
        for rr, ja, jb in segs:
            for j in range(ja, jb + 1):
                if tgt is not None and not np.isnan(g.h[rr, j]) and g.h[rr, j] >= tgt:
                    px = max(g.o[rr, j], tgt) if j > ja or rr != e_row else tgt; kind = 1; j1 = j if rr == d else 0; break
            if px is not None: break
        if px is None:
            cc = g.c[d, :jof(exit_t) + 1]; ok = np.flatnonzero(~np.isnan(cc)); px = cc[ok[-1]] - TICK
        rows.append(dict(day=d, j0=0 if e_row != d else e_j + 1, j1=j1, side=1, entry=e, exit=px, kind=kind,
                         slips=0, date=ts[d], sig=sig, net=(px - e) * PV - COST,
                         ovn=(g.c[d, jof(830)] - e) * PV if e_row != d else np.nan))
    return pd.DataFrame(rows)


def stat(t, nm, w=52):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    if len(x) < 3: return f"{nm:<{w}} n={len(x)}"
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    a, b = x[y < 2023], x[y >= 2023]
    return (f"{nm:<{w}} n={len(x):3d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf:.2f} t={x.mean() / x.std() * np.sqrt(len(x)):4.1f}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${a.mean():5.0f} | 23-26 ${b.mean():5.0f} | worst ${x.min():,.0f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    print(__doc__.split("\n")[0])
    A = adx(sessions(g))
    br = bridge(g, A)
    ours = with_slippage(load_mc(g, MON_FILE)); ours["net"] = (ours.exit - ours.entry) * ours.side * PV - COST
    ours = ours[ours.date >= "2018-01-01"].reset_index(drop=True)

    print("\n1. As specified, and ours (per NQ):")
    print(stat(br, "Bridge: Sun 19:00 -> Mon 15:55, ADX(7) 10-50 & DI+>DI-, 100-pt target"))
    print(stat(ours, "ours (MultiCharts): Mon 8:30 -> 15:00, stop 0.5 ATR"))
    print(f"   Bridge: target hit {np.mean(br.kind == 1):.0%}; days traded {len(br)} of "
          f"{len(bridge(g, A, filt=False))} Mondays; overnight part (Sun 19:00 -> Mon 8:30) ${br.ovn.mean():.0f} a trade")
    for nm, t in (("Bridge", br), ("ours", ours)):
        print(f"   {nm} by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())

    print("\n2. Which part does the work?")
    nf = bridge(g, A, filt=False)
    print(stat(nf, "Bridge without the ADX filter"))
    print(stat(nf[~nf.sig], "  the Mondays the filter skips"))
    print(stat(bridge(g, A, target=None), "Bridge, no target (hold to 15:55)"))
    print(stat(bridge(g, A, exit_t=1500), "Bridge, out at 15:00"))
    ov = bridge(g, A, exit_t=830, target=None)
    print(stat(ov, "overnight part only (Sun 19:00 -> Mon 8:30, filtered)"))
    sig_days = set(br.date)
    print(stat(ours[ours.date.isin(sig_days)], "ours on the Bridge-filter Mondays"))
    print(stat(ours[~ours.date.isin(sig_days)], "ours on the other Mondays"))

    print("\n3. Placebo: the same rule on other weekdays (previous evening 19:00 -> 15:55, ADX filter, target):")
    for wd, nm in ((1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday")):
        print(stat(bridge(g, A, weekday=wd), f"   {nm}"))

    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print("\n4. Standard metrics per NQ (long-only strategies, so longs = all):")
    rows = {"Bridge Monday Long": (dl(br), br.net), "ours": (dl(ours), ours.net), "Bridge, no filter": (dl(nf), nf.net)}
    print(M.table(rows))
    h = {f"{k} 2023+": v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}
    b, p = R.report(h, n=3000); print(b); print(p)
    print(f"   daily correlation Bridge vs ours: {np.corrcoef(dl(br), dl(ours))[0, 1]:.2f}")

    print("\n5. Funded bench (Apex 50K PA, cushion sizing from $1,500), current plan with each Monday version:")
    lab = pickle.load(open(SP + "lab.pkl", "rb")); atr = g.daily_atr(15)
    lab.add("MON_BR", br, slippage=False)
    lab.add("MON_BR_NF", nf, slippage=False)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "VCS_MC": 1}
    base = {k: v for k, v in plan.items() if k != "MON_MC"}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    for nm, pl in (("current plan (ours 1 MNQ)", plan), ("Bridge 1 MNQ instead of ours", {**base, "MON_BR": 1}),
                   ("Bridge 2 MNQ instead of ours", {**base, "MON_BR": 2}), ("ours + Bridge 1 MNQ", {**plan, "MON_BR": 1}),
                   ("no Monday strategy", base)):
        a, c = lab.score(pl, 250, **CS), lab.score(pl, 500, **CS)
        print(f"   {nm:<32} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
    print("   controls (is it just more Monday size?):")
    for nm, pl in (("ours 2 MNQ", {**base, "MON_MC": 2}), ("ours + Bridge no-filter 1 MNQ", {**plan, "MON_BR_NF": 1}),
                   ("Bridge no-filter 1 MNQ instead of ours", {**base, "MON_BR_NF": 1})):
        a, c = lab.score(pl, 250, **CS), lab.score(pl, 500, **CS)
        print(f"   {nm:<38} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
    both = pd.concat([ours.assign(net=ours.net), br]).groupby("date").net.sum()
    print(f"   ours + Bridge per NQ each, daily: Sharpe {M.perf(dl(pd.DataFrame({'date': both.index, 'net': both.values})))['sharpe']:.2f}"
          f" (ours alone {M.perf(dl(ours))['sharpe']:.2f}, Bridge alone {M.perf(dl(br))['sharpe']:.2f})")
