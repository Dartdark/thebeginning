"""MNQ portfolio 'v4 + N-Day Long' (user's post, 2026-10-25: NA 3 / ON 4 / TOTM 4 / N-Day Long 2 MNQ, $750 shared daily cap,
report 2019-05-16 -> 2026-07-28: PF 1.29, net $96,792, 3,551 trades, max DD -$8,756). No v4 code was supplied: built from the
post's rules on top of the v2 rebuild (analysis/mnq_sharedcap_test.py, same data / fills / costs). ASSUMED where the post is silent:
  NA    the v2 noise-area leg (both sides, :00 / :30 decisions, VWAP / band exit), 3 MNQ; 'adaptive' unknown -> v2 rules, and a
        variant without the Monday / holiday blocks.
  ON    v2 overnight-gap fade short (z >= 1, 08:31 -> 12:00), 4 MNQ.
  TOTM  v2 3rd session of the month long (50-day trend filter, 08:31 -> 15:01) + an ATR stop: entry - 1 x ATR14 (RTH true
        range; multiple not given), 4 MNQ.
  NDAY  N-Day Long: first 1-minute close above the highest RTH high of the previous 5 sessions (08:31-14:30), long at that
        close; stop entry - 1 x ATR14 (StopATRMult 1), target entry + 3 x that risk (TargetRR 3); flat at the 15:00 close;
        one a day; 2 MNQ.
  Cap   realized + open P&L of all legs <= -$750 -> everything flat for the day (as v2).
Costs per MNQ $0.725 + 1 tick per fill (ours); also Apex real $1.04 + 1 tick.
  python3 analysis/mnq_v4_nday_test.py [SCRATCH_DIR] > analysis/outputs/mnq_v4_nday_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import mnq_sharedcap_test as MS
import metrics as M, montecarlo as MC

g, tr, C, C1501, PV = MS.g, MS.tr, MS.C, MS.C1501, MS.PV
J0, J1 = MS.J0, MS.J1
H = np.array([pd.Series(g.h[r, J0:J1 + 1]).ffill().bfill().to_numpy() for r in tr])
L = np.array([pd.Series(g.l[r, J0:J1 + 1]).ffill().bfill().to_numpy() for r in tr])
dh, dl, dc = H.max(1), L.min(1), C[:, -1]
pc = np.r_[np.nan, dc[:-1]]
trng = np.fmax(dh, pc) - np.fmin(dl, pc)
ATR = pd.Series(trng).rolling(14).mean().shift(1).to_numpy()
HH = pd.Series(dh).rolling(5).max().shift(1).to_numpy()
I1430 = int(np.where(MS.hhmm == 1430)[0][0])


def stop_target_exit(d, m0, e, side, stop, target):
    """First minute after m0 whose low (long) reaches the stop or high the target; stop first if both. Else the 15:00 close."""
    for m in range(m0 + 1, 390):
        if (L[d, m] <= stop) if side > 0 else (H[d, m] >= stop): return m, stop
        if target is not None and ((H[d, m] >= target) if side > 0 else (L[d, m] <= target)): return m, target
    return 389, C[d, 389]


def day_events(d, na_q=3, on_q=4, tm_q=4, nd_q=2, tm_stop=1.0, nd_stop=1.0, nd_rr=3.0, nd_look=None, **kw):
    ev = MS.day_paths(d, na_q=na_q, on_q=on_q, tm_q=tm_q, **kw)
    if ev["TOTM"] and tm_stop and np.isfinite(ATR[d]):
        e = C[d, 0]; m, x = stop_target_exit(d, 0, e, 1, e - tm_stop * ATR[d], None)
        if m < 389: ev["TOTM"] = [(0, tm_q, e), (m, -tm_q, x)]
    ev["NDAY"] = []
    hh = HH[d] if nd_look is None else pd.Series(dh[max(0, d - nd_look):d]).max()
    if nd_q and np.isfinite(hh) and np.isfinite(ATR[d]):
        hit = np.where(C[d, :I1430 + 1] > hh)[0]
        if len(hit):
            m0 = hit[0]; e = C[d, m0]; r = nd_stop * ATR[d]
            m, x = stop_target_exit(d, m0, e, 1, e - r, e + nd_rr * r)
            ev["NDAY"] = [(m0, nd_q, e), (m if m < 389 else 390, -nd_q, x if m < 389 else C1501[d])]
    return ev


def run(cost=0.725 + 0.5, cap=750.0, start="2018-01-01", **kw):
    rows = []
    for d in range(len(tr)):
        if MS.dts[d] < pd.Timestamp(start): continue
        ev = day_events(d, **kw); r = {"date": MS.dts[d]}; n = 0
        for leg in ev:
            r[leg], f = MS.realize(ev[leg], d, cost); r[leg + "_t"] = len(ev[leg]) // 2 if leg != "NA" else sum(1 for e in ev[leg] if abs(e[1]) != 0) // 2
        allev = [e for Lx in ev.values() for e in Lx]
        r["sum"], _ = MS.realize(allev, d, cost); r["sum_cap"], _ = MS.realize(allev, d, cost, cap=cap)
        rows.append(r)
    return pd.DataFrame(rows).set_index("date")


def pf(x): x = x[x != 0]; return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    R = run(); R.to_csv("analysis/outputs/mnq_v4_nday_daily.csv")
    print("\n1. 2018-01 -> 2026-10, the post's sizes (NA 3, ON 4, TOTM 4, N-Day 2 MNQ), our costs, per day:")
    for col, nm in (("NA", "NA 3 MNQ"), ("ON", "ON short 4"), ("TOTM", "TOTM long 4 + 1 ATR stop"), ("NDAY", "N-Day Long 2 (5-day high, 1 ATR / 3R)"),
                    ("sum", "four legs, no cap"), ("sum_cap", "four legs + $750 cap")):
        print(MS.line(R[col], nm, w=40) + f"  PF(days) {pf(R[col]):.2f}")
    w = R[(R.index >= "2019-05-16") & (R.index <= "2026-07-28")]
    print(f"\n   the report's window 2019-05-16 -> 2026-07-28: four legs + cap ${w.sum_cap.sum():,.0f} (report $96,792), day PF {pf(w.sum_cap):.2f} "
          f"(report trade PF 1.29), max DD ${-(w.sum_cap.cumsum() - w.sum_cap.cumsum().cummax()).min():,.0f} (report $8,756)")
    for a, b in (("2019-05-16", "2021-12-31"), ("2022-01-01", "2023-06-30"), ("2023-07-01", "2026-07-28")):
        s = R[(R.index >= a) & (R.index <= b)]
        print(f"   {a} -> {b}: " + ", ".join(f"{c} ${s[c].sum():,.0f}" for c in ("NA", "ON", "TOTM", "NDAY", "sum_cap")))
    print("   by year, four legs + cap:", R.sum_cap.groupby(R.index.year).sum().round(0).astype(int).to_dict())
    print("   daily correlations between legs:"); print(R[["NA", "ON", "TOTM", "NDAY"]].corr().round(2).to_string())

    print("\n2. Variants (four legs + cap unless named):")
    V = {"Apex real costs ($1.04 + 1 tick)": dict(cost=1.04 + 0.5), "no cap": dict(cap=1e9), "cap $1,500": dict(cap=1500.0),
         "NA without Monday / holiday blocks": dict(block_mon=False, hol=False), "TOTM without the ATR stop": dict(tm_stop=0),
         "N-Day stop 2 ATR": dict(nd_stop=2.0), "N-Day target 1R": dict(nd_rr=1.0), "N-Day lookback 10": dict(nd_look=10), "N-Day lookback 3": dict(nd_look=3)}
    for nm, kw in V.items():
        x = run(**kw); print(MS.line(x.sum_cap, nm, w=40) + f" | N-Day alone ${x.NDAY.sum() / (len(x) / 252):,.0f}/yr t {x.NDAY[x.NDAY != 0].mean() / x.NDAY[x.NDAY != 0].std() * np.sqrt((x.NDAY != 0).sum()):.1f}")

    print("\n3. Metrics (daily, at the post's size) and Monte Carlo:")
    rows = {"four legs + cap 2018-26": (R.sum_cap, None), "2023+": (R.sum_cap[R.index >= "2023-01-01"], None)}
    for c in ("NA", "ON", "TOTM", "NDAY"): rows[c] = (R[c], None)
    print(M.table(rows))
    x = R.sum_cap
    print(MC.report(x[x != 0].values, daily=x.values, size=1.0, label="four legs + cap (NA 3, ON 4, TOTM 4, NDAY 2 MNQ)"))
    xr = x[(x.index >= "2019-05-16") & (x.index <= "2026-07-28")]; d_ = xr[xr != 0].values; rng = np.random.default_rng(1); dds = []
    for _ in range(10000):
        e = np.cumsum(rng.permutation(d_)); dds.append(-(e - np.maximum.accumulate(e)).min())
    e = np.cumsum(d_); real = -(e - np.maximum.accumulate(e)).min()
    print(f"   reshuffled DAILY results (their trade-order test, here by day), 10,000 runs: max DD 5% ${np.percentile(dds, 5):,.0f} / "
          f"50% ${np.percentile(dds, 50):,.0f} / 95% ${np.percentile(dds, 95):,.0f} / max ${max(dds):,.0f}; realised ${real:,.0f} (rank {np.mean(np.array(dds) < real):.0%})")
