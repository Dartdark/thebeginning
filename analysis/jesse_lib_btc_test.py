"""jesse.trade library, BTC strategies with free code (user 2026-11-13; code read logged in; triage checks/candidates/jesse_library/TRIAGE.md).
Pre-registered here before running: each strategy AS CODED on its own timeframe, Coinbase spot BTC 1-min 2018-06 -> 2026-10 (UTC
candles, as Jesse), one position at a time, Jesse order semantics: decisions on candle closes; market orders at that close;
stop / take-profit orders rest and fill on later 1-min bars (stop first inside a minute, at the stop or the open if gapped);
limit entries live for one candle (should_cancel_entry True). Higher-timeframe candles in Jesse include the FORMING candle:
modelled for close-based moving averages (EMA / TEMA / SMA) by updating the last completed value with the current price;
shifted / Wilder indicators on the higher timeframe use completed candles. Costs 0.05% fee a side + 0.02% slippage on market /
stop fills (limit fills fee only). Results per trade in % of entry price and in R (R = the coded initial stop distance).
Strategies (as coded; Jesse indicator defaults, period 14 where not given):
  TEMA  TemaTrendFollowing, 30m: TEMA10 > TEMA80 and 4h TEMA20 > TEMA70, ADX > 40, CMO > 40 -> buy limit at price - ATR (one
        candle), stop 4 ATR, target 3 ATR from the fill (mirror short)
  ADXW  ADXWilliamsStrategy, 15m: DI+ > DI-, ADX > 50, Williams %R < -80 -> buy at the close; stop = SMA50, target = highest
        high of the last 30 candles; out when the opposite signal fires (mirror short); skipped when the stop is on the wrong side
  TWR   TrendWaveRider, 15m: DI+ > DI- and ADX > 50, SMA25 > SMA50, CCI(14) < -100 -> buy; stop and target 3.5 ATR (mirror)
  ALLI  AlligatorAi, 30m: price > lips > teeth > jaw on 30m and on 4h, ADX > 30, close > EMA100(4h), CMO > 20, StochRSI k < 20 ->
        buy; stop and target 2 ATR (mirror)
  TST   TrendSwingTrader V1, 4h: EMA100 < EMA50 < EMA21 < close and ADX > 25 -> buy; stop 2 ATR; half off at 3 ATR, then the stop
        goes to break-even and trails 2 ATR behind the close (never below entry) (mirror)
  TURT  TurtleAI, 1h: close > Donchian(20) high of the previous candles, close > SMA200(4h), ADX > 30, Choppiness < 40, not on
        the candle a trade closed -> buy; stop 2.5 ATR trailing (max of old stop and close - 2.5 ATR) (mirror)
Placebo: same entry moments, random side, same exits (40 runs). Bar for 'promising': t >= 2 with 2018-22 and 2023+ both positive
and placebo p < 0.05; then the add / replace bench against the BTC ADX piece (correlation shown here).
  tools/run_stamped.sh analysis/jesse_lib_btc_test.py > analysis/outputs/jesse_lib_btc_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import btc_adx_ensemble_test as P
print(__doc__.split("\n")[0])
FEE, SLIP = 0.0005, 0.0002
m = P.load()                                                     # 1-min, UTC bar-open index
MT = m.index.values; MO, MH, ML = (m[k].to_numpy() for k in ("open", "high", "low"))


def bars(rule): return P.rs(m, rule)


def wilder(x, n):
    out = np.full(len(x), np.nan); s = np.nan; cnt = 0; acc = 0.0
    for i, v in enumerate(x):
        if np.isnan(v): continue
        if np.isnan(s):
            acc += v; cnt += 1
            if cnt == n: s = acc / n; out[i] = s
            continue
        s = s + (v - s) / n; out[i] = s
    return out


def tr_(b):
    pc = b.close.shift(); return pd.concat([b.high - b.low, (b.high - pc).abs(), (b.low - pc).abs()], axis=1).max(axis=1).to_numpy()


def atr(b, n=14): return wilder(tr_(b), n)


def dmi(b, n=14):
    H, L = b.high.to_numpy(), b.low.to_numpy(); up = np.r_[np.nan, np.diff(H)]; dn = np.r_[np.nan, -np.diff(L)]
    pdm = np.where((up > dn) & (up > 0), up, 0.0); ndm = np.where((dn > up) & (dn > 0), dn, 0.0); pdm[0] = ndm[0] = np.nan
    a = wilder(tr_(b), n); p = wilder(pdm, n); q = wilder(ndm, n)
    pdi = 100 * p / a; ndi = 100 * q / a; dx = 100 * np.abs(pdi - ndi) / (pdi + ndi)
    return pdi, ndi, wilder(dx, n)


def ema(x, n): return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy()


def tema(x, n):
    e1 = ema(x, n); e2 = ema(e1, n); e3 = ema(e2, n); return 3 * e1 - 3 * e2 + e3


def cmo(c, n=14):
    d = np.diff(c, prepend=np.nan); u = pd.Series(np.where(d > 0, d, 0.0)).rolling(n).sum(); v = pd.Series(np.where(d < 0, -d, 0.0)).rolling(n).sum()
    return (100 * (u - v) / (u + v)).to_numpy()


def htf_at(b_low, b_high, values, forming=None):
    """value of a higher-timeframe series at each low-tf close. forming(k_prev_state_index, price) -> value using the forming
    candle; None = last COMPLETED higher-tf candle."""
    tc = (b_low.index + (b_low.index[1] - b_low.index[0])).values          # low-tf close times
    span = b_high.index[1] - b_high.index[0]
    done = np.searchsorted((b_high.index + span).values, tc, side="right") - 1
    if forming is None:
        v = np.full(len(tc), np.nan); ok = done >= 0; v[ok] = values[done[ok]]; return v
    return forming(done, b_low.close.to_numpy())


def ema_forming(vals_prev, n):
    """EMA including the forming candle: prev completed EMA stepped with the current price"""
    a = 2 / (n + 1)
    def f(done, price):
        v = np.full(len(done), np.nan); ok = done >= 0; v[ok] = vals_prev[done[ok]] + a * (price[ok] - vals_prev[done[ok]]); return v
    return f


def tema_forming(close_h, n):
    a = 2 / (n + 1); e1 = ema(close_h, n); e2 = ema(e1, n); e3 = ema(e2, n)
    def f(done, price):
        v = np.full(len(done), np.nan); ok = done >= 0; k = done[ok]
        x1 = e1[k] + a * (price[ok] - e1[k]); x2 = e2[k] + a * (x1 - e2[k]); x3 = e3[k] + a * (x2 - e3[k]); v[ok] = 3 * x1 - 3 * x2 + x3; return v
    return f


def sma_forming(close_h, n):
    cs = np.r_[0.0, np.cumsum(close_h)]
    def f(done, price):
        v = np.full(len(done), np.nan); ok = done >= n - 2; k = done[ok]
        v[ok] = (cs[k + 1] - cs[k + 1 - (n - 1)] + price[ok]) / n; return v
    return f


def smma(x, n):
    out = np.full(len(x), np.nan); s = np.nan
    for i, v in enumerate(x):
        if np.isnan(v): continue
        if i < n - 1: continue
        s = np.nanmean(x[i - n + 1:i + 1]) if np.isnan(s) else (s * (n - 1) + v) / n; out[i] = s
    return out


def alligator(close):
    hl = close                                                       # Jesse's default source is close
    jaw = np.r_[np.full(8, np.nan), smma(hl, 13)[:-8]]; teeth = np.r_[np.full(5, np.nan), smma(hl, 8)[:-5]]; lips = np.r_[np.full(3, np.nan), smma(hl, 5)[:-3]]
    return jaw, teeth, lips


def srsi_k(c, n=14, ns=14, k=3):
    d = np.diff(c, prepend=np.nan); g = wilder(np.where(d > 0, d, 0.0), n); l = wilder(np.where(d < 0, -d, 0.0), n)
    rsi = 100 - 100 / (1 + g / l); r = pd.Series(rsi); st = 100 * (r - r.rolling(ns).min()) / (r.rolling(ns).max() - r.rolling(ns).min())
    return st.rolling(k).mean().to_numpy()


def cci(b, n=14):
    tp = ((b.high + b.low + b.close) / 3); ma = tp.rolling(n).mean(); md = tp.rolling(n).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    return ((tp - ma) / (0.015 * md)).to_numpy()


def chop(b, n=14):
    a1 = pd.Series(tr_(b)).rolling(n).sum(); hh = b.high.rolling(n).max().to_numpy(); ll = b.low.rolling(n).min().to_numpy()
    return (100 * np.log10(a1.to_numpy() / (hh - ll)) / np.log10(n))


def minute_index(b):
    return np.searchsorted(MT, (b.index + (b.index[1] - b.index[0])).values)   # first minute after each candle close


def simulate(b, sig, plan, manage=None, limit=None, seed=None, cooldown_close=False, half=False):
    """sig: array +1/-1/0 at each candle close. plan(i, s, entry) -> (stop, target or None). manage(i, pos) -> 'exit' or new stop
    (called at each later candle close). limit(i, s) -> limit price for a one-candle limit entry (else market at the close)."""
    rng = np.random.default_rng(seed) if seed is not None else None
    C = b.close.to_numpy(); mp = minute_index(b); n = len(C); out = []; i = 0
    while i < n - 2:
        s = sig[i]
        if not s: i += 1; continue
        if rng is not None: s = int(rng.choice([-1, 1]))
        if limit is not None:                                       # resting limit for the next candle only
            lp = limit(i, s); fill = None
            for k in range(mp[i], min(mp[i + 1], len(MT))):
                if (s == 1 and ML[k] <= lp) or (s == -1 and MH[k] >= lp): fill = k; break
            if fill is None: i += 1; continue
            e = min(lp, MO[fill]) if s == 1 else max(lp, MO[fill]); cost_in = FEE; k0 = fill + 1; j = i + 1
        else:
            e = C[i]; cost_in = FEE + SLIP; k0 = mp[i]; j = i
        stop, tgt = plan(i, s, e)
        if stop is None or (e - stop) * s <= 0: i += 1; continue
        R = abs(e - stop) / e; pos = {"s": s, "e": e, "stop": stop, "tgt": tgt, "half": False, "best": C[j], "i0": j, "half_at": half}
        px = None; parts = []
        while j < n - 1:
            for k in range(k0, min(mp[j + 1], len(MT))):
                if (s == 1 and ML[k] <= pos["stop"]) or (s == -1 and MH[k] >= pos["stop"]):
                    px = (min(pos["stop"], MO[k]) if s == 1 else max(pos["stop"], MO[k])); why = "stop"; cst = FEE + SLIP; break
                if pos["tgt"] is not None and ((s == 1 and MH[k] >= pos["tgt"]) or (s == -1 and ML[k] <= pos["tgt"])):
                    if pos.get("half_at") and not pos["half"]:
                        parts.append((0.5, pos["tgt"], FEE)); pos["half"] = True; pos["tgt"] = None
                        if manage: manage(j, pos, event="half")
                        continue
                    px = pos["tgt"]; why = "target"; cst = FEE; break
            if px is not None: break
            j += 1; k0 = mp[j]
            if manage:
                r = manage(j, pos)
                if r == "exit": px = C[j]; why = "signal"; cst = FEE + SLIP; break
        if px is None: break
        q = 1.0 - sum(p[0] for p in parts)
        ret = sum(w * s * (p_ - e) / e - w * c_ for w, p_, c_ in parts) + q * (s * (px - e) / e - cst) - cost_in
        out.append((b.index[i], b.index[j], s, ret, ret / R, why, e, len(parts) > 0))
        i = j + 1 if cooldown_close else j + 1
    t = pd.DataFrame(out, columns=["t", "tx", "side", "ret", "r", "why", "e", "halfed"]); t["yr"] = t.t.dt.year
    return t


def tt(x): return x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan


ADXD = None
def report(nm, t, ref=None):
    x = t.ret; a = t[t.yr <= 2022]; z = t[t.yr >= 2023]; pf = x[x > 0].sum() / -x[x < 0].sum() if (x < 0).any() else np.inf
    print(f"\n{nm}: {len(t)} trades ({len(t) / 8.3:.0f} a year), win {np.mean(x > 0):.0%}, mean {100 * x.mean():+.3f}% ({t.r.mean():+.3f}R), PF {pf:.2f}, t {tt(x):.2f} | "
          f"2018-22 {100 * a.ret.mean():+.3f}% (t {tt(a.ret):.2f}) | 2023+ {100 * z.ret.mean():+.3f}% (t {tt(z.ret):.2f})")
    print(f"   longs {100 * x[t.side == 1].mean():+.3f}% (t {tt(x[t.side == 1]):.2f}, n {(t.side == 1).sum()}) | shorts {100 * x[t.side == -1].mean():+.3f}% (t {tt(x[t.side == -1]):.2f}, n {(t.side == -1).sum()}) | exits {t.why.value_counts().to_dict()}")
    print("   by year % (sum of trade returns): " + "  ".join(f"{y} {100 * g.ret.sum():+.0f}" for y, g in t.groupby("yr")))
    if ADXD is not None:
        dd = t.groupby(t.tx.dt.normalize()).ret.sum().reindex(ADXD.index, fill_value=0.0)
        print(f"   daily corr with the BTC ADX ensemble (spot, both sides): {np.corrcoef(dd, ADXD)[0, 1]:+.2f}")


def placebo(nm, run_fn, real):
    pm = np.array([run_fn(seed=s).ret.mean() for s in range(40)])
    print(f"   placebo (random side, same moments, 40 runs): mean {100 * pm.mean():+.3f}%, p95 {100 * np.percentile(pm, 95):+.3f}%, real {100 * real.ret.mean():+.3f}%, p = {np.mean(pm >= real.ret.mean()):.2f}")


adx_ref = P.run(P.setup()); ADXD = adx_ref.groupby(pd.DatetimeIndex(adx_ref.tx).normalize()).ret.sum()
ADXD = ADXD.reindex(pd.date_range("2018-06-01", ADXD.index.max()), fill_value=0.0)
R_ = {}

# ---- TEMA (30m)
b = bars("30min"); h4 = bars("4h"); C = b.close.to_numpy(); A = atr(b); pdi, ndi, ADX = dmi(b); CM = cmo(C)
st_ = np.sign(tema(C, 10) - tema(C, 80))
lt_ = np.sign(htf_at(b, h4, None, tema_forming(h4.close.to_numpy(), 20)) - htf_at(b, h4, None, tema_forming(h4.close.to_numpy(), 70)))
sig = np.where((st_ == 1) & (lt_ == 1) & (ADX > 40) & (CM > 40), 1, np.where((st_ == -1) & (lt_ == -1) & (ADX > 40) & (CM < -40), -1, 0))
run = lambda seed=None: simulate(b, sig, lambda i, s, e: (e - s * 4 * A[i], e + s * 3 * A[i]), limit=lambda i, s: C[i] - s * A[i], seed=seed)
R_["TEMA"] = run(); report("TEMA  TemaTrendFollowing (30m)", R_["TEMA"]); placebo("TEMA", run, R_["TEMA"])

# ---- ADXW (15m)
b = bars("15min"); C = b.close.to_numpy(); pdi, ndi, ADX = dmi(b)
H, L = b.high.to_numpy(), b.low.to_numpy(); hh = pd.Series(H).rolling(30).max().to_numpy(); ll = pd.Series(L).rolling(30).min().to_numpy()
wr = (-100 * (pd.Series(H).rolling(14).max() - b.close.reset_index(drop=True)) / (pd.Series(H).rolling(14).max() - pd.Series(L).rolling(14).min())).to_numpy()
s50 = pd.Series(C).rolling(50).mean().to_numpy()
sig = np.where((pdi > ndi) & (ADX > 50) & (wr < -80), 1, np.where((pdi < ndi) & (ADX > 50) & (wr > -20), -1, 0))
def mgw(j, pos, event=None): return "exit" if sig[j] == -pos["s"] else None
run = lambda seed=None: simulate(b, sig, lambda i, s, e: (s50[i], hh[i] if s == 1 else ll[i]), manage=mgw, seed=seed)
R_["ADXW"] = run(); report("ADXW  ADXWilliamsStrategy (15m)", R_["ADXW"]); placebo("ADXW", run, R_["ADXW"])

# ---- TWR (15m)
CC = cci(b); A = atr(b); s25 = pd.Series(C).rolling(25).mean().to_numpy()
sig = np.where((pdi > ndi) & (ADX > 50) & (s25 > s50) & (CC < -100), 1, np.where((pdi < ndi) & (ADX > 50) & (s25 < s50) & (CC > 100), -1, 0))
run = lambda seed=None: simulate(b, sig, lambda i, s, e: (e - s * 3.5 * A[i], e + s * 3.5 * A[i]), seed=seed)
R_["TWR"] = run(); report("TWR   TrendWaveRider (15m)", R_["TWR"]); placebo("TWR", run, R_["TWR"])

# ---- ALLI (30m, 4h big tf)
b = bars("30min"); C = b.close.to_numpy(); A = atr(b); pdi, ndi, ADX = dmi(b); CM = cmo(C); SK = srsi_k(C)
jw, te, li = alligator(C); J4, T4, L4 = (htf_at(b, h4, x) for x in alligator(h4.close.to_numpy()))
E100 = htf_at(b, h4, None, ema_forming(ema(h4.close.to_numpy(), 100), 100))
tr1 = np.where((C > li) & (li > te) & (te > jw), 1, np.where((C < li) & (li < te) & (te < jw), -1, 0))
tr4 = np.where((C > L4) & (L4 > T4) & (T4 > J4), 1, np.where((C < L4) & (L4 < T4) & (T4 < J4), -1, 0))
sig = np.where((tr1 == 1) & (ADX > 30) & (tr4 == 1) & (C > E100) & (CM > 20) & (SK < 20), 1,
               np.where((tr1 == -1) & (ADX > 30) & (tr4 == -1) & (C < E100) & (CM < -20) & (SK > 80), -1, 0))
run = lambda seed=None: simulate(b, sig, lambda i, s, e: (e - s * 2 * A[i], e + s * 2 * A[i]), seed=seed)
R_["ALLI"] = run(); report("ALLI  AlligatorAi (30m)", R_["ALLI"]); placebo("ALLI", run, R_["ALLI"])

# ---- TST (4h)
b = h4; C = b.close.to_numpy(); A = atr(b); pdi, ndi, ADX = dmi(b)
e1, e2, e3 = ema(C, 21), ema(C, 50), ema(C, 100)
sig = np.where((e3 < e2) & (e2 < e1) & (e1 < C) & (ADX > 25), 1, np.where((e3 > e2) & (e2 > e1) & (e1 > C) & (ADX > 25), -1, 0))
def plan_tst(i, s, e): return e - s * 2 * A[i], e + s * 3 * A[i]
def mg_tst(j, pos, event=None):
    s = pos["s"]
    if event == "half": pos["stop"] = pos["e"]; return None
    if pos["half"]:
        ns = max(C[j] - 2 * A[j], pos["e"]) if s == 1 else min(C[j] + 2 * A[j], pos["e"]); pos["stop"] = ns
    return None
def run(seed=None): return simulate(b, sig, plan_tst, manage=mg_tst, seed=seed, half=True)
R_["TST"] = run(); report("TST   TrendSwingTrader V1 (4h)", R_["TST"]); placebo("TST", run, R_["TST"])

# ---- TURT (1h, 4h SMA200 forming)
b = bars("1h"); C = b.close.to_numpy(); A = atr(b); pdi, ndi, ADX = dmi(b); CH = chop(b)
dh = pd.Series(b.high.to_numpy()).rolling(20).max().shift(1).to_numpy(); dl = pd.Series(b.low.to_numpy()).rolling(20).min().shift(1).to_numpy()
S200 = htf_at(b, h4, None, sma_forming(h4.close.to_numpy(), 200))
sig = np.where((C > dh) & (C > S200) & (ADX > 30) & (CH < 40), 1, np.where((C < dl) & (C < S200) & (ADX > 30) & (CH < 40), -1, 0))
def mg_t(j, pos, event=None):
    s = pos["s"]; pos["stop"] = max(pos["stop"], C[j] - 2.5 * A[j]) if s == 1 else min(pos["stop"], C[j] + 2.5 * A[j]); return None
run = lambda seed=None: simulate(b, sig, lambda i, s, e: (e - s * 2.5 * A[i], None), manage=mg_t, seed=seed, cooldown_close=True)
R_["TURT"] = run(); report("TURT  TurtleAI (1h)", R_["TURT"]); placebo("TURT", run, R_["TURT"])

for k, t in R_.items(): t.to_csv(f"scratch_data/jesse_lib_{k}.csv", index=False)
