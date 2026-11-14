"""FIX 2026-11-14 (checker): the trailing best/peak close was keyed by id(pos), which Python reuses after a trade ends (1,072 of 1,116 ES trades started from an old best); now stored on the position.
jesse.trade strategies as APEX-LEGAL INTRADAY versions on NQ (user 2026-11-13: 'none of em can be intraday?'). Pre-registered here,
before running: every library strategy whose bars are <= 1h, ported as coded to NQ futures (24h 1-min, rolls difference-adjusted,
bars on the CT clock, indicators continuous across sessions as a 24h chart), in two forms: (1) as coded (holds overnight) and
(2) Apex-legal: no new entries from 14:45 to 17:00 CT, every position out at the last bar closing at or before 15:45 CT
(15m: 15:45; 30m: 15:30; 1h: 15:00). Costs per NQ: $7.25 + 1 tick ($5) per market / stop fill (targets: no slippage).
Strategies: TEMA (30m), ADXWilliams (15m), TrendWaveRider (15m), AlligatorAi (30m), TurtleAI (1h), ETHSTPullback (30m, 4h regime
from completed candles), SPYTFDipLS (1h), and the premium rebuilds AlligatorV2 (30m), TrendWaveRiderV2 (15m), Turtle V2 / V3 (1h).
Not portable intraday: TrendSwingTrader V1 / V2 (4h bars), BBSqueezeTrend (4h squeeze, ~15 signals a year); CL mean reversion's
Apex version was already tested (F).
Bar for 'promising': Apex form t >= 2 with 2018-22 and 2023+ both positive and random-side placebo p < 0.05 (20 runs).
  tools/run_stamped.sh analysis/jesse_nq_intraday_test.py > analysis/outputs/jesse_nq_intraday_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
src = open("analysis/jesse_lib_btc_test.py", encoding="utf-8").read().split("adx_ref = P.run(P.setup())")[0]
E = {"__name__": "lib", "__doc__": "x\n"}; exec(compile(src, "jesse_lib_engine", "exec"), E)
np, pd = E["np"], E["pd"]
print(__doc__.split("\n")[0])
atr, dmi, ema, tema, cmo, srsi_k, alligator, htf_at, ema_forming, tema_forming, sma_forming, cci, chop, simulate, tt = (E[k] for k in (
    "atr", "dmi", "ema", "tema", "cmo", "srsi_k", "alligator", "htf_at", "ema_forming", "tema_forming", "sma_forming", "cci", "chop", "simulate", "tt"))
import co_oc_reversal_test as CO, roll_adjust as RA
g = CO.load("NQ"); c = g.c.ravel().astype(float); o = g.o.ravel().astype(float); h = g.h.ravel().astype(float); l = g.l.ravel().astype(float)
J = RA.roll_jumps(g, "NQ"); adj = np.zeros(len(c))
for jj, jump in J.items(): adj[:jj] += jump
ok = ~np.isnan(c); ts = (pd.to_datetime(np.repeat(g.ts, 1440)) + pd.to_timedelta(np.tile(np.arange(1440), len(g.ts)), "m") - pd.Timedelta(minutes=1))[ok]
mm = pd.DataFrame({"open": o[ok] + adj[ok], "high": h[ok] + adj[ok], "low": l[ok] + adj[ok], "close": c[ok] + adj[ok]}, index=ts)
mm = mm[mm.index >= "2017-06-01"]
E["MT"], E["MO"], E["MH"], E["ML"] = mm.index.values, mm.open.to_numpy(), mm.high.to_numpy(), mm.low.to_numpy(); E["FEE"], E["SLIP"] = 0.0, 0.0
agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
B = {k: mm.resample(k, label="left", closed="left").agg(agg).dropna() for k in ("15min", "30min", "1h", "4h")}
print(f"NQ 1-min {mm.index[0]} -> {mm.index[-1]} CT, rolls adjusted {len(J)}")


def apex_flags(b, tf_min):
    ce = b.index + pd.Timedelta(minutes=tf_min); hm = ce.hour * 100 + ce.minute
    last = {15: 1545, 30: 1530, 60: 1500}[tf_min]
    return np.asarray((hm >= 1445) & (hm < 1700)), np.asarray(hm == last)


def run(b, tf_min, sig, plan, manage=None, limit=None, apex=False, seed=None, cooldown=False):
    s = sig.copy(); noent, flat = apex_flags(b, tf_min)
    if apex: s[noent] = 0
    def mg(j, pos, event=None):
        if apex and flat[j] and event is None: return "exit"
        return manage(j, pos, event) if manage else None
    t = simulate(b, s, plan, manage=mg, limit=limit, seed=seed, cooldown_close=cooldown)
    t["usd"] = t.ret * t.e * 20 - 7.25 - 5 - np.where(t.why == "target", 0.0, 5.0)
    return t


def show(nm, t):
    x = t.usd; a = x[t.yr <= 2022]; z = x[t.yr >= 2023]; pf = x[x > 0].sum() / -x[x < 0].sum() if (x < 0).any() else np.inf
    print(f"   {nm:<10} {len(t):5d} trades, win {np.mean(x > 0):.0%}, ${x.mean():7.1f} per NQ, PF {pf:4.2f}, t {tt(x):5.2f} | 2018-22 ${a.mean():7.1f} (t {tt(a):5.2f}) | 2023+ ${z.mean():7.1f} (t {tt(z):5.2f}) | longs t {tt(x[t.side == 1]):5.2f} shorts t {tt(x[t.side == -1]):5.2f}")


S = {}
# --- TEMA 30m
b = B["30min"]; C = b.close.to_numpy(); A = atr(b); _, _, ADX = dmi(b); CM = cmo(C); h4 = B["4h"]
st_ = np.sign(tema(C, 10) - tema(C, 80)); lt_ = np.sign(htf_at(b, h4, None, tema_forming(h4.close.to_numpy(), 20)) - htf_at(b, h4, None, tema_forming(h4.close.to_numpy(), 70)))
sig = np.where((st_ == 1) & (lt_ == 1) & (ADX > 40) & (CM > 40), 1, np.where((st_ == -1) & (lt_ == -1) & (ADX > 40) & (CM < -40), -1, 0))
S["TEMA"] = (b, 30, sig, (lambda A_: lambda i, s, e: (e - s * 4 * A_[i], e + s * 3 * A_[i]))(A), None, (lambda C_, A_: lambda i, s: C_[i] - s * A_[i])(C, A), False)
# --- ADXW / TWR 15m
b = B["15min"]; C = b.close.to_numpy(); A = atr(b); pdi, ndi, ADX = dmi(b); H, L = b.high.to_numpy(), b.low.to_numpy()
hh = pd.Series(H).rolling(30).max().to_numpy(); ll = pd.Series(L).rolling(30).min().to_numpy()
hh14, ll14 = pd.Series(H).rolling(14).max().to_numpy(), pd.Series(L).rolling(14).min().to_numpy(); wr = -100 * (hh14 - C) / (hh14 - ll14)
s50 = pd.Series(C).rolling(50).mean().to_numpy(); s25 = pd.Series(C).rolling(25).mean().to_numpy(); CC = cci(b)
sigW = np.where((pdi > ndi) & (ADX > 50) & (wr < -80), 1, np.where((pdi < ndi) & (ADX > 50) & (wr > -20), -1, 0))
S["ADXW"] = (b, 15, sigW, (lambda: lambda i, s, e: (s50[i], hh[i] if s == 1 else ll[i]))(), (lambda sg: lambda j, pos, event=None: "exit" if sg[j] == -pos["s"] else None)(sigW), None, False)
sigT = np.where((pdi > ndi) & (ADX > 50) & (s25 > s50) & (CC < -100), 1, np.where((pdi < ndi) & (ADX > 50) & (s25 < s50) & (CC > 100), -1, 0))
S["TWR"] = (b, 15, sigT, (lambda A_: lambda i, s, e: (e - s * 3.5 * A_[i], e + s * 3.5 * A_[i]))(A), None, None, False)
s10, s30 = pd.Series(C).rolling(10).mean().to_numpy(), pd.Series(C).rolling(30).mean().to_numpy()
sigT2 = np.where((pdi > ndi) & (ADX > 40) & (s10 > s30) & (CC < -100), 1, np.where((pdi < ndi) & (ADX > 40) & (s10 < s30) & (CC > 100), -1, 0))
S["TWRV2rb"] = (b, 15, sigT2, (lambda A_: lambda i, s, e: (e - s * 2.5 * A_[i], e + s * 2 * A_[i]))(A), None, None, False)
# --- Alligator 30m (free and V2 rebuild)
b = B["30min"]; C = b.close.to_numpy(); A = atr(b); _, _, ADX = dmi(b); CM = cmo(C); SK = srsi_k(C)
jw, te, li = alligator(C); J4, T4, L4 = (htf_at(b, h4, x) for x in alligator(h4.close.to_numpy()))
tr1 = np.where((C > li) & (li > te) & (te > jw), 1, np.where((C < li) & (li < te) & (te < jw), -1, 0))
tr4 = np.where((C > L4) & (L4 > T4) & (T4 > J4), 1, np.where((C < L4) & (L4 < T4) & (T4 < J4), -1, 0))
for nm, ax, en, S_, T_ in (("ALLI", 30, 100, 2, 2), ("ALLIV2rb", 40, 50, 3, 2)):
    EH = htf_at(b, h4, None, ema_forming(ema(h4.close.to_numpy(), en), en))
    sg = np.where((tr1 == 1) & (ADX > ax) & (tr4 == 1) & (C > EH) & (CM > 20) & (SK < 20), 1, np.where((tr1 == -1) & (ADX > ax) & (tr4 == -1) & (C < EH) & (CM < -20) & (SK > 80), -1, 0))
    S[nm] = (b, 30, sg, (lambda A_, a, c_: lambda i, s, e: (e - s * a * A_[i], e + s * c_ * A_[i]))(A, S_, T_), None, None, False)
# --- ETHST 30m (4h regime from completed candles, EMA200 forming)
st30 = E.get("supertrend")
def supertrend(bb, period, factor):
    Hh, Ll, Cc = bb.high.to_numpy(), bb.low.to_numpy(), bb.close.to_numpy(); a = atr(bb, period); hl2 = (Hh + Ll) / 2
    ub = hl2 + factor * a; lb = hl2 - factor * a; fu = ub.copy(); fl = lb.copy(); st = np.full(len(Cc), np.nan); up = True
    for i in range(1, len(Cc)):
        if np.isnan(a[i]): continue
        if not np.isnan(fu[i - 1]):
            fu[i] = ub[i] if (ub[i] < fu[i - 1] or Cc[i - 1] > fu[i - 1]) else fu[i - 1]
            fl[i] = lb[i] if (lb[i] > fl[i - 1] or Cc[i - 1] < fl[i - 1]) else fl[i - 1]
        if up and Cc[i] < fl[i]: up = False
        elif not up and Cc[i] > fu[i]: up = True
        st[i] = fl[i] if up else fu[i]
    return st
ST4 = htf_at(b, h4, supertrend(h4, 10, 3.5)); E200 = htf_at(b, h4, None, ema_forming(ema(h4.close.to_numpy(), 200), 200)); st30 = supertrend(b, 10, 3.0)
reg = np.where((C > ST4) & (C > E200), 1, np.where((C < ST4) & (C < E200), -1, 0))
since = np.zeros(len(b), int); cnt = 9999
for i in range(1, len(b)): cnt = 0 if reg[i] != reg[i - 1] else cnt + 1; since[i] = cnt
d30 = np.where(C > st30, 1, -1); d30p = np.r_[0, d30[:-1]]
sigE = np.where((reg != 0) & (ADX >= 24) & (d30 == reg) & ((d30p != reg) | (since <= 7)), reg, 0)
def mk_eth(C_, A_, rg):
    pk = {}
    def mg(j, pos, event=None):
        s = pos["s"]
        if rg[j] != s: return "exit"
        p_ = pos.get("_peak", pos["e"]); p_ = max(p_, C_[j]) if s == 1 else min(p_, C_[j]); pos["_peak"] = p_
        tr = min(p_ - 9 * A_[j], C_[j] - 0.5 * A_[j]) if s == 1 else max(p_ + 9 * A_[j], C_[j] + 0.5 * A_[j])
        pos["stop"] = max(pos["stop"], tr) if s == 1 else min(pos["stop"], tr)
    return mg
S["ETHST"] = (b, 30, sigE, (lambda A_: lambda i, s, e: (e - s * 7 * A_[i], None))(A), mk_eth(C, A, reg), None, False)
# --- Turtle 1h (free and V2 / V3 rebuilds) and SPY 1h
b = B["1h"]; C = b.close.to_numpy(); A = atr(b); _, _, ADX = dmi(b); CH = chop(b)
for nm, dn, sm, ax, ch, K in (("TURT", 20, 200, 30, 40, 2.5), ("TURTV2rb", 55, 200, 20, 40, 2.0), ("TURTV3rb", 30, 200, 20, 40, 1.5)):
    DH = pd.Series(b.high.to_numpy()).rolling(dn).max().shift(1).to_numpy(); DL = pd.Series(b.low.to_numpy()).rolling(dn).min().shift(1).to_numpy()
    SH = htf_at(b, h4, None, sma_forming(h4.close.to_numpy(), sm))
    sg = np.where((C > DH) & (C > SH) & (ADX > ax) & (CH < ch), 1, np.where((C < DL) & (C < SH) & (ADX > ax) & (CH < ch), -1, 0))
    mg = (lambda C_, A_, K_: lambda j, pos, event=None: pos.__setitem__("stop", max(pos["stop"], C_[j] - K_ * A_[j]) if pos["s"] == 1 else min(pos["stop"], C_[j] + K_ * A_[j])))(C, A, K)
    S[nm] = (b, 60, sg, (lambda A_, K_: lambda i, s, e: (e - s * K_ * A_[i], None))(A, K), mg, None, True)
L4s = htf_at(b, h4, supertrend(h4, 22, 2.0)); A4 = htf_at(b, h4, atr(h4)); X4 = htf_at(b, h4, dmi(h4)[2])
e18, e40 = ema(C, 18), ema(C, 40)
sigS = np.where((C > L4s) & (C < e18), 1, np.where((C < L4s) & (X4 > 22) & (C > e40), -1, 0)); sigS[np.isnan(L4s) | np.isnan(A4)] = 0
def mk_spy(C_, A1, A4_):
    bs = {}
    def mg(j, pos, event=None):
        s = pos["s"]; bb_ = pos.get("_best", pos["e"]); bb_ = max(bb_, C_[j]) if s == 1 else min(bb_, C_[j]); pos["_best"] = bb_
        if s == 1: pos["stop"] = max(pos["stop"], min(bb_ - 3 * A4_[j], C_[j] - 0.5 * A1[j]))
        else: pos["stop"] = min(pos["stop"], max(bb_ + 3 * A4_[j], C_[j] + 0.5 * A1[j]))
    return mg
S["SPY"] = (b, 60, sigS, (lambda A4_: lambda i, s, e: (e - 1.5 * A4_[i], None) if s == 1 else (e + 0.75 * A4_[i], e - 2.5 * A4_[i]))(A4), mk_spy(C, A, A4), None, False)

print("\nper NQ contract, after costs; (1) as coded on the 24h chart, (2) APEX-legal intraday")
res = {}
for nm, (b, tf, sig, plan, mg, lim, cd) in S.items():
    print(f"\n{nm}")
    t1 = run(b, tf, sig, plan, mg, lim, apex=False, cooldown=cd); show("as coded", t1)
    t2 = run(b, tf, sig, plan, mg, lim, apex=True, cooldown=cd); show("APEX", t2); res[nm] = t2
    pm = np.array([run(b, tf, sig, plan, mg, lim, apex=True, seed=s_, cooldown=cd).usd.mean() for s_ in range(20)])
    print(f"   APEX placebo (random side, 20 runs): mean ${pm.mean():.1f}, p95 ${np.percentile(pm, 95):.1f}, p = {np.mean(pm >= t2.usd.mean()):.2f}")
    t2.assign(date=t2.tx.dt.normalize().dt.date, net=t2.usd).to_csv(f"scratch_data/jesse_nq_apex_{nm}.csv", index=False)
