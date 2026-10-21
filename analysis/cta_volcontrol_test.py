"""CTA trigger levels and vol-control fund rebalancing (2026-10-12, from multi_strategy/PRACTITIONER_SOURCES.md).

Both are forced flows that bank flow desks (JPM, Nomura, Goldman) model for clients; here they are
rebuilt from public descriptions and tested on NQ (ES for the vol-control funds' own vol).

V. Vol-control funds (S&P Daily Risk Control style): exposure E = min(1.5, 10% / vol), vol = the
   larger of two EWMA vols of daily ES returns (lambda 0.94 and 0.97, annualized). After a day's
   return r the fund's exposure drifts to E(1+r)/(1+E r); the rebalance it must trade at the close
   is flow = E_new - drifted E (in units of fund size).
   V1 lag 0 (vol includes today): flow estimated at 14:00 from the 14:00 ES price; trade NQ
      14:01 -> 15:00 in the flow's direction when |flow| is large.
   V2 lag 1 (vol up to yesterday): flow known before the open; trade 8:30 -> 15:00 / 14:00 -> 15:00.
   V3 Late-Day Flow (MultiCharts trades) split by whether the vol-control flow agrees with it.
C. CTA trend models (Nomura / GS style): signals sign(close - close N days ago), N = 21, 63, 126,
   252 trading days (1, 3, 6, 12 months), position = mean of the signals x min(2, 15% / 63-day vol).
   The trigger level for lookback N today is the close N days ago: closing beyond it flips the signal.
   C1 next day: after a close that flipped >= m signals, trade the next day 8:30 -> 15:00 in the flip
      direction (CTAs spread execution over the following sessions).
   C2 same day, into the close: at 14:00, if the price is beyond a trigger that would flip a signal
      at the close, follow 14:01 -> 15:00 (CTAs that trade the settlement).
   C3 same day, the break itself: buy (sell) stop at the nearest trigger above (below) the 8:45
      price, 8:45 -> 14:00, stop 0.3 ATR, out 15:00.
   Placebo for C: the same rules with lookbacks CTAs don't use (N = 35, 45, 90, 160, 200).

Per NQ after $7.25 + 1 tick per market/stop fill. 2018-2026 with the 2023-26 holdout.
  python3 analysis/cta_volcontrol_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
from news_meanrev_test import row, summ

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, RT, TICK = 20.0, 7.25 + 2 * 0.25 * 20, 0.25
CTA_N, PLACEBO_N = (21, 63, 126, 252), (35, 45, 90, 160, 200)
NT = [0]


def rep(name, pnl, dts, mask=None, w=62):
    """pnl: signed $ per NQ per day before costs (market entry and exit)."""
    x = pd.Series(pnl, index=dts)
    m = (dts.year >= 2018) & ~np.isnan(x.values) & (True if mask is None else mask)
    x = x[m] - RT
    if len(x) < 15: print(f"  {name:<{w}} n={len(x)}"); return x
    NT[0] += 1
    y = x.groupby(x.index.year).sum(); h = x[x.index.year >= 2023]; d = x[x.index.year <= 2022]
    t = x.mean() / x.std() * np.sqrt(len(x))
    pf = x[x > 0].sum() / -x[x < 0].sum()
    flag = " <==" if abs(t) >= 3 else (" <" if abs(t) >= 2 else "")
    print(f"  {name:<{w}} n={len(x):4d} avg ${x.mean():5.0f} PF {pf:.2f} t={t:5.1f} yrs+ {(y>0).sum()}/{len(y)}"
          f" | 18-22 ${d.mean():5.0f} | 23+ ${h.mean():5.0f}{flag}")
    return x


def ewma_vol(r, lam):
    v = np.full(len(r), np.nan); acc = np.nan
    for i, x in enumerate(r):
        if np.isnan(x): v[i] = acc; continue
        acc = x * x if np.isnan(acc) else lam * acc + (1 - lam) * x * x
        v[i] = acc
    return np.sqrt(252 * v)


def vc_exposure(r, target=0.10, cap=1.5):
    vol = np.fmax(ewma_vol(r, 0.94), ewma_vol(r, 0.97))
    return np.minimum(cap, target / vol)


def vc_flow(e_prev, e_new, r):
    drift = e_prev * (1 + r) / (1 + e_prev * r)
    return e_new - drift


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
    atr = g.daily_atr(15)
    tr = g.trading; dts = pd.DatetimeIndex(g.ts[tr])
    o830, c840, c900 = g.o[tr, 511], g.c[tr, 840], g.c[tr, 900]
    o841 = g.o[tr, 841]
    print(__doc__.split("\n")[0])

    # ES closes aligned to NQ trading rows
    ei = pd.Series(np.arange(len(es.dates)), index=es.dates).reindex(g.dates[tr]).to_numpy()
    ok = ~np.isnan(ei); ei = np.where(ok, ei, 0).astype(int)
    e900 = np.where(ok, es.c[ei, 900], np.nan); e840 = np.where(ok, es.c[ei, 840], np.nan)
    e900 = pd.Series(e900).ffill().to_numpy()
    r_es = np.r_[np.nan, e900[1:] / e900[:-1] - 1]

    # ------------------------------------------------------------------ V. vol-control
    print("\n=== V. Vol-control funds (10% target, EWMA 0.94/0.97, cap 150%) ===")
    E = vc_exposure(r_es)
    # V1 lag 0: at 14:00 estimate today's return and exposure from the 14:00 ES price
    prev = np.r_[np.nan, e900[:-1]]
    r14 = e840 / prev - 1
    v94, v97 = ewma_vol(r_es, 0.94) ** 2 / 252, ewma_vol(r_es, 0.97) ** 2 / 252
    pv94, pv97 = np.r_[np.nan, v94[:-1]], np.r_[np.nan, v97[:-1]]
    vol14 = np.sqrt(252 * np.fmax(0.94 * pv94 + 0.06 * r14 ** 2, 0.97 * pv97 + 0.03 * r14 ** 2))
    E14 = np.minimum(1.5, 0.10 / vol14)
    Eprev = np.r_[np.nan, E[:-1]]
    f14 = vc_flow(Eprev, E14, r14)
    print(f"  flow (fund units) at 14:00: median |flow| {np.nanmedian(np.abs(f14)):.3f}, 90th pct {np.nanpercentile(np.abs(f14), 90):.3f}")
    last_hour = (c900 - o841) * PV
    day_up = (c840 - o830) > 0
    for q in (0.0, 0.03, 0.06, 0.10):
        rep(f"V1 |flow14| > {q}: follow flow 14:01->15:00", np.sign(f14) * last_hour, dts, np.abs(f14) > q)
    for q in (0.03, 0.06):
        rep(f"V1 sell flow > {q} on UP days (opposes LETF buying)", -last_hour, dts, (f14 < -q) & day_up)
        rep(f"V1 sell flow > {q} on DOWN days (same way as LETF)", -last_hour, dts, (f14 < -q) & ~day_up)
        rep(f"V1 buy flow > {q} (vol falling)", last_hour, dts, f14 > q)
    # V2 lag 1: exposure set from yesterday's vol, so today's flow is known in the morning
    Elag = np.r_[np.nan, E[:-1]]; Elag2 = np.r_[np.nan, np.nan, E[:-2]]
    f_lag = Elag - Elag2 * (1 + r_es) / (1 + Elag2 * r_es)          # approx: drift by today's return unknown at the open
    f_lag_open = Elag - Elag2                                        # known before the open
    day = (c900 - o830) * PV
    for q in (0.03, 0.06, 0.10):
        rep(f"V2 |flow known at open| > {q}: follow 8:30->15:00", np.sign(f_lag_open) * day, dts, np.abs(f_lag_open) > q)
        rep(f"V2 |flow known at open| > {q}: follow 14:01->15:00", np.sign(f_lag_open) * last_hour, dts, np.abs(f_lag_open) > q)
    # V3 Late-Day Flow trades split by vol-control flow
    ldf = load_mc(g, "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx")
    ldf["net"] = (ldf.exit - ldf.entry) * ldf.side * PV - 7.25 - 2 * TICK * PV
    pos = pd.Series(np.arange(len(tr)), index=tr)
    li = pos.reindex(ldf.day).to_numpy()
    ldf = ldf[~np.isnan(li)].reset_index(drop=True); li = li[~np.isnan(li)]
    ff = f14[li.astype(int)]
    agree = np.sign(ff) == ldf.side.to_numpy()
    print("\n  V3 Late-Day Flow (MC trades, $ per NQ after costs + 2 ticks) by vol-control flow at 14:00:")
    for nm, m in (("flow agrees", agree), ("flow opposes", ~agree),
                  ("longs, flow opposes (selling)", (ldf.side > 0).to_numpy() & ~agree),
                  ("longs, flow agrees", (ldf.side > 0).to_numpy() & agree),
                  ("shorts, flow agrees (selling)", (ldf.side < 0).to_numpy() & agree),
                  ("shorts, flow opposes", (ldf.side < 0).to_numpy() & ~agree)):
        x = ldf.net[m]; y = ldf.date[m].dt.year
        h = x[y >= 2023]
        print(f"    {nm:<32} n={len(x):4d} avg ${x.mean():5.0f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f} | 23+ n={len(h)} ${h.mean():5.0f}")
    big_sell = (ff < -0.06)
    x = ldf.net[(ldf.side > 0).to_numpy() & big_sell]
    print(f"    longs with sell flow > 0.06      n={len(x):4d} avg ${x.mean():5.0f}")

    # ------------------------------------------------------------------ C. CTA trigger levels
    print("\n=== C. CTA trend-model trigger levels ===")
    cl = pd.Series(c900).ffill().to_numpy()
    r_nq = np.r_[np.nan, cl[1:] / cl[:-1] - 1]
    vol63 = pd.Series(r_nq).rolling(63).std().to_numpy() * np.sqrt(252)

    def model(Ns):
        S = np.full((len(Ns), len(cl)), np.nan)
        for i, n in enumerate(Ns):
            S[i, n:] = np.sign(cl[n:] - cl[:-n])
        pos_ = np.nanmean(S, 0) * np.minimum(2, 0.15 / vol63)
        return S, pos_

    for Ns, lab in ((CTA_N, "CTA lookbacks 21/63/126/252"), (PLACEBO_N, "placebo lookbacks 35/45/90/160/200")):
        S, P = model(Ns)
        flips = np.nansum(S[:, 1:] != S[:, :-1], 0); flips = np.r_[0, flips]
        fdir = np.r_[0, np.nansum(S[:, 1:] - S[:, :-1], 0)] / 2          # + = signals flipped up
        dP = np.r_[np.nan, np.diff(P)]
        print(f"\n  {lab}: flips per year {np.mean(flips[252:]) * 252:.0f}")
        nxt = np.r_[day[1:], np.nan]                                  # next day's 8:30 -> 15:00
        nxt_o = np.r_[(o830[1:] - cl[:-1]) * PV, np.nan]               # overnight into the next open
        for m in (1, 2):
            sel = np.abs(fdir) >= m
            rep(f"C1 {lab[:7]} >= {m} flips -> next day 8:30-15:00", np.sign(fdir) * nxt, dts, sel)
        rep(f"C1 {lab[:7]} >= 1 flip -> overnight (15:00 -> 8:30)", np.sign(fdir) * nxt_o, dts, np.abs(fdir) >= 1)
        q = np.nanpercentile(np.abs(dP), 80)
        rep(f"C1 {lab[:7]} model position change top 20% -> next day", np.sign(dP) * nxt, dts, np.abs(dP) >= q)
        # C2: at 14:00, would the close at the 14:00 price flip a signal?
        flip14 = np.zeros(len(cl))
        for i, n in enumerate(Ns):
            ref = np.r_[np.full(n, np.nan), cl[:-n]]                    # close n days ago
            prev_sig = S[i, :]; prev_sig = np.r_[np.nan, prev_sig[:-1]]
            new_sig = np.sign(c840 - ref)
            flip14 += np.where((new_sig != prev_sig) & ~np.isnan(prev_sig) & ~np.isnan(new_sig), new_sig, 0)
        rep(f"C2 {lab[:7]} 14:00 price flips a signal -> 14:01-15:00", np.sign(flip14) * last_hour, dts, flip14 != 0)
        # C3: stop entry at the nearest trigger, 8:45 -> 14:00
        rows = []
        for k in range(260, len(tr)):
            d = tr[k]
            if dts[k].year < 2018 or np.isnan(atr[d]): continue
            p0 = g.c[d, jof(845)]
            if np.isnan(p0): continue
            lv = []
            for i, n in enumerate(Ns):
                ref = cl[k - n]; s_prev = S[i, k - 1]
                if s_prev < 0 and ref > p0: lv.append((ref - p0, 1, ref))
                if s_prev > 0 and ref < p0: lv.append((p0 - ref, -1, ref))
            lv = [x for x in lv if x[0] <= 1.0 * atr[d]]
            if not lv: continue
            _, side, L = min(lv)
            hit = None
            for j in range(jof(846), jof(1400) + 1):
                if np.isnan(g.h[d, j]): continue
                if (side > 0 and g.h[d, j] >= L) or (side < 0 and g.l[d, j] <= L): hit = j; break
            if hit is None or hit + 1 > jof(1400): continue
            r_ = row(g, d, hit + 1, side, jof(1500), None, None)
            if r_ is None: continue
            e = r_["entry"]; stop = e - side * 0.3 * atr[d]
            r_ = row(g, d, hit + 1, side, jof(1500), stop, None)
            rows.append(r_)
        t3 = pd.DataFrame(rows)
        print("  " + summ(t3, f"C3 {lab[:7]} break of nearest trigger, stop 0.3 ATR", 60))
    print(f"\ncomparisons: {NT[0]} (plus the C3 rows); with this many, |t| >= 3 is the bar")
