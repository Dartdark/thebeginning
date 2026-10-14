"""ES mean-reversion families (user's focus, 2026-10-14), with NQ alongside; 2018-2026, day session, flat 15:00 CT.
Fills: signal on a 5-min bar close, enter at the next 1-min open +/- 1 tick; stops on 1-min bars (+1 tick), targets are limits
(no slip), time exit at the 15:00 close (-/+ 1 tick). Costs: ES $5, NQ $7.25 commission + the ticks. ATR = 15-day average
of full-day ranges, known before the day. Each family: the parameter with the best 2018-22 t is chosen, 2023-26 is the holdout.
  F1 VWAP band fade (9:00-14:00): |close - session VWAP| >= k ATR -> fade, target VWAP, stop k ATR beyond; k 0.3 / 0.5 / 0.7
  F2 RSI(2) on 5-min closes (8:45-14:30): < L long, > 100-L short; out at RSI crossing 50 or 6 bars, stop 0.3 ATR; L 5 / 10
  F3 morning extension: |10:30 - 8:30| >= k ATR -> fade 10:31 -> 15:00, stop at the day's extreme so far; k 0.5 / 0.75 / 1.0
  F4 opening gap fade: |8:30 - prior 15:00| >= k ATR -> fade at 8:31, target the prior close, stop one gap; k 0.2 / 0.3 / 0.5
  F5 prior-session high / low first touch 9:00-14:00 -> fade, stop s ATR, target 2s; s 0.1 / 0.15 / 0.25
  F6 IBS (prior session close in its 8:30-15:00 range): <= q long, >= 1-q short, 8:31 -> 15:00; q 0.1 / 0.2 / 0.3
Bug fixed 2026-10-14: the first run booked wrong-side stops as profits on gap days (F5 'Sharpe 6.4'); the simulator now
exits at market when a stop / target is already crossed at entry, and F5 needs price inside the prior range until 9:00.
  python3 analysis/es_mean_reversion_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import line
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPEC = {"ES": ("ge.pkl", 50.0, 0.25, 5.0), "NQ": ("g24.pkl", 20.0, 0.25, 7.25)}
J0, J1 = jof(830), jof(1500)


class Mkt:
    def __init__(self, s):
        f, self.pv, self.tick, self.comm = SPEC[s]
        g = pickle.load(open(SP + f, "rb")); self.g = g
        tr = g.trading; idx = pd.DatetimeIndex(g.ts[tr])
        ok = ~np.isnan(g.c[tr, J0:J1 + 1]).all(1) & (g.last_j[tr] >= J1)
        self.rows = tr[ok]; self.idx = idx[ok]
        self.O, self.H, self.L = (pd.DataFrame(a[self.rows]).ffill(axis=1).to_numpy() for a in (g.o, g.h, g.l))
        self.C = pd.DataFrame(g.c[self.rows]).ffill(axis=1).to_numpy(); self.V = np.nan_to_num(g.v[self.rows])
        rng = pd.Series(np.nanmax(g.h[self.rows], 1) - np.nanmin(g.l[self.rows], 1), index=self.idx)
        self.atr = rng.rolling(15).mean().shift(1).to_numpy()

    def sim(self, i, j, side, stop, target, jend=J1):
        """enter at the open of minute j; returns net $ and exit minute."""
        e = self.O[i, j] + side * self.tick
        # guard: a stop already crossed at entry (wrong side of the market) or a target already passed = out at market
        if (side > 0 and (e - self.tick <= stop or (target is not None and e >= target))) or \
           (side < 0 and (e + self.tick >= stop or (target is not None and e <= target))):
            return -2 * self.tick * self.pv - self.comm, j
        for m in range(j, jend + 1):
            if side > 0 and self.L[i, m] <= stop:
                px = (min(self.O[i, m], stop) if m > j else stop) - self.tick; return (px - e) * self.pv - self.comm, m
            if side < 0 and self.H[i, m] >= stop:
                px = (max(self.O[i, m], stop) if m > j else stop) + self.tick; return (e - px) * self.pv - self.comm, m
            if target is not None and ((side > 0 and self.H[i, m] >= target) or (side < 0 and self.L[i, m] <= target)):
                return (target - e) * side * self.pv - self.comm, m
        px = self.C[i, jend] - side * self.tick; return (px - e) * side * self.pv - self.comm, jend


def fam(M_, name, k):
    out = []; n = len(M_.idx)
    for i in range(1, n):
        a = M_.atr[i]
        if np.isnan(a) or M_.idx[i] < pd.Timestamp("2018-01-01"): continue
        C, H, L, O = M_.C[i], M_.H[i], M_.L[i], M_.O[i]
        if name == "F1":
            tp = (H + L + C) / 3; v = M_.V[i].copy(); v[:J0 + 1] = 0
            vw = np.cumsum(tp * v) / np.maximum(np.cumsum(v), 1e-9)
            for j in range(jof(900), jof(1400) + 1, 5):
                d = C[j] - vw[j]
                if abs(d) >= k * a:
                    s = -np.sign(d); out.append((M_.idx[i], *M_.sim(i, j + 1, s, C[j] - s * k * a, vw[j]))); break
        elif name == "F2":
            cl = C[J0:J1 + 1:5]; dif = np.diff(cl); up = pd.Series(np.maximum(dif, 0)).ewm(alpha=0.5).mean().to_numpy()
            dn = pd.Series(np.maximum(-dif, 0)).ewm(alpha=0.5).mean().to_numpy(); rsi = 100 - 100 / (1 + up / np.maximum(dn, 1e-9))
            b = 3; busy = -1
            while b < len(rsi):
                j = J0 + 5 * (b + 1)
                if j < jof(845) or j > jof(1430) or j <= busy: b += 1; continue
                s = 1 if rsi[b] < k else (-1 if rsi[b] > 100 - k else 0)
                if s:
                    jend = j + 30
                    for bb in range(b + 1, min(b + 7, len(rsi))):
                        if (s > 0 and rsi[bb] >= 50) or (s < 0 and rsi[bb] <= 50): jend = J0 + 5 * (bb + 1); break
                    net, mx = M_.sim(i, j + 1, s, C[j] - s * 0.3 * a, None, min(jend, J1))
                    out.append((M_.idx[i], net, mx)); busy = mx; b = (mx - J0) // 5
                b += 1
        elif name == "F3":
            mv = C[jof(1030)] - C[J0]
            if abs(mv) >= k * a:
                s = -np.sign(mv); ext = np.nanmax(H[J0:jof(1030) + 1]) if s < 0 else np.nanmin(L[J0:jof(1030) + 1])
                out.append((M_.idx[i], *M_.sim(i, jof(1031), s, ext + s * -1 * 0 + (-s) * M_.tick * 0, None)))
        elif name == "F4":
            pc = M_.C[i - 1, J1]; gap = C[J0] - pc
            if abs(gap) >= k * a:
                s = -np.sign(gap); out.append((M_.idx[i], *M_.sim(i, J0 + 1, s, C[J0] - s * abs(gap), pc)))
        elif name == "F5":
            ph, pl = np.nanmax(M_.H[i - 1, J0:J1 + 1]), np.nanmin(M_.L[i - 1, J0:J1 + 1])
            if np.nanmax(H[J0:jof(900)]) >= ph or np.nanmin(L[J0:jof(900)]) <= pl: continue   # already outside before 9:00
            for j in range(jof(900), jof(1400) + 1):
                if H[j] >= ph: out.append((M_.idx[i], *M_.sim(i, j + 1, -1, ph + k * a, ph - 2 * k * a))); break
                if L[j] <= pl: out.append((M_.idx[i], *M_.sim(i, j + 1, 1, pl - k * a, pl + 2 * k * a))); break
        elif name == "F6":
            ph, pl, pc = np.nanmax(M_.H[i - 1, J0:J1 + 1]), np.nanmin(M_.L[i - 1, J0:J1 + 1]), M_.C[i - 1, J1]
            ibs = (pc - pl) / max(ph - pl, 1e-9)
            s = 1 if ibs <= k else (-1 if ibs >= 1 - k else 0)
            if s: out.append((M_.idx[i], *M_.sim(i, J0 + 1, s, -1e12 if s > 0 else 1e12, None)))
    t = pd.DataFrame(out, columns=["d", "net", "jx"]); return pd.Series(t.net.values, index=pd.DatetimeIndex(t.d))


GRID = {"F1": (0.3, 0.5, 0.7), "F2": (5, 10), "F3": (0.5, 0.75, 1.0), "F4": (0.2, 0.3, 0.5), "F5": (0.1, 0.15, 0.25), "F6": (0.1, 0.2, 0.3)}
NAMES = {"F1": "VWAP band fade", "F2": "RSI(2) 5-min", "F3": "morning extension fade", "F4": "opening gap fade",
         "F5": "prior high/low fade", "F6": "IBS next session"}

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    best = {}
    for s in ("ES", "NQ"):
        M_ = Mkt(s); print(f"\n===== {s} =====")
        for f, ks in GRID.items():
            res = []
            for k in ks:
                x = fam(M_, f, k); d = x[x.index.year < 2023]
                res.append((d.mean() / d.std() * np.sqrt(len(d)) if len(d) > 5 else -9, k, x))
            res.sort(key=lambda r: -r[0])
            for tt, k, x in res:
                tag = "  <- design pick" if k == res[0][1] else ""
                print(line(x, f"{f} {NAMES[f]} k={k}", 40) + tag)
            best[(s, f)] = res[0][2]
    # metrics on ES design picks with holdout t >= 1
    print("\nES design picks, standard metrics (1 ES):")
    rows = {}
    for f in GRID:
        x = best[("ES", f)]; days = pd.DatetimeIndex(sorted(set(x.index))); d = x.groupby(x.index).sum()
        allD = Mkt.__dict__  # placeholder
        rows[f"{f} {NAMES[f]}"] = (d, x)
    print(M.table(rows))

    # follow-up (from es_mean_reversion_premise.py: session-to-next-session autocorrelation -0.10, ES 2023-26 -0.15):
    # fade yesterday's 8:30 -> 15:00 move, 8:31 -> 15:00, all days and only after |move| >= 0.5 / 1.0 x its 60-day sd
    print("\nfollow-up: fade yesterday's session move")
    for s in ("ES", "NQ"):
        M_ = Mkt(s); mv = pd.Series(M_.C[:, J1] - M_.C[:, J0], index=M_.idx); sd = mv.rolling(60).std().shift(1)
        x = pd.Series([M_.sim(i, J0 + 1, -np.sign(mv.iloc[i - 1]), -1e12 if mv.iloc[i - 1] < 0 else 1e12, None)[0]
                       for i in range(1, len(mv))], index=M_.idx[1:]); x = x[x.index >= "2018-01-01"]
        for th in (0, 0.5, 1.0):
            m = (mv.shift(1).abs() >= th * sd).reindex(x.index).fillna(False)
            print(line(x[m], f"{s} fade yesterday, |move| >= {th} sd", 40))
