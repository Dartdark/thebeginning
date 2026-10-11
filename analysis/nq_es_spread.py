"""NQ-ES intraday spread test (beta-weighted, from the 8:30 open): does a large spread
move reverse (fade) or continue (follow)? Gross $ per 1 NQ of notional, before costs.
Needs the pickled grids from a scratch run; kept as a record of the 2026-10-11 test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
g = pickle.load(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/g24.pkl","rb"))
ge = pickle.load(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/ge.pkl","rb"))
# common trading dates
dn = pd.Series(np.arange(len(g.dates)), index=g.dates); de = pd.Series(np.arange(len(ge.dates)), index=ge.dates)
common = np.intersect1d(g.dates[g.trading], ge.dates[ge.trading])
rn, re = dn[common].to_numpy(), de[common].to_numpy()
Cn = pd.DataFrame(g.c[rn]).ffill(axis=1).to_numpy(); Ce = pd.DataFrame(ge.c[re]).ffill(axis=1).to_numpy()
a = jof(830)
ln, le = np.log(Cn), np.log(Ce)
times = [t for t in range(900, 1431, 5) if t % 100 in (0, 15, 30, 45)]
J = np.array([jof(t) for t in times])
# beta from previous 20 days of 5-min returns in RTH
r5n = np.diff(ln[:, a:jof(1500)+1:5], axis=1); r5e = np.diff(le[:, a:jof(1500)+1:5], axis=1)
cov = pd.Series([np.nansum(x*y) for x, y in zip(r5n, r5e)]).rolling(20).sum().shift(1)
var = pd.Series([np.nansum(y*y) for y in r5e]).rolling(20).sum().shift(1)
beta = (cov / var).to_numpy()
print("beta median", np.nanmedian(beta).round(2))
S = (ln[:, J] - ln[:, [a]]) - beta[:, None] * (le[:, J] - le[:, [a]])        # spread move since 8:30, log units
norm = pd.DataFrame(np.abs(S)).rolling(14).mean().shift(1).to_numpy()
fw = {}
for H in (30, 60, 120):
    Jh = np.minimum(J + H, jof(1500))
    fw[H] = ((ln[:, Jh] - ln[:, J]) - beta[:, None] * (le[:, Jh] - le[:, J]))
NQpx = Cn[:, J]
rows = []
for k in (1.0, 1.5, 2.0, 2.5, 3.0):
    m = (np.abs(S) > k * norm) & ~np.isnan(norm) & ~np.isnan(beta)[:, None]
    for H in (30, 60, 120):
        f = -np.sign(S[m]) * fw[H][m]          # fade: + means spread reverted
        dollars = f * NQpx[m] * 20             # $ per 1 NQ notional (ES leg beta-weighted)
        rows.append(dict(k=k, H=H, n=m.sum(), days=m.any(1).sum(), mean_bp=f.mean()*1e4, t=f.mean()/f.std()*np.sqrt(m.sum()), usd_per_NQ=dollars.mean(), win=(f > 0).mean()))
print(pd.DataFrame(rows).round(2).to_string(index=False))
pickle.dump(dict(rn=rn, re=re, common=common, beta=beta), open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/sp_idx.pkl","wb"))
print("\nFollow the spread, first signal of the day, hold to 15:00; $ per 1 NQ notional (ES leg beta-weighted), gross")
end = jof(1500)
yr = pd.DatetimeIndex(pd.to_datetime(common.astype(str))).year
for k in (1.5, 2.0, 2.5, 3.0):
    m = (np.abs(S) > k * norm) & ~np.isnan(norm) & ~np.isnan(beta)[:, None]
    res = []
    for d in np.nonzero(m.any(1))[0]:
        i = np.argmax(m[d]); j = J[i]
        f = np.sign(S[d, i]) * ((ln[d, end] - ln[d, j]) - beta[d] * (le[d, end] - le[d, j]))
        res.append((yr[d], f * Cn[d, j] * 20))
    r = pd.DataFrame(res, columns=["yr", "usd"])
    by = r.groupby("yr").usd.mean()
    print(f"k={k}: days {len(r)}, gross ${r.usd.mean():.0f}, t={r.usd.mean()/r.usd.std()*np.sqrt(len(r)):.1f}, win {(r.usd>0).mean():.0%}, years+ {(by>0).sum()}/{len(by)}  " + " ".join(f"{v:.0f}" for v in by))
