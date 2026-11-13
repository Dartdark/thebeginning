"""Pivot Continuation port (user 2026-11-10: '6J Pivot Continuation' research note, 'see if this can be improved'). PRE-REGISTERED
(header committed before the first run). No 6J data here (export on TODO), so the frozen rules go to every market we hold - the
note's own question: does Twin's core idea, trading through confirmed swings, work elsewhere?
Rules exactly as the note: 60-minute candles anchored to the hour (17:00 Globex), skipping empty hours; a swing low is strictly lower
than the 3 candles on each side, confirmed when the 3rd right candle closes; the newest confirmed swing low is support. While flat,
a sell stop at support, entries 17:00-10:00 CT; the first touch consumes the level whether or not it is traded; stop = the latest
confirmed swing high, frozen at entry (no trade if it is not above the fill); out at the 15:30 CT close (next available bar on
short sessions); one position at a time, 1 contract. LONG mirror: buy stop at the latest swing high, stop = latest swing low.
1-minute bars (the note used 5-minute: stop fills here are finer). Fill = level, or the bar's open if it gaps through; costs
$5 a round trip ($7.25 NQ) + 1 tick per fill (entry, exit) - stricter than the note's $10: 6J would be $5 + 2 x $6.25 = $17.50.
ITEMS: 8 markets (NQ ES YM GC CL NG 6E ZN) x 2 sides = 16, bar t_threshold(16), and positive in BOTH the note's development
(2018-23) and holdout (2024+). Context: 2018-22 / 2023+. Any pass: placebo with comparable NON-pivot levels (the note's open item:
at each confirmation the level is a random other candle's low / high among the 6 before and 3 after the swing, 200 runs), the
standard test, the data sweep and an ingredient breakdown (swing strength, pivot timeframe, window, stop, exit, 2x ATR target).
  tools/run_stamped.sh analysis/pivot_continuation_test.py > analysis/outputs/pivot_continuation_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from metrics import t_threshold

SP = "scratch_data/"
MK = {"NQ": ("g24", 20.0, 0.25, 7.25), "ES": ("ge", 50.0, 0.25, 5.0), "YM": ("gy", 5.0, 1.0, 5.0), "GC": ("gc", 100.0, 0.1, 5.0),
      "CL": ("cl", 1000.0, 0.01, 5.0), "NG": ("ng", 10000.0, 0.001, 5.0), "6E": ("e6", 125000.0, 0.00005, 5.0), "ZN": ("zn", 1000.0, 0.015625, 5.0)}


class Flat:
    def __init__(self, g):
        self.O, self.H, self.L, self.C = (getattr(g, k).ravel() for k in "ohlc")
        self.ts0 = pd.Timestamp(g.ts[0]); self.N = len(self.C)
        self.valid = np.isfinite(self.C); v = np.nonzero(self.valid)[0]; ix = np.searchsorted(v, np.arange(self.N))
        self.nxt = np.where(ix < len(v), v[np.minimum(ix, len(v) - 1)], self.N)        # first bar with data at or after t

    def candles(self, k=60):
        """k-minute candles: bucket b holds the bars closing at minutes b*k+1 .. b*k+k (MultiCharts close stamps)."""
        n = (self.N - 1) // k; sl = slice(1, 1 + n * k)
        with np.errstate(all="ignore"):
            h = np.nanmax(self.H[sl].reshape(n, k), 1); l = np.nanmin(self.L[sl].reshape(n, k), 1)
        ok = np.isfinite(h); end = (np.arange(n) + 1) * k
        return h[ok], l[ok], end[ok]


def swings(h, l, end, s=3, rng=None):
    """Confirmed swing highs / lows: (avail minute, price) in time order."""
    n = len(h); hi, lo = [], []
    for i in range(s, n - s):
        win_h, win_l = np.r_[h[i - s:i], h[i + 1:i + s + 1]], np.r_[l[i - s:i], l[i + 1:i + s + 1]]
        av = end[i + s] + 1
        if h[i] > win_h.max():
            hi.append((av, h[i] if rng is None else h[max(0, i - 6) + rng.choice([j for j in range(min(i, 6) + s + 1) if j != min(i, 6)])]))
        if l[i] < win_l.min():
            lo.append((av, l[i] if rng is None else l[max(0, i - 6) + rng.choice([j for j in range(min(i, 6) + s + 1) if j != min(i, 6)])]))
    return np.array(hi), np.array(lo)


def run(F, side, hi, lo, pv, tick, comm, win=(1021, 600), exit_hm=930, target_atr=None, atr15=None):
    """side -1: sell stop at the latest swing low, stop at the latest swing high; +1 mirror. Returns trades DataFrame."""
    lev, opp = (lo, hi) if side < 0 else (hi, lo)
    if not len(lev) or not len(opp): return pd.DataFrame(columns=["entry", "net", "side"])
    out = []; busy_until = -1
    for k in range(len(lev)):
        a, p = int(lev[k, 0]), lev[k, 1]; b = int(lev[k + 1, 0]) if k + 1 < len(lev) else F.N
        seg = F.L[a:b] if side < 0 else F.H[a:b]
        hit = np.nonzero((seg <= p) if side < 0 else (seg >= p))[0]
        if not len(hit): continue
        m = a + hit[0]; col = m % 1440
        if m <= busy_until or not (col >= win[0] or col <= win[1]): continue
        j = np.searchsorted(opp[:, 0], m, side="right") - 1
        if j < 0: continue
        sp = opp[j, 1]; o = F.O[m]
        e = (min(o, p) if side < 0 else max(o, p)) if np.isfinite(o) else p
        if (side < 0 and sp <= e) or (side > 0 and sp >= e): continue
        e_fill = (min(o, p) if side < 0 else max(o, p)) if np.isfinite(o) else p
        e_fill = e_fill - tick if side < 0 else e_fill + tick
        row = m // 1440; xt = row * 1440 + exit_hm
        if col > exit_hm: xt += 1440
        xt = F.nxt[min(xt, F.N - 1)]
        if xt >= F.N or xt - m > 4 * 1440: continue
        tp = None
        if target_atr is not None:
            r = atr15[m]
            if np.isfinite(r): tp = e_fill + side * target_atr * r
        px = None
        for t in range(m + 1, xt + 1):
            if not F.valid[t]: continue
            if (side < 0 and F.H[t] >= sp) or (side > 0 and F.L[t] <= sp):
                px = (max(F.O[t], sp) + tick) if side < 0 else (min(F.O[t], sp) - tick); break
            if tp is not None and ((side < 0 and F.L[t] <= tp) or (side > 0 and F.H[t] >= tp)):
                px = tp if not ((side < 0 and F.O[t] < tp) or (side > 0 and F.O[t] > tp)) else F.O[t]; break
        if px is None: px = F.C[xt] - side * tick; t = xt
        out.append((F.ts0 + pd.Timedelta(minutes=int(m)), side * (px - e_fill) * pv - comm, side)); busy_until = t
    return pd.DataFrame(out, columns=["entry", "net", "side"])


def tt(x): return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def show(x, d, nm, bar=None):
    if len(x) < 10: return f"   {nm:<30} n={len(x)}"
    x = pd.Series(x.values, index=pd.DatetimeIndex(d)); y = x.index.year; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    dev, ho = x[y <= 2023], x[y >= 2024]; t = tt(x)
    flag = "  PASS" if bar is not None and t >= bar and dev.mean() > 0 and ho.mean() > 0 else ""
    return (f"   {nm:<30} n {len(x):4d} ${x.mean():6.1f} PF {pf:4.2f} t {t:5.2f} win {np.mean(x > 0):.0%} | 2018-23 ${dev.mean():6.1f} (t {tt(dev):4.1f})"
            f" 2024+ ${ho.mean():6.1f} (t {tt(ho):4.1f}) | 18-22 ${x[y <= 2022].mean():6.1f} 23+ ${x[y >= 2023].mean():6.1f} | yrs+ {(x.groupby(y).sum() > 0).sum()}/{y.nunique()}{flag}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); bar = t_threshold(16); print(f"   items 16, bar t >= {bar:.2f}; both 2018-23 and 2024+ positive")
    R = {}
    for nm, (pk, pv, tick, comm) in MK.items():
        g = pickle.load(open(SP + pk + ".pkl", "rb")); F = Flat(g); h, l, end = F.candles(60); hi, lo = swings(h, l, end)
        for side, sn in ((-1, "short"), (1, "long")):
            T = run(F, side, hi, lo, pv, tick, comm); T = T[T.entry >= "2018-01-01"]; R[(nm, sn)] = T
            print(show(T.net, T.entry, f"{nm} {sn}", bar), flush=True)
        del g, F
    pd.concat({f"{a}_{b}": t for (a, b), t in R.items()}).to_csv("analysis/outputs/pivot_continuation_trades.csv")
