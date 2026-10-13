"""RSI + EMA + rolling VWAP pullback (Rule-Based Trader, "We Combined RSI, EMA, and VWAP on QQQ",
2 Oct 2026), tested on NQ 2018-2026 (2026-10-13).

Article: long QQQ when a fast RSI is oversold, a long EMA is rising and the close is well below the
10-day rolling volume-weighted price; buy the next open, hold until short-term momentum recovers
(avg 3.6 days), no stop. QQQ 1999-2026: 215 trades, PF 3.54, 79.5% win; 2018-2026: 67 trades, PF 2.66
(before costs). Exact RSI period / level, EMA length, discount and exit are not given, so a small
grid around the usual choices is shown, not one fitted version.

Daily bars from the 1-minute NQ grid: close = 15:00 CT (the cash close), high / low / volume of
8:30-15:00. Base spec: RSI(2) < 10, EMA(200) above its value 5 days ago, close < 10-day VWAP x (1 - 2%),
exit at the 15:00 close when RSI(2) > 70 (or after 10 days).

Executions (per NQ after $7.25 + 1 tick per market fill, per round trip):
  HOLD   the article's trade: buy the next 8:30 open, sell the 15:00 close of the exit day, held
         overnight (NOT allowed on Apex: positions must be flat by 15:59 CT).
  RTH    Apex-legal, day session only: each day of the holding window, 8:30 open -> 15:00 close.
  NIGHT  Apex-legal, re-enter overnight: buy at midnight CT after the signal, each day sell at 15:55
         (15:00 on the exit day) and buy again at the next midnight. Gap: 15:55-24:00.
  EVE    like NIGHT but re-entering at the 17:00 CT reopen (gap 15:55-17:00 only); reported only, the
         funded bench can't hold a position across calendar dates.
  python3 analysis/qqq_rsi_ema_vwap_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle, itertools; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25
RT = COST + 2 * TICK * PV


def rsi(c, n):
    d = np.diff(c, prepend=np.nan)
    up = pd.Series(np.where(d > 0, d, 0.0)).ewm(alpha=1 / n, adjust=False).mean()
    dn = pd.Series(np.where(d < 0, -d, 0.0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn.replace(0, np.nan))).fillna(100).to_numpy()


def daily(g):
    tr = g.trading
    a, b = jof(831), jof(1500)
    C = pd.Series(g.c[tr, b]).ffill().to_numpy()
    with np.errstate(all="ignore"):
        Hh = np.nanmax(g.h[tr, a:b + 1], 1); Ll = np.nanmin(g.l[tr, a:b + 1], 1)
    V = np.nansum(g.v[tr, a:b + 1], 1)
    return tr, pd.DatetimeIndex(g.ts[tr]), C, Hh, Ll, V


def signals(C, Hh, Ll, V, rsi_n=2, rsi_lo=10.0, ema_n=200, disc=0.02, use_ema=True, use_vwap=True,
            exit_rsi=70.0, max_hold=10):
    """List of (signal index i, exit index x): signal at the close of day i, exit at the close of x."""
    R_ = rsi(C, rsi_n)
    ema = pd.Series(C).ewm(span=ema_n, adjust=False).mean().to_numpy()
    rising = ema > np.r_[np.full(5, np.nan), ema[:-5]]
    tp = (Hh + Ll + C) / 3
    vw = pd.Series(tp * V).rolling(10).sum() / pd.Series(V).rolling(10).sum()
    vw = vw.to_numpy()
    out = []; i = 210
    while i < len(C) - 1:
        ok = R_[i] < rsi_lo
        if use_ema: ok &= bool(rising[i])
        if use_vwap: ok &= C[i] < vw[i] * (1 - disc)
        if ok:
            x = i + 1
            while x < len(C) - 1 and R_[x] <= exit_rsi and x - i < max_hold: x += 1
            out.append((i, x)); i = x + 1          # no overlapping positions
        else:
            i += 1
    return out


def legs(g, tr, sig, mode):
    """Trade rows (one per position for HOLD / EVE, one per day otherwise) for the funded bench."""
    rows = []; ts = pd.DatetimeIndex(g.ts)
    for i, x in sig:
        d0, dx = tr[i + 1], tr[x]
        if ts[d0].year < 2018: continue
        if mode == "HOLD":
            e, px = g.o[d0, 511], g.c[dx, 900]
            if np.isnan(e) or np.isnan(px): continue
            rows.append(dict(day=d0, j0=511, j1=900, side=1, entry=e + TICK, exit=px - TICK, kind=0, slips=0,
                             net=(px - e - 2 * TICK) * PV - COST, date=ts[d0], days=x - i))
            continue
        if mode == "EVE":
            # 17:00 open of the signal day's evening -> 15:55 next day, repeated; last leg out 15:00
            pnl = 0.0; ok = True
            for k in range(i, x):
                de, dn = tr[k], tr[k + 1]
                e = g.o[de, jof(1701)] if not np.isnan(g.o[de, jof(1701)]) else np.nan
                if np.isnan(e):                     # weekend / holiday: re-enter at the Sunday reopen row
                    sun = dn - 1
                    e = g.o[sun, jof(1701)]
                j_out = jof(1500) if k + 1 == x else jof(1555)
                px = g.c[dn, j_out]
                if np.isnan(e) or np.isnan(px): ok = False; break
                pnl += (px - e - 2 * TICK) * PV - COST
            if ok: rows.append(dict(date=ts[d0], net=pnl, side=1, days=x - i, day=d0))
            continue
        for k in range(i + 1, x + 1):
            d = tr[k]
            j_in = 511 if mode == "RTH" else 1
            j_out = 900 if (mode == "RTH" or k == x) else jof(1555)
            e, px = g.o[d, j_in], g.c[d, j_out]
            if np.isnan(e) or np.isnan(px): continue
            rows.append(dict(day=d, j0=j_in, j1=j_out, side=1, entry=e + TICK, exit=px - TICK, kind=0, slips=0,
                             net=(px - e - 2 * TICK) * PV - COST, date=ts[d], pos=i))
    return pd.DataFrame(rows)


def per_position(t, mode):
    if mode in ("HOLD", "EVE"): return t
    return t.groupby("pos").agg(net=("net", "sum"), date=("date", "first")).reset_index()


def line(t, name, w=58):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); h = x[y >= 2023]
    pf = lambda s: s[s > 0].sum() / max(1e-9, -s[s < 0].sum())
    tt = x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 1 else np.nan
    return (f"{name:<{w}} n={len(x):3d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f} t={tt:4.1f}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 23+ n={len(h)} ${h.mean():5.0f} PF {pf(h):.2f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    tr, dts, C, Hh, Ll, V = daily(g)
    print(__doc__.split("\n")[0])
    print(f"\nDaily bars {dts[0].date()} .. {dts[-1].date()}; signals need 210 days of history (trading from late 2018)")

    print("\n1. The article's filter comparison (base spec), per NQ, per position:")
    for nm, ue, uv in (("RSI only", False, False), ("RSI + EMA", True, False), ("RSI + VWAP", False, True),
                       ("RSI + EMA + VWAP", True, True)):
        s = signals(C, Hh, Ll, V, use_ema=ue, use_vwap=uv)
        for mode in ("HOLD", "RTH", "NIGHT", "EVE"):
            t = per_position(legs(g, tr, s, mode), mode)
            print(line(t, f"{nm:<17} {mode}"))
    print("   (QQQ 2018-2026 in the article: 67 trades, 76.1% win, PF 2.66, before costs)")

    print("\n2. Neighbouring specs (RSI + EMA + VWAP), HOLD and NIGHT:")
    for (rn, lo), ema_n, disc, ex in itertools.product(((2, 5), (2, 10), (2, 15), (3, 20)), (100, 200),
                                                       (0.0, 0.02, 0.03), (50, 70)):
        s = signals(C, Hh, Ll, V, rn, lo, ema_n, disc, exit_rsi=ex)
        if len(s) < 8: continue
        a = per_position(legs(g, tr, s, "HOLD"), "HOLD"); b = per_position(legs(g, tr, s, "NIGHT"), "NIGHT")
        pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
        print(f"  RSI({rn})<{lo:<2} EMA{ema_n} disc {disc:.0%} exit RSI>{ex}: n={len(a):3d}"
              f" HOLD avg ${a.net.mean():5.0f} PF {pf(a.net):.2f} | NIGHT avg ${b.net.mean():5.0f} PF {pf(b.net):.2f}")

    # base spec in detail
    s = signals(C, Hh, Ll, V)
    print(f"\n3. Base spec in detail: {len(s)} positions, average hold {np.mean([x - i for i, x in s]):.1f} days")
    hold = per_position(legs(g, tr, s, "HOLD"), "HOLD")
    print("   HOLD by year:", hold.groupby(hold.date.dt.year).net.sum().round(0).astype(int).to_dict())
    night_legs = legs(g, tr, s, "NIGHT"); night = per_position(night_legs, "NIGHT")
    print("   NIGHT by year:", night.groupby(night.date.dt.year).net.sum().round(0).astype(int).to_dict())

    # placebo: random signal days with a rising EMA, same hold lengths
    ema = pd.Series(C).ewm(span=200, adjust=False).mean().to_numpy()
    rising = np.where(ema > np.r_[np.full(5, np.nan), ema[:-5]])[0]
    rising = rising[(rising >= 210) & (rising < len(C) - 12)]
    hl = [x - i for i, x in s]; rng = np.random.default_rng(5); pl_h, pl_n = [], []
    for r in range(200):
        days_ = np.sort(rng.choice(rising, len(s), replace=False))
        ps = [(i, min(i + rng.choice(hl), len(C) - 2)) for i in days_]
        pl_h.append(per_position(legs(g, tr, ps, "HOLD"), "HOLD").net.mean())
        pl_n.append(per_position(legs(g, tr, ps, "NIGHT"), "NIGHT").net.mean())
    print(f"   placebo (random rising-EMA days, same hold lengths, 200 runs): HOLD real ${hold.net.mean():.0f} vs"
          f" ${np.mean(pl_h):.0f} (95% ${np.percentile(pl_h, 95):.0f}); NIGHT real ${night.net.mean():.0f} vs"
          f" ${np.mean(pl_n):.0f} (95% ${np.percentile(pl_n, 95):.0f})")

    # standard metrics and funded bench for the Apex-legal NIGHT version
    days = dts[dts.year >= 2018]; D2 = days[days.year >= 2023]
    dl = lambda t, ix: t.groupby(t.date.dt.normalize()).net.sum().reindex(ix, fill_value=0.0)
    hd = hold.assign(date=hold.date)
    print("\n4. Standard metrics per NQ (daily P&L; HOLD booked on the entry day):")
    print(M.table({"HOLD (not Apex-legal)": (dl(hd, days), hd.net), "NIGHT (Apex-legal)": (dl(night_legs, days), night.net),
                   "NIGHT 2023-26": (dl(night_legs, D2), night.net[night.date.dt.year >= 2023])}))
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    lab.add("RSIV", night_legs, slippage=False)
    dts2 = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts2.year >= 2018
    P = {k: pd.Series(lab.daily(k), index=dts2)[mk] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "RSIV")}
    print("   correlation with the plan:", pd.DataFrame(P).corr().round(2).loc["RSIV"].to_dict())
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2}
    CS = dict(fmin=0.5, fmax=1.0, ref=2000.0)
    for nm, p in (("current plan", plan), ("+ RSI/EMA/VWAP NIGHT 1 MNQ", {**plan, "RSIV": 1}),
                  ("+ RSI/EMA/VWAP NIGHT 2 MNQ", {**plan, "RSIV": 2})):
        a = lab.score(p, 250, **CS); b = lab.score(p, 500, **CS)
        print(f"   {nm:<28} 1y ${a['expected']:,.0f} 2y ${b['expected']:,.0f} blown {a['blown']:.0%} / {b['blown']:.0%}")
    Bt, Pm = R.report({"NIGHT 2023-26": dl(night_legs, D2), "NIGHT 2018-26": dl(night_legs, days)}, n=5000)
    print(Bt); print(Pm)

    print("\n5. RSI only (the strongest NQ variant), Apex-legal NIGHT: placebo and funded bench")
    s1 = signals(C, Hh, Ll, V, use_ema=False, use_vwap=False)
    n1_legs = legs(g, tr, s1, "NIGHT"); n1 = per_position(n1_legs, "NIGHT")
    hl1 = [x - i for i, x in s1]; allix = np.arange(210, len(C) - 12); pl = []
    for r in range(200):
        days_ = np.sort(rng.choice(allix, len(s1), replace=False))
        pl.append(per_position(legs(g, tr, [(i, min(i + rng.choice(hl1), len(C) - 2)) for i in days_], "NIGHT"), "NIGHT").net.mean())
    print(f"   real ${n1.net.mean():.0f} per position vs random days with the same hold lengths ${np.mean(pl):.0f}"
          f" (95% ${np.percentile(pl, 95):.0f}); real beats {np.mean(n1.net.mean() > np.array(pl)):.0%}")
    print("   by year:", n1.groupby(n1.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print(M.table({"RSI only NIGHT": (dl(n1_legs, days), n1.net), "  2023-26": (dl(n1_legs, D2), n1.net[n1.date.dt.year >= 2023])}))
    lab.add("RSI1", n1_legs, slippage=False)
    for nm, p in (("+ RSI-only NIGHT 1 MNQ", {**plan, "RSI1": 1}), ("+ RSI-only NIGHT 2 MNQ", {**plan, "RSI1": 2})):
        a = lab.score(p, 250, **CS); b = lab.score(p, 500, **CS)
        print(f"   {nm:<28} 1y ${a['expected']:,.0f} 2y ${b['expected']:,.0f} blown {a['blown']:.0%} / {b['blown']:.0%}")
    print("   note: EVE rows are incomplete (positions with a missing 17:00 bar are dropped), so they are not used")
