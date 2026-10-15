"""Checker robustness: day-clustered test, run-length sensitivity, confounders, lagged-flag placebo."""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
exec(open("checks/candidates/vb_single_print_filter/replica.py").read().split("# ---------- interior single-print flag")[0])
J = B["j"]; reg = (J >= g.jof(900)) & (J <= g.jof(1500)); TICK = 0.25
def runlen(d):
    h, l = H[d, reg], L[d, reg]
    if np.isnan(h).any(): return None
    lo = np.round(l / TICK).astype(int); hi = np.round(h / TICK).astype(int); base = lo.min()
    cnt = np.zeros(hi.max() - base + 1, int)
    for a, b in zip(lo, hi): cnt[a - base:b - base + 1] += 1
    one = np.r_[False, cnt == 1, False].astype(int); dif = np.diff(one)
    s = np.where(dif == 1)[0]; e = np.where(dif == -1)[0] - 1
    inner = [(ee - ss + 1) for ss, ee in zip(s, e) if ss > 0 and ee < len(cnt) - 1]
    return max(inner) if inner else 0
tr = list(g.trading); rows = []
for n, d in enumerate(tr):
    if n < 2: continue
    p, pp = tr[n - 1], tr[n - 2]
    rr = H[p, reg]; ll = L[p, reg]; cc = C[p, reg]; oo = O[p, reg]
    rows.append(dict(date=ts[d].strftime("%Y-%m-%d"), run=runlen(p), run2=runlen(pp),
                     prng=(np.nanmax(rr) - np.nanmin(ll)) / atr[d] if atr[d] > 0 else np.nan,
                     pret=(cc[-1] - oo[0]) / atr[d] if atr[d] > 0 else np.nan))
F = pd.DataFrame(rows)
nxt = F[["date", "run"]].copy(); nxt["run_next"] = F.run.shift(-2)  # run of THIS day's own session (look-ahead placebo)
R = pd.read_csv("checks/candidates/vb_single_print_filter/replica_trades.csv")
D = R.groupby("date").net.sum().rename("pnl").reset_index().merge(F, on="date")
own = {}
for n, d in enumerate(tr): own[ts[d].strftime("%Y-%m-%d")] = runlen(d)
D["run_own"] = D.date.map(own)
D["y"] = D.date.str[:4].astype(int)
def tt(a, b): return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
print("DAY-LEVEL (traded days, day P&L sum)")
for k in (4, 6, 8, 10, 12, 16, 24):
    f = D.run.fillna(0) >= k
    print(f" run>={k:2d}: flagged {f.mean():.0%} days, kept ${D.pnl[~f].mean():6.1f} skipped ${D.pnl[f].mean():6.1f}, t {tt(D.pnl[~f], D.pnl[f]):.2f};"
          f" 2023+ diff {D.pnl[~f & (D.y>=2023)].mean()-D.pnl[f & (D.y>=2023)].mean():+.0f}")
for nm, col in (("lag-2 session run>=8 (placebo)", "run2"), ("own same-day session run>=8 (look-ahead)", "run_own")):
    f = D[col].fillna(0) >= 8; print(f" {nm}: kept ${D.pnl[~f].mean():.1f} skipped ${D.pnl[f].mean():.1f}, t {tt(D.pnl[~f], D.pnl[f]):.2f}")
f = (D.run.fillna(0) >= 8).astype(float)
print("\nflag vs prev range/ATR and prev return/ATR: corr", np.corrcoef(f, D.prng.fillna(D.prng.mean()))[0, 1].round(3), np.corrcoef(f, D.pret.fillna(0))[0, 1].round(3))
X = np.c_[np.ones(len(D)), f, D.prng.fillna(D.prng.mean()), D.pret.fillna(0), D.pret.fillna(0).abs()]
b, *_ = np.linalg.lstsq(X, D.pnl.values, rcond=None); res = D.pnl.values - X @ b
se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * res.var(ddof=X.shape[1]))
print("OLS day pnl ~ flag + prev range + prev ret + |prev ret|: coef", b.round(1), "t", (b / se).round(2))
q = pd.qcut(D.prng, 3, labels=["lo", "mid", "hi"])
print("\nflag effect within prev-range terciles (kept - skipped $/day, n flagged):")
for lv in ["lo", "mid", "hi"]:
    m = q == lv; ff = f.astype(bool)
    print(f" {lv}: {D.pnl[m & ~ff].mean() - D.pnl[m & ff].mean():+.0f}  (n {int((m & ff).sum())}/{int(m.sum())})")
fb = f.astype(bool)
print("\nwithout 2020:", round(D.pnl[~fb & (D.y != 2020)].mean() - D.pnl[fb & (D.y != 2020)].mean(), 1),
      "t", round(tt(D.pnl[~fb & (D.y != 2020)], D.pnl[fb & (D.y != 2020)]), 2))
w = D.pnl.clip(D.pnl.quantile(.025), D.pnl.quantile(.975))
print("winsorised 2.5%:", round(w[~fb].mean() - w[fb].mean(), 1), "t", round(tt(w[~fb], w[fb]), 2))
print("totals: all $%.0f, kept $%.0f, skipped $%.0f" % (D.pnl.sum(), D.pnl[~fb].sum(), D.pnl[fb].sum()))
# trade outcome mix
R["flag"] = R.kept == 0
print("\nexit mix (share) by flag:\n", pd.crosstab(R.flag, R.kind, normalize="index").round(3))
print("trades per traded day: kept", R[~R.flag].groupby("date").size().mean().round(2), "skipped", R[R.flag].groupby("date").size().mean().round(2))
print("\nSIMPLE ALTERNATIVES at the same ~29% skip share (day-level):")
for nm, s in (("prev range/ATR top 29%", D.prng), ("prev return/ATR top 29%", D.pret), ("|prev return| top 29%", D.pret.abs())):
    ff = s >= s.quantile(1 - fb.mean())
    print(f" {nm}: kept-skipped ${D.pnl[~ff].mean()-D.pnl[ff].mean():+.0f}, t {tt(D.pnl[~ff], D.pnl[ff]):.2f}, overlap with SP flag {(ff & fb).sum() / fb.sum():.0%}")
for nm, s in (("prev range", D.prng), ("prev ret", D.pret)):
    X = np.c_[np.ones(len(D)), f, s.fillna(s.mean())]
    b, *_ = np.linalg.lstsq(X, D.pnl.values, rcond=None); res = D.pnl.values - X @ b
    se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * res.var(ddof=3)); print(f" OLS pnl ~ flag + {nm}: flag coef {b[1]:.0f} t {b[1]/se[1]:.2f}; {nm} t {b[2]/se[2]:.2f}")
for half, m in (("2018-22", D.y < 2023), ("2023+", D.y >= 2023)):
    Dm = D[m]; fm = f[m]
    X = np.c_[np.ones(len(Dm)), fm, Dm.prng.fillna(D.prng.mean()), Dm.pret.fillna(0)]
    b, *_ = np.linalg.lstsq(X, Dm.pnl.values, rcond=None); res = Dm.pnl.values - X @ b
    se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * res.var(ddof=4)); print(f" {half}: flag coef {b[1]:.0f} t {b[1]/se[1]:.2f} (controls prev range, prev ret)")
