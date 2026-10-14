"""WorldQuant's 101 Formulaic Alphas (Kakushadze 2015, SSRN 2701346) on NQ (user's upload, 2026-10-14).

The paper's alphas are cross-sectional stock weights (rank across ~2,000 stocks, industry-neutralized, held 0.6-6.4
days, 2010-13, no costs). One instrument has no cross-section, so the time-series port is:
  rank(x)          -> percentile of x among its own last 60 days
  IndNeutralize(x) -> x;  cap -> 1;  scale(x) -> x / mean |x| over 60 days;  min/max of two series elementwise
  daily bar        -> NQ regular session 8:30-15:00 CT (open, high, low, close, volume, vwap); returns close to close;
                      adv{d} = d-day mean of close x volume
Trade (delay-1, flat by 15:59): the alpha at day t-1's 15:00 close sets day t's position, 8:30 open -> 14:59 close,
1 NQ, $7.25 + 2 ticks ($17.25) a round trip.
  "sign"     long if the alpha is above its own 60-day median, short if below (trades almost every day)
  "extreme"  long only in its top 20% of the last 60 days, short only in its bottom 20%
Design = first valid day (warm-up up to ~2 years) .. 2022; holdout 2023-26. 101 alphas x 2 rules = multiple testing,
so the check is the cross-section: do design winners stay winners, versus 200 random-sign runs?
Combination ("mega-alpha", the paper's own use): vote of all 101 signs; vote of the design winners only.
ES (2017-26) as the second instrument.
  python3 analysis/alpha101_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
RK = 60
SPLIT = pd.Timestamp("2023-01-01")
SPEC = {"NQ": (20.0, 7.25 + 2 * 0.25 * 20.0), "ES": (50.0, 5.0 + 2 * 0.25 * 50.0)}


# ---------------- operators (time-series port) ----------------
def W(d): return max(1, int(np.floor(d)))
def rank(x): return x.rolling(RK, min_periods=RK).rank(pct=True)
def delay(x, d): return x.shift(W(d))
def delta(x, d): return x - x.shift(W(d))
def correlation(x, y, d):
    r = x.rolling(W(d)).corr(y); return r.replace([np.inf, -np.inf], np.nan).clip(-1, 1)
def covariance(x, y, d): return x.rolling(W(d)).cov(y)
def scale(x, a=1.0): return a * x / x.abs().rolling(RK).mean()
def signedpower(x, a): return np.sign(x) * np.abs(x) ** a
def decay_linear(x, d):
    w = np.arange(1, W(d) + 1, dtype=float); w /= w.sum()
    return x.rolling(W(d)).apply(lambda v: np.dot(v, w), raw=True)
def ts_min(x, d): return x.rolling(W(d)).min()
def ts_max(x, d): return x.rolling(W(d)).max()
def ts_argmax(x, d): return x.rolling(W(d)).apply(np.argmax, raw=True) + 1
def ts_argmin(x, d): return x.rolling(W(d)).apply(np.argmin, raw=True) + 1
def ts_rank(x, d): return x.rolling(W(d)).rank(pct=True)
def ssum(x, d): return x.rolling(W(d)).sum()
def product(x, d): return x.rolling(W(d)).apply(np.prod, raw=True)
def stddev(x, d): return x.rolling(W(d)).std()
def sign(x): return np.sign(x)
def log(x): return np.log(x)
def ind(x, *_): return x
def emax(a, b): return pd.concat([a, b], axis=1).max(axis=1, skipna=False)
def emin(a, b): return pd.concat([a, b], axis=1).min(axis=1, skipna=False)
def lt(a, b): return (a < b).astype(float).where(a.notna() & b.notna())
def iff(cond, a, b):
    """cond ? a : b, NaN where the condition can't be computed."""
    a = a if isinstance(a, pd.Series) else pd.Series(a, index=cond.index)
    b = b if isinstance(b, pd.Series) else pd.Series(b, index=cond.index)
    return a.where(cond.astype(bool), b).where(cond.notna())
def gt(a, b): return lt(b, a)


def daily_bars(g):
    j0, j1 = jof(831), jof(1500)
    rows = g.trading
    o = g.o[rows, j0]; h = np.nanmax(g.h[rows, j0:j1 + 1], 1); l = np.nanmin(g.l[rows, j0:j1 + 1], 1)
    cc = pd.DataFrame(g.c[rows, j0:j1 + 1]).ffill(axis=1).iloc[:, -1].to_numpy()
    vv = np.nan_to_num(g.v[rows, j0:j1 + 1]); px = np.nan_to_num(g.c[rows, j0:j1 + 1])
    v = vv.sum(1); vwap = (px * vv).sum(1) / np.where(v > 0, v, np.nan)
    idx = pd.DatetimeIndex(g.ts[rows])
    B = pd.DataFrame(dict(open=o, high=h, low=l, close=cc, volume=v, vwap=vwap, row=rows), index=idx)
    B = B[B.open.notna() & (B.volume > 0)]
    B["vwap"] = B.vwap.fillna((B.high + B.low + B.close) / 3)
    return B


def alphas(B):
    open, high, low, close, volume, vwap = (B[k] for k in ("open", "high", "low", "close", "volume", "vwap"))
    returns = close.pct_change(); cap = pd.Series(1.0, index=B.index)
    adv = {d: (close * volume).rolling(d).mean() for d in (5, 10, 15, 20, 30, 40, 50, 60, 81, 120, 150, 180)}
    adv20 = adv[20]; one = pd.Series(1.0, index=B.index)
    hl2 = (high + low) / 2
    A = {}
    A[1] = rank(ts_argmax(signedpower(iff(lt(returns, 0 * one), stddev(returns, 20), close), 2.), 5)) - 0.5
    A[2] = -1 * correlation(rank(delta(log(volume), 2)), rank((close - open) / open), 6)
    A[3] = -1 * correlation(rank(open), rank(volume), 10)
    A[4] = -1 * ts_rank(rank(low), 9)
    A[5] = rank(open - ssum(vwap, 10) / 10) * (-1 * abs(rank(close - vwap)))
    A[6] = -1 * correlation(open, volume, 10)
    A[7] = iff(lt(adv20, volume), (-1 * ts_rank(abs(delta(close, 7)), 60)) * sign(delta(close, 7)), -1 * one)
    A[8] = -1 * rank((ssum(open, 5) * ssum(returns, 5)) - delay(ssum(open, 5) * ssum(returns, 5), 10))
    d1 = delta(close, 1)
    A[9] = iff(lt(0 * one, ts_min(d1, 5)), d1, iff(lt(ts_max(d1, 5), 0 * one), d1, -1 * d1))
    A[10] = rank(iff(lt(0 * one, ts_min(d1, 4)), d1, iff(lt(ts_max(d1, 4), 0 * one), d1, -1 * d1)))
    A[11] = (rank(ts_max(vwap - close, 3)) + rank(ts_min(vwap - close, 3))) * rank(delta(volume, 3))
    A[12] = sign(delta(volume, 1)) * (-1 * d1)
    A[13] = -1 * rank(covariance(rank(close), rank(volume), 5))
    A[14] = (-1 * rank(delta(returns, 3))) * correlation(open, volume, 10)
    A[15] = -1 * ssum(rank(correlation(rank(high), rank(volume), 3)), 3)
    A[16] = -1 * rank(covariance(rank(high), rank(volume), 5))
    A[17] = ((-1 * rank(ts_rank(close, 10))) * rank(delta(d1, 1))) * rank(ts_rank(volume / adv20, 5))
    A[18] = -1 * rank((stddev(abs(close - open), 5) + (close - open)) + correlation(close, open, 10))
    A[19] = (-1 * sign((close - delay(close, 7)) + delta(close, 7))) * (1 + rank(1 + ssum(returns, 250)))
    A[20] = ((-1 * rank(open - delay(high, 1))) * rank(open - delay(close, 1))) * rank(open - delay(low, 1))
    m8, s8, m2 = ssum(close, 8) / 8, stddev(close, 8), ssum(close, 2) / 2
    A[21] = iff(lt(m8 + s8, m2), -1 * one, iff(lt(m2, m8 - s8), one, iff(gt(volume / adv20, one) + (volume / adv20 == 1), one, -1 * one)))
    A[22] = -1 * (delta(correlation(high, volume, 5), 5) * rank(stddev(close, 20)))
    A[23] = iff(lt(ssum(high, 20) / 20, high), -1 * delta(high, 2), 0 * one)
    c100 = delta(ssum(close, 100) / 100, 100) / delay(close, 100)
    A[24] = iff(lt(c100, 0.05 * one) + (c100 == 0.05), -1 * (close - ts_min(close, 100)), -1 * delta(close, 3))
    A[25] = rank((((-1 * returns) * adv20) * vwap) * (high - close))
    A[26] = -1 * ts_max(correlation(ts_rank(volume, 5), ts_rank(high, 5), 5), 3)
    A[27] = iff(lt(0.5 * one, rank(ssum(correlation(rank(volume), rank(vwap), 6), 2) / 2.0)), -1 * one, one)
    A[28] = scale((correlation(adv20, low, 5) + hl2) - close)
    A[29] = ts_min(product(rank(rank(scale(log(ssum(ts_min(rank(rank(-1 * rank(delta(close - 1, 5)))), 2), 1))))), 1), 5) \
        + ts_rank(delay(-1 * returns, 6), 5)
    A[30] = ((1.0 - rank(sign(close - delay(close, 1)) + sign(delay(close, 1) - delay(close, 2)) + sign(delay(close, 2) - delay(close, 3))))
             * ssum(volume, 5)) / ssum(volume, 20)
    A[31] = (rank(rank(rank(decay_linear(-1 * rank(rank(delta(close, 10))), 10)))) + rank(-1 * delta(close, 3))) \
        + sign(scale(correlation(adv20, low, 12)))
    A[32] = scale(ssum(close, 7) / 7 - close) + 20 * scale(correlation(vwap, delay(close, 5), 230))
    A[33] = rank(-1 * (1 - open / close))
    A[34] = rank((1 - rank(stddev(returns, 2) / stddev(returns, 5))) + (1 - rank(delta(close, 1))))
    A[35] = (ts_rank(volume, 32) * (1 - ts_rank((close + high) - low, 16))) * (1 - ts_rank(returns, 32))
    A[36] = (((2.21 * rank(correlation(close - open, delay(volume, 1), 15))) + (0.7 * rank(open - close)))
             + (0.73 * rank(ts_rank(delay(-1 * returns, 6), 5)))) + rank(abs(correlation(vwap, adv20, 6))) \
        + (0.6 * rank((ssum(close, 200) / 200 - open) * (close - open)))
    A[37] = rank(correlation(delay(open - close, 1), close, 200)) + rank(open - close)
    A[38] = (-1 * rank(ts_rank(close, 10))) * rank(close / open)
    A[39] = (-1 * rank(delta(close, 7) * (1 - rank(decay_linear(volume / adv20, 9))))) * (1 + rank(ssum(returns, 250)))
    A[40] = (-1 * rank(stddev(high, 10))) * correlation(high, volume, 10)
    A[41] = (high * low) ** 0.5 - vwap
    A[42] = rank(vwap - close) / rank(vwap + close)
    A[43] = ts_rank(volume / adv20, 20) * ts_rank(-1 * delta(close, 7), 8)
    A[44] = -1 * correlation(high, rank(volume), 5)
    A[45] = -1 * ((rank(ssum(delay(close, 5), 20) / 20) * correlation(close, volume, 2)) * rank(correlation(ssum(close, 5), ssum(close, 20), 2)))
    sl = (delay(close, 20) - delay(close, 10)) / 10 - (delay(close, 10) - close) / 10
    A[46] = iff(lt(0.25 * one, sl), -1 * one, iff(lt(sl, 0 * one), one, -1 * d1))
    A[47] = (((rank(1 / close) * volume) / adv20) * ((high * rank(high - close)) / (ssum(high, 5) / 5))) - rank(vwap - delay(vwap, 5))
    A[48] = ind((correlation(delta(close, 1), delta(delay(close, 1), 1), 250) * delta(close, 1)) / close) / ssum((delta(close, 1) / delay(close, 1)) ** 2, 250)
    A[49] = iff(lt(sl, -0.1 * one), one, -1 * d1)
    A[50] = -1 * ts_max(rank(correlation(rank(volume), rank(vwap), 5)), 5)
    A[51] = iff(lt(sl, -0.05 * one), one, -1 * d1)
    A[52] = (((-1 * ts_min(low, 5)) + delay(ts_min(low, 5), 5)) * rank((ssum(returns, 240) - ssum(returns, 20)) / 220)) * ts_rank(volume, 5)
    A[53] = -1 * delta(((close - low) - (high - close)) / (close - low).replace(0, np.nan), 9)
    A[54] = (-1 * ((low - close) * open ** 5)) / ((low - high).replace(0, np.nan) * close ** 5)
    A[55] = -1 * correlation(rank((close - ts_min(low, 12)) / (ts_max(high, 12) - ts_min(low, 12))), rank(volume), 6)
    A[56] = 0 - (1 * (rank(ssum(returns, 10) / ssum(ssum(returns, 2), 3)) * rank(returns * cap)))
    A[57] = 0 - (1 * ((close - vwap) / decay_linear(rank(ts_argmax(close, 30)), 2)))
    A[58] = -1 * ts_rank(decay_linear(correlation(ind(vwap), volume, 3.92795), 7.89291), 5.50322)
    A[59] = -1 * ts_rank(decay_linear(correlation(ind(vwap * 0.728317 + vwap * (1 - 0.728317)), volume, 4.25197), 16.2289), 8.19648)
    clv = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
    A[60] = 0 - (1 * ((2 * scale(rank(clv * volume))) - scale(rank(ts_argmax(close, 10)))))
    A[61] = lt(rank(vwap - ts_min(vwap, 16.1219)), rank(correlation(vwap, adv[180], 17.9282)))
    A[62] = lt(rank(correlation(vwap, ssum(adv20, 22.4101), 9.91009)), lt(rank(open) + rank(open), rank(hl2) + rank(high))) * -1
    A[63] = (rank(decay_linear(delta(ind(close), 2.25164), 8.22237))
             - rank(decay_linear(correlation(vwap * 0.318108 + open * (1 - 0.318108), ssum(adv[180], 37.2467), 13.557), 12.2883))) * -1
    A[64] = lt(rank(correlation(ssum(open * 0.178404 + low * (1 - 0.178404), 12.7054), ssum(adv[120], 12.7054), 16.6208)),
               rank(delta(hl2 * 0.178404 + vwap * (1 - 0.178404), 3.69741))) * -1
    A[65] = lt(rank(correlation(open * 0.00817205 + vwap * (1 - 0.00817205), ssum(adv[60], 8.6911), 6.40374)),
               rank(open - ts_min(open, 13.635))) * -1
    A[66] = (rank(decay_linear(delta(vwap, 3.51013), 7.23052))
             + ts_rank(decay_linear(((low * 0.96633 + low * (1 - 0.96633)) - vwap) / (open - hl2).replace(0, np.nan), 11.4157), 6.72611)) * -1
    A[67] = (rank(high - ts_min(high, 2.14593)) ** rank(correlation(ind(vwap), ind(adv20), 6.02936))) * -1
    A[68] = lt(ts_rank(correlation(rank(high), rank(adv[15]), 8.91644), 13.9333), rank(delta(close * 0.518371 + low * (1 - 0.518371), 1.06157))) * -1
    A[69] = (rank(ts_max(delta(ind(vwap), 2.72412), 4.79344)) ** ts_rank(correlation(close * 0.490655 + vwap * (1 - 0.490655), adv20, 4.92416), 9.0615)) * -1
    A[70] = (rank(delta(vwap, 1.29456)) ** ts_rank(correlation(ind(close), adv[50], 17.8256), 17.9171)) * -1
    A[71] = emax(ts_rank(decay_linear(correlation(ts_rank(close, 3.43976), ts_rank(adv[180], 12.0647), 18.0175), 4.20501), 15.6948),
                 ts_rank(decay_linear(rank((low + open) - (vwap + vwap)) ** 2, 16.4662), 4.4388))
    A[72] = rank(decay_linear(correlation(hl2, adv[40], 8.93345), 10.1519)) / \
        rank(decay_linear(correlation(ts_rank(vwap, 3.72469), ts_rank(volume, 18.5188), 6.86671), 2.95011))
    w_ = open * 0.147155 + low * (1 - 0.147155)
    A[73] = emax(rank(decay_linear(delta(vwap, 4.72775), 2.91864)), ts_rank(decay_linear((delta(w_, 2.03608) / w_) * -1, 3.33829), 16.7411)) * -1
    A[74] = lt(rank(correlation(close, ssum(adv[30], 37.4843), 15.1365)),
               rank(correlation(rank(high * 0.0261661 + vwap * (1 - 0.0261661)), rank(volume), 11.4791))) * -1
    A[75] = lt(rank(correlation(vwap, volume, 4.24304)), rank(correlation(rank(low), rank(adv[50]), 12.4413)))
    A[76] = emax(rank(decay_linear(delta(vwap, 1.24383), 11.8259)),
                 ts_rank(decay_linear(ts_rank(correlation(ind(low), adv[81], 8.14941), 19.569), 17.1543), 19.383)) * -1
    A[77] = emin(rank(decay_linear((hl2 + high) - (vwap + high), 20.0451)), rank(decay_linear(correlation(hl2, adv[40], 3.1614), 5.64125)))
    A[78] = rank(correlation(ssum(low * 0.352233 + vwap * (1 - 0.352233), 19.7428), ssum(adv[40], 19.7428), 6.83313)) ** \
        rank(correlation(rank(vwap), rank(volume), 5.77492))
    A[79] = lt(rank(delta(ind(close * 0.60733 + open * (1 - 0.60733)), 1.23438)), rank(correlation(ts_rank(vwap, 3.60973), ts_rank(adv[150], 9.18637), 14.6644)))
    A[80] = (rank(sign(delta(ind(open * 0.868128 + high * (1 - 0.868128)), 4.04545))) ** ts_rank(correlation(high, adv[10], 5.11456), 5.53756)) * -1
    A[81] = lt(rank(log(product(rank(rank(correlation(vwap, ssum(adv[10], 49.6054), 8.47743)) ** 4), 14.9655))),
               rank(correlation(rank(vwap), rank(volume), 5.07914))) * -1
    A[82] = emin(rank(decay_linear(delta(open, 1.46063), 14.8717)),
                 ts_rank(decay_linear(correlation(ind(volume), open * 0.634196 + open * (1 - 0.634196), 17.4842), 6.92131), 13.4283)) * -1
    hlc = (high - low) / (ssum(close, 5) / 5)
    A[83] = (rank(delay(hlc, 2)) * rank(rank(volume))) / (hlc / (vwap - close).replace(0, np.nan))
    A[84] = signedpower(ts_rank(vwap - ts_max(vwap, 15.3217), 20.7127), delta(close, 4.96796))
    A[85] = rank(correlation(high * 0.876703 + close * (1 - 0.876703), adv[30], 9.61331)) ** \
        rank(correlation(ts_rank(hl2, 3.70596), ts_rank(volume, 10.1595), 7.11408))
    A[86] = lt(ts_rank(correlation(close, ssum(adv20, 14.7444), 6.00049), 20.4195), rank((open + close) - (vwap + open))) * -1
    A[87] = emax(rank(decay_linear(delta(close * 0.369701 + vwap * (1 - 0.369701), 1.91233), 2.65461)),
                 ts_rank(decay_linear(abs(correlation(ind(adv[81]), close, 13.4132)), 4.89768), 14.4535)) * -1
    A[88] = emin(rank(decay_linear((rank(open) + rank(low)) - (rank(high) + rank(close)), 8.06882)),
                 ts_rank(decay_linear(correlation(ts_rank(close, 8.44728), ts_rank(adv[60], 20.6966), 8.01266), 6.65053), 2.61957))
    A[89] = ts_rank(decay_linear(correlation(low * 0.967285 + low * (1 - 0.967285), adv[10], 6.94279), 5.51607), 3.79744) \
        - ts_rank(decay_linear(delta(ind(vwap), 3.48158), 10.1466), 15.3012)
    A[90] = (rank(close - ts_max(close, 4.66719)) ** ts_rank(correlation(ind(adv[40]), low, 5.38375), 3.21856)) * -1
    A[91] = (ts_rank(decay_linear(decay_linear(correlation(ind(close), volume, 9.74928), 16.398), 3.83219), 4.8667)
             - rank(decay_linear(correlation(vwap, adv[30], 4.01303), 2.6809))) * -1
    A[92] = emin(ts_rank(decay_linear(lt(hl2 + close, low + open), 14.7221), 18.8683),
                 ts_rank(decay_linear(correlation(rank(low), rank(adv[30]), 7.58555), 6.94024), 6.80584))
    A[93] = ts_rank(decay_linear(correlation(ind(vwap), adv[81], 17.4193), 19.848), 7.54455) / \
        rank(decay_linear(delta(close * 0.524434 + vwap * (1 - 0.524434), 2.77377), 16.2664))
    A[94] = (rank(vwap - ts_min(vwap, 11.5783)) ** ts_rank(correlation(ts_rank(vwap, 19.6462), ts_rank(adv[60], 4.02992), 18.0926), 2.70756)) * -1
    A[95] = lt(rank(open - ts_min(open, 12.4105)), ts_rank(rank(correlation(ssum(hl2, 19.1351), ssum(adv[40], 19.1351), 12.8742)) ** 5, 11.7584))
    A[96] = emax(ts_rank(decay_linear(correlation(rank(vwap), rank(volume), 3.83878), 4.16783), 8.38151),
                 ts_rank(decay_linear(ts_argmax(correlation(ts_rank(close, 7.45404), ts_rank(adv[60], 4.13242), 3.65459), 12.6556), 14.0365), 13.4143)) * -1
    A[97] = (rank(decay_linear(delta(ind(low * 0.721001 + vwap * (1 - 0.721001)), 3.3705), 20.4523))
             - ts_rank(decay_linear(ts_rank(correlation(ts_rank(low, 7.87871), ts_rank(adv[60], 17.255), 4.97547), 18.5925), 15.7152), 6.71659)) * -1
    A[98] = rank(decay_linear(correlation(vwap, ssum(adv[5], 26.4719), 4.58418), 7.18088)) \
        - rank(decay_linear(ts_rank(ts_argmin(correlation(rank(open), rank(adv[15]), 20.8187), 8.62571), 6.95668), 8.07206))
    A[99] = lt(rank(correlation(ssum(hl2, 19.8975), ssum(adv[60], 19.8975), 8.8136)), rank(correlation(low, volume, 6.28259))) * -1
    A[100] = 0 - (1 * ((1.5 * scale(ind(ind(rank(clv * volume))))) - scale(ind(correlation(close, rank(adv20), 5) - rank(ts_argmin(close, 30)))))
                   * (volume / adv20))
    A[101] = (close - open) / ((high - low) + 0.001)
    return pd.DataFrame({k: pd.Series(v, index=B.index).replace([np.inf, -np.inf], np.nan) for k, v in A.items()})


def positions(S, rule):
    """Position for day t from the alpha at day t-1's close."""
    if rule == "sign":
        med = S.rolling(RK, min_periods=RK).median()
        p = np.sign(S - med).where(S.notna() & med.notna())
    else:
        r = S.rolling(RK, min_periods=RK).rank(pct=True)
        p = pd.DataFrame(np.where(r >= 0.8, 1.0, np.where(r <= 0.2, -1.0, 0.0)), index=S.index, columns=S.columns).where(r.notna())
    return p.shift(1)


def day_moves(g, B, pv, cost):
    """$ per contract, long, 8:30 open -> 14:59 close, and the cost."""
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    x = cf[B.row.values * 1440 + jof(1459)]
    return pd.Series((x - B.open.values) * pv, index=B.index), cost


def stats(pnl):
    p = pnl.dropna(); p = p[p != 0]
    if len(p) < 30: return dict(n=len(p), avg=np.nan, t=np.nan, d=np.nan, h=np.nan, td=np.nan, th=np.nan, yrs="")
    y = p.index.year; d, h = p[p.index < SPLIT], p[p.index >= SPLIT]
    tt = lambda x: x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
    by = p.groupby(y).sum()
    return dict(n=len(p), avg=p.mean(), t=tt(p), d=d.mean(), h=h.mean(), td=tt(d), th=tt(h), yrs=f"{(by > 0).sum()}/{len(by)}")


def evaluate(P, mv, cost):
    pnl = P.mul(mv, axis=0) - P.abs() * cost
    return pnl, pd.DataFrame({k: stats(pnl[k]) for k in P}).T


def cross_check(T, nm):
    """Do design winners stay winners? Spearman of design t vs holdout t, and the hit rate."""
    ok = T.td.notna() & T.th.notna()
    rho = T[ok].td.astype(float).rank().corr(T[ok].th.astype(float).rank())
    win = T[ok & (T.td.astype(float) > 1.0)]
    return dict(set=nm, n=int(ok.sum()), design_pos=float(np.mean(T[ok].td.astype(float) > 0)), holdout_pos=float(np.mean(T[ok].th.astype(float) > 0)),
                rho=rho, winners=len(win), winners_hold_pos=float(np.mean(win.th.astype(float) > 0)) if len(win) else np.nan,
                winners_hold_avg=float(win.h.astype(float).mean()) if len(win) else np.nan)


def run_instrument(g, sym):
    pv, cost = SPEC[sym]
    B = daily_bars(g); A = alphas(B); mv, cost = day_moves(g, B, pv, cost)
    out = {}
    for rule in ("sign", "extreme"):
        P = positions(A, rule)
        pnl, T = evaluate(P, mv, cost)
        out[rule] = (P, pnl, T)
    return B, A, mv, cost, out


def placebo(P, mv, cost, n=200, seed=7):
    """Random signs on each alpha's own trading days: the null for the cross-section numbers."""
    rng = np.random.default_rng(seed); res = []
    act = P.notna() & (P != 0)
    for i in range(n):
        Q = pd.DataFrame(rng.choice([-1.0, 1.0], size=P.shape), index=P.index, columns=P.columns).where(act, 0.0).where(P.notna())
        _, T = evaluate(Q, mv, cost); res.append(cross_check(T, "placebo"))
    return pd.DataFrame(res)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    g = pickle.load(open(SP + "g24.pkl", "rb")); ge = pickle.load(open(SP + "ge.pkl", "rb"))
    print(__doc__.split("\n")[0])
    res = {}
    for G, sym in ((g, "NQ"), (ge, "ES")):
        B, A, mv, cost, out = run_instrument(G, sym); res[sym] = (B, A, mv, cost, out)
        valid = A.notna().sum()
        print(f"\n=== {sym}: {len(B)} sessions {B.index[0].date()} .. {B.index[-1].date()}; alphas with values {int((valid > 300).sum())}/101;"
              f" first valid day median {A.apply(lambda s: s.first_valid_index()).median().date()}")
        lo = mv.copy(); lo_net = lo - cost
        print(f"   benchmark always long 8:30->14:59: avg ${lo_net.mean():.0f} | design ${lo_net[lo_net.index < SPLIT].mean():.0f} holdout ${lo_net[lo_net.index >= SPLIT].mean():.0f}")
        for rule, (P, pnl, T) in out.items():
            Tf = T.astype({c: float for c in ("n", "avg", "t", "d", "h", "td", "th")})
            print(f"\n   rule '{rule}': top 10 by design t (of {T.td.notna().sum()})")
            show = Tf.sort_values("td", ascending=False).head(10).copy()
            show["long%"] = [float((P[k] > 0).sum() / max(1, (P[k] != 0).sum() - P[k].isna().sum())) for k in show.index]
            print(show.to_string(float_format=lambda v: f"{v:,.2f}"))
            cc = cross_check(T, f"{sym} {rule}"); print("   cross-section:", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in cc.items()})
            if sym == "NQ":
                pl = placebo(P, mv, cost, n=200)
                print(f"   placebo (random signs, same days, 200 runs): rho {pl.rho.mean():+.2f} (5-95% {pl.rho.quantile(.05):+.2f}..{pl.rho.quantile(.95):+.2f});"
                      f" winners' holdout positive {pl.winners_hold_pos.mean():.0%} (95% {pl.winners_hold_pos.quantile(.95):.0%});"
                      f" holdout positive overall {pl.holdout_pos.mean():.0%} (95% {pl.holdout_pos.quantile(.95):.0%})")
                res[sym + rule + "pl"] = pl

    # combination: the paper's "mega-alpha"
    print("\n=== Combination (vote of signs), 1 contract, trade when |vote| >= threshold")
    combos = {}
    for sym in ("NQ", "ES"):
        B, A, mv, cost, out = res[sym]
        P, pnl, T = out["sign"]
        Tf = T.astype({c: float for c in ("td",)})
        sel = Tf[Tf.td > 1.0].index.tolist()
        for nm, cols in (("all 101", list(P.columns)), (f"design winners ({len(sel)})", sel)):
            vote = P[cols].mean(axis=1, skipna=True)
            cnt = P[cols].notna().sum(axis=1)
            for thr in (0.0, 0.1, 0.2):
                pos = np.sign(vote).where((vote.abs() > thr) & (cnt >= 0.6 * len(cols)), 0.0)
                p_ = pos * mv - pos.abs() * cost
                s = stats(p_)
                L, S_ = p_[pos > 0], p_[pos < 0]
                print(f"   {sym} {nm:<22} |vote|>{thr:.1f}: n {s['n']:4d} avg ${s['avg']:5.0f} t {s['t']:4.1f} | design ${s['d']:5.0f} holdout ${s['h']:5.0f}"
                      f" (t {s['th']:4.1f}) yrs {s['yrs']} | longs ${L.mean():5.0f} ({(pos > 0).sum()}) shorts ${S_.mean():5.0f} ({(pos < 0).sum()})")
                combos[(sym, nm, thr)] = (p_, pos)
        # NQ winners applied to ES (out-of-instrument): same alpha numbers
    B, A, mv, cost, out = res["ES"]
    selNQ = res["NQ"][4]["sign"][2].astype({"td": float}).query("td > 1.0").index.tolist()
    P = out["sign"][0]; vote = P[selNQ].mean(axis=1)
    pos = np.sign(vote).where(P[selNQ].notna().sum(axis=1) >= 0.6 * len(selNQ), 0.0)
    p_ = pos * mv - pos.abs() * cost; s = stats(p_)
    print(f"   ES using NQ's design winners ({len(selNQ)}): n {s['n']} avg ${s['avg']:.0f} t {s['t']:.1f} | design ${s['d']:.0f} holdout ${s['h']:.0f} yrs {s['yrs']}")

    # standard metrics for the NQ combinations, longs / shorts, holdout resampling
    print("\n=== Standard metrics, NQ, 1 contract")
    B = res["NQ"][0]; days = B.index[B.index >= pd.Timestamp("2018-01-01")]
    rows = {}
    for key in (("NQ", "all 101", 0.0), ("NQ", [k for k in combos if k[0] == "NQ" and k[1].startswith("design")][0][1], 0.0)):
        p_, pos = combos[key]
        nm = f"{key[1]}"
        rows[nm] = (p_.reindex(days).fillna(0), p_[pos != 0].dropna())
        rows[nm + " longs"] = (p_.where(pos > 0, 0).reindex(days).fillna(0), p_[pos > 0].dropna())
        rows[nm + " shorts"] = (p_.where(pos < 0, 0).reindex(days).fillna(0), p_[pos < 0].dropna())
    print(M.table(rows))
    hold = {k: v[0][v[0].index >= SPLIT] for k, v in rows.items() if not k.endswith("s")}
    b_, p_ = R.report(hold, n=3000); print(b_); print(p_)
    pickle.dump(dict(T={s: {r: res[s][4][r][2] for r in ("sign", "extreme")} for s in ("NQ", "ES")}), open(SP + "alpha101.pkl", "wb"))

    print("\n=== The one design standout: Alpha#37 'extreme' (design t 3.8, best of 196 NQ tests) by year, longs / shorts, ES")
    for sym in ("NQ", "ES"):
        B, A, mv, cost, out = res[sym]
        pos = out["extreme"][0][37]; p_ = out["extreme"][1][37]
        act = pos.fillna(0) != 0; x = p_[act]
        by = x.groupby(x.index.year).agg(["count", "mean", "sum"])
        print(f"   {sym}: " + " | ".join(f"{y} n{int(r['count'])} ${r['mean']:.0f}" for y, r in by.iterrows()))
        for sd, nm in ((1, "longs"), (-1, "shorts")):
            q = p_[pos == sd]; d_, h_ = q[q.index < SPLIT], q[q.index >= SPLIT]
            print(f"      {nm}: n {len(q)} avg ${q.mean():.0f} | design ${d_.mean():.0f} holdout ${h_.mean():.0f} (t {h_.mean() / h_.std() * np.sqrt(len(h_)):.1f})")
    B = res["NQ"][0]; days = B.index
    pos = res["NQ"][4]["extreme"][0][37]; p_ = res["NQ"][4]["extreme"][1][37].fillna(0)
    print(M.table({"A37 extreme NQ": (p_, p_[pos.fillna(0) != 0]), "  longs": (p_.where(pos > 0, 0), p_[pos > 0]), "  shorts": (p_.where(pos < 0, 0), p_[pos < 0])}))
    b_, q_ = R.report({"A37 2023+": p_[p_.index >= SPLIT]}, n=3000); print(b_); print(q_)
