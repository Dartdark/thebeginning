"""Paper batch 2026-11-10 (user upload, 5 PDFs). PRE-REGISTERED (header committed before the first run). 9 items, bar t_threshold(9),
and positive in 2018-22 and 2023+. Costs $7.25 NQ / $5 others + 1 tick per fill; per contract.
A FOMC announcement reversal (Baglioni & Ribeiro, SSRN 4182628, Feb 2025: ES 1997-2020, 180 meetings, +18 bp net an event, Sharpe
  0.56): pre return = 12:45 CT the day before -> 12:45 CT on the FOMC day (24h15m -> 15 min before the 13:00 CT statement); trade the
  OTHER way. A1 ES / A2 NQ in at the 12:50 close, out at the 14:50 close (the paper); A3 ES / A4 NQ in at 13:20 (the paper's
  '20 minutes after'), out 15:20. FOMC dates: analysis/event_days.FOMC_DATES (69 scheduled meetings 2018-26).
B FX local-hours effect (Breedon & Ranaldo, SSRN 2099321, 2012: EUR/USD falls in European hours 02:00-08:00 NY, rises 08:00-16:00
  NY, 1997-2007, Sharpe 1.3 / 0.9 after spreads): B1 short 6E 01:00 -> 07:00 CT close-to-close, B2 long 6E 07:00 -> 15:00 CT; weekdays.
C Hedgers and speculators (Kang, Rouwenhorst & Tang, SSRN 2449315: commercials earn a liquidity premium on weekly position changes;
  non-commercial net buying in week t -> lower returns in t+1): Legacy COT (data/cot/deacot*.zip); Q = weekly change in
  non-commercial net (long - short) / open interest; side = -sign(Q); hold from the release Friday 15:59 CT close to the next
  Friday's, in-session moves only (the 16:00-17:00 break and roll gaps left out); each market's weekly return / its trailing
  26-week sd; ITEM C1 = the equal-weight average over GC CL NG 6E ZN ES NQ YM each week (personal account at most: holds a week).
D Spread trades (Park, Fed FEDS 2019-025): excess net number of speculators = non-commercial long traders - short traders;
  indicator = 1 if > 0 in 3-month Eurodollars (SOFR 3M from 2023, Eurodollars delisted) and < 0 in 30-year T-bonds; STEEP =
  13-week average, latest report released before the FOMC day. D1 ES / D2 NQ long 08:30 -> 12:45 CT on FOMC days with STEEP > 0,
  flat otherwise (context: every FOMC day, and STEEP = 0 days).
E Volatility-managed sizing (Moreira & Muir, SSRN 2659431, J. Finance 2017) - CONTEXT, not an item: each personal-book piece
  (scratch_data/personal_P.pkl) and the total, size each month by 1 / the previous month's realised variance of its daily P&L,
  normalised by the expanding mean of those weights (no look-ahead); annualised Sharpe managed vs plain, 2019-22 and 2023+;
  NQ buy-and-hold the same way. A piece gain here would be a lead for the funded / personal sizing benches.
  tools/run_stamped.sh analysis/papers_1110_test.py > analysis/outputs/papers_1110_test_output.txt
"""
import sys, glob, pickle, zipfile, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from metrics import t_threshold
from event_days import FOMC_DATES

SP = "scratch_data/"
MK = {"NQ": ("g24", 20.0, 0.25, 7.25, "209742"), "ES": ("ge", 50.0, 0.25, 5.0, "13874A"), "YM": ("gy", 5.0, 1.0, 5.0, "124603"),
      "GC": ("gc", 100.0, 0.1, 5.0, "088691"), "CL": ("cl", 1000.0, 0.01, 5.0, "067651"), "NG": ("ng", 10000.0, 0.001, 5.0, "023651"),
      "6E": ("e6", 125000.0, 0.00005, 5.0, "099741"), "ZN": ("zn", 1000.0, 0.015625, 5.0, "043602")}
BAR = t_threshold(9)
G = {}


def grid(m):
    if m not in G: G[m] = pickle.load(open(SP + MK[m][0] + ".pkl", "rb"))
    return G[m]


def tt(x): x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def show(x, nm, item=False):
    x = pd.Series(x).dropna().sort_index()
    if len(x) < 5: return f"   {nm:<46} n={len(x)}"
    y = x.index.year; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum()); a, b = x[y <= 2022], x[y >= 2023]; t = tt(x)
    flag = ("  PASS" if (t >= BAR and a.mean() > 0 and b.mean() > 0) else "  fail") if item else ""
    return (f"   {nm:<46} n {len(x):4d} avg {x.mean():8.2f} PF {pf:4.2f} t {t:5.2f} win {np.mean(x > 0):.0%} | 18-22 {a.mean():8.2f} 23+ {b.mean():8.2f}"
            f" | yrs+ {(x.groupby(y).sum() > 0).sum()}/{y.nunique()}{flag}")


def cflat(g): return pd.Series(g.c.ravel()).ffill().to_numpy()


def at(g, cf, d, hhmm, back=0):
    r = int((pd.Timestamp(d) - pd.Timestamp(g.ts[0])).days) - back
    return cf[r * 1440 + jof(hhmm)] if 0 <= r < g.D else np.nan


def cot():
    out = []
    for f in sorted(glob.glob("data/cot/deacot*.zip")):
        z = zipfile.ZipFile(f); d = pd.read_csv(z.open(z.namelist()[0]), low_memory=False); out.append(d)
    d = pd.concat(out); d["code"] = d["CFTC Contract Market Code"].astype(str).str.strip(); d["date"] = pd.to_datetime(d["As of Date in Form YYYY-MM-DD"])
    return d.drop_duplicates(["code", "date"]).sort_values("date")


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); print(f"   items 9, bar t >= {BAR:.2f}")
    F = pd.to_datetime(FOMC_DATES)
    # ---------------- A
    print("\nA. FOMC announcement reversal (fade the 24h pre-announcement move), $ per contract:")
    for m in ("ES", "NQ"):
        g = grid(m); cf = cflat(g); pv, tick, comm = MK[m][1:4]; R = {"pre": {}, "a": {}, "b": {}}
        for d in F:
            pre = at(g, cf, d, 1245) - at(g, cf, d, 1245, back=1)
            if not np.isfinite(pre) or pre == 0: continue
            s = -np.sign(pre); R["pre"][d] = pre
            for k, (i, o) in (("a", (1250, 1450)), ("b", (1320, 1520))):
                e, x = at(g, cf, d, i), at(g, cf, d, o)
                if np.isfinite(e) and np.isfinite(x): R[k][d] = s * (x - e) * pv - comm - 2 * tick * pv
        pre = pd.Series(R["pre"]); post = pd.Series({d: at(g, cf, d, 1459) - at(g, cf, d, 1300) for d in pre.index})
        print(f"   {m}: corr(pre 12:45->12:45, post 13:00->14:59) {pre.corr(post):+.2f} over {len(pre)} meetings")
        print(show(pd.Series(R["a"]), f"ITEM {m} fade, 12:50 -> 14:50", True)); print(show(pd.Series(R["b"]), f"ITEM {m} fade, 13:20 -> 15:20", True))
    # ---------------- B
    print("\nB. 6E local-hours effect, $ per 6E:")
    g = grid("6E"); cf = cflat(g); pv, tick, comm = MK["6E"][1:4]; days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days >= "2018-01-01"]
    s1 = pd.Series({d: -(at(g, cf, d, 700) - at(g, cf, d, 100)) * pv - comm - 2 * tick * pv for d in days})
    s2 = pd.Series({d: (at(g, cf, d, 1500) - at(g, cf, d, 700)) * pv - comm - 2 * tick * pv for d in days})
    print(show(s1, "ITEM short 6E 01:00 -> 07:00 CT", True)); print(show(s2, "ITEM long 6E 07:00 -> 15:00 CT", True))
    print(show(s1 + comm + 2 * tick * pv, "   (gross) short 01:00 -> 07:00")); print(show(s2 + comm + 2 * tick * pv, "   (gross) long 07:00 -> 15:00"))
    # ---------------- C
    print("\nC. Commercials' liquidity premium (fade the week's non-commercial net change), weekly, vol-normalised:")
    D = cot(); W = {}
    for m in MK:
        g = grid(m); c = g.c.ravel(); ts0 = pd.Timestamp(g.ts[0])
        v = np.nonzero(np.isfinite(c))[0]; dc = np.diff(c[v]); gap = np.diff(v) > 30; dc[gap] = 0.0       # in-session moves only
        S = pd.Series(np.r_[0.0, np.cumsum(dc)], index=v); lvl = pd.Series(c[v], index=v)
        x = D[D.code == MK[m][4]].set_index("date"); oi = x["Open Interest (All)"].astype(float)
        net = (x["Noncommercial Positions-Long (All)"].astype(float) - x["Noncommercial Positions-Short (All)"].astype(float)) / oi
        Q = net.diff().dropna(); r = {}
        for tday, q in Q.items():
            f0 = tday + pd.Timedelta(days=3); f1 = f0 + pd.Timedelta(days=7)
            i0 = int((f0 - ts0).days) * 1440 + jof(1559); i1 = int((f1 - ts0).days) * 1440 + jof(1559)
            k0, k1 = S.index.searchsorted(i0, "right") - 1, S.index.searchsorted(i1, "right") - 1
            if k0 < 0 or k1 <= k0 or q == 0: continue
            r[f0] = -np.sign(q) * (S.iloc[k1] - S.iloc[k0]) / lvl.iloc[k0]
        r = pd.Series(r); r = r[r.index >= "2018-01-01"]; W[m] = r / r.abs().rolling(26, min_periods=8).mean().shift(1)
        print(show(r * 100, f"   {m} (% a week, unscaled)"))
    P = pd.DataFrame(W).mean(axis=1).dropna(); print(show(P, "ITEM C1 equal-weight 8 markets (vol units)", True))
    # ---------------- D
    print("\nD. Speculators' steepening -> pre-FOMC drift (long 08:30 -> 12:45 CT):")
    ex = lambda code: (lambda x: (x["Traders-Noncommercial-Long (All)"].astype(float) - x["Traders-Noncommercial-Short (All)"].astype(float)))(D[D.code == code].set_index("date"))
    sh = pd.concat([ex("132741")[lambda s: s.index < "2023-01-01"], ex("134741")[lambda s: s.index >= "2023-01-01"]]).sort_index()
    bd = ex("020601"); I = ((sh > 0) & (bd.reindex(sh.index) < 0)).astype(float); STEEP = I.rolling(13, min_periods=6).mean()
    rel = STEEP.copy(); rel.index = rel.index + pd.Timedelta(days=3)                            # released the Friday after
    st = pd.Series({d: rel[rel.index < d].iloc[-1] if (rel.index < d).any() else np.nan for d in F})
    print(f"   STEEP on FOMC days: > 0 on {(st > 0).sum()} of {st.notna().sum()}")
    for m in ("ES", "NQ"):
        g = grid(m); cf = cflat(g); pv, tick, comm = MK[m][1:4]
        x = pd.Series({d: (at(g, cf, d, 1245) - at(g, cf, d, 830)) * pv - comm - 2 * tick * pv for d in F})
        print(show(x, f"   {m} every FOMC day")); print(show(x[st > 0], f"ITEM {m} STEEP > 0", True)); print(show(x[st == 0], f"   {m} STEEP = 0"))
    # ---------------- E
    print("\nE. Volatility-managed sizing (context): annualised Sharpe of daily P&L, plain -> managed (2019-22 | 2023+)")
    Pp = pd.read_pickle(SP + "personal_P.pkl"); Pp["TOTAL"] = Pp.sum(axis=1)
    g = grid("NQ"); cf = cflat(g); days = pd.DatetimeIndex(g.ts[g.trading])
    nq = pd.Series([at(g, cf, d, 1559) for d in days], index=days).pct_change() * 1e4; Pp = Pp.join(nq.rename("NQ buy-hold (bp)"), how="left")
    sr = lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else np.nan
    for c in Pp.columns:
        x = Pp[c].fillna(0.0); x = x[x.index >= "2018-01-01"]; mo = x.index.to_period("M")
        rv = (x ** 2).groupby(mo).sum(); w = (1 / rv.replace(0, np.nan)).shift(1); w = w / w.expanding().mean().shift(1)
        mx = x * w.reindex(mo).to_numpy(); ok = np.isfinite(mx) & (x.index >= "2019-01-01"); a, b = x[ok], mx[ok]; e = a.index.year <= 2022
        print(f"   {c:<26} {sr(a):5.2f} -> {sr(b):5.2f} | 19-22 {sr(a[e]):5.2f} -> {sr(b[e]):5.2f} | 23+ {sr(a[~e]):5.2f} -> {sr(b[~e]):5.2f}")
