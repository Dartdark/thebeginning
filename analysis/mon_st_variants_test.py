"""Monday Long by the Friday before, and Swing Target shorts only (user 2026-11-08; leads from ingredient_ablation5). PRE-REGISTERED (header
committed before the run; POST HOC in origin: 4 variants, bar ~3.65 for promotion). Rebuilds = analysis/ingredient_ablation5.py.
  Monday Long (Mondays, buy the 08:30 open, stop 0.5 ATR15, out 15:00):  A only after a down Friday (Friday 08:30 -> 15:00 close < open)
    B only after an up Friday   C every Monday, 2x size after a down Friday (1x after up)
  Swing Target v3 shorts only (first break of the prior 2-day RTH range, short side only; long breaks not traded)
Books (each a REPLACEMENT, both sides from the same Python rebuild): personal book (MondayLong / SwingTarget column, 1 MNQ); funded 150K
x 1.5 + Twin 2 with Monday Long 1.5 MNQ (rebuild as the base). Per NQ costs $7.25 + 1 tick per market / stop fill.
Placebos: Monday A / B = random Monday subsets of the same size per year (500 runs); ST shorts = the checker's own label shuffle via a
filter file (kept = short trades among all rebuild trades).
  tools/run_stamped.sh analysis/mon_st_variants_test.py > analysis/outputs/mon_st_variants_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close
from ingredient_ablation3 import line
from ingredient_ablation5 import swing
from new_sources_150k import daypaths
import bench150 as BB

PV, TICK, COMM = 20.0, 0.25, 7.25


def mondays(g):
    atr = g.daily_atr(15); ts = pd.DatetimeIndex(g.ts); trs = set(g.trading.tolist()); rows = []
    for r in g.trading:
        d = ts[r]
        if d < pd.Timestamp("2018-01-01") or d.dayofweek != 0 or is_early_close(d) or np.isnan(atr[r]): continue
        j0, jx = jof(831), jof(1500); e = g.o[r, j0]
        if np.isnan(e) or np.isnan(g.c[r, jx]): continue
        e += TICK; sp = e - 0.5 * atr[r]; px = None; worst = 0.0
        for j in range(j0, jx + 1):
            if np.isnan(g.c[r, j]): continue
            worst = min(worst, g.l[r, j] - e)
            if g.l[r, j] <= sp: px = min(g.o[r, j], sp) - TICK; break
        if px is None: px = g.c[r, jx] - TICK
        p = next((q for q in range(r - 1, r - 5, -1) if q in trs), None)
        up = p is not None and g.c[p, jof(1500)] > g.o[p, jof(831)]
        net = (px - e) * PV - COMM; rows.append(dict(date=d, net=net, adv=min(worst * PV - COMM, net), up_fri=up))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); M = mondays(g)
    V = {"as is (every Monday)": M.assign(w=1.0), "A after a down Friday only": M[~M.up_fri].assign(w=1.0),
         "B after an up Friday only": M[M.up_fri].assign(w=1.0), "C 2x after a down Friday": M.assign(w=np.where(M.up_fri, 1.0, 2.0))}
    print("\n1. Monday Long (per NQ; C per unit of base size):")
    for nm, t in V.items(): print(line(t.net * t.w, t.date, nm))
    cnt = lambda t: t.groupby(t.date.dt.year).size(); rng = np.random.default_rng(47)
    for nm in ("A after a down Friday only", "B after an up Friday only"):
        t = V[nm]; c = cnt(t); pm = [np.mean(np.concatenate([M[M.date.dt.year == y].net.sample(n, random_state=int(rng.integers(1e9))).values for y, n in c.items()])) for _ in range(500)]
        print(f"   {nm}: random Mondays (same count per year) ${np.mean(pm):.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${t.net.mean():.0f}; p {np.mean(np.array(pm) >= t.net.mean()):.3f}")
    print("\n2. Swing Target v3:")
    S0 = swing(g); Ss = swing(g, side_only=-1); print(line(S0.net, S0.date, "both sides (rebuild)")); print(line(Ss.net, Ss.date, "shorts only"))
    print(f"      shorts by year $: {Ss.groupby(Ss.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    cd = "checks/candidates/st_shorts"; os.makedirs(cd, exist_ok=True)
    S0.assign(date=S0.date.dt.strftime("%Y-%m-%d"), kept=(S0.side < 0).astype(int))[["date", "side", "net", "kept"]].to_csv(f"{cd}/trades.csv", index=False)
    json.dump({"kind": "filter", "pre_registered": False, "variants": 4}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# Swing Target v3, shorts only (2026-11-08, post hoc)\nFilter on the v3 rebuild trades: keep the short breaks (first break of the prior 2-day RTH low), drop the long breaks. $7.25 + 1 tick per fill.\n")
    for nm, k in (("A after a down Friday only", "mon_downfri"), ("B after an up Friday only", "mon_upfri")):
        cdm = f"checks/candidates/{k}"; os.makedirs(cdm, exist_ok=True); keep = (~M.up_fri if k == "mon_downfri" else M.up_fri).astype(int)
        M.assign(date=M.date.dt.strftime("%Y-%m-%d"), side=1, kept=keep)[["date", "side", "net", "kept"]].to_csv(f"{cdm}/trades.csv", index=False)
        json.dump({"kind": "filter", "pre_registered": False, "variants": 4}, open(f"{cdm}/meta.json", "w"))
        open(f"{cdm}/spec.md", "w").write(f"# Monday Long, {nm} (2026-11-08, post hoc)\nFilter on Monday Long trades (buy 08:30, stop 0.5 ATR, out 15:00) by the Friday before (08:30 -> 15:00 close vs open).\n")
    dmn = lambda t, w=None: ((t.net * (1.0 if w is None else w)) / 10 - 0.55 * (1.0 if w is None else w)).groupby(t.date).sum()
    print("\n3. Personal book 1-year MC return / DD p95 (column replaced by the rebuild as is vs the variant, 1 MNQ base):")
    BB.personal({nm: dmn(t, t.w) for nm, t in V.items()}, drop=("MondayLong",))
    BB.personal({"ST both sides (rebuild)": dmn(S0), "ST shorts only": dmn(Ss)}, drop=("SwingTarget",))
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts); lab = ctx["lab"]
    for nm, t in V.items():
        W1, R1 = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a * w, n * w) for d, a, n, w in zip(t.date, t.adv, t.net, t.w)]); lab.W["MON_" + nm[0]] = W1; lab.C["MON_" + nm[0]] = R1[:, -1]
    base = {k: v for k, v in BB.BASE_FUNDED.items() if k != "MON_MC"}; q = BB.BASE_FUNDED["MON_MC"]
    BB.BASE_FUNDED = {**base, "MON_a": q}
    print(); BB.funded_bench(ctx, {nm: {**base, "MON_" + nm[0]: q} for nm in list(V)[1:]}, label=f"Funded 150K x 1.5 + Twin 2 (Monday Long {q} MNQ, rebuild as the base)")
