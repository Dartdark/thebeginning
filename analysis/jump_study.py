"""5-minute jump strategy study (user upload 2026-11-11). See analysis/jump_lib.py for the scores and the papers.

trades(b, M, mask, side, ...) simulates: signal bar = a 5-min bar in `mask`; entry at the open of the next minute (market);
stop = R points against, target = tp x R in favour (limit), R = `rmode` of the signal bar; out at `hold` minutes or 15:55 CT;
one trade at a time. Costs (testing standard): $7.25 a contract + 1 tick ($5) on every market / stop fill, none on the target.
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import jump_lib as L

PT, COMM, TICK = 20.0, 7.25, 5.0


class Mkt:
    def __init__(self):
        m = L.minute(); self.m = m
        self.arr = (m.open.to_numpy(), m.high.to_numpy(), m.low.to_numpy(), m.close.to_numpy())
        self.ts = m.ts.to_numpy(); self.hm = (m.ts.dt.hour * 100 + m.ts.dt.minute).to_numpy()
        self.sess = m.sess.to_numpy()
        # last tradable minute index of each minute's session: last bar stamped <= 15:55 of that session (else last bar before a > 10-min gap)
        n = len(m); gap = np.r_[(np.diff(self.ts) > np.timedelta64(10, "m")), True]
        late = (self.hm > 1555) & (self.hm <= 1700)
        stopper = gap | np.r_[late[1:], True]            # bar i is the last before a gap or before the 15:56-17:00 zone
        idx = np.where(stopper, np.arange(n), n); self.end = np.minimum.accumulate(idx[::-1])[::-1]
        self.late = late


def rvals(b, rmode, k=1.0):
    if rmode == "rng": return (b.rng * k).to_numpy()
    if rmode == "absr": return (b.r.abs() * k).to_numpy()
    if rmode == "sig": return (b.sig * b.f * k).to_numpy()
    raise ValueError(rmode)


def trades(b, M, mask, side, rmode="rng", k=1.0, tp=0.3, hold=240, cost=True, minR=2.0, one=True, entry_ok=None):
    """side: array of +1/-1 per bar (direction to trade). Returns DataFrame of trades."""
    R = rvals(b, rmode, k); i1 = b.i1.to_numpy(); o = M.arr[0]; rows = []; busy = -1
    sd = np.asarray(side)
    for q in np.flatnonzero(np.asarray(mask)):
        e = i1[q] + 1
        if e >= len(o) - 1 or (one and e <= busy): continue
        if M.late[e] or M.ts[e] - M.ts[e - 1] > np.timedelta64(2, "m"): continue      # no entry in 15:56-17:00 or across a gap
        if entry_ok is not None and not entry_ok[e]: continue
        r = R[q]; s = int(sd[q])
        if not np.isfinite(r) or r < minR or s == 0: continue
        r = round(r * 4) / 4
        px = o[e]; iend = min(M.end[e], e + hold)
        if iend <= e: continue
        ex, why, ix = L.walk(M.arr, e, s, px - s * r, px + s * round(tp * r * 4) / 4, iend)
        gross = s * (ex - px) * PT
        c = (COMM + TICK + (0 if why == "tgt" else TICK)) if cost else 0.0
        rows.append((M.ts[e], M.sess[e], s, r, px, ex, why, gross, gross - c, (ix - e + 1), q))
        busy = ix
    return pd.DataFrame(rows, columns=["ts", "sess", "side", "R", "entry", "exit", "why", "gross", "net", "mins", "q"])


def summ(t, label=""):
    if not len(t): return f"{label:<44} no trades"
    x = t.net; g = t.gross
    pf = x[x > 0].sum() / -x[x < 0].sum() if (x < 0).any() else np.inf
    tt = x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan
    rr = (t.gross / (t.R * PT))
    return (f"{label:<44} n {len(t):5d} win {np.mean(g > 0):5.1%} tgt {np.mean(t.why == 'tgt'):5.1%} net ${x.mean():7.1f} PF {pf:4.2f} t {tt:5.2f} "
            f"avgR {rr.mean():+.3f} R$ {t.R.mean() * PT:5.0f} mins {t.mins.mean():4.0f} L/S {np.sum(t.side > 0)}/{np.sum(t.side < 0)}")


if __name__ == "__main__":
    b = L.bars(); M = Mkt()
    per = sys.argv[1] if len(sys.argv) > 1 else "design"
    yr = b.ts.dt.year
    P = ((yr >= 2018) & (yr <= 2022)) if per == "design" else (yr >= 2023) if per == "holdout" else (yr >= 2018)
    print(f"period {per}: {b.ts[P].min()} .. {b.ts[P].max()}   (breakeven win at 0.3R before costs = 76.9%)")
    sgn = np.sign(b.r).fillna(0).to_numpy()
    rth = ((b.hhmm > 830) & (b.hhmm <= 1500)).to_numpy()
    for score in ("J", "s"):
        z = b[score].abs().to_numpy() if score == "J" else b.s.to_numpy()
        for thr in (3, 4, 5, 6, 8):
            for nm, d in (("follow", sgn), ("fade", -sgn)):
                for rm in ("rng", "sig"):
                    kk = 1.0 if rm == "rng" else 4.0
                    for sn, sm in (("all", np.ones(len(b), bool)), ("rth", rth), ("on", ~rth)):
                        t = trades(b, M, P.to_numpy() & (z > thr) & sm, d, rm, kk)
                        print(summ(t, f"{score}>{thr} {nm} R={rm} {sn}"))
