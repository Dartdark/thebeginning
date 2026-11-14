"""Test: the reference's trail (spy_dip_filter_settle.spy mg) keeps the best close in a dict keyed by id(pos). CPython reuses the id of
a freed dict, so a new trade can start with an OLD trade's best close. Re-run the reference simulate with (a) as written,
(b) the best close stored on the position itself (pos['bb']), and count id reuse. Run from repo root."""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
src = open("analysis/spy_dip_filter_settle.py", encoding="utf-8").read().split("\nSPEC = ")[0]
G = {"__name__": "ref", "__doc__": "x\n"}; exec(compile(src, "spy_dip_ref", "exec"), G)
b, sig, plan, mg = G["spy"]("ES"); simulate, atr, htf_at, dmi = G["simulate"], G["atr"], G["htf_at"], G["dmi"]
C = b.close.to_numpy()
# rebuild A1 / A4 exactly as spy() (closure values are not exposed)
A1 = mg.__closure__[[c for c in mg.__code__.co_freevars].index("A1")].cell_contents
A4 = mg.__closure__[[c for c in mg.__code__.co_freevars].index("A4")].cell_contents
seen = {}; reuse = [0]
def mg_count(j, pos, event=None):
    k = id(pos)
    if pos.get("_first") is None:
        pos["_first"] = True
        if k in seen: reuse[0] += 1
        seen[k] = 1
    return mg(j, pos, event)
def mg_fixed(j, pos, event=None):
    s = pos["s"]; bb_ = pos.get("bb", pos["e"]); bb_ = max(bb_, C[j]) if s == 1 else min(bb_, C[j]); pos["bb"] = bb_
    if s == 1: pos["stop"] = max(pos["stop"], min(bb_ - 3 * A4[j], C[j] - 0.5 * A1[j]))
    else: pos["stop"] = min(pos["stop"], max(bb_ + 3 * A4[j], C[j] + 0.5 * A1[j]))
usd = lambda t: (t.ret * t.e * 50.0 - 5.0 - 12.5 - np.where(t.why == "target", 0.0, 12.5)) / 10 - 0.55
entry_t = b.index + pd.Timedelta(hours=1); ses = pd.DatetimeIndex((entry_t + pd.Timedelta(hours=7)).normalize())
rise = G["prior"](G["SR"]["VIX/VIX3M (term structure)"], ses, G["RULES"]["rising"]) == 1
tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x))
for nm, f in (("as written (id(pos) key)", mg_count), ("fixed (best on the position)", mg_fixed)):
    t = simulate(b, sig, plan, manage=f); t["usd"] = usd(t); k = t[~rise[np.searchsorted(b.index.values, t.t.values)]]
    yrs = (k.t.max() - k.t.min()).days / 365.25; e = k.usd.groupby(k.tx.dt.normalize()).sum().cumsum()
    print(f"{nm:<30} unfiltered {len(t)} trades ${t.usd.sum():,.0f} t {tt(t.usd):.2f} | session+drop {len(k)} trades ${k.usd.sum() / yrs:,.0f}/yr t {tt(k.usd):.2f} "
          f"2018-22 t {tt(k.usd[k.yr <= 2022]):.2f} 2023+ t {tt(k.usd[k.yr >= 2023]):.2f} maxDD ${(e - e.cummax()).min():,.0f}")
    if nm.startswith("fixed"): t.to_csv("checks/candidates/mc_es_dip_buy/ref_fixed_unfiltered.csv", index=False)
print(f"position dicts that reused an earlier position id: {reuse[0]}")
for nm, f in (("as written", mg), ("fixed", mg_fixed)):
    t = simulate(b, np.where(rise, 0, sig), plan, manage=f); t["usd"] = usd(t); yrs = (t.t.max() - t.t.min()).days / 365.25
    print(f"block-signals (session) {nm:<11} {len(t)} trades ${t.usd.sum() / yrs:,.0f}/yr t {tt(t.usd):.2f}")
