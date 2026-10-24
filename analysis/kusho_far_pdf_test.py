"""Kusho 'Finished Auction Retest' v0.9 (the PDF the user posted 2026-10-24, checks/candidates/kusho_far/; the author's
forum write-up with the full code). Differences from the FAR final tested 2026-10-23 (analysis/kusho_test.py):
  - the PDF's wick test 'Low <= Open + TickSize' is always true: NO wick filter (strict = wick <= 1 tick);
  - break-even at 1.5R (FAR final 0.5R);
  - chart time zone UTC+2: entries 09:00-13:59 and the 21:00 flatten are UTC+2 times (= ~02:00-06:59 entries and a
    14:00 CT flatten), not Central times. Readings: fixed UTC+2, Europe/Berlin, and Central (the 10-23 reading).
Rebuild = analysis/kusho_test.py's engine (minute-by-minute fills, limit 1 tick through, $7.25 + 1 tick per stop / market
fill, roll jumps removed) with the times, break-even and wick rule as parameters. Author: Apr 2020 - Aug 2026, 2,066 trades,
50% win, PF 1.34, $171 a trade ($5 commission + 1 tick).
  python3 analysis/kusho_far_pdf_test.py SCRATCH_DIR
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from kusho_test import Data, TICK, PV, COST, line
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def chart_hhmm(D, tz):
    ts = pd.DatetimeIndex(D.g.ts[D.row]) + pd.to_timedelta(D.e % 1440, unit="m")
    loc = ts.tz_localize("America/Chicago", ambiguous="NaT", nonexistent="shift_forward").tz_convert(tz)
    return np.nan_to_num(np.asarray(loc.hour * 100 + loc.minute, float), nan=-1).astype(int)


def run(D, mode="FAR", conv="ours", rand_p=None, seed=1, wick_on=True, ema_on=True, flat_rth=False,
        start=900, end=1345, eod=2100, be_r=0.5, wick_ticks=70, HH=None):
    HH = D.hhmm if HH is None else HH
    o, h, l, c = D.o, D.h, D.l, D.c
    th_e = 0.25 if conv == "ours" else 0.0; th_t = 1.0 if conv == "ours" else 0.0
    shorts = mode in ("v9", "C03"); c03 = mode == "C03"
    rng = np.random.default_rng(seed); out = []; n = len(D.C)
    pos = 0; armed = None
    for k in range(60, n):
        e1 = D.e[k]; m0 = e1 - 14
        # ---- 1. pending limit for this bar ----
        if armed is not None and pos == 0:
            side, lim, sk, atr_s = armed; armed = None
            if D.e[k] - D.e[k - 1] == 15:
                for m in range(m0, e1 + 1):
                    if not np.isfinite(o[m]): continue
                    if (c03 or flat_rth) and D.td[k] in D.early and m > D.early[D.td[k]]: break
                    if (side > 0 and l[m] <= lim - th_e) or (side < 0 and h[m] >= lim + th_e):
                        fill = min(o[m], lim) if side > 0 else max(o[m], lim)
                        pos = side; ent = fill; fm = m; kf = k; be_done = False; eod_pending = False
                        if c03:
                            sw = (D.L[sk - 9:sk].min() if side > 0 else D.H[sk - 9:sk].max()) + D.cum[sk]
                            Rr = (fill - sw) * side
                            if 0 < Rr <= 3 * atr_s: stop, tgt, swing = sw, fill + side * 3 * Rr, True
                            else: stop, tgt, swing, Rr = fill - side * atr_s, fill + side * atr_s, False, atr_s
                            beoff = np.round(0.05 * atr_s / TICK) * TICK
                            mfe = 0.0
                        else:
                            stop, tgt, swing, Rr = fill - side * 50.0, fill + side * 50.0, False, 50.0
                            for L_ in range(2, 11):
                                a, b_, cc = (D.L if side > 0 else -D.H)[[k - L_, k - L_ + 1, k - L_ - 1]]
                                if a < b_ and a < cc:
                                    sw = (D.L[k - L_] if side > 0 else D.H[k - L_]) + D.cum[k]; rk = (fill - sw) * side / TICK
                                    if rk <= 500: stop, tgt, swing, Rr = sw, fill + side * (fill - sw) * side * 3, True, (fill - sw) * side
                                    break
                        break
        # ---- 2. open position: exits during this bar (from the bar after the fill bar) ----
        exit_px = None
        if pos != 0 and k > kf:
            for m in range(m0, e1 + 1):
                if not np.isfinite(o[m]): continue
                if eod_pending:
                    exit_px, kind, xm = o[m] - pos * TICK, "eod", m; break
                hit_s = (l[m] <= stop) if pos > 0 else (h[m] >= stop)
                hit_t = (h[m] >= tgt + th_t) if pos > 0 else (l[m] <= tgt - th_t)
                if hit_s or hit_t:
                    if hit_s and (not hit_t or (o[m] <= stop if pos > 0 else o[m] >= stop) or not ((o[m] >= tgt) if pos > 0 else (o[m] <= tgt))):
                        px = min(o[m], stop) if pos > 0 else max(o[m], stop); exit_px, kind, xm = px - pos * TICK, "stop", m
                    else:
                        px = max(o[m], tgt) if pos > 0 else min(o[m], tgt); exit_px, kind, xm = px, "target", m
                    break
                if c03: mfe = max(mfe, (h[m] - ent) if pos > 0 else (ent - l[m]))
                if c03 or flat_rth:
                    t_ = D.td[k]; mm = m % 1440; hm = (mm // 60) * 100 + mm % 60
                    flat_m = D.early.get(t_, None)
                    if (flat_m is not None and m >= flat_m) or (flat_m is None and hm >= 1545 and D.hhmm[k] <= 1600):
                        exit_px, kind, xm = c[m] - pos * TICK, "flat", m; break
        if pos != 0 and k == kf and c03:
            for m in range(fm + 1, e1 + 1):
                if np.isfinite(h[m]): mfe = max(mfe, (h[m] - ent) if pos > 0 else (ent - l[m]))
        if pos != 0 and k == kf and (c03 or flat_rth) and D.td[k] in D.early and e1 >= D.early[D.td[k]]:
            xm = D.early[D.td[k]]; exit_px, kind = c[xm] - pos * TICK, "flat"     # filled in a half-day's last bar: out at the close
        if exit_px is not None:
            gross = (exit_px - ent) * pos
            for j in D.rolls[(D.rolls > fm) & (D.rolls <= xm)]:
                p = j - 1
                while not np.isfinite(c[p]): p -= 1
                gross -= (c[j] - c[p]) * pos
            out.append(dict(date=pd.Timestamp(D.g.ts[fm // 1440]), exit_date=pd.Timestamp(D.g.ts[xm // 1440]), side=pos, entry=ent,
                            exit=exit_px, kind=kind, swing=swing, fm=fm, xm=xm, net=gross * PV - COST))
            pos = 0
        # ---- 3. bar close: break-even, EOD flag, new signal ----
        if pos != 0:
            if k == kf: eod_pending = False
            if swing and not be_done:
                fav = (mfe if c03 else ((D.H[k] + D.cum[k] - ent) if pos > 0 else (ent - D.L[k] - D.cum[k])))
                if fav >= be_r * Rr:
                    stop = ent + pos * (beoff if c03 else 5 * TICK); be_done = True
            if not c03 and not flat_rth and HH[k] >= eod: eod_pending = True
            continue
        hm = HH[k]
        if not (start <= hm <= end) or not np.isfinite(D.atr[k]): continue
        t_ = D.td[k]
        if (c03 or flat_rth) and t_ in D.early and D.e[k] >= D.early[t_]: continue
        tol = 0.5 * D.atr[k] if c03 else wick_ticks * TICK
        dn = shorts and t_ < len(D.down) and D.down[t_]
        if rand_p is not None:
            if rng.random() < rand_p:
                sd = int(rng.choice([-1, 1])) if shorts else 1
                armed = (sd, D.O[k] + D.cum[k], k, D.atr[k])
            continue
        if D.C[k] > D.O[k] and (D.C[k] > D.ema[k] or not ema_on) and ((D.O[k] - D.L[k]) <= tol or not wick_on):
            armed = (1, D.O[k] + D.cum[k], k, D.atr[k])
        elif dn and D.C[k] < D.O[k] and (D.C[k] < D.ema[k] or not ema_on) and ((D.H[k] - D.O[k]) <= tol or not wick_on):
            armed = (-1, D.O[k] + D.cum[k], k, D.atr[k])
    t = pd.DataFrame(out)
    wk = t.exit_date.dt.dayofweek
    t["weekend"] = wk >= 5
    t["exit_date"] = t.exit_date + pd.to_timedelta(np.where(wk == 6, 1, np.where(wk == 5, 2, 0)), unit="D")   # Sunday-evening exits book on Monday
    return t[t.date >= "2018-01-01"].reset_index(drop=True)




if __name__ == "__main__" and "--central" not in sys.argv:
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); D = Data(g, adjust=True)
    Hu, Hb = chart_hhmm(D, "Etc/GMT-2"), chart_hhmm(D, "Europe/Berlin")
    pdf = dict(start=900, end=1359, eod=2100, be_r=1.5, wick_on=False)
    rows = [("PDF code, chart UTC+2 (main reading)", dict(HH=Hu, **pdf)),
            ("PDF code, chart Europe/Berlin", dict(HH=Hb, **pdf)),
            ("PDF code, chart Central (10-23 reading)", dict(**pdf)),
            ("UTC+2, strict no-wick (<= 1 tick)", dict(HH=Hu, **{**pdf, "wick_on": True}, wick_ticks=1)),
            ("UTC+2, wick <= 70 ticks (FAR final)", dict(HH=Hu, **{**pdf, "wick_on": True}, wick_ticks=70)),
            ("UTC+2, break-even 0.5R", dict(HH=Hu, **{**pdf, "be_r": 0.5})),
            ("UTC+2, no EMA filter", dict(HH=Hu, **{**pdf, "ema_on": False}))]
    print("\nPer NQ after costs, 2018-2026 (author's span Apr 2020 -> Aug 2026 shown separately):")
    res = {}
    for nm, kw in rows:
        t = run(D, "FAR", "ours", **kw); res[nm] = t
        print(line(t, nm))
    t = res["PDF code, chart UTC+2 (main reading)"]
    a = t[(t.date >= "2020-04-01") & (t.date <= "2026-08-31")]
    print(line(a, "UTC+2, author's span 2020-04 -> 2026-08"))
    print(line(a[a.date < "2023-01-01"], "   2020-04 -> 2022 (author's OOS)")); print(line(a[a.date >= "2023-01-01"], "   2023 -> (author's IS)"))
    print("   by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   exits:", t.kind.value_counts().to_dict(), "| entry hours CT:", pd.Series(t.fm % 1440 // 60).value_counts().sort_index().to_dict())
    pl = [run(D, "FAR", "ours", rand_p=len(t) / 21000, seed=s, HH=Hu, **pdf).net.mean() for s in range(5)]
    print(f"   placebo (random signal bars, same window, order and exits; 5 runs): ${np.mean(pl):.0f} (max ${max(pl):.0f}) vs ${t.net.mean():.0f}")
    t.to_csv("checks/candidates/kusho_far/python_trades_pdf_utc2.csv", index=False)


def central_checks(D):
    """Added after the first run: the Central reading matches the author (trades a year, win rate), so the follow-ups use it."""
    pdf = dict(start=900, end=1359, eod=2100, be_r=1.5, wick_on=False)
    t = run(D, "FAR", "ours", **pdf)
    print("\nCentral reading (matches the author's trade count / win rate):")
    print(line(t, "PDF code, Central")); print(line(t[~t.weekend], "  without weekend holds"))
    print(line(run(D, "FAR", "ours", **{**pdf, "wick_on": True}, wick_ticks=1), "  strict no-wick (<= 1 tick)"))
    f = run(D, "FAR", "ours", flat_rth=True, **pdf); print(line(f, "  flat 15:45 (Apex-shaped)"))
    v9 = pd.read_csv("checks/candidates/kusho/python_trades_v9_rolladj.csv", parse_dates=["date", "exit_date"])
    a = t.groupby("exit_date").net.sum(); b = v9.groupby("exit_date").net.sum(); idx = a.index.union(b.index)
    print(f"   daily corr with Kusho v9 21:00 (in the personal plan): {np.corrcoef(a.reindex(idx, fill_value=0), b.reindex(idx, fill_value=0))[0, 1]:+.2f}; "
          f"same entry minutes {len(set(t.fm) & set(v9.fm[v9.side > 0]))} of {len(t)}")
    t.to_csv("checks/candidates/kusho_far/python_trades_pdf_central.csv", index=False)
    return t, f


if __name__ == "__main__" and "--central" in sys.argv:
    g = pickle.load(open(SP + "g24.pkl", "rb")); central_checks(Data(g, adjust=True))
