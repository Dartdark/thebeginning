"""Score every direction signal in both engines (analysis/direction_engine.py); thresholds and
follow/fade chosen on 2018-2022 only, then the 2023-2026 holdout. Benchmark: ONB's own bias."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
D = pd.read_pickle(SP + "dirfeat.pkl"); O = pd.read_pickle(SP + "dir_outcomes.pkl")
D = D.loc[D.index.intersection(O.index)]; O = O.loc[D.index]
des = D.index.year <= 2022


def pnl(sig, eng):
    return pd.Series(np.where(sig > 0, O[(eng, 1)], np.where(sig < 0, O[(eng, -1)], 0.0)), index=sig.index)


def st(p, traded):
    p = p[traded]; yrs = p.groupby(p.index.year).sum()
    pf = p[p > 0].sum() / max(1, -p[p < 0].sum())
    return p.mean(), p.mean() / p.std() * np.sqrt(len(p)), pf, (yrs > 0).sum(), len(yrs), len(p)


def signals():
    yield "ONB bias (benchmark)", "", D.onb.astype(float)
    yield "always long", "", pd.Series(1.0, index=D.index)
    for k in [c for c in D.columns if c not in ("y830", "y845", "onb")]:
        x = D[k]
        lo, hi = x[des].quantile([1 / 3, 2 / 3])
        yield k, "sign", np.sign(x).fillna(0)
        yield k, "tercile", pd.Series(np.where(x >= hi, 1, np.where(x <= lo, -1, 0)), index=x.index).where(x.notna(), 0)


rows = []
onbp = {e: pnl(D.onb, e) for e in ("open", "orb")}
for name, mode, s in signals():
    for eng in ("open", "orb"):
        best = None
        for flip in ((1,) if "bench" in name or name == "always long" else (1, -1)):
            p = pnl(s * flip, eng); tr = (s != 0) & (p != 0)
            a = st(p[des], tr[des])
            if best is None or a[0] > best[1][0]: best = (flip, a, p, tr)
        flip, a, p, tr = best
        b = st(p[~des], tr[~des])
        both = (s != 0) & (D.onb != 0)
        rows.append(dict(signal=name, mode=mode, engine=eng, dir="follow" if flip > 0 else "fade",
                         des_avg=a[0], des_t=a[1], des_pf=a[2], des_yrs=f"{a[3]}/{a[4]}",
                         hold_avg=b[0], hold_t=b[1], hold_pf=b[2], hold_yrs=f"{b[3]}/{b[4]}",
                         trades_yr=(a[5] + b[5]) / 8.8,
                         agree_onb=(np.sign(s[both] * flip) == D.onb[both]).mean(),
                         corr_onb=np.corrcoef(p, onbp[eng])[0, 1]))
R = pd.DataFrame(rows)
pd.set_option("display.width", 260)
for eng in ("open", "orb"):
    print(f"\n=== engine '{eng}' (sorted by design t; {len(R[R.engine==eng])} signals) ===")
    print(R[R.engine == eng].sort_values("des_t", ascending=False).head(25).to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
R.to_pickle(SP + "dir_scores.pkl")
