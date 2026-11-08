"""Bitcoin weekend move -> S&P / Nasdaq Sunday open (user's clip, 2026-11-05: 'alpha 0, beta 0.4 of the S&P 500 on Bitcoin's weekend
return'). Coinbase spot BTC-USD 1-min (Central time) vs ES / NQ 1-min (CT).
  BTC weekend return = spot close Fri 16:00 -> Sun 17:00 CT. Gap = futures Fri last close (<= 16:00) -> Sun 17:01 open.
  1. Does BTC 'predict' the open? beta, R^2, sign agreement, 2018-22 vs 2023+ (the open itself cannot be traded: the market is shut).
  2. Tradable question: after the open, does the gap's miss vs the BTC-implied gap (residual, beta fitted on the previous 52 weekends
     only) predict the next move (Sun 17:01 -> 20:00, -> Mon 03:00, -> Mon 08:30) or Monday's regular session (08:30 -> 15:00)?
  3. Does the raw BTC weekend move predict those windows?
  python3 analysis/btc_weekend_beta_test.py > analysis/outputs/btc_weekend_beta_test_output.txt
"""
import sys, glob, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

sp = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/BTCUSD_spot_1min_*.csv"))])
sp = sp.drop_duplicates(["date", "time"]).set_index(["date", "time"]).close


def spot(dt, hhmm, back=10):
    for k in range(back):
        m = (hhmm // 100) * 60 + hhmm % 100 - k; t = (m // 60) * 100 + m % 60
        v = sp.get((dt, t))
        if v is not None: return v
    return np.nan


def last_close(g, r, upto):
    c = g.c[r, :jof(upto) + 1]; c = c[~np.isnan(c)]; return c[-1] if len(c) else np.nan


def first_open(g, r, frm, to=None):
    o = g.o[r, jof(frm):(jof(to) + 1 if to else None)]; o = o[~np.isnan(o)]; return o[0] if len(o) else np.nan


def close_at(g, r, hhmm):
    return last_close(g, r, hhmm)


def build(g, name):
    rows = []
    for f in range(g.D - 3):
        ts = pd.Timestamp(g.ts[f])
        if ts.dayofweek != 4 or ts < pd.Timestamp("2018-12-01"): continue
        s, m = f + 2, f + 3                                            # Sunday, Monday rows
        fc = last_close(g, f, 1600); so = first_open(g, s, 1701, 1730)
        if np.isnan(fc) or np.isnan(so): continue
        b0, b1 = spot(int(g.dates[f]), 1600), spot(int(g.dates[s]), 1700)
        if np.isnan(b0) or np.isnan(b1): continue
        c20, c03, c830 = close_at(g, s, 2000), close_at(g, m, 300), close_at(g, m, 830)
        o_rth, c_rth = first_open(g, m, 831, 900), close_at(g, m, 1500)
        rows.append(dict(date=ts, btc=np.log(b1 / b0), gap=np.log(so / fc), to20=np.log(c20 / so), to03=np.log(c03 / so),
                         to830=np.log(c830 / so), rth=np.log(c_rth / o_rth) if o_rth > 0 else np.nan, px=so))
    d = pd.DataFrame(rows).set_index("date")
    # walk-forward beta: previous 52 weekends only
    bet = []; X, Y = d.btc.to_numpy(), d.gap.to_numpy()
    for i in range(len(d)):
        a, b = X[max(0, i - 52):i], Y[max(0, i - 52):i]
        bet.append(np.polyfit(a, b, 1)[0] if len(a) >= 26 else np.nan)
    d["beta_wf"] = bet; d["resid"] = d.gap - d.beta_wf * d.btc
    return d


def reg(x, y):
    m = ~(np.isnan(x) | np.isnan(y)); x, y = x[m], y[m]
    b, a = np.polyfit(x, y, 1); r = np.corrcoef(x, y)[0, 1]
    e = y - (a + b * x); se = np.sqrt(e.var(ddof=2) / ((x - x.mean()) ** 2).sum())
    return b, r * r, b / se, np.mean(np.sign(x) == np.sign(y)), len(x)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for name, pk, pv, cost in (("ES", "scratch_data/ge.pkl", 50.0, 5.0 + 2 * 12.5), ("NQ", "scratch_data/g24_ext.pkl", 20.0, 7.25 + 2 * 5.0)):
        g = pickle.load(open(pk, "rb")); d = build(g, name)
        print(f"\n===== {name}: {len(d)} weekends {d.index[0].date()} -> {d.index[-1].date()}")
        print("1. Gap vs BTC weekend return (beta, R^2, t, sign agreement):")
        for per, x in (("all", d), ("2018-22", d[d.index < "2023"]), ("2023+", d[d.index >= "2023"]), ("2025+", d[d.index >= "2025"])):
            b, r2, t, hit, n = reg(x.btc.values, x.gap.values)
            print(f"   {per:<8} n={n:3d} beta {b:5.3f}  R^2 {r2:5.1%}  t {t:5.1f}  same sign {hit:5.1%}")
        big = d[d.btc.abs() >= 0.05]
        b, r2, t, hit, n = reg(big.btc.values, big.gap.values)
        print(f"   |BTC| >= 5%: n={n} beta {b:.3f} R^2 {r2:.1%} same sign {hit:.1%}")
        print("2. After the open: does the residual (gap - walk-forward beta x BTC) predict the next move? (negative beta = fade works)")
        for col in ("to20", "to03", "to830", "rth"):
            for per, x in (("2019-22", d[d.index < "2023"]), ("2023+", d[d.index >= "2023"])):
                b, r2, t, hit, n = reg(x.resid.values, x[col].values)
                print(f"   resid -> {col:<6} {per:<8} n={n:3d} slope {b:6.3f} t {t:5.1f} R^2 {r2:4.1%}")
        print("3. Raw BTC weekend move -> the same windows:")
        for col in ("to20", "to830", "rth"):
            b, r2, t, hit, n = reg(d.btc.values, d[col].values)
            print(f"   btc -> {col:<6} n={n:3d} slope {b:6.3f} t {t:5.1f} same sign {hit:5.1%}")
        # simple trade on the residual: fade |resid| beyond 1 sd of the previous 52 weekends, 17:01 -> 08:30, per contract
        sd = d.resid.rolling(52, min_periods=26).std().shift(1); sig = -np.sign(d.resid) * (d.resid.abs() > sd)
        pnl = (sig * d.to830 * d.px * pv - (sig != 0) * cost)[sig != 0]
        if len(pnl) > 5:
            print(f"4. Fade the residual (|resid| > 1 sd, 17:01 -> Mon 08:30): {len(pnl)} trades ${pnl.mean():.0f} a trade, t {pnl.mean() / pnl.std() * np.sqrt(len(pnl)):.1f}, "
                  f"2023+ ${pnl[pnl.index >= '2023'].mean():.0f}")
        d.to_csv(f"analysis/outputs/btc_weekend_beta_{name}.csv")
