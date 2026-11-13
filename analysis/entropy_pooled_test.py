"""Pooled entropy-gate test on VB, Twin, Noise longs. Pre-registered: checks/candidates/entropy_pooled/PREREG.md (2026-11-11).
  python analysis/entropy_pooled_test.py [holdout]  -> analysis/outputs/entropy_pooled_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import jump_lib as JL
HOLD = "holdout" in sys.argv
CUT, PV, COST = 1.3505, 20.0, 7.25 + 2 * 5.0
R = "mc_reports/Backtesting Strategy Performance Report "
ENG = {"VB": (R + "VB v1.xlsx", 0), "TWIN": (R + "_ @NQ - 1 Minute Twin Continuation v2.xlsx", 0),
       "NOISE_L": (R + "_ @NQ - 15 Minutes NQ Noise RTH Anchor.xlsx", 1)}

def barlen(p):
    try:
        st = pd.read_excel(p, sheet_name="Settings", header=None); c = dict(zip(st[0].astype(str), st[1].astype(str))).get("Compression", "5 Minutes")
        return int(c.split()[0]) if "Minute" in c else 5
    except Exception: return 5

def trades(p, longs_only):
    r = pd.read_excel(p, sheet_name="List of Trades", header=2)
    en = r[r.Type.astype(str).str.startswith("Entry")].reset_index(drop=True); ex = r[r.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    n = min(len(en), len(ex)); en, ex = en.iloc[:n], ex.iloc[:n]
    side = np.where(en.Type.astype(str).str.contains("Long"), 1, -1)
    t = pd.DataFrame(dict(et=pd.to_datetime(en.Date), side=side,
                          net=side * (ex.Price.to_numpy(float) - en.Price.to_numpy(float)) * PV - COST))
    t["sig"] = t.et - pd.Timedelta(minutes=barlen(p))
    return t[t.side > 0].reset_index(drop=True) if longs_only else t

m = JL.minute(); ts = m.ts.to_numpy(); cl = m.close.to_numpy()
def ent(x):
    s = np.sign(np.diff(x)).astype(int) + 1
    p = np.bincount(s[:-1] * 3 + s[1:], minlength=9) / max(1, len(s) - 1); p = p[p > 0]
    return -(p * np.log(p)).sum()
def entropy_at(sig):
    e = sig.to_numpy().astype("datetime64[ns]"); j = np.searchsorted(ts, e, side="right"); lo = np.searchsorted(ts, e - np.timedelta64(30, "m"))
    return np.array([ent(cl[a:b]) if b - a >= 20 else np.nan for a, b in zip(lo, j)])

T = {}
for k, (p, lo) in ENG.items():
    t = trades(p, lo); t["E"] = entropy_at(t.sig); t["yr"] = t.et.dt.year; T[k] = t[t.yr >= 2018].reset_index(drop=True)
    print(f"{k}: {len(T[k])} trades 2018+, entropy missing {T[k].E.isna().sum()}, gate-on share {np.mean(T[k].E <= CUT):.0%}")

def stat(sets):
    num = den = 0.0; rows = []
    for k, (x, on) in sets.items():
        a, b = x[on], x[~on]; se2 = a.var() / len(a) + b.var() / len(b); d = a.mean() - b.mean()
        num += d / se2; den += 1 / se2; rows.append((k, len(a), len(b), d, d / np.sqrt(se2), a.mean(), b.mean()))
    return num / np.sqrt(den), rows

def report(sel, lab):
    sets = {k: (t.net.to_numpy()[sel(t)], (t.E <= CUT).to_numpy()[sel(t)]) for k, t in T.items()}
    z, rows = stat(sets); print(f"=== {lab}: pooled z {z:.2f}")
    for k, na, nb, d, tt, ma, mb in rows: print(f"   {k:<8} gate on {na:4d} ${ma:7.1f} | rest {nb:4d} ${mb:7.1f} | diff ${d:7.1f} t {tt:5.2f}")
    return z, sets

z, sets = report(lambda t: (t.yr <= 2022).to_numpy(), "Gate 1: design 2018-2022")
rng = np.random.default_rng(1); pz = []
for _ in range(2000):
    s2 = {}
    for k, (x, on) in sets.items():
        o = np.zeros(len(x), bool); o[rng.choice(len(x), on.sum(), replace=False)] = True; s2[k] = (x, o)
    pz.append(stat(s2)[0])
print(f"   placebo (2,000 random same-size subsets per strategy): p = {np.mean(np.array(pz) >= z):.3f}")
print("--- information only (design): sides")
for s, nm in ((1, "longs"), (-1, "shorts")):
    for k, t in T.items():
        x = t[(t.yr <= 2022) & (t.side == s)]
        if len(x) > 30:
            a, b = x[x.E <= CUT].net, x[~(x.E <= CUT)].net
            print(f"   {nm:<7}{k:<8} diff ${a.mean() - b.mean():7.1f} t {(a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b)):5.2f} (n {len(a)}/{len(b)})")
if HOLD: report(lambda t: (t.yr >= 2023).to_numpy(), "Gate 2: ONE LOOK at 2023+")
