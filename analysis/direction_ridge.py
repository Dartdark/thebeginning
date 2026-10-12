"""New direction source: ridge score on signals that do NOT overlap Overnight Bias (2026-10-12).

Inputs (all known by 8:45 CT; analysis/direction_search.py): Asia-session return (NQ, ES),
first 15 minutes, previous RTH return / close location / last hour / 15:00-16:00, NQ-ES previous
day, 2/5/10/20/60-day momentum, distance to the 50-day MA, VIX change and VIX vs its 20-day MA.
Overnight-range features (gap, on_flow, europe_ret ...) are left out on purpose: they agree with
ONB's bias 80-95% of the time.
Target: (long outcome - short outcome) / 2 of the trade engine (analysis/direction_engine.py).
Frozen: fit on 2018-2022 only (standardized with design means/sd), then 2023-2026 untouched.
Walk-forward: refit every January on all earlier years (from 2018), score the next year.
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
D = pd.read_pickle(SP + "dirfeat.pkl"); O = pd.read_pickle(SP + "dir_outcomes.pkl")
D = D.loc[D.index.intersection(O.index)]; O = O.loc[D.index]
FEAT = ["asia_ret", "es_asia_ret", "first15", "prev_rth_ret", "prev_clv", "prev_last_hour", "prev_post_close",
        "nq_minus_es_prevday%", "mom2", "mom5", "mom10", "mom20", "mom60", "ma50_dist", "vix_chg", "vix_vs_ma20"]
X = D[FEAT].copy()
# scale-free: price features as % of the 8:30 price proxy (60-day mean abs value) to handle NQ 6k -> 25k
for k in FEAT:
    if k not in ("prev_clv", "nq_minus_es_prevday%", "vix_chg", "vix_vs_ma20"):
        X[k] = X[k] / X[k].abs().rolling(60, min_periods=20).mean().shift(1)
X = X.clip(-5, 5)
yrs = D.index.year


def fit(mask, eng, lam=50.0):
    Xm = X[mask]; mu, sd = Xm.mean(), Xm.std()
    Z = ((Xm - mu) / sd).fillna(0).to_numpy()
    y = ((O[(eng, 1)] - O[(eng, -1)]) / 2)[mask].to_numpy()
    w = np.linalg.solve(Z.T @ Z + lam * len(Z) / 100 * np.eye(Z.shape[1]), Z.T @ (y - y.mean()))
    return mu, sd, w


def score(mu, sd, w, rows):
    return pd.Series(((X[rows] - mu) / sd).fillna(0).to_numpy() @ w, index=X.index[rows])


def pnl(sig, eng):
    return pd.Series(np.where(sig > 0, O[(eng, 1)].loc[sig.index], np.where(sig < 0, O[(eng, -1)].loc[sig.index], 0.0)), index=sig.index)


def stats(p, name):
    p = p[p != 0]; y = p.groupby(p.index.year).sum()
    pf = p[p > 0].sum() / -p[p < 0].sum()
    return f"{name:<46} n={len(p):4d} avg ${p.mean():5.0f} PF {pf:.2f} t={p.mean()/p.std()*np.sqrt(len(p)):4.1f} years+ {(y>0).sum()}/{len(y)}"


if __name__ == "__main__":
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    ltr = pd.DatetimeIndex(lab.g.ts[lab.tr])
    onb_real = pd.Series(lab.daily("ONB"), index=ltr); onbml = pd.Series(lab.daily("ONB_ML2_MC"), index=ltr)
    des = yrs <= 2022
    for eng in ("open", "orb"):
        print(f"\n===== engine '{eng}' =====")
        mu, sd, w = fit(des, eng)
        print("weights (z units):", ", ".join(f"{k} {v:+.0f}" for k, v in sorted(zip(FEAT, w), key=lambda t: -abs(t[1]))))
        s = score(mu, sd, w, np.ones(len(X), bool))
        cut = s[des].abs().quantile(1 / 3)
        for nm, sig in (("all days, sign of score", np.sign(s)), ("|score| above design 33rd pct", np.sign(s).where(s.abs() >= cut, 0))):
            p = pnl(sig, eng)
            print(stats(p[des], f"FROZEN design 2018-22 {nm}")); print(stats(p[~des], f"FROZEN holdout 2023-26 {nm}"))
        # walk-forward
        wf = []
        for Y in range(2020, 2027):
            mu2, sd2, w2 = fit(yrs < Y, eng); s2 = score(mu2, sd2, w2, yrs == Y)
            wf.append(pnl(np.sign(s2), eng))
        wf = pd.concat(wf); print(stats(wf, "WALK-FORWARD 2020-2026, sign of score"))
        print("  walk-forward by year:", wf.groupby(wf.index.year).mean().round(0).astype(int).to_dict())
        # overlap with ONB
        p = pnl(np.sign(s), eng); both = (D.onb != 0)
        print(f"  agrees with ONB bias {np.mean(np.sign(s[both]) == D.onb[both]):.0%} of ONB days; "
              f"daily P&L corr with real ONB {np.corrcoef(p, onb_real.reindex(p.index).fillna(0))[0,1]:.2f}, "
              f"with ONB ML v2 {np.corrcoef(p, onbml.reindex(p.index).fillna(0))[0,1]:.2f}")
        base = pnl(pd.Series(1.0, index=X.index), eng)
        print(stats(base[~des], "baseline: always long, holdout"))
