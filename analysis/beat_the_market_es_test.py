"""'Beat the Market' intraday momentum (Zarattini, Aziz, Barbon, SSRN 4824172), the user's EasyLanguage SPY replication
(2026-10-25; checks/candidates/beat_the_market_spy/). Questions: does the 30-minute-bar VWAP behave like the paper's
1-minute VWAP, why is the hit ratio lower and the drawdown shallower? Run on ES 1-minute RTH bars (08:31-15:00 CT =
09:30-16:00 ET) as an SPY proxy (same index; SPY ~ ES / 10), 2018-2026 (2017 = warm-up).
  Rule (the user's code, StopMode 1, dynamic sizing): sigma(slot) = mean |close(slot) / open - 1| over the prior LookBack
  days for each 30-minute close; UB = max(open, prior close) x (1 + sigma), LB = min(...) x (1 - sigma). At each 30-minute
  close 10:00-15:30 ET: exit a long if close <= max(UB, VWAP) (short mirror); then, if flat, long if close > max(UB, VWAP),
  short if close < min(LB, VWAP). Flat at the 16:00 ET close. Size = equity x min(4, 0.02 / 14-day stdev of daily returns),
  compounded daily. Costs as a fraction of price: the paper's $0.0035 + $0.001 per SPY share each side (SPY = ES / 10).
  Variants: VWAP from 30-minute bars (the user's: (H+L+C)/3 x volume per 30-min bar) vs from 1-minute bars (the paper);
  fill at the signal close (the paper and the user) vs the next minute's open; LookBack 90 vs 14; slippage $0.005.
  python3 analysis/beat_the_market_es_test.py [SCRATCH_DIR] > analysis/outputs/beat_the_market_es_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
g = pickle.load(open(SP + "ge.pkl", "rb"))
J0, J1 = jof(831), jof(1500)
tr = g.trading; full = ~np.isnan(g.c[tr, J1]) & ~np.isnan(g.o[tr, J0]); tr = tr[full]
dts = pd.DatetimeIndex(g.ts[tr])
C1 = np.array([pd.Series(g.c[r, J0:J1 + 1]).ffill().bfill().to_numpy() for r in tr])          # 390 one-minute closes
O1 = np.array([pd.Series(g.o[r, J0:J1 + 1]).fillna(pd.Series(g.c[r, J0:J1 + 1]).ffill()).bfill().to_numpy() for r in tr])
H1 = np.array([pd.Series(g.h[r, J0:J1 + 1]).fillna(pd.Series(g.c[r, J0:J1 + 1]).ffill()).bfill().to_numpy() for r in tr])
L1 = np.array([pd.Series(g.l[r, J0:J1 + 1]).fillna(pd.Series(g.c[r, J0:J1 + 1]).ffill()).bfill().to_numpy() for r in tr])
V1 = np.nan_to_num(g.v[tr, J0:J1 + 1])
OPEN = O1[:, 0]; CLOSE = C1[:, -1]; PC = np.r_[np.nan, CLOSE[:-1]]
K = np.arange(29, 390, 30)                                  # 30-min closes: 10:00 ... 16:00 ET (13 of them)
CK = C1[:, K]
tp1 = (H1 + L1 + C1) / 3; vw1 = np.cumsum(tp1 * V1, 1) / np.maximum(np.cumsum(V1, 1), 1)
H30 = np.maximum.reduceat(H1, np.arange(0, 390, 30), axis=1); L30 = np.minimum.reduceat(L1, np.arange(0, 390, 30), axis=1)
V30 = np.add.reduceat(V1, np.arange(0, 390, 30), axis=1); tp30 = (H30 + L30 + CK) / 3
vw30 = np.cumsum(tp30 * V30, 1) / np.maximum(np.cumsum(V30, 1), 1)
dret = pd.Series(CLOSE).pct_change()
vol14 = dret.rolling(14).std().shift(1).to_numpy()            # known before the open (uses closes to yesterday)


def run(lookback=90, vwap="30m", fill="close", slip=0.001, comm=0.0035, start="2018-01-01"):
    sig = pd.DataFrame(np.abs(CK / OPEN[:, None] - 1)).rolling(lookback).mean().shift(1).to_numpy()
    UB = np.fmax(OPEN, PC)[:, None] * (1 + sig); LB = np.fmin(OPEN, PC)[:, None] * (1 - sig)
    VW = vw30 if vwap == "30m" else vw1[:, K]
    cps = (slip + comm) / (CK / 10)                           # cost per side as a fraction of price (SPY = ES / 10)
    lev = np.where(np.isfinite(vol14), np.minimum(4.0, 0.02 / vol14), 1.0)
    rows, day_r = [], np.zeros(len(tr))
    for d in range(len(tr)):
        if dts[d] < pd.Timestamp(start) or np.isnan(sig[d]).any(): continue
        pos, ep, ek, r = 0, 0.0, 0, 0.0
        for k in range(13):
            c = CK[d, k]; ls, ss = max(UB[d, k], VW[d, k]), min(LB[d, k], VW[d, k])
            px = c if fill == "close" else (O1[d, K[k] + 1] if K[k] + 1 < 390 else c)
            if k == 12:                                       # 16:00 ET: exit on close
                if pos: x = c; t = pos * (x / ep - 1) - cps[d, k] - cps[d, ek]; rows.append((d, pos, t)); r += t; pos = 0
                break
            if pos == 1 and c <= ls or pos == -1 and c >= ss:
                t = pos * (px / ep - 1) - cps[d, k] - cps[d, ek]; rows.append((d, pos, t)); r += t; pos = 0
            if pos == 0:
                if c > ls: pos, ep, ek = 1, px, k
                elif c < ss: pos, ep, ek = -1, px, k
        day_r[d] = r * lev[d]
    T = pd.DataFrame(rows, columns=["d", "side", "r"]); T["r_lev"] = T.r * lev[T.d]
    sel = dts >= pd.Timestamp(start); R = pd.Series(day_r[sel], index=dts[sel])
    nav = (1 + R).cumprod(); dd = (nav / nav.cummax() - 1).min(); yrs = len(R) / 252
    traded = R[R != 0]
    return dict(total=nav.iloc[-1] - 1, irr=nav.iloc[-1] ** (1 / yrs) - 1, vol=R.std() * np.sqrt(252), sharpe=R.mean() / R.std() * np.sqrt(252),
                mdd=dd, trips=len(T), hit_trip=(T.r > 0).mean(), hit_day=(traded > 0).mean(), win_loss=T.r[T.r > 0].mean() / -T.r[T.r < 0].mean(),
                cost_share=None), T, R


def show(nm, res):
    s, T, R = res
    return (f"   {nm:<44} total {s['total']:7.0%}  IRR {s['irr']:5.1%}  vol {s['vol']:5.1%}  Sharpe {s['sharpe']:4.2f}  MDD {s['mdd']:6.1%}  "
            f"round trips {s['trips']:5d}  hit/trip {s['hit_trip']:5.1%}  hit/day {s['hit_day']:5.1%}  avg win/avg loss {s['win_loss']:4.2f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    print(f"\nES RTH days {len(tr)} ({dts[0].date()} .. {dts[-1].date()}); results 2018-01-02 onward, costs = the paper's unless stated.")
    base = run()
    print(show("the user's version (LB 90, 30-min VWAP, fill at close)", base))
    print(show("paper VWAP (1-minute bars)", run(vwap="1m")))
    print(show("fill at the next minute's open", run(fill="next")))
    print(show("1-min VWAP + next-minute fill", run(vwap="1m", fill="next")))
    print(show("LookBack 14 (paper base)", run(lookback=14)))
    print(show("slippage $0.005 / share (~half a cent spread)", run(slip=0.005)))
    print(show("no costs", run(slip=0, comm=0)))
    print(show("ES futures costs ($5 round trip + 1 tick a side = $0.03 a SPY share a side)", run(slip=0.0265, comm=0.0035)))
    print(show("ES futures costs, LookBack 14", run(lookback=14, slip=0.0265, comm=0.0035)))
    print(show("2018-2026, 30-min VWAP, from 2019 (check)", run(start="2019-01-01")))
    a, b = vw30[:, :12], vw1[:, K[:12]]
    diff = (a - b) / b * 1e4
    print(f"\n   30-min vs 1-min VWAP at the decision points: mean difference {np.nanmean(diff):+.2f} bp, mean |difference| "
          f"{np.nanmean(np.abs(diff)):.2f} bp, 95th pct {np.nanpercentile(np.abs(diff), 95):.1f} bp; the band sits ~"
          f"{np.nanmean(pd.DataFrame(np.abs(CK / OPEN[:, None] - 1)).rolling(90).mean().shift(1).to_numpy()) * 1e4:.0f} bp from the open")
    s1, T1, R1 = base; s2, T2, R2 = run(vwap="1m")
    agree = (np.sign(R1) == np.sign(R2)) | ((R1 == 0) & (R2 == 0))
    print(f"   same-day result sign agreement 30-min vs 1-min VWAP: {agree.mean():.0%}; daily return corr {np.corrcoef(R1, R2)[0, 1]:.2f}")
    print("\n   by year (user's version):", {y: f"{v:+.0%}" for y, v in ((1 + R1).groupby(R1.index.year).prod() - 1).items()})
    print("   by year (1-min VWAP):     ", {y: f"{v:+.0%}" for y, v in ((1 + R2).groupby(R2.index.year).prod() - 1).items()})
