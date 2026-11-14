"""AlligatorV2 rebuild and TrendSwingTrader V1 longs against the PERSONAL book (user 2026-11-13 'run them both').
Spot signals (Coinbase, Jesse semantics, analysis/jesse_lib_btc_test.py engine) executed on CME Micro Bitcoin: entry at the same 15m
close (next one when CME is shut), a resting MBT stop at the spot stop distance (longs and SHORTS), the half-off and every other exit
copied at the spot time; marked at every 16:00 CT close; $2.50 a round trip + 1 tick a fill. Base = the plan's personal book
including the BTC ADX piece (analysis/btc_adx_personal_bench.py). Variants at 1 MBT: AlligatorV2 rebuild both sides / longs only;
TST V1 longs; both together. 1-year block MC median year / p95 DD, mean of 5 seeds, paired vs the plan.
  tools/run_stamped.sh analysis/jesse_rebuilds_personal_bench.py > analysis/outputs/jesse_rebuilds_personal_bench_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
src = open("analysis/btc_adx_personal_bench.py", encoding="utf-8").read()
head = src.split("S = PB.run(PB.setup())")[0]
g = {"__name__": "bench", "__doc__": __doc__}
exec(compile(head.replace("print(__doc__.split", "pass  # (__doc__.split"), "personal_bench_head", "exec"), g)
print(__doc__.split("\n")[0])
np, pd, PB, MC, days, P, FT, FO, FL, FC, fac, ctd, MARK, ns = (g[k] for k in ("np", "pd", "PB", "MC", "days", "P", "FT", "FO", "FL", "FC", "fac", "ctd", "MARK", "ns"))
FH = g["f15"].high.to_numpy(); MULT, TICK, COMM = 0.1, 5.0, 2.5


def mark(S):
    """both sides; S: t, tx, side, R (stop distance as a fraction), th (half time or NaT)"""
    seg_d, seg_v, n = [], [], 0
    for k in S.itertuples():
        ie = np.searchsorted(FT, np.datetime64(k.t)); ix = np.searchsorted(FT, np.datetime64(k.tx))
        if ix >= len(FT) or ie >= ix: continue
        s = int(k.side); pe = FC[ie] + s * TICK; real = pe / fac[ie]; stop = pe * (1 - s * k.R)
        ih = min(max(np.searchsorted(FT, np.datetime64(k.th)), ie), ix) if pd.notna(k.th) else None
        end, exit_px = ix, FC[ix] - s * TICK
        hit = np.flatnonzero((FL[ie + 1:ix + 1] <= stop) if s == 1 else (FH[ie + 1:ix + 1] >= stop))
        if len(hit):
            jj = ie + 1 + hit[0]; exit_px = (min(stop, FO[jj]) if s == 1 else max(stop, FO[jj])) - s * TICK; end = jj
            if ih is not None and jj <= ih: ih = None
        pts = sorted(set([ie, end] + [m for m in MARK[(MARK > ie) & (MARK < end)]] + ([ih] if ih is not None and ie < ih < end else [])))
        px = {q: FC[q] for q in pts}; px[ie] = pe; px[end] = exit_px; q = 1.0
        if ih is not None and ih <= ie: seg_d.append(ctd[ie]); seg_v.append(0.5 * s * (FC[ie] - pe) / pe * real * MULT); q = 0.5
        elif ih is not None and ih >= end: seg_d.append(ctd[end]); seg_v.append(0.5 * s * (FC[end] - exit_px) / pe * real * MULT)
        for a, b_ in zip(pts[:-1], pts[1:]):
            seg_d.append(ctd[b_]); seg_v.append(q * s * (px[b_] - px[a]) / pe * real * MULT)
            if ih is not None and b_ == ih: q = 0.5
        seg_d.append(ctd[end]); seg_v.append(-(COMM + (COMM / 4 if ih is not None else 0.0))); n += 1
    seg_d = pd.DatetimeIndex(seg_d); keep = seg_d <= days[-1]
    return pd.Series(np.array(seg_v)[keep], index=ns["to_trading_day"](seg_d[keep])).groupby(level=0).sum().reindex(days, fill_value=0.0), n


esrc = open("analysis/jesse_lib_btc_test.py", encoding="utf-8").read().split("adx_ref = P.run(P.setup())")[0]
E = {"__name__": "lib", "__doc__": "x\n"}; exec(compile(esrc, "jesse_lib_engine", "exec"), E)
bars, atr, dmi, ema, cmo, srsi_k, alligator, htf_at, ema_forming, simulate = (E[k] for k in ("bars", "atr", "dmi", "ema", "cmo", "srsi_k", "alligator", "htf_at", "ema_forming", "simulate"))
# AlligatorV2 rebuild (ADX 40, CMO 20, StochRSI 20, stop 3, target 2, 4h EMA 50)
b = bars("30min"); h4 = bars("4h"); C = b.close.to_numpy(); A = atr(b); _, _, ADX = dmi(b); CM = cmo(C); SK = srsi_k(C)
jw, te, li = alligator(C); J4, T4, L4 = (htf_at(b, h4, x) for x in alligator(h4.close.to_numpy())); E50 = htf_at(b, h4, None, ema_forming(ema(h4.close.to_numpy(), 50), 50))
tr1 = np.where((C > li) & (li > te) & (te > jw), 1, np.where((C < li) & (li < te) & (te < jw), -1, 0))
tr4 = np.where((C > L4) & (L4 > T4) & (T4 > J4), 1, np.where((C < L4) & (L4 < T4) & (T4 < J4), -1, 0))
sig = np.where((tr1 == 1) & (ADX > 40) & (tr4 == 1) & (C > E50) & (CM > 20) & (SK < 20), 1, np.where((tr1 == -1) & (ADX > 40) & (tr4 == -1) & (C < E50) & (CM < -20) & (SK > 80), -1, 0))
AL = simulate(b, sig, lambda i, s, e: (e - s * 3 * A[i], e + s * 2 * A[i]))
# TST V1 (21 / 50 / 100, ADX 25, stop 2, half 3, trail 2), longs
b4 = h4; C4 = b4.close.to_numpy(); A4 = atr(b4); _, _, X4 = dmi(b4)
e1, e2, e3 = ema(C4, 21), ema(C4, 50), ema(C4, 100)
s4 = np.where((e3 < e2) & (e2 < e1) & (e1 < C4) & (X4 > 25), 1, 0); s4[:200] = 0
def mg(j, pos, event=None):
    if event == "half": pos["stop"] = pos["e"]; return None
    if pos["half"]: pos["stop"] = max(C4[j] - 2 * A4[j], pos["e"])
TS = simulate(b4, s4, lambda i, s, e: (e - 2 * A4[i], e + 3 * A4[i]), manage=mg, half=True)
w = lambda t: t[(t.t >= FT[0]) & (t.tx <= FT[-1])].reset_index(drop=True)
ser = {}
for nm, t in (("ALLI both", w(AL)), ("ALLI longs", w(AL[AL.side == 1])), ("TST longs", w(TS))):
    ser[nm], n = mark(t); print(f"{nm}: {n} trades on MBT, ${ser[nm].sum() / ((days[-1] - pd.Timestamp('2018-12-17')).days / 365.25):,.0f} a year per MBT; "
                              f"max DD ${(ser[nm].cumsum() - ser[nm].cumsum().cummax()).min():,.0f}; by year " + " ".join(f"{y} {v:+,.0f}" for y, v in ser[nm].groupby(ser[nm].index.year).sum().items() if y >= 2019))
S0 = PB.run(PB.setup()); S0 = S0[(S0.t >= FT[0]) & (S0.tx <= FT[-1]) & (S0.side == 1)].reset_index(drop=True)
btc, _ = mark(S0.assign(side=1))
cor = lambda a, c: np.corrcoef(a[a.index.year >= 2019], c[c.index.year >= 2019])[0, 1]
print(f"daily corr: ALLI vs BTC ADX {cor(ser['ALLI both'], btc):+.2f}, TST vs BTC ADX {cor(ser['TST longs'], btc):+.2f}, ALLI vs TST {cor(ser['ALLI both'], ser['TST longs']):+.2f}, ALLI vs rest of book {cor(ser['ALLI both'], P.sum(axis=1)):+.2f}")
plan = P.sum(axis=1) + btc
V = {"PLAN (book + BTC ADX)": plan, "+ AlligatorV2 rebuild 1 MBT (both sides)": plan + ser["ALLI both"], "+ AlligatorV2 rebuild longs 1 MBT": plan + ser["ALLI longs"],
     "+ TST V1 longs 1 MBT": plan + ser["TST longs"], "+ both (ALLI both sides + TST longs)": plan + ser["ALLI both"] + ser["TST longs"]}
mc = lambda x, sd: (lambda d: (d["pnl_p50"], d["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=sd))
for per, m in (("2019-26", days.year >= 2019), ("2019-22", (days.year >= 2019) & (days.year <= 2022)), ("2023+", days.year >= 2023)):
    print(f"\n{per}: {'variant':<44}{'$ a year p50':>13}{'DD p95':>9}{'ret/DD':>8}{'vs plan':>9}{'seeds better':>14}")
    R = {nm: [mc(x[m], sd) for sd in range(1, 6)] for nm, x in V.items()}
    pr = [a / b_ for a, b_ in R["PLAN (book + BTC ADX)"]]
    for nm, rr in R.items():
        r = [a / b_ for a, b_ in rr]
        print(f"        {nm:<44}${np.mean([a for a, _ in rr]):>11,.0f} ${np.mean([b_ for _, b_ in rr]):>7,.0f} {np.mean(r):7.2f} {np.mean(r) - np.mean(pr):+8.2f} {sum(a > b_ for a, b_ in zip(r, pr))}/5")
