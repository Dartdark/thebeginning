"""NFP Fade replacement hunt (user, 2026-10-17). NFP Fade is the plan's weakest line ($375 a year at $500 risk, P(losing
year) 31%; analysis/plan_montecarlo_test.py). Swap it for each candidate we already have a trade list for, on the funded bench.
PRE-REGISTERED acceptance: the swap must beat the plan on expected payouts within 1 AND 2 years, with blown accounts no
higher and the median days to all 6 payouts no longer (speed_to_13k.run, 3-year horizon, every start day).
Candidates: none (drop NFP); Vol-Control Sell (VCS_MC, B, MC-confirmed); ES MOC auction follow (B; >= 0.3 ATR 14:00->14:50
move, follow 14:51 -> 15:00, stop 0.25 ATR; traded as MES); High-win Morning Momentum (HW, B; risk-sized).
  python3 analysis/nfp_replacement_test.py [SCRATCH_DIR]
"""
import sys, io, pickle, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    argv = sys.argv; sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        G = runpy.run_path("analysis/high_winrate_bench.py", run_name="__main__")
    sys.argv = argv; lab = G["lab"]
    import speed_to_13k as SPD
    import s_rank_es_round1_test as ER
    # ES MOC follow -> per-MES daily worst / close on the lab's day index
    ge = pickle.load(open(SP + "ge.pkl", "rb")); tr = ge.trading[pd.DatetimeIndex(ge.ts[ge.trading]) >= "2018-01-01"]
    atr = ge.daily_atr(15)[tr]; cf = pd.Series(ge.c.ravel()).ffill().to_numpy(); P = lambda t: cf[tr * 1440 + jof(t)]
    full = ge.last_j[tr] >= jof(1500); mv = P(1450) - P(1400); m = full & (np.abs(mv) >= 0.3 * atr) & (mv != 0)
    t = ER.trades(ge, tr[m], np.sign(mv[m]).astype(int), jof(1451), jof(1500), 0.25 * atr[m])
    adv = []
    for r in t.itertuples():
        seg = ge.l[r.day, r.j0:r.j1 + 1] if r.side > 0 else ge.h[r.day, r.j0:r.j1 + 1]
        worst = (np.nanmin(seg) - r.entry) * 50 if r.side > 0 else (r.entry - np.nanmax(seg)) * 50
        adv.append(min(worst - 5.0, r.net))
    t["adv"] = adv
    print(f"ES MOC follow: {len(t)} trades, ${t.net.mean():.0f} per ES, t {t.net.mean() / t.net.std() * np.sqrt(len(t)):.1f}, "
          f"2018-22 ${t.net[t.index.year < 2023].mean():.0f} / 2023+ ${t.net[t.index.year >= 2023].mean():.0f}")
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); pos = pd.Series(np.arange(len(dates)), index=dates)
    Wd = np.zeros(len(dates)); Cd = np.zeros(len(dates))
    for d, r in t.iterrows():
        d = pd.Timestamp(d).normalize()
        if d in pos.index: i = pos[d]; Wd[i] += r.adv / 10; Cd[i] += r.net / 10      # per MES
    lab.W["MOC_MES"] = Wd[:, None] * np.ones((1, lab.W["VB"].shape[1])); lab.C["MOC_MES"] = Cd
    print("daily corr with NFP / plan:", {k: round(float(np.corrcoef(lab.C["MOC_MES"], lab.C[k])[0, 1]), 2) for k in ("NFP_MC", "VB", "LDF_MC", "ONB_ML2_MC")})
    base = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    nonfp = {k: v for k, v in base.items() if k != "NFP_MC"}
    plans = {"plan (with NFP $500)": base, "drop NFP, nothing instead": nonfp}
    for q in (1, 2, 3): plans[f"NFP -> VCS {q} MNQ"] = {**nonfp, "VCS_MC": q}
    for q in (1, 2, 3, 4): plans[f"NFP -> ES MOC follow {q} MES"] = {**nonfp, "MOC_MES": q}
    for r_ in (150, 250): plans[f"NFP -> HW risk ${r_}"] = {**nonfp, "HW": ("risk", r_)}
    rows = {}
    for nm, p in plans.items():
        a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
        s = SPD.run(lab, p, fmin=0.5, fmax=1.0, ref=1500.0)
        rows[nm] = dict(y1=a["expected"], y2=c["expected"], blown1=a["blown"], blown2=c["blown"], days6=s["median"], all6_2y=s["full2y"], per_month=s["per_month"])
    df = pd.DataFrame(rows).T; b0 = df.iloc[0]
    df["passes"] = (df.y1 >= b0.y1) & (df.y2 >= b0.y2) & (df.blown2 <= b0.blown2) & (df.days6 <= b0.days6)
    print("\nFunded bench (cushion sizing, full from $1,500; days6 = median trading days to all 6 payouts, inf = under half get there):")
    print(df.to_string(formatters={"y1": "${:,.0f}".format, "y2": "${:,.0f}".format, "blown1": "{:.0%}".format, "blown2": "{:.0%}".format,
                                   "days6": "{:.0f}".format, "all6_2y": "{:.0%}".format, "per_month": "${:,.0f}".format}))

    # follow-up (not pre-registered, counted as extra trials): ES MOC follow ADDED with NFP kept; and why NFP matters
    print("\nFollow-up: ES MOC follow added on top of the plan (NFP kept):")
    for q in (1, 2):
        p = {**base, "MOC_MES": q}
        a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0); s = SPD.run(lab, p, fmin=0.5, fmax=1.0, ref=1500.0)
        print(f"   plan + MOC {q} MES: 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%} days6 {s['median']:.0f} all6 2y {s['full2y']:.0%}")
    names, bb = lab._base(base); Cp = sum(bb[i] * lab.C[k] for i, k in enumerate(names)); eq = pd.Series(np.cumsum(Cp)); dd = eq.cummax() - eq
    nfp = pd.Series(bb[names.index("NFP_MC")] * lab.C["NFP_MC"]); act = nfp != 0
    print(f"   NFP days: {int(act.sum())}; avg NFP P&L when the plan is in a drawdown > $1,000: ${nfp[act & (dd > 1000)].mean():.0f} "
          f"(n {int((act & (dd > 1000)).sum())}) vs otherwise ${nfp[act & (dd <= 1000)].mean():.0f}; plan P&L on NFP days excl. NFP "
          f"${(Cp - nfp)[act].mean():.0f} vs all days ${(Cp - nfp).mean():.0f}")

    # how noisy is the bench for small changes? reshuffle NFP's trade results among its own days (same total, same days)
    print("\nBench noise check: NFP's own results reshuffled among its 78 days (same sum), 20 draws:")
    rng = np.random.default_rng(7); act_ix = np.where(lab.C["NFP_MC"] != 0)[0]; res = []
    W0, C0 = lab.W["NFP_MC"].copy(), lab.C["NFP_MC"].copy()
    for k in range(20):
        perm = rng.permutation(act_ix); lab.W["NFP_SH"] = W0.copy(); lab.C["NFP_SH"] = C0.copy()
        lab.W["NFP_SH"][act_ix] = W0[perm]; lab.C["NFP_SH"][act_ix] = C0[perm]; lab.stop["NFP_SH"] = lab.stop["NFP_MC"].copy(); lab.stop["NFP_SH"][act_ix] = lab.stop["NFP_MC"][perm]
        p = {**nonfp, "NFP_SH": ("risk", 500)}
        a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
        res.append((a["expected"], c["expected"], a["blown"], c["blown"]))
    r = np.array(res)
    print(f"   1y ${r[:, 0].min():,.0f} .. ${r[:, 0].max():,.0f} | 2y ${r[:, 1].min():,.0f} .. ${r[:, 1].max():,.0f} | blown 2y {r[:, 3].min():.0%} .. {r[:, 3].max():.0%} "
          f"(median {np.median(r[:, 3]):.0%}); actual NFP order: 3%")
