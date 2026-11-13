"""Drift-burst fade + order-flow turn (user 2026-11-12, combination 1; PRE-REGISTERED: checks/candidates/drift_burst/PREREG.md, committed
bcd8989 before any return). Christensen, Oomen & Reno, 'The drift burst hypothesis' (arXiv 2601.08974) + Cont, Kukanov & Stoikov,
'The price impact of order book events' (arXiv 1011.6402).
Sections: (1) the statistic on 1-minute bars (null distribution, event counts per market); (2) the paper's LOOK-AHEAD measure on our
data (reversal from the after-the-fact peak) vs what is left at the first crossing / at the confirmed turn; (3) the pre-registered
trades A / B / C by period, year, side; (4) random-time placebo; (5) longer exits (information).
  tools/run_stamped.sh analysis/drift_burst_test.py > analysis/outputs/drift_burst_test_output.txt
"""
import sys, glob, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from numba import njit
from overnight_round import roll_minutes
import jump_lib as L

SPEC = {"GC": (100.0, 0.10, 5.0, "scratch_data/gc.pkl"), "CL": (1000.0, 0.01, 5.0, "scratch_data/cl.pkl"),
        "ES": (50.0, 0.25, 5.0, "scratch_data/ge.pkl"), "NQ": (20.0, 0.25, 7.25, "scratch_data/g24.pkl")}
H, HV, C, REARM, DROP, CONF_WIN, HOLD = 5.0, 25.0, 4.5, 2.0, 1.0, 15, 5


def minutes(sym):
    if sym == "NQ":
        m = L.minute()[["ts", "open", "high", "low", "close", "volume"]].copy()
    else:
        d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"data/{sym}_1min_20*.csv"))], ignore_index=True).drop_duplicates(["date", "time"])
        d["ts"] = pd.to_datetime(d.date.astype(str), format="%Y%m%d") + pd.to_timedelta(d.time // 100 * 60 + d.time % 100, unit="m")
        m = d.sort_values("ts").reset_index(drop=True)[["ts", "open", "high", "low", "close", "volume"]]
    g = pickle.load(open(SPEC[sym][3], "rb")); rl = roll_minutes(g, sym)
    rts = (pd.DatetimeIndex(g.ts[rl // 1440]) + pd.to_timedelta(rl % 1440, unit="m")).to_numpy()
    roll = np.zeros(len(m), bool); p = np.searchsorted(m.ts.to_numpy(), rts); roll[p[p < len(m)]] = True
    m["roll"] = roll; m["hm"] = m.ts.dt.hour * 100 + m.ts.dt.minute
    return m.reset_index(drop=True)


@njit(cache=True)
def tstat(tmin, c, roll, h, hv):
    n = len(c); T = np.full(n, np.nan); M = 0.0; S = 0.0; since = 0
    for i in range(n):
        if i == 0 or tmin[i] - tmin[i - 1] > 10:
            M = 0.0; S = 0.0; since = 0; continue
        dt = tmin[i] - tmin[i - 1]; r = 0.0 if roll[i] else np.log(c[i] / c[i - 1])
        M = np.exp(-dt / h) * (M + r); S = np.exp(-dt / hv) * (S + r * r); since += dt
        if since >= hv and S > 0: T[i] = np.sqrt(2.0 * h) * (M / h) / np.sqrt(S / hv)
    return T


@njit(cache=True)
def events(T, tmin, inwin, c_thr, rearm, drop, conf_win):
    """returns arrays: cross index, confirm index (-1 if none in conf_win), peak index (look-ahead: max |T| until re-arm / 30 min), sign"""
    n = len(T); cr = []; cf = []; pk = []; sg = []; armed = True
    i = 0
    while i < n:
        t = T[i]
        if np.isnan(t):
            armed = True; i += 1; continue
        if armed and abs(t) > c_thr and inwin[i]:
            s = 1 if t > 0 else -1; mx = abs(t); conf = -1; peak = i; j = i + 1
            while j < n and not np.isnan(T[j]) and tmin[j] - tmin[i] <= 30 and abs(T[j]) >= rearm:
                if s * T[j] > mx:
                    mx = s * T[j]; peak = j
                if conf < 0 and tmin[j] - tmin[i] <= conf_win and s * T[j] <= mx - drop: conf = j
                j += 1
            cr.append(i); cf.append(conf); pk.append(peak); sg.append(s); armed = False; i = j; continue
        if abs(t) < rearm: armed = True
        i += 1
    return np.array(cr), np.array(cf), np.array(pk), np.array(sg)


def trades(m, sig_idx, side, stop_from, sym, hold=HOLD, cost=True):
    pv, tick, comm = SPEC[sym][:3]; o, h, l, c = (m[k].to_numpy() for k in ("open", "high", "low", "close")); tm = m.tmin.to_numpy(); rows = []
    for k, s, a in zip(sig_idx, side, stop_from):
        e = k + 1
        if e + hold >= len(o) or tm[e] - tm[k] > 2 or tm[e + hold - 1] - tm[e] > hold + 2: continue
        px = o[e]; stp = (h[a:k + 1].max() + tick) if s < 0 else (l[a:k + 1].min() - tick)
        if (s < 0 and stp <= px) or (s > 0 and stp >= px): continue           # already through the burst extreme at the open: no trade
        ex, why = c[e + hold - 1], "time"
        for i in range(e, e + hold):
            if (s < 0 and h[i] >= stp) or (s > 0 and l[i] <= stp):
                ex = max(stp, o[i]) if s < 0 else min(stp, o[i]); why = "stop"; break
        g = s * (ex - px) * pv; rows.append((m.ts.iat[e], s, px, ex, why, g, g - ((comm + 2 * tick * pv) if cost else 0.0), abs(stp - px) * pv))
    return pd.DataFrame(rows, columns=["ts", "side", "entry", "exit", "why", "gross", "net", "risk"])


def line(t, lab):
    if len(t) < 3: return f"   {lab:<34} n {len(t)}"
    x = t.net; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum()); tt = x.mean() / x.std() * np.sqrt(len(x)); y = pd.DatetimeIndex(t.ts).year
    return (f"   {lab:<34} n {len(t):4d} win {np.mean(x > 0):5.1%} gross ${t.gross.mean():6.1f} net ${x.mean():6.1f} PF {pf:4.2f} t {tt:5.2f} "
            f"| 18-22 n {int((y <= 2022).sum())} ${x[y <= 2022].mean():6.1f} | 23+ n {int((y >= 2023).sum())} ${x[y >= 2023].mean():6.1f} | risk ${t.risk.mean():5.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); rng = np.random.default_rng(1); OUT = {}
    of = None
    for sym in ("GC", "CL", "ES", "NQ"):
        m = minutes(sym); m = m[m.ts >= "2017-11-01"].reset_index(drop=True)
        m["tmin"] = m.ts.to_numpy().astype("datetime64[m]").astype(np.int64)   # datetime64 unit-safe (us vs ns)
        T = tstat(m.tmin.to_numpy(), m.close.to_numpy(), m.roll.to_numpy(), H, HV)
        inwin = ((m.hm > 100) & (m.hm <= 1500) & (m.ts >= "2018-01-01")).to_numpy()
        RATE = {"GC": 221, "CL": 268, "ES": 69, "NQ": 69}[sym]            # paper's events a year at c = 4.0 (Amendment 1)
        des = inwin & (m.ts < "2023-01-01").to_numpy(); lo_, hi_ = 1.0, 6.0
        for _ in range(40):                                              # bisection: c giving RATE events a year in 2018-22
            mid = (lo_ + hi_) / 2; n_ = len(events(T, m.tmin.to_numpy(), des, mid, REARM, DROP, CONF_WIN)[0]) / 5.0
            lo_, hi_ = (mid, hi_) if n_ > RATE else (lo_, mid)
        cthr = (lo_ + hi_) / 2
        cr, cf, pk, sg = events(T, m.tmin.to_numpy(), inwin, cthr, REARM, DROP, CONF_WIN)
        print(f"\n   calibrated threshold c = {cthr:.2f} (paper's {RATE} events a year in 2018-22)", end="")
        Tw = T[inwin & ~np.isnan(T)]
        yrs = (m.ts.iat[-1] - pd.Timestamp("2018-01-01")).days / 365.25
        print(f"\n===== {sym}: {m.ts.iat[0].date()} .. {m.ts.iat[-1].date()}; T in window: sd {np.std(Tw):.2f}, |T| > 4 {np.mean(np.abs(Tw) > 4):.5f} "
              f"(normal 0.00006), > 4.5 {np.mean(np.abs(Tw) > 4.5):.5f}; events {len(cr)} ({len(cr) / yrs:.0f} a year), confirmed within 15 min {np.mean(cf >= 0):.0%}")
        c = m.close.to_numpy(); tm = m.tmin.to_numpy()
        def rev(idx, s):
            ok = (idx >= 5) & (idx + 5 < len(c)); idx, s = idx[ok], s[ok]
            ok2 = (tm[idx + 5] - tm[idx] <= 7) & (tm[idx] - tm[idx - 5] <= 7); idx, s = idx[ok2], s[ok2]
            rm, rp = np.log(c[idx] / c[idx - 5]), np.log(c[idx + 5] / c[idx])
            return len(idx), np.mean(np.sign(rp) == -np.sign(rm)), np.mean(-s * rp) * 1e4, np.mean(np.abs(rm)) * 1e4
        for lab, idx in (("at the PEAK (paper, look-ahead)", pk), ("at the first crossing (causal)", cr), ("at the confirmed turn (causal)", cf)):
            ok = idx >= 0; n, pr, mv, run = rev(idx[ok], sg[ok])
            print(f"   5-min reversal {lab:<33} n {n:4d}  reversal {pr:5.1%}  next 5 min against the burst {mv:+6.2f} bp  (burst 5-min move {run:5.1f} bp)")
        A = trades(m, cr, -sg, np.maximum(cr - 5, 0), sym); okb = cf >= 0
        B = trades(m, cf[okb], -sg[okb], np.maximum(cr[okb] - 5, 0), sym)
        print(line(A, "A first cross, 5 min")); print(line(B, "B confirmed turn, 5 min (primary)" if sym in ("GC", "CL") else "B confirmed turn, 5 min"))
        for s_, nm in ((1, "longs (fade a drop)"), (-1, "shorts (fade a rise)")): print(line(B[B.side == s_], "   B " + nm))
        yb = pd.DatetimeIndex(B.ts).year; print("   B by year: " + "  ".join(f"{k} ${g.net.sum():,.0f} ({len(g)})" for k, g in B.groupby(yb)))
        for hd in (15, 30): print(line(trades(m, cf[okb], -sg[okb], np.maximum(cr[okb] - 5, 0), sym, hold=hd), f"B, hold {hd} min (info)"))
        # placebo: random window bars (same count per year), fade the last 5-min move, same exits
        if len(B) < 5: print("   too few trades for a placebo"); OUT[sym] = (m, T, cr, cf, pk, sg, B); continue
        cand = np.flatnonzero(inwin & ~np.isnan(T)); yc = m.ts.dt.year.to_numpy()[cand]; nb = pd.Series(yb).value_counts(); pm = []
        for _ in range(200):
            pick = np.sort(np.concatenate([rng.choice(cand[yc == y], k, replace=False) for y, k in nb.items()]))
            s = -np.sign(c[pick] - c[np.maximum(pick - 5, 0)]); ok = s != 0
            pm.append(trades(m, pick[ok], s[ok].astype(int), np.maximum(pick[ok] - 5, 0), sym).net.mean())
        pm = np.array(pm); print(f"   placebo B (random bars, fade the last 5 min, same exits, 200 runs): mean ${pm.mean():.1f}, p95 ${np.percentile(pm, 95):.1f}; "
                                 f"real ${B.net.mean():.1f}, p {np.mean(pm >= B.net.mean()):.3f}")
        OUT[sym] = (m, T, cr, cf, pk, sg, B)
    # ---- C: NQ, B + aggressor flow turned (data/OF_1min_*, RTH, ET clock -> CT) ----
    m, T, cr, cf, pk, sg, B = OUT["NQ"]
    o = pd.concat([pd.read_csv(f, usecols=["date", "time", "upvol", "downvol"]) for f in sorted(glob.glob("data/OF_1min_20*.csv"))])
    o["ts"] = pd.to_datetime(o.date.astype(str), format="%Y%m%d") + pd.to_timedelta(o.time // 100 * 60 + o.time % 100 - 60, unit="m")
    dl = (o.set_index("ts").upvol - o.set_index("ts").downvol); dl = dl[~dl.index.duplicated()]
    d2 = pd.Series(dl.reindex(m.ts.to_numpy()).to_numpy()).rolling(2, min_periods=2).sum().to_numpy()
    okb = cf >= 0; idx = cf[okb]; s_f = -sg[okb]; fl = d2[idx]; hm = m.hm.to_numpy()[idx]; ofwin = (hm > 830) & (hm <= 1500) & ~np.isnan(fl) & (m.ts.to_numpy()[idx] <= np.datetime64("2026-07-07"))
    turn = np.sign(fl) == s_f
    Cc = trades(m, idx[ofwin & turn], s_f[ofwin & turn], np.maximum(cr[okb][ofwin & turn] - 5, 0), "NQ")
    Cn = trades(m, idx[ofwin & ~turn], s_f[ofwin & ~turn], np.maximum(cr[okb][ofwin & ~turn] - 5, 0), "NQ")
    Bw = trades(m, idx[ofwin], s_f[ofwin], np.maximum(cr[okb][ofwin] - 5, 0), "NQ")
    print("\n===== C: NQ 08:30-15:00 CT, order flow at the confirmed turn (aggressor delta of the last 2 bars; data to 2026-07-07)")
    print(line(Bw, "B in the order-flow window")); print(line(Cc, "C flow turned (primary)")); print(line(Cn, "flow still with the burst (control)"))
    yc = pd.DatetimeIndex(Cc.ts).year; print("   C by year: " + "  ".join(f"{k} ${g.net.sum():,.0f} ({len(g)})" for k, g in Cc.groupby(yc)))
    for s_, nm in ((1, "longs"), (-1, "shorts")): print(line(Cc[Cc.side == s_], "   C " + nm))
