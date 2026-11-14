"""Premium rebuilds by matching, round 2 (pre-registered checks/candidates/jesse_premium_rebuilds/PREREG.md): AlligatorV2,
TrendWaveRiderV2, Turtle V2, Turtle V3 from their free parents' code + the premiums' published daily equity curves.
  tools/run_stamped.sh analysis/jesse_premium_rebuilds.py [ALLI|TWR|TURT2|TURT3] > analysis/outputs/jesse_premium_rebuilds_<X>_output.txt
"""
import sys, json, glob, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
WHICH = sys.argv[1] if len(sys.argv) > 1 else "ALLI"
src = open("analysis/jesse_lib_btc_test.py", encoding="utf-8").read().split("adx_ref = P.run(P.setup())")[0]
E = {"__name__": "lib", "__doc__": "x\n"}; exec(compile(src, "jesse_lib_engine", "exec"), E)
np, pd = E["np"], E["pd"]
print(__doc__.split("\n")[0], "|", WHICH)
bars, atr, dmi, ema, cmo, srsi_k, alligator, htf_at, ema_forming, cci, chop, sma_forming, simulate, tt = (E[k] for k in (
    "bars", "atr", "dmi", "ema", "cmo", "srsi_k", "alligator", "htf_at", "ema_forming", "cci", "chop", "sma_forming", "simulate", "tt"))
q15 = bars("15min")
MIN1 = (E["MT"], E["MO"], E["MH"], E["ML"])


def use_15m():
    E["MT"], E["MO"], E["MH"], E["ML"] = q15.index.values, q15.open.to_numpy(), q15.high.to_numpy(), q15.low.to_numpy()


def use_1m(): E["MT"], E["MO"], E["MH"], E["ML"] = MIN1


def site(name, periods):
    out = []
    for p in periods:
        fn = f"scratch_data/jesse_site/{name}__{p.replace(' ', '_')}.json"
        try: j = json.load(open(fn))
        except FileNotFoundError: continue
        d = j["equity_curve"][0]["data"]; t = pd.to_datetime([x["time"] for x in d], unit="s"); v = np.array([x["value"] for x in d])
        out.append(pd.Series(np.r_[np.abs(np.diff(v)) > 1e-6, False], index=t))
    s = pd.concat(out); return s[~s.index.duplicated()].sort_index()


FIT = ("2022 - 2023", "2023 - 2024"); CHK = ("2024 - 2025",) + tuple(f"Q{q} of {y}" for y in (2025, 2026) for q in (1, 2, 3, 4))


def active(t, idx, tf):
    a = np.zeros(len(idx), bool); dv = idx.values
    for r in t.itertuples():
        d0 = np.datetime64((pd.Timestamp(r.t) + tf).normalize()); d1 = np.datetime64((pd.Timestamp(r.tx) + tf - pd.Timedelta(seconds=1)).normalize())
        a[(dv >= d0) & (dv <= d1)] = True
    return pd.Series(a, index=idx)


def f1(a, b):
    a = a.values.astype(bool); b = b.values.astype(bool); tp = (a & b).sum(); return 2 * tp / (a.sum() + b.sum()) if (a.sum() + b.sum()) else 0.0


# ---------------- strategy families: build(params) -> (bars, sig, plan, manage) ----------------
if WHICH == "ALLI":
    PREM, PAR, TF = "alligatorv2", "alligatorai-by-o1-preview-model", pd.Timedelta(minutes=30)
    b = bars("30min"); h4 = bars("4h"); C = b.close.to_numpy(); A = atr(b); _, _, ADX = dmi(b); CM = cmo(C); SK = srsi_k(C)
    jw, te, li = alligator(C); J4, T4, L4 = (htf_at(b, h4, x) for x in alligator(h4.close.to_numpy()))
    EH = {n: htf_at(b, h4, None, ema_forming(ema(h4.close.to_numpy(), n), n)) for n in (50, 100, 200)}
    tr1 = np.where((C > li) & (li > te) & (te > jw), 1, np.where((C < li) & (li < te) & (te < jw), -1, 0))
    tr4 = np.where((C > L4) & (L4 > T4) & (T4 > J4), 1, np.where((C < L4) & (L4 < T4) & (T4 < J4), -1, 0))
    GRID = list(itertools.product((20, 25, 30, 35, 40), (10, 20, 30), (10, 20, 30), (1.5, 2, 2.5, 3), (1.5, 2, 3, 4), (50, 100, 200)))
    PARENT = (30, 20, 20, 2, 2, 100); NAMES = ("adx", "cmo", "srsi", "stop", "target", "ema4h")
    def build(p):
        ax, cm, sk, S, T, en = p
        sig = np.where((tr1 == 1) & (ADX > ax) & (tr4 == 1) & (C > EH[en]) & (CM > cm) & (SK < sk), 1,
                       np.where((tr1 == -1) & (ADX > ax) & (tr4 == -1) & (C < EH[en]) & (CM < -cm) & (SK > 100 - sk), -1, 0))
        return b, sig, (lambda i, s, e: (e - s * S * A[i], e + s * T * A[i])), None
elif WHICH == "TWR":
    PREM, PAR, TF = "trendwaveriderv2", "trendwaverider", pd.Timedelta(minutes=15)
    b = q15; C = b.close.to_numpy(); A = atr(b); pdi, ndi, ADX = dmi(b); CC = cci(b)
    SM = {n: pd.Series(C).rolling(n).mean().to_numpy() for n in (10, 20, 25, 30, 50, 100)}
    GRID = list(itertools.product((30, 40, 50), ((10, 30), (25, 50), (50, 100), (20, 100)), (50, 100, 150), (2, 2.5, 3, 3.5, 4), (2, 3, 3.5, 4, 5)))
    PARENT = (50, (25, 50), 100, 3.5, 3.5); NAMES = ("adx", "sma", "cci", "stop", "target")
    def build(p):
        ax, (fa, sl), cc, S, T = p
        sig = np.where((pdi > ndi) & (ADX > ax) & (SM[fa] > SM[sl]) & (CC < -cc), 1, np.where((pdi < ndi) & (ADX > ax) & (SM[fa] < SM[sl]) & (CC > cc), -1, 0))
        return b, sig, (lambda i, s, e: (e - s * S * A[i], e + s * T * A[i])), None
else:
    PREM = "turtle-v2" if WHICH == "TURT2" else "turtle-v3"; PAR, TF = "turtleai-by-o1-preview-model", pd.Timedelta(hours=1)
    b = bars("1h"); h4 = bars("4h"); C = b.close.to_numpy(); A = atr(b); _, _, ADX = dmi(b); CH = chop(b)
    DH = {n: pd.Series(b.high.to_numpy()).rolling(n).max().shift(1).to_numpy() for n in (10, 20, 30, 55)}
    DL = {n: pd.Series(b.low.to_numpy()).rolling(n).min().shift(1).to_numpy() for n in (10, 20, 30, 55)}
    SH = {n: htf_at(b, h4, None, sma_forming(h4.close.to_numpy(), n)) for n in (100, 200)}
    GRID = list(itertools.product((10, 20, 30, 55), (100, 200), (20, 25, 30, 35), (35, 40, 45, 50, 100), (1.5, 2, 2.5, 3, 3.5)))
    PARENT = (20, 200, 30, 40, 2.5); NAMES = ("donchian", "sma4h", "adx", "chop", "trail")
    def build(p):
        dn, sm, ax, ch, K = p
        sig = np.where((C > DH[dn]) & (C > SH[sm]) & (ADX > ax) & (CH < ch), 1, np.where((C < DL[dn]) & (C < SH[sm]) & (ADX > ax) & (CH < ch), -1, 0))
        def mg(j, pos, event=None):
            s = pos["s"]; pos["stop"] = max(pos["stop"], C[j] - K * A[j]) if s == 1 else min(pos["stop"], C[j] + K * A[j])
        return b, sig, (lambda i, s, e: (e - s * K * A[i], None)), mg

TIX = b.index.values


def run(p, lo, hi):
    bb, sig, plan, mg = build(p); sig = sig.copy()
    sig[(TIX < np.datetime64(lo)) | (TIX >= np.datetime64(hi))] = 0; sig[np.isnan(sig.astype(float))] = 0
    return simulate(bb, sig.astype(int), plan, manage=mg, cooldown_close=(WHICH.startswith("TURT")))


VF, VC = site(PREM, FIT), site(PREM, CHK); PF_, PC_ = site(PAR, FIT), site(PAR, CHK)
use_15m()
pa = run(PARENT, "2021-12-01", "2026-12-31")
print(f"parent code vs parent site curve: fit F1 {f1(active(pa, PF_.index, TF), PF_):.3f}, check F1 {f1(active(pa, PC_.index, TF), PC_):.3f} (ceiling)")
pfit, pchk = f1(active(pa, VF.index, TF), VF), f1(active(pa, VC.index, TF), VC)
print(f"parent code vs PREMIUM curve: fit F1 {pfit:.3f}, check F1 {pchk:.3f}; premium active days fit {VF.sum()}, check {VC.sum()}")
rows = []
for p in GRID:
    t = run(p, "2021-12-01", "2024-01-01")
    rows.append((p, f1(active(t, VF.index, TF), VF), len(t)))
G = pd.DataFrame(rows, columns=["p", "fit_f1", "n"]).sort_values("fit_f1", ascending=False).reset_index(drop=True)
print(f"grid {len(G)}: fit F1 median {G.fit_f1.median():.3f}, 95th {G.fit_f1.quantile(.95):.3f}, best {G.fit_f1.max():.3f}")
chk = []
for k in range(5):
    t = run(G.p[k], "2023-12-01", "2026-12-31"); chk.append(f1(active(t, VC.index, TF), VC))
    print(f"   rank {k + 1}: {dict(zip(NAMES, G.p[k]))} fit F1 {G.fit_f1[k]:.3f} n {G.n[k]} -> check F1 {chk[-1]:.3f}")
ok = chk[0] >= 0.6 and abs(chk[0] - G.fit_f1[0]) <= 0.10 and chk[0] > pchk
print(f"ACCEPT rank 1: {ok} (check {chk[0]:.3f} >= 0.6, within 0.10 of fit {G.fit_f1[0]:.3f}, above parent's check {pchk:.3f})")
G.assign(p=G.p.astype(str)).to_csv(f"checks/candidates/jesse_premium_rebuilds/grid_{WHICH}.csv", index=False)
if ok:
    use_1m(); t = run(G.p[0], "2018-06-01", "2026-12-31"); x = t.ret
    per = {"2018-21 (unseen)": t.yr <= 2021, "2022-23 (fit)": (t.yr >= 2022) & (t.yr <= 2023), "2024-26 (check)": t.yr >= 2024}
    print(f"\nREBUILD on our data (1-min fills): {len(t)} trades, win {np.mean(x > 0):.0%}, {100 * x.mean():+.3f}% a trade, PF {x[x > 0].sum() / -x[x < 0].sum():.2f}, t {tt(x):.2f}")
    print("   " + " | ".join(f"{k}: {100 * x[m].mean():+.3f}% t {tt(x[m]):.2f} n {m.sum()}" for k, m in per.items()))
    print(f"   longs {100 * x[t.side == 1].mean():+.3f}% (t {tt(x[t.side == 1]):.2f}) | shorts {100 * x[t.side == -1].mean():+.3f}% (t {tt(x[t.side == -1]):.2f})")
    print("   by year %: " + "  ".join(f"{y} {100 * g.ret.sum():+.0f}" for y, g in t.groupby("yr")))
    bb, sig, plan, mg = build(G.p[0])
    pm = np.array([simulate(bb, sig, plan, manage=mg, seed=s, cooldown_close=WHICH.startswith("TURT")).ret.mean() for s in range(40)])
    print(f"   placebo (random side, 40 runs): mean {100 * pm.mean():+.3f}%, p95 {100 * np.percentile(pm, 95):+.3f}%, p = {np.mean(pm >= x.mean()):.2f}")
    t.to_csv(f"checks/candidates/jesse_premium_rebuilds/trades_{WHICH}.csv", index=False)
