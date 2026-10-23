"""Kusho FAR final, Kusho v9 and C03 (Kusho's intraday version), user's files 2026-10-23 (checks/candidates/kusho/).
User: 'assume the reports agree, test them' -> rebuilt from the code on our NQ 24-hour 1-minute grid (Dec 2017 onward),
fills and exits walked minute by minute (= MultiCharts' 1-minute Bar Magnifier / 1-minute chart).
  FAR  15-min bar stamped 09:00-13:45: C > O, C > EMA50 (15-min closes), lower wick <= 70 ticks -> buy limit at its open,
       next bar only; at the fill bar's close: stop at the latest fractal swing low of bars 2-10 back if risk <= 500 ticks
       (target 3R, break-even +5 ticks once the bar's HIGH reaches +0.5R, checked at 15-min closes from the fill bar),
       else 200-tick stop / target; exits work from the bar after the fill bar; market exit at the next bar after the first
       bar stamped >= 21:00 (holds through 16-17:00 and weekends). One position. Swing risk <= 0 is accepted (as coded).
  v9   FAR + mirrored shorts on DOWN days (prior session's 15:00 close < SMA of the last 50 15:00 closes, SMA falling vs
       5 sessions earlier).
  C03  same family in ATR units, flat 15:45 / early close: wick <= 0.5 x ATR15 (Wilder 20, 15-min); R = fill - lowest low
       of the 9 bars before the signal bar; 0 < R <= 3 ATR -> swing stop, 3R target, break-even fill + 0.05 ATR once the
       post-fill-minute favourable excursion >= 0.5R (15-min closes); else stop / target 1 ATR; shorts on DOWN days.
Fill conventions: 'ours' = entry limit needs 1 tick through, targets 1 point through (repo standard); 'touch' = the C03
header's MultiCharts setting (limits fill on touch). Costs $7.25 per NQ + 1 tick per stop / market fill. Trades held
across a contract switch in our continuous series have that jump removed (as the author's roll correction does).
Half-day limits armed after the close are dropped (Codex: they could fill at the evening reopen as coded).
  python3 analysis/kusho_test.py SCRATCH_DIR
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R, montecarlo as MC
from overnight_round import roll_minutes

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25


class Data:
    def __init__(self, g):
        self.g = g; self.o, self.h, self.l, self.c = (getattr(g, x).ravel() for x in ("o", "h", "l", "c"))
        B = g.bars(15); bc = B["c"].ravel(); keep = np.flatnonzero(np.isfinite(bc))
        self.e = keep * 15                                                        # flat index of each bar's last minute
        self.O, self.H, self.L, self.C = (B[x].ravel()[keep] for x in ("o", "h", "l", "c"))
        self.row = self.e // 1440; col = self.e % 1440; self.hhmm = (col // 60) * 100 + col % 60
        n = len(self.C); a = 2 / 51; ema = np.empty(n); ema[0] = self.C[0]
        for i in range(1, n): ema[i] = ema[i - 1] + a * (self.C[i] - ema[i - 1])
        self.ema = ema
        pc = np.r_[self.C[0], self.C[:-1]]; tr = np.maximum(self.H - self.L, np.maximum(abs(self.H - pc), abs(self.L - pc)))
        atr = np.full(n, np.nan); atr[19] = tr[:20].mean()
        for i in range(20, n): atr[i] = atr[i - 1] + (tr[i] - atr[i - 1]) / 20
        self.atr = atr
        trd = g.trading
        self.td = np.searchsorted(trd, self.row + (self.hhmm > 1600), side="left")   # trading-date index of each bar
        # DOWN regime per trading date (prior session's 15:00 close vs SMA50 of 15:00 closes, SMA falling vs 5 sessions back)
        c15 = np.full(len(trd), np.nan); m = self.hhmm == 1500
        ok = m & (self.td < len(trd)); c15[self.td[ok]] = self.C[ok]
        has = np.isfinite(c15); vals = c15[has]; sma_at = np.full(len(trd), np.nan)
        cs = np.cumsum(vals); pos = np.cumsum(has) - 1                             # index into vals of the last stored close
        for t in range(len(trd)):
            k = pos[t]
            if k >= 49: sma_at[t] = (cs[k] - (cs[k - 50] if k >= 50 else 0)) / 50
        down = np.zeros(len(trd), bool)
        for t in range(6, len(trd)):
            p, q = t - 1, t - 6
            if has[p] and np.isfinite(sma_at[p]) and np.isfinite(sma_at[q]): down[t] = c15[p] < sma_at[p] and sma_at[p] < sma_at[q]
        self.down = down
        # scheduled close per trading row: early close if RTH bars exist but none 13:00-15:00 (flat at the last bar before 13:00)
        self.early = {}
        for t, r in enumerate(trd):
            day = g.c[r]
            if np.isfinite(day[8 * 60 + 31:11 * 60]).any() and not np.isfinite(day[13 * 60:15 * 60 + 1]).any():
                last = np.flatnonzero(np.isfinite(day[:13 * 60]))[-1]; self.early[t] = r * 1440 + last
        self.rolls = np.sort(roll_minutes(g, "NQ"))


def run(D, mode="FAR", conv="ours", rand_p=None, seed=1, wick_on=True, ema_on=True, flat_rth=False):
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
                            sw = D.L[sk - 9:sk].min() if side > 0 else D.H[sk - 9:sk].max()
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
                                    sw = D.L[k - L_] if side > 0 else D.H[k - L_]; rk = (fill - sw) * side / TICK
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
                fav = (mfe if c03 else ((D.H[k] - ent) if pos > 0 else (ent - D.L[k])))
                if fav >= 0.5 * Rr:
                    stop = ent + pos * (beoff if c03 else 5 * TICK); be_done = True
            if not c03 and not flat_rth and D.hhmm[k] >= 2100: eod_pending = True
            continue
        hm = D.hhmm[k]
        if not (900 <= hm <= 1345) or not np.isfinite(D.atr[k]): continue
        t_ = D.td[k]
        if (c03 or flat_rth) and t_ in D.early and D.e[k] >= D.early[t_]: continue
        tol = 0.5 * D.atr[k] if c03 else 70 * TICK
        dn = shorts and t_ < len(D.down) and D.down[t_]
        if rand_p is not None:
            if rng.random() < rand_p:
                sd = int(rng.choice([-1, 1])) if shorts else 1
                armed = (sd, D.O[k], k, D.atr[k])
            continue
        if D.C[k] > D.O[k] and (D.C[k] > D.ema[k] or not ema_on) and ((D.O[k] - D.L[k]) <= tol or not wick_on):
            armed = (1, D.O[k], k, D.atr[k])
        elif dn and D.C[k] < D.O[k] and (D.C[k] < D.ema[k] or not ema_on) and ((D.H[k] - D.O[k]) <= tol or not wick_on):
            armed = (-1, D.O[k], k, D.atr[k])
    t = pd.DataFrame(out)
    wk = t.exit_date.dt.dayofweek
    t["weekend"] = wk >= 5
    t["exit_date"] = t.exit_date + pd.to_timedelta(np.where(wk == 6, 1, np.where(wk == 5, 2, 0)), unit="D")   # Sunday-evening exits book on Monday
    return t[t.date >= "2018-01-01"].reset_index(drop=True)


def line(t, nm):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / -x[x < 0].sum()
    a, b = x[y < 2023], x[y >= 2023]; ta = lambda q: q.mean() / q.std() * np.sqrt(len(q))
    return (f"   {nm:<34} n={len(x):5d} win {np.mean(x > 0):.0%} ${x.mean():5.0f} PF {pf:.2f} t {ta(x):4.1f} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():4.0f} (t {ta(a):.1f}) | 23+ ${b.mean():4.0f} (t {ta(b):.1f})")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); D = Data(g)
    res = {}
    for mode in ("FAR", "v9", "C03"):
        print(f"\n== {mode} ==")
        for conv in ("ours", "touch"):
            t = run(D, mode, conv); res[(mode, conv)] = t
            print(line(t, f"{mode}, fills {conv}"))
            if conv == "ours":
                print(line(t[t.side > 0], "  longs")); 
                if (t.side < 0).any(): print(line(t[t.side < 0], "  shorts"))
                print("   by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
                print("   exits:", t.kind.value_counts().to_dict(), f"| swing {t.swing.mean():.0%} | held overnight {np.mean(t.exit_date > t.date):.0%}"
                      f" | per MNQ ${t.net.mean() / 10:.2f}, {len(t) / ((t.date.max() - pd.Timestamp('2018-01-01')).days / 365.25):.0f} a year")
                w = t[t.weekend]
                print(f"   held over a weekend: {len(w)} trades, ${w.net.sum():,.0f} of ${t.net.sum():,.0f} ({w.net.sum() / t.net.sum():.0%}); "
                      f"the other {len(t) - len(w)} trades ${t.net[~t.weekend].mean():.0f} each")
                top = t.net.sort_values(ascending=False); k10 = int(0.1 * len(t))
                print(f"   tail: best 10% ${top.iloc[:k10].sum():,.0f}, rest ${top.iloc[k10:].sum():,.0f}")
        t = res[(mode, "ours")]
        pr = [run(D, mode, "ours", rand_p=len(t) / 21000, seed=s) for s in range(5)]
        pl = [x.net.mean() for x in pr]
        print(f"   placebo (random signal bars in the window, same limit order / exits, 5 runs, ~{np.mean([len(x) for x in pr]):.0f} trades): "
              f"${np.mean(pl):.0f} (max ${max(pl):.0f}) vs ${t.net.mean():.0f}")
        print(line(run(D, mode, "ours", wick_on=False), "  no wick condition"))
        print(line(run(D, mode, "ours", ema_on=False), "  no EMA condition"))
    print("\n== Apex-shaped Kusho: v9 / FAR flat at 15:45 (early closes at the scheduled close), everything else as coded ==")
    for mode in ("FAR", "v9"):
        t = run(D, mode, "ours", flat_rth=True); res[(mode + "_RTH", "ours")] = t
        print(line(t, f"{mode} flat 15:45")); print(line(t[t.side > 0], "  longs"))
        if (t.side < 0).any(): print(line(t[t.side < 0], "  shorts"))
        print("   by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict(), "| exits:", t.kind.value_counts().to_dict())
    for mode in ("FAR", "v9", "C03", "v9_RTH"):
        t = res[(mode, "ours")]; alld = pd.bdate_range("2018-01-01", t.exit_date.max())
        dl = lambda q: q.groupby(q.exit_date).net.sum().reindex(alld, fill_value=0.0)
        print(f"\n{mode}: standard metrics per NQ (our fills)")
        rows = {mode: (dl(t), t.net), "longs": (dl(t[t.side > 0]), t.net[t.side > 0])}
        if (t.side < 0).any(): rows["shorts"] = (dl(t[t.side < 0]), t.net[t.side < 0])
        print(M.table(rows))
        bt, pm = R.report({f"{k} 2023+": v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}, n=2000); print(bt)
        print(MC.report(t.net, dl(t), size=0.1, label="1 MNQ"))
        t.to_csv(f"checks/candidates/kusho/python_trades_{mode}.csv", index=False)
