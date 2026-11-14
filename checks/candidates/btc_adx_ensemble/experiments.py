"""Checker stress tests on the replica (items 1-7 of the brief). python3 experiments.py > (stdout)"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replica as RP
from compare import compare
HERE = os.path.dirname(os.path.abspath(__file__))
D = RP.get_data(); M = pd.read_csv(os.path.join(HERE, "trades.csv"))


def tt(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): return x[x > 0].sum() / -x[x < 0].sum() if (x < 0).any() else np.nan


def summ(T, lab):
    x = T.net; y = pd.to_datetime(T.t).dt.year
    by = x.groupby(y).sum()
    d = x.groupby(pd.to_datetime(T.t).dt.normalize()).sum()
    return (f"{lab:34s} n {len(x):4d} mean {x.mean():+.3f}R win {(x > 0).mean():.0%} PF {pf(x):.2f} t {tt(x):.2f} "
            f"| daily-sum t {tt(d):.2f} | 18-22 {x[y < 2023].mean():+.3f} 23+ {x[y >= 2023].mean():+.3f} (t {tt(x[y >= 2023]):.2f}) "
            f"| yrs+ {(by > 0).sum()}/{len(by)} | L {x[T.side == 1].mean():+.3f} S {x[T.side == -1].mean():+.3f}")


def match(T): r, _ = compare(M, T, verbose=False); return f"match vs maker {r['match_of_maker']:.1%}, R corr {r['corr']:.3f}"


base = RP.run(D)
print("== base replica"); print(summ(base, "replica base"), "|", match(base)); print(summ(M, "maker trades.csv"))

print("\n== 1. look-ahead: shift each input by one more candle (+1) and by one candle into the future (-1, planted leak)")
for kw in ({"ema_shift": 1}, {"vol_shift": 1}, {"h1_shift": 1}, {"ema_shift": 1, "vol_shift": 1, "h1_shift": 1},
           {"ema_shift": -1}, {"vol_shift": -1}, {"h1_shift": -1}):
    T = RP.run(D, **kw); print(summ(T, str(kw)), "|", match(T))

print("\n== 2. indicator definitions")
h1 = D["h1"]; H, L, C = (h1[k].to_numpy() for k in ("high", "low", "close"))
a1, a2, a3 = RP.adx_talib(H, L, C, 14), RP.adx_ewm(H, L, C, 14), RP.adx_sma(H, L, C, 14)
w = slice(500, None)
print(f"ADX talib vs ewm: max |diff| after 500 bars {np.nanmax(abs(a1[w] - a2[w])):.2e}; vs SMA-ADX corr {pd.Series(a1[w]).corr(pd.Series(a3[w])):.3f}, mean |diff| {np.nanmean(abs(a1[w] - a3[w])):.2f}")
atr_e = pd.Series(RP.tr_arr(H, L, C)).iloc[1:].ewm(alpha=1 / 14, adjust=False).mean().reindex(range(len(C))).to_numpy()
print(f"ATR talib vs ewm: max rel diff after 500 bars {np.nanmax(abs(RP.atr_talib(H, L, C, 14)[w] / atr_e[w] - 1)):.2e}")
# independent SuperTrend: classic pandas formulation (TradingView 'ta.supertrend') with RMA ATR
atr10 = pd.Series(RP.tr_arr(H, L, C)).ewm(alpha=1 / 10, adjust=False).mean().to_numpy()
hl2 = (H + L) / 2; up = hl2 - 3 * atr10; dn = hl2 + 3 * atr10; U = up.copy(); Dn = dn.copy(); tr_ = np.ones(len(C))
for i in range(1, len(C)):
    U[i] = max(up[i], U[i - 1]) if C[i - 1] > U[i - 1] else up[i]
    Dn[i] = min(dn[i], Dn[i - 1]) if C[i - 1] < Dn[i - 1] else dn[i]
    tr_[i] = 1 if (tr_[i - 1] == -1 and C[i] > Dn[i - 1]) else (-1 if (tr_[i - 1] == 1 and C[i] < U[i - 1]) else tr_[i - 1])
st = RP.supertrend(H, L, C); mine = np.sign(C - st)
print(f"SuperTrend direction agreement (replica vs TradingView-style) after 500 bars: {(mine[w] == tr_[w]).mean():.2%}")
for fn in ("ewm", "sma"):
    T = RP.run(D, adx_fn=fn); print(summ(T, f"ADX={fn}"), "|", match(T))
T = RP.run(D, no_adx=True); print(summ(T, "no ADX filter (both books)"))

print("\n== 3. fill realism")
for kw, lab in (({"fill": "price"}, "stops at stop-0.05%, targets/half at price"), ({"entry_delay": 1}, "entry one 15m candle late"),
                ({"fill": "price", "entry_delay": 1}, "both"), ({"fill": "price", "adverse": 0.002}, "stops at stop-0.20%"),
                ({"cost": 0.0012}, "costs 0.12%/side")):
    T = RP.run(D, **kw); print(summ(T, lab))
gd = base[base.why == "guard"]
print(f"guard exits {len(gd)}: mean {gd.net.mean():+.2f}R")
P = RP.run(D, fill="price"); print("exit reasons base / price-fill:", base.why.value_counts().to_dict(), P.why.value_counts().to_dict())
for w_ in ("stop", "tp"):
    print(f"  {w_}: close-fill mean {base[base.why == w_].net.mean():+.3f}R vs price-fill {P[P.why == w_].net.mean():+.3f}R")

print("\n== 4. independence")
for X, lab in ((base, "replica"), (M, "maker")):
    X = X.copy(); X["y"] = pd.to_datetime(X.t).dt.year; X["d"] = pd.to_datetime(X.t).dt.normalize()
    for per, m in (("all", X.y > 0), ("2018-22", X.y < 2023), ("2023+", X.y >= 2023)):
        for sd, ms in (("both", X.side != 0), ("long", X.side == 1), ("short", X.side == -1)):
            Z = X[m & ms]; ds = Z.groupby("d").net.sum()
            print(f"{lab:8s} {per:8s} {sd:5s} book40 n {(Z.book == 40).sum():3d} t {tt(Z[Z.book == 40].net):5.2f} | book50 n {(Z.book == 50).sum():3d} t {tt(Z[Z.book == 50].net):5.2f} "
                  f"| daily-sum days {len(ds):3d} mean {ds.mean():+.3f} t {tt(ds):5.2f}")
    same = X.groupby(["t", "side"]).book.nunique(); print(f"{lab}: entries shared by both books {int((same == 2).sum())} of {len(X)} rows; corr book40/book50 daily R",
          round(X.pivot_table(index="d", columns="book", values="net", aggfunc="sum").fillna(0).corr().iloc[0, 1], 3))

print("\n== 5. concentration")
for X, lab in ((base, "replica"), (M, "maker")):
    x = X.net.sort_values(ascending=False); k = int(np.ceil(len(x) * 0.05)); y = pd.to_datetime(X.t).dt.year
    by = X.net.groupby(y).sum(); bst = by.idxmax()
    print(f"{lab}: total {x.sum():.1f}R; top 5% ({k}) = {x.iloc[:k].sum():.1f}R = {x.iloc[:k].sum() / x.sum():.0%}; without them {x.iloc[k:].sum():.1f}R ({x.iloc[k:].mean():+.3f}/trade); "
          f"best year {bst} {by.max():.1f}R, without it {X.net[y != bst].sum():.1f}R ({X.net[y != bst].mean():+.3f}/trade, t {tt(X.net[y != bst]):.2f})")
    print("   by year R:", {int(k_): round(v, 1) for k_, v in by.items()})

print("\n== 6. neighbours")
for kw in ({"levels": (35,)}, {"levels": (40,)}, {"levels": (45,)}, {"levels": (50,)}, {"levels": (55,)}, {"levels": (60,)},
           {"levels": (35, 45)}, {"levels": (45, 55)}, {"levels": (30,)}, {"levels": (25,)},
           {"stop_atr": 2.0}, {"stop_atr": 3.0}, {"tp_atr": 6.0}, {"tp_atr": 10.0}):
    T = RP.run(D, **kw); print(summ(T, str(kw)))

print("\n== 7. drawdown (combined books, closed-trade R by exit time, 3% account per R, simple sum)")
for X, lab in ((base, "replica"), (M, "maker"), (P, "replica price-fill")):
    X = X.copy(); X["tx"] = pd.to_datetime(X.tx); X = X.sort_values("tx")
    eq = X.net.cumsum().to_numpy(); dd = eq - np.maximum.accumulate(np.r_[0, eq])[1:]
    i = dd.argmin(); pk = np.argmax(np.r_[0, eq][:i + 2]) if i else 0
    los = (X.net < 0).to_numpy(); run = best = 0
    for v in los: run = run + 1 if v else 0; best = max(best, run)
    hw = np.maximum.accumulate(np.r_[0, eq])[1:]; under = (eq < hw); dur = 0; mx = 0; st0 = None
    tx = X.tx.to_numpy()
    for j, u in enumerate(under):
        if u and st0 is None: st0 = tx[j - 1] if j else tx[j]
        if not u and st0 is not None: mx = max(mx, (tx[j] - st0) / np.timedelta64(1, "D")); st0 = None
    yr = X.groupby(X.tx.dt.year).net.apply(lambda s: (s.cumsum() - np.maximum.accumulate(np.r_[0, s.cumsum()])[1:]).min())
    print(f"{lab}: max DD {dd.min():.1f}R = {dd.min() * 3:.0f}% of account at 3%/R (ending {X.tx.iloc[i]:%Y-%m-%d}); longest losing streak {best} book trades; "
          f"longest underwater {mx:.0f} days; worst in-year DD R {yr.round(1).to_dict()}")
    # compounded at 3% per R
    w_ = np.cumprod(1 + 0.03 * X.net.to_numpy()); print(f"   compounded at 3%/R: max DD {((w_ / np.maximum.accumulate(w_)) - 1).min():.0%}, final x{w_[-1]:.1f}")

print("\n== placebo: ADX series rotated by random offsets (>= 60 days), both books")
rng = np.random.default_rng(7); nh = len(D["h1"]); rows = []
for k in range(40):
    off = int(rng.integers(24 * 60, nh - 24 * 60)); T = RP.run(D, adx_roll=off)
    rows.append(dict(run=k, n=len(T), mean=T.net.mean()))
    for v in T.net: pass
    T.assign(run=k)[["run", "date", "side", "net"]].to_csv(os.path.join(HERE, "placebo.csv"), mode="w" if k == 0 else "a", header=k == 0, index=False)
Pl = pd.DataFrame(rows); print(Pl.describe().round(3).to_string()); print(f"share of placebo means >= replica {base.net.mean():.3f}: {(Pl['mean'] >= base.net.mean()).mean():.3f}")
