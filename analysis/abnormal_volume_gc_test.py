"""Abnormal trading volume on gold (user's 3 MultiCharts files + slides, 2026-10-24; Bajo 2010, SSRN 675587; the NQ test
was analysis/abnormal_volume_test.py, F). Daily GC sessions from our 1-minute bars (17:00 -> 16:00 CT, the MC daily bar):
  NAV 'excl'  = AbnormalVolumeStrategy.txt / the paper: ln(1 + vol) vs mean / sd of the previous 66 days (current excluded)
  NAV 'incl'  = The_Abnormal_Trading v1 / v2: Average / StandardDev(.., 1) of ln(1 + vol) over 66 days INCLUDING today
Rules (one GC, entry at the next session's 17:00 open, exit at its 15:59 CT close = MC 'next bar at market' +
SetExitOnClose, flat before the Apex 15:59 limit):
  A. AbnormalVolumeStrategy: event day NAV > 2.33 and close-to-close move > 1% -> follow it next session; 30-day
     cool-down (any event resets it); VolFilter 0 (no volume filter) / 1 (high) / 2 (low) / 3 (high or low); fade.
  B. v1 as coded: at a session's close it checks NAV[1] and (C - O) / O [1] of the PREVIOUS session and buys / sells
     the next bar -> the trade is two sessions after the event ('lag 2'); 'lag 1' = what the comments intend.
     Paper settings 66 / 2.33 / 1%; the slides' tuned settings 160 / 1.5 / 0.3% (in-sample 2019-23, out 2024+).
  C. v2 = B + size floor($500 / (2 x ATR14 x point value)), at least 1 contract (GC and MGC).
Costs $7.25 per GC round trip + 1 tick ($10) per market fill. Sessions with a contract roll inside are dropped.
  python3 analysis/abnormal_volume_gc_test.py > analysis/outputs/abnormal_volume_gc_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
sys.argv = [sys.argv[0], "scratch_data/"]
import s_rank_gap_round2_test as SG
import metrics as M, resampling as R, montecarlo as MC

PV, TICK, COMM = 100.0, 0.10, 7.25
NTRIAL = {"n": 0}


def sessions():
    S = SG.Sym("GC"); out, _ = SG.rolls_gc(S); S.set_rolls(out); g = S.g
    V = g.v.ravel(); ok = np.where(~np.isnan(S.C))[0]; row, j = ok // 1440, ok % 1440
    sid = row + (j > 960)
    u, st = np.unique(sid, return_index=True); en = np.r_[st[1:], len(ok)]
    D = pd.DataFrame(dict(sid=u, a=ok[st], b=ok[en - 1]))
    D["o"] = S.O[ok[st]]; D["c"] = S.C[ok[en - 1]]
    D["h"] = np.maximum.reduceat(S.H[ok], st); D["l"] = np.minimum.reduceat(S.L[ok], st)
    D["v"] = np.add.reduceat(np.nan_to_num(V[ok]), st)
    x1559 = u * 1440 + 959; has = ~np.isnan(S.C[np.clip(x1559, 0, S.N - 1)])
    D["x"] = np.where(has, S.C[np.clip(x1559, 0, S.N - 1)], D.c)
    D["roll"] = S.has_roll(D.a.values, D.b.values)
    D["date"] = pd.DatetimeIndex(S.TS[np.clip(u, 0, len(S.TS) - 1)])
    D = D[(D.date.dt.dayofweek < 5) & (D.v > 0)].reset_index(drop=True)
    pc = D.c.shift(1); tr = np.maximum(D.h, pc) - np.minimum(D.l, pc); D["atr"] = tr.rolling(14).mean()
    return D


def nav(D, look=66, mode="excl"):
    lv = np.log(D.v + 1)
    if mode == "excl":
        m = lv.shift(1).rolling(look).mean(); s = lv.shift(1).rolling(look).std()
    else:
        m = lv.rolling(look).mean(); s = lv.rolling(look).std()
    return (lv - m) / s


def trades_from(D, side, lag=1, qty=None):
    """side[i] = +1 / -1 decided at session i's close; trade session i + lag (open -> 15:59)."""
    idx = np.where(side != 0)[0]; idx = idx[idx + lag < len(D)]
    t = D.iloc[idx + lag].copy(); t["side"] = side[idx]; t["ev"] = D.date.values[idx]
    t["q"] = 1.0 if qty is None else qty[idx]
    t["gross"] = (t.x - t.o) * t.side * PV * t.q
    t["net"] = t.gross - (COMM + 2 * TICK * PV) * t.q
    t = t[~t.roll]
    return t.set_index("date")


def rule_A(D, filt=1, thr=2.33, look=66, minr=0.01, cool=30, rev=False, longs=True, shorts=True):
    n = nav(D, look, "excl").values; r = (D.c / D.c.shift(1) - 1).values
    side = np.zeros(len(D)); last = -1000; pos_day = -1
    for i in range(len(D)):
        if np.isnan(n[i]): continue
        hi, lo = n[i] > thr, n[i] < -thr
        ev = True if filt == 0 else hi if filt == 1 else lo if filt == 2 else (hi or lo)
        if ev:
            if i - last > cool:
                b, s = r[i] > minr, r[i] < -minr
                if rev: b, s = s, b
                if b and longs: side[i] = 1
                elif s and shorts: side[i] = -1
            last = i
    return side


def rule_B(D, look=66, thr=2.33, minr=0.01):
    n = nav(D, look, "incl").values; er = ((D.c - D.o) / D.o).values
    return np.where(n > thr, np.where(er > minr, 1, np.where(er < -minr, -1, 0)), 0)


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(t, nm, w=52, count=True, start="2018-01-01"):
    if count: NTRIAL["n"] += 1
    t = t[t.index >= start]
    if len(t) < 5: return f"   {nm:<{w}} n={len(t)}"
    x = t.net; y = t.index.year; by = x.groupby(y).sum(); a, b = x[y < 2024], x[y >= 2024]
    L, S_ = x[t.side > 0], x[t.side < 0]
    return (f"   {nm:<{w}} n={len(x):4d} ${x.mean():5.0f} PF {pf(x):4.2f} t {tst(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | <24 ${a.mean():5.0f} t {tst(a):4.1f} | 24+ n {len(b)} ${b.mean():5.0f} t {tst(b):4.1f} | L {len(L)} ${L.mean() if len(L) else 0:4.0f} S {len(S_)} ${S_.mean() if len(S_) else 0:4.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    D = sessions(); print(f"GC sessions {len(D)} ({D.date.iloc[0].date()} -> {D.date.iloc[-1].date()}), roll sessions dropped {int(D.roll.sum())}")
    every = trades_from(D, np.ones(len(D))); print(f"   every session long, open -> 15:59: ${every[every.index >= '2018'].net.mean():.0f} a day (gold's drift + costs)")

    print("\nA. AbnormalVolumeStrategy.txt (paper NAV, close-to-close > 1%, 30-day cool-down), per GC, 2018-26:")
    A1 = trades_from(D, rule_A(D)); print(line(A1, "VolFilter 1 = high volume (paper)"))
    for f, nm in ((0, "VolFilter 0 = no volume filter (cool-down 0)"), (2, "VolFilter 2 = low volume"), (3, "VolFilter 3 = high or low")):
        print(line(trades_from(D, rule_A(D, filt=f, cool=0 if f == 0 else 30)), nm))
    print(line(trades_from(D, rule_A(D, cool=0)), "VolFilter 1, no cool-down"))
    print(line(trades_from(D, rule_A(D, thr=1.64, cool=0)), "VolFilter 1, NAV 1.64, no cool-down"))
    print(line(trades_from(D, rule_A(D, rev=True, cool=0)), "VolFilter 1 faded, no cool-down"))

    print("\nB. The_Abnormal_Trading v1 (NAV incl. today, (C - O) / O), per GC:")
    cases = {"paper 66 / 2.33 / 1%, as coded (lag 2)": (dict(), 2), "paper 66 / 2.33 / 1%, lag 1 (intended)": (dict(), 1),
             "slides 160 / 1.5 / 0.3%, as coded (lag 2)": (dict(look=160, thr=1.5, minr=0.003), 2),
             "slides 160 / 1.5 / 0.3%, lag 1": (dict(look=160, thr=1.5, minr=0.003), 1)}
    keep = {}
    for nm, (kw, lag) in cases.items():
        keep[nm] = t = trades_from(D, rule_B(D, **kw), lag=lag); print(line(t, nm))
    tb = keep["slides 160 / 1.5 / 0.3%, as coded (lag 2)"]
    print(line(tb, "slides, as coded, 2019-01 -> 2023-12 (their in-sample)", count=False, start="2019-01-01").replace("<24", "<24") if False else "", end="")
    ins = tb[(tb.index >= "2019-01-01") & (tb.index < "2024-01-01")]; oos = tb[tb.index >= "2024-01-01"]
    print(f"   slides as coded, their in-sample 2019-23: n {len(ins)} ${ins.net.mean():.0f} PF {pf(ins.net):.2f} t {tst(ins.net):.1f} "
          f"(slides: 273 trades, PF 1.33 at 1 contract); out of sample 2024+: n {len(oos)} ${oos.net.mean():.0f} PF {pf(oos.net):.2f} t {tst(oos.net):.1f}")
    print("   by year (slides, as coded):", tb.groupby(tb.index.year).net.sum().round(0).astype(int).to_dict())
    print("   neighbours of the tuned point (as coded):")
    for lk in (66, 120, 160, 200):
        for th in (1.0, 1.5, 2.0):
            for mr in (0.003, 0.005):
                t = trades_from(D, rule_B(D, look=lk, thr=th, minr=mr), lag=2); NTRIAL["n"] += 1
                t = t[t.index >= "2018"]
                print(f"      look {lk:3d} NAV {th} move {mr:.1%}: n {len(t):3d} ${t.net.mean():5.0f} t {tst(t.net):4.1f}", end="\n" if mr == 0.005 else " |")

    print("\n   placebos for the slides' rule (as coded): random side on the same sessions, 500 seeds; all sessions with a > 0.3% "
          "(C-O)/O move two sessions earlier (no volume)")
    rng = np.random.default_rng(1); tb18 = tb[tb.index >= "2018"]
    m = np.array([(tb18.net.values * 0 + ((tb18.x - tb18.o) * rng.choice([-1, 1], len(tb18)) * PV - COMM - 2 * TICK * PV)).mean() for _ in range(500)])
    print(f"      random side: ${m.mean():.0f} (95th pct ${np.percentile(m, 95):.0f}); rule ${tb18.net.mean():.0f} beats {np.mean(m < tb18.net.mean()):.0%}")
    er = ((D.c - D.o) / D.o).values; mom = np.where(er > 0.003, 1, np.where(er < -0.003, -1, 0))
    print(line(trades_from(D, mom, lag=2), "      no volume filter, same move rule, lag 2"))

    print("\nC. v2 sizing ($500 per 2 x ATR14, min 1), slides' settings, as coded:")
    for nm, pv in (("GC", 100.0), ("MGC", 10.0)):
        q = np.maximum(np.floor(500 / (D.atr.values * 2 * pv)), 1); q = np.nan_to_num(q, nan=1.0)
        side = rule_B(D, look=160, thr=1.5, minr=0.003); t = trades_from(D, side, lag=2, qty=q)
        if nm == "MGC": t["net"] = t.gross / 10 - (COMM / 10 + 2 * TICK * 10) * t.q; t["gross"] = t.gross / 10
        t = t[t.index >= "2018"]
        print(f"   {nm}: n {len(t)}, contracts median {t.q.median():.0f} max {t.q.max():.0f}; ${t.net.sum():,.0f} total, ${t.net.mean():.0f} a trade, "
              f"PF {pf(t.net):.2f}, t {tst(t.net):.1f}; 2024+ ${t[t.index >= '2024'].net.sum():,.0f}")

    print("\nD. Metrics per GC (daily), the best two lines:")
    days = pd.DatetimeIndex(D.date[D.date >= "2018-01-01"])
    rows = {}
    for nm, t in (("paper A", A1), ("slides as coded", tb)):
        dd = t.net.groupby(level=0).sum().reindex(days, fill_value=0.0)
        for per, s in (("2018-26", "2018-01-01"), ("2023+", "2023-01-01")):
            rows[f"{nm} {per}"] = (dd[dd.index >= s], t[t.index >= s].net)
    print(M.table(rows))
    dd = tb.net.groupby(level=0).sum().reindex(days, fill_value=0.0)
    print(MC.report(tb[tb.index >= "2018"].net.values, daily=dd.values, size=0.1, label="slides as coded 1 MGC"))
    print(f"\n   trials {NTRIAL['n']}; t threshold {M.t_threshold(NTRIAL['n']):.2f}; deflated Sharpe (slides as coded) "
          f"{M.deflated_sharpe(dd.values, NTRIAL['n']):.2f}")
