"""jesse.trade library, the rest of the shortlist (user 2026-11-13 'test the rest'), free code as coded, ported to our data.
Engine and conventions: analysis/jesse_lib_btc_test.py (Jesse order semantics, stops / targets on 1-min bars, placebo = random side).
  BBSQ  BBSqueezeTrend (author: ETH-USDT 30m / 4h anchor; no ETH data -> BTC spot): 4h Bollinger(29, 1.82) inside Keltner(29,
        1.56, EMA mid, ATR) for >= 4 bars, then the FORMING 4h candle is out of the squeeze -> enter on that 30m close in the
        direction of the 11-bar linear-regression slope of 4h closes, if 4h ADX(14) >= 19.11; once per 4h candle. Stop 1.74 x
        ATR(14, 4h); trail 3.71 x ATR(14, 4h) from the best 30m close, ratchet only. Jesse's forming 4h candle modelled for the
        BB / KC / ATR / slope (close, high, low so far); ADX from completed 4h candles.
  ETHST ETHSTPullback30m (author: ETH-USDT 30m / 4h -> BTC spot): regime = 4h close vs SuperTrend(10, 3.5) line AND vs EMA200
        (forming 4h candle for EMA and close; SuperTrend line from completed candles); entry when 30m ADX(14) >= 24, 30m close is
        on the regime side of SuperTrend(10, 3) and either it just crossed back (reclaim) or the regime turned <= 7 bars ago.
        Stop 7 ATR(14, 30m); chandelier trail min(best close - 9 ATR, close - 0.5 ATR), ratchet; out when the regime is no
        longer the trade's side.
  SPY   SPYTFDipLS (author: SPY 1h / 4h) -> ES and NQ futures (24h 1-min, rolls difference-adjusted): regime from COMPLETED 4h
        candles, close vs SuperTrend(22, 2.0); long when bullish and the 1h close < EMA18 (buy the dip): stop 1.5 x ATR(14, 4h),
        trail min(best close - 3 x ATR4h, close - 0.5 x ATR1h), ratchet; short when bearish, 4h ADX > 22 and the 1h close >
        EMA40: stop 0.75 x ATR4h, target 2.5 x ATR4h, trail max(best close + 3 x ATR4h, close + 0.5 x ATR1h). Holds overnight
        (personal account only). Costs ES $5 + 1 tick ($12.50), NQ $7.25 + 1 tick ($5) per market / stop fill, per contract.
Bar for 'promising' (fixed before running): t >= 2, 2018-22 and 2023+ both positive, placebo p < 0.05.
  tools/run_stamped.sh analysis/jesse_lib_rest_test.py > analysis/outputs/jesse_lib_rest_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
src = open("analysis/jesse_lib_btc_test.py", encoding="utf-8").read().split("adx_ref = P.run(P.setup())")[0]
E = {"__name__": "lib", "__doc__": "x\n"}; exec(compile(src, "jesse_lib_engine", "exec"), E)
np, pd, P = E["np"], E["pd"], E["P"]
print(__doc__.split("\n")[0])
atr, dmi, ema, wilder, tr_, bars, simulate, tt = (E[k] for k in ("atr", "dmi", "ema", "wilder", "tr_", "bars", "simulate", "tt"))


def supertrend(b, period, factor, atr_vals=None):
    H, L, C = b.high.to_numpy(), b.low.to_numpy(), b.close.to_numpy()
    a = atr(b, period) if atr_vals is None else atr_vals; hl2 = (H + L) / 2
    ub = hl2 + factor * a; lb = hl2 - factor * a; fu = ub.copy(); fl = lb.copy(); st = np.full(len(C), np.nan); up = True
    for i in range(1, len(C)):
        if np.isnan(a[i]): continue
        if not np.isnan(fu[i - 1]):
            fu[i] = ub[i] if (ub[i] < fu[i - 1] or C[i - 1] > fu[i - 1]) else fu[i - 1]
            fl[i] = lb[i] if (lb[i] > fl[i - 1] or C[i - 1] < fl[i - 1]) else fl[i - 1]
        if up and C[i] < fl[i]: up = False
        elif not up and C[i] > fu[i]: up = True
        st[i] = fl[i] if up else fu[i]
    return st


def report(nm, t, unit="%", usd=None):
    x = t.ret if usd is None else usd; a = x[t.yr <= 2022]; z = x[t.yr >= 2023]
    pf = x[x > 0].sum() / -x[x < 0].sum() if (x < 0).any() else np.inf
    f = (lambda v: f"{100 * v:+.3f}%") if usd is None else (lambda v: f"${v:+,.0f}")
    print(f"\n{nm}: {len(t)} trades ({len(t) / 8.3:.0f} a year), win {np.mean(x > 0):.0%}, mean {f(x.mean())} ({t.r.mean():+.3f}R), PF {pf:.2f}, t {tt(x):.2f} | "
          f"2018-22 {f(a.mean())} (t {tt(a):.2f}) | 2023+ {f(z.mean())} (t {tt(z):.2f})")
    print(f"   longs {f(x[t.side == 1].mean())} (t {tt(x[t.side == 1]):.2f}, n {(t.side == 1).sum()}) | shorts {f(x[t.side == -1].mean())} (t {tt(x[t.side == -1]):.2f}, n {(t.side == -1).sum()}) | exits {t.why.value_counts().to_dict()}")
    print("   by year: " + "  ".join(f"{y} {(100 * g.sum() if usd is None else g.sum()):+,.0f}" for y, g in x.groupby(t.yr)))


def placebo(run_fn, real, val=lambda t: t.ret):
    pm = np.array([val(run_fn(seed=s)).mean() for s in range(40)])
    print(f"   placebo (random side, 40 runs): mean {pm.mean():+.5f}, p95 {np.percentile(pm, 95):+.5f}, real {val(real).mean():+.5f}, p = {np.mean(pm >= val(real).mean()):.2f}")


R_ = {}
# ================= BBSQ on BTC (30m, forming 4h anchor) =================
b = bars("30min"); h4 = bars("4h"); C30 = b.close.to_numpy()
n_bb, dev, kcm, slp, adxt, nsq, sm, tm = 29, 1.82, 1.56, 11, 19.11, 4, 1.74, 3.71
H4C, H4H, H4L = h4.close.to_numpy(), h4.high.to_numpy(), h4.low.to_numpy()
tc = (b.index + pd.Timedelta(minutes=30)).values
done = np.searchsorted((h4.index + pd.Timedelta(hours=4)).values, tc, side="right") - 1      # last completed 4h candle
start = h4.index.values; cur = np.searchsorted(start, b.index.values, side="right") - 1        # forming 4h candle index
grp = pd.Series(cur); fh = pd.Series(b.high.to_numpy()).groupby(grp).cummax().to_numpy(); fl_ = pd.Series(b.low.to_numpy()).groupby(grp).cummin().to_numpy()
complete_now = done == cur                                                                    # this 30m close completes the 4h candle
emaK = ema(H4C, n_bb); atrK = wilder(tr_(h4), n_bb); atr14 = wilder(tr_(h4), 14); _, _, adx4 = dmi(h4)
sqC = None
def sq_at(k_last, price, hi, lo):
    """squeeze state of a 4h candle whose close is `price` with the previous completed candle index k_last"""
    w = np.r_[H4C[k_last - n_bb + 2:k_last + 1], price]; m_ = w.mean(); s_ = w.std()
    em = emaK[k_last] + 2 / (n_bb + 1) * (price - emaK[k_last]); trf = max(hi - lo, abs(hi - H4C[k_last]), abs(lo - H4C[k_last]))
    at = atrK[k_last] + (trf - atrK[k_last]) / n_bb
    return (m_ + dev * s_ < em + kcm * at) and (m_ - dev * s_ > em - kcm * at)
sq_done = np.zeros(len(h4), bool)
for k in range(n_bb + 2, len(h4)): sq_done[k] = sq_at(k - 1, H4C[k], H4H[k], H4L[k])
sig = np.zeros(len(b), int); atr_f = np.full(len(b), np.nan); fired_at = {}
for i in range(len(b)):
    k = cur[i]; d_ = done[i]
    if d_ < n_bb + 6 or k < 0: continue
    if complete_now[i]: continue                                                              # the forming candle is the NEXT one only after this close
    on_forming = sq_at(d_, C30[i], fh[i], fl_[i])
    if on_forming or not sq_done[d_] or not sq_done[d_ - nsq + 1:d_ + 1].all(): continue
    if k in fired_at or adx4[d_] < adxt: continue
    w = np.r_[H4C[d_ - slp + 2:d_ + 1], C30[i]]; slope = np.polyfit(np.arange(slp), w, 1)[0]
    trf = max(fh[i] - fl_[i], abs(fh[i] - H4C[d_]), abs(fl_[i] - H4C[d_])); atr_f[i] = atr14[d_] + (trf - atr14[d_]) / 14
    sig[i] = 1 if slope > 0 else -1; fired_at[k] = i
best = {}
def mg_bbsq(j, pos, event=None):
    s = pos["s"]; key = id(pos); bb_ = best.get(key, pos["e"]); bb_ = max(bb_, C30[j]) if s == 1 else min(bb_, C30[j]); best[key] = bb_
    a = atr14[done[j]] if done[j] >= 0 else np.nan
    ns = bb_ - s * tm * a
    if (s == 1 and ns > pos["stop"]) or (s == -1 and ns < pos["stop"]): pos["stop"] = ns
run = lambda seed=None: simulate(b, sig, lambda i, s, e: (e - s * sm * atr_f[i], None), manage=mg_bbsq, seed=seed)
R_["BBSQ"] = run(); report("BBSQ  BBSqueezeTrend on BTC (30m / 4h)", R_["BBSQ"]); placebo(run, R_["BBSQ"])

# ================= ETHST on BTC (30m, 4h regime) =================
A30 = atr(b); _, _, ADX30 = dmi(b); st30 = supertrend(b, 10, 3.0)
st4 = supertrend(h4, 10, 3.5); e200 = ema(H4C, 200); a2 = 2 / 201
reg = np.zeros(len(b), int)
for i in range(len(b)):
    d_ = done[i]
    if d_ < 210 or np.isnan(st4[d_]): continue
    line = st4[d_]; em = e200[d_] + a2 * (C30[i] - e200[d_])                                  # forming EMA200
    reg[i] = 1 if (C30[i] > line and C30[i] > em) else (-1 if (C30[i] < line and C30[i] < em) else 0)
since = np.zeros(len(b), int); c_ = 9999
for i in range(1, len(b)):
    c_ = 0 if reg[i] != reg[i - 1] else c_ + 1; since[i] = c_
d30 = np.where(C30 > st30, 1, -1); d30p = np.r_[0, d30[:-1]]
sig = np.where((reg != 0) & (ADX30 >= 24) & (d30 == reg) & ((d30p != reg) | (since <= 7)), reg, 0)
peak = {}
def mg_eth(j, pos, event=None):
    s = pos["s"]
    if reg[j] != s: return "exit"
    key = id(pos); pk = peak.get(key, pos["e"]); pk = max(pk, C30[j]) if s == 1 else min(pk, C30[j]); peak[key] = pk
    trail = min(pk - 9 * A30[j], C30[j] - 0.5 * A30[j]) if s == 1 else max(pk + 9 * A30[j], C30[j] + 0.5 * A30[j])
    pos["stop"] = max(pos["stop"], trail) if s == 1 else min(pos["stop"], trail)
run = lambda seed=None: simulate(b, sig, lambda i, s, e: (e - s * 7 * A30[i], None), manage=mg_eth, seed=seed)
R_["ETHST"] = run(); report("ETHST ETHSTPullback30m on BTC (30m / 4h)", R_["ETHST"]); placebo(run, R_["ETHST"])
ADXD = E.get("ADXD")
ref = P.run(P.setup()); AD = ref.groupby(pd.DatetimeIndex(ref.tx).normalize()).ret.sum()
for k in ("BBSQ", "ETHST"):
    t = R_[k]; dd = t.groupby(t.tx.dt.normalize()).ret.sum(); idx = pd.date_range("2018-06-01", AD.index.max())
    print(f"   {k} daily corr with the BTC ADX ensemble: {np.corrcoef(dd.reindex(idx, fill_value=0), AD.reindex(idx, fill_value=0))[0, 1]:+.2f}")

# ================= SPY -> ES / NQ (1h, completed 4h anchor) =================
import co_oc_reversal_test as CO, roll_adjust as RA
SPEC = {"ES": (50.0, 0.25, 5.0), "NQ": (20.0, 0.25, 7.25)}
for sym in ("ES", "NQ"):
    g = CO.load(sym); c = g.c.ravel().astype(float); o = g.o.ravel().astype(float); h = g.h.ravel().astype(float); l = g.l.ravel().astype(float)
    J = RA.roll_jumps(g, sym); adj = np.zeros(len(c))
    for jj, jump in J.items(): adj[:jj] += jump
    ok = ~np.isnan(c); ts = (pd.to_datetime(np.repeat(g.ts, 1440)) + pd.to_timedelta(np.tile(np.arange(1440), len(g.ts)), "m") - pd.Timedelta(minutes=1))[ok]
    mm = pd.DataFrame({"open": o[ok] + adj[ok], "high": h[ok] + adj[ok], "low": l[ok] + adj[ok], "close": c[ok] + adj[ok]}, index=ts)
    mm = mm[mm.index >= "2017-06-01"]
    E["MT"], E["MO"], E["MH"], E["ML"] = mm.index.values, mm.open.to_numpy(), mm.high.to_numpy(), mm.low.to_numpy()
    E["FEE"], E["SLIP"] = 0.0, 0.0
    print(f"\n[{sym}] 1-min {mm.index[0]} -> {mm.index[-1]} CT, {len(mm):,} bars, rolls adjusted {len(J)}")
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    b = mm.resample("1h", label="left", closed="left").agg(agg).dropna(); h4 = mm.resample("4h", label="left", closed="left").agg(agg).dropna()
    C1 = b.close.to_numpy(); A1 = atr(b); st4 = supertrend(h4, 22, 2.0); a4 = atr(h4); _, _, adx4 = dmi(h4)
    done = np.searchsorted((h4.index + pd.Timedelta(hours=4)).values, (b.index + pd.Timedelta(hours=1)).values, side="right") - 1
    L4 = np.where(done >= 0, st4[np.maximum(done, 0)], np.nan); A4 = np.where(done >= 0, a4[np.maximum(done, 0)], np.nan); X4 = np.where(done >= 0, adx4[np.maximum(done, 0)], np.nan)
    e18, e40 = ema(C1, 18), ema(C1, 40)
    bull = C1 > L4; bear = (C1 < L4) & (X4 > 22)
    sig = np.where(bull & (C1 < e18), 1, np.where(bear & (C1 > e40), -1, 0)); sig[np.isnan(L4) | np.isnan(A4)] = 0
    bestS = {}
    def mg_spy(j, pos, event=None):
        s = pos["s"]; key = id(pos); bb_ = bestS.get(key, pos["e"]); bb_ = max(bb_, C1[j]) if s == 1 else min(bb_, C1[j]); bestS[key] = bb_
        if s == 1:
            tr = min(bb_ - 3 * A4[j], C1[j] - 0.5 * A1[j]); pos["stop"] = max(pos["stop"], tr)
        else:
            tr = max(bb_ + 3 * A4[j], C1[j] + 0.5 * A1[j]); pos["stop"] = min(pos["stop"], tr)
    def plan(i, s, e): return (e - 1.5 * A4[i], None) if s == 1 else (e + 0.75 * A4[i], e - 2.5 * A4[i])
    pv, tick, comm = SPEC[sym]
    usd = lambda t: t.ret * t.e * pv - comm - 2 * tick * pv + np.where(t.why == "target", tick * pv, 0.0)
    run = lambda seed=None: simulate(b, sig, plan, manage=mg_spy, seed=seed)
    t = run(); R_["SPY_" + sym] = t.assign(usd=usd(t))
    report(f"SPY   SPYTFDipLS on {sym} (1h / 4h, per contract)", t, usd=usd(t)); placebo(run, t, val=usd)
for k, t in R_.items(): t.to_csv(f"scratch_data/jesse_lib_{k}.csv", index=False)
