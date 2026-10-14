"""Forced-flow round 4: the groups on the untested list (2026-10-14, user: "test everything on the list").

  A. Closing-auction (MOC) imbalances. Nasdaq / NYSE publish market-on-close imbalances from 14:50 CT and they clear
     at the 15:00 CT cash close. No imbalance data here, so price is the proxy: does the 14:00 / 14:30 -> 14:50 move
     carry into 14:50 -> 15:00 (imbalance in the same direction), and is 14:50 -> 15:00 itself followed or faded at
     15:00 -> 15:15? Trade: follow at the 14:51 open, out at the 15:00 close, when |move| >= 0 / 0.1 / 0.2 ATR.
  B. Nasdaq-100 / S&P quarterly rebalance closes (3rd Friday of Mar / Jun / Sep / Dec, 15:00 CT; 35 days) vs the
     other monthly 3rd Fridays and other Fridays: 13:00 -> 15:00, 14:00 -> 15:00, 14:50 -> 15:00, 15:00 -> 15:15, and
     direction by the quarter's NQ return (winners trimmed at the rebalance?).
  C. European close (London 16:30 local, 10:30 CT except the 3-4 DST-mismatch weeks a year when it is 11:30 CT):
     follow the 8:30 -> London-close move to 15:00 (the C-tier "morning direction at 10:30" as a trade), |move| >= 0 /
     0.25 / 0.5 ATR, stop none / 0.5 / 1.0 ATR. Natural experiment: in the mismatch weeks, is the 11:30 decision
     (London's real close) better than the 10:30 one?
  D. Following the Asian and European opens: Tokyo 9:00 JST (18:00 CST / 19:00 CDT) and London 8:00 local
     (2:00 CT, 3:00 CT in the mismatch weeks). Follow the first 15 / 30 minutes' move to +1h / +2h / 8:25 CT.
Promotion rule (many tests): |t| >= 2.5 over 2018-26 with the same sign in 2018-22 and 2023-26; a survivor gets the
full metrics, longs / shorts, bootstrap / permutation on 2023+, a placebo and the funded bench.
NQ 1 contract, $7.25 + 1 tick a fill for trades; signal studies in $ per NQ before costs.
  python3 analysis/forced_groups_round4_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from option_income_etf_test import roll_rows
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25
SPLIT = pd.Timestamp("2023-01-01")
SURV = []


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def tdiff(a, b):
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b)) if min(len(a), len(b)) > 5 else np.nan


def line(x, nm, w=64, test=True):
    x = pd.Series(x).dropna()
    if len(x) < 8: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    a, b = x[y < 2023], x[y >= 2023]; t = tstat(x)
    ok = test and abs(t) >= 2.5 and np.sign(a.mean()) == np.sign(b.mean()) == np.sign(t)
    if ok: SURV.append((nm, x))
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.0f} PF {pf:4.2f} t {t:4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():6.0f} 23-26 ${b.mean():6.0f}{'  <-- passes' if ok else ''}")


def ct_of(dates, hh, mm, tz):
    """CT clock time (hhmm) of a local hh:mm in tz on each date."""
    loc = pd.DatetimeIndex([pd.Timestamp(d.date()) + pd.Timedelta(hours=hh, minutes=mm) for d in dates]).tz_localize(tz)
    c = loc.tz_convert("America/Chicago"); return np.array(c.hour * 100 + c.minute)


class Flat:
    """Flat minute arrays (row * 1440 + j) so trades can cross midnight."""
    def __init__(self, g):
        self.o, self.h, self.l, self.c = (getattr(g, k).ravel() for k in "ohlc")
        self.cf = pd.Series(self.c).ffill().to_numpy()

    def trade(self, e_i, x_i, side, stop_pts):
        """Entry at the open of flat bar e_i (+ / - 1 tick), out at the close of x_i or at the stop. Returns net $ or nan."""
        o = self.o[e_i]
        if np.isnan(o) or side == 0: return np.nan
        e = o + side * TICK
        if stop_pts is not None and np.isfinite(stop_pts):
            sp = e - side * stop_pts
            seg = self.l[e_i:x_i + 1] if side > 0 else self.h[e_i:x_i + 1]
            hit = np.where((seg <= sp) if side > 0 else (seg >= sp))[0]
            if len(hit):
                j = e_i + hit[0]; oo = self.o[j]
                px = (sp if j == e_i or np.isnan(oo) else (min(oo, sp) if side > 0 else max(oo, sp))) - side * TICK
                return (px - e) * side * PV - COMM
        px = self.cf[x_i] - side * TICK
        return (px - e) * side * PV - COMM


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); F = Flat(g); atr_all = g.daily_atr(15)
    tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= "2018-01-01"]; idx = pd.DatetimeIndex(g.ts[tr]); D = len(tr)
    atr = atr_all[tr]; base = tr * 1440
    P = lambda t: F.cf[base + jof(t)]                                  # close of the bar ending at t, per trading row
    mv = lambda a, b: pd.Series((P(b) - P(a)) * PV, index=idx)
    fri = idx.dayofweek == 4

    # ---------------- A. MOC imbalance proxy ----------------
    print("\nA. Closing-auction (MOC) proxy, $ per NQ before costs")
    m_1450 = mv(1450, 1500); m_1515 = mv(1500, 1515)
    for a in (1400, 1430):
        s = mv(a, 1450); sg = np.sign(s)
        print(line(sg * m_1450, f"sign({a}->14:50) x (14:50->15:00)"))
        big = (s.abs() / PV) >= 0.2 * atr
        print(line((sg * m_1450)[big], f"   same, |{a}->14:50| >= 0.2 ATR"))
    print(line(np.sign(m_1450) * m_1515, "sign(14:50->15:00) x (15:00->15:15): follow the auction after the close"))
    print(line(np.sign(mv(1400, 1500)) * m_1515, "sign(14:00->15:00) x (15:00->15:15) (known post-settlement reversal)", test=False))
    print("   trade: follow the 14:30 -> 14:50 move at the 14:51 open, out 15:00 close (net)")
    s30 = mv(1430, 1450)
    for th in (0.0, 0.1, 0.2):
        net = pd.Series([F.trade(b + jof(1451), b + jof(1500), int(np.sign(v)), None) if abs(v) / PV >= th * a_ and v != 0 else np.nan
                         for b, v, a_ in zip(base, s30, atr)], index=idx)
        print(line(net, f"MOC follow 14:51 -> 15:00, |14:30->14:50| >= {th} ATR"))

    # ---------------- B. quarterly rebalance closes ----------------
    print("\nB. Quarterly rebalance closes (3rd Friday of Mar / Jun / Sep / Dec), $ per NQ before costs")
    k = roll_rows(g, tr); q = k[np.isin(idx[k].month, (3, 6, 9, 12))]; mo = np.setdiff1d(k, q); of = np.setdiff1d(np.where(fri)[0], k)
    for a, b in ((1300, 1500), (1400, 1500), (1450, 1500), (1500, 1515)):
        s = mv(a, b)
        print(line(s.iloc[q], f"{a}->{b}: quarterly 3rd Fridays", test=False) + f"\n      monthly-only {s.iloc[mo].mean():6.0f} | other Fridays {s.iloc[of].mean():6.0f} | quarterly - other Fridays t {tdiff(s.iloc[q], s.iloc[of]):.1f}")
    qret = pd.Series(P(1500), index=idx).pct_change(63)
    s = mv(1400, 1500).iloc[q]; d_ = -np.sign(qret.iloc[q])
    print(line(d_ * s, "against the quarter's NQ return, 14:00 -> 15:00 (winners trimmed?)"))
    print(line(np.sign(mv(830, 1400).iloc[q]) * s, "follow the day's 8:30 -> 14:00 move, 14:00 -> 15:00"))

    # ---------------- C. European close ----------------
    print("\nC. European close: follow 8:30 -> London close to 15:00 (net, 1 NQ)")
    lc = ct_of(idx, 16, 30, "Europe/London"); mism = lc != 1030
    print(f"   London close in CT: {pd.Series(lc).value_counts().to_dict()} (mismatch days {mism.sum()})")
    o831 = g.o[tr, jof(831)]
    res_c = {}
    for th, st in itertools.product((0.0, 0.25, 0.5), (None, 0.5, 1.0)):
        out = []
        for i in range(D):
            j = jof(int(lc[i])); dmove = F.cf[base[i] + j] - o831[i]
            if np.isnan(dmove) or abs(dmove) < th * atr[i] or dmove == 0: out.append(np.nan); continue
            out.append(F.trade(base[i] + j + 1, base[i] + jof(1500), int(np.sign(dmove)), st * atr[i] if st else None))
        res_c[(th, st)] = pd.Series(out, index=idx)
        print(line(res_c[(th, st)], f"follow from the London close, |move| >= {th} ATR, stop {st if st else 'none'}"))
    print("   natural experiment on the mismatch days (London closes at 11:30 CT): decide at 10:30 vs at 11:30, |move| >= 0.25 ATR, no stop")
    for dec in (1030, 1130):
        out = []
        for i in np.where(mism)[0]:
            dmove = F.cf[base[i] + jof(dec)] - o831[i]
            out.append(F.trade(base[i] + jof(dec) + 1, base[i] + jof(1500), int(np.sign(dmove)), None) if abs(dmove) >= 0.25 * atr[i] else np.nan)
        print(line(pd.Series(out, index=idx[mism]), f"   mismatch days, decide at {dec}", test=False))
    for dec in (1030, 1130):
        out = []
        for i in np.where(~mism)[0]:
            dmove = F.cf[base[i] + jof(dec)] - o831[i]
            out.append(F.trade(base[i] + jof(dec) + 1, base[i] + jof(1500), int(np.sign(dmove)), None) if abs(dmove) >= 0.25 * atr[i] else np.nan)
        print(line(pd.Series(out, index=idx[~mism]), f"   normal days, decide at {dec}", test=False))

    # ---------------- D. Asian / European opens ----------------
    print("\nD. Follow the Tokyo and London opens (net, 1 NQ). Tokyo = the evening before each trading day")
    ev = tr - 1                                                        # calendar row of the evening before (Sunday for Monday)
    tko = ct_of(idx, 9, 0, "Asia/Tokyo")                              # 9:00 JST on the trading date = the evening before in CT
    lno = ct_of(idx, 8, 0, "Europe/London")
    print(f"   Tokyo open in CT (evening before): {pd.Series(tko).value_counts().to_dict()}; London open in CT: {pd.Series(lno).value_counts().to_dict()}")
    for nm, opens, row_of in (("Tokyo", tko, ev), ("London", lno, tr)):
        for win, hold in itertools.product((15, 30), (60, 120, "8:25")):
            out = []
            for i in range(D):
                j0 = row_of[i] * 1440 + jof(int(opens[i]))                # bar closing at the open time
                js = j0 + win
                jx = (tr[i] * 1440 + jof(825)) if hold == "8:25" else js + hold
                s = F.cf[js] - F.cf[j0]
                out.append(F.trade(js + 1, jx, int(np.sign(s)), None) if s == s and s != 0 else np.nan)
            print(line(pd.Series(out, index=idx), f"{nm} open: follow the first {win} min, hold {hold}{' min' if hold != '8:25' else ''}"))

    print(f"\nSurvivors (|t| >= 2.5, same sign 2018-22 and 2023-26): {len(SURV)}")
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days >= "2018-01-01"]
    for nm, x in SURV:
        print(f"\n== {nm}")
        dl = x.groupby(x.index.normalize()).sum().reindex(days, fill_value=0.0)
        print(M.table({nm[:40]: (dl, x)}))
        b_, p_ = R.report({nm[:40] + ", 2023+": dl[days >= SPLIT]}, n=3000); print(b_); print(p_)
    pickle.dump(dict(surv=SURV, res_c=res_c), open(SP + "forced_round4.pkl", "wb"))
