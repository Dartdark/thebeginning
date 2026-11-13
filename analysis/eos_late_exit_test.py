"""Expiration Open Short held to 14:55 (user 2026-11-08: 'do it'; lead from ingredient_ablation4: out 14:55 $789 vs $501, same t).
PRE-REGISTERED (header committed before the run; 1 variant; POST HOC in origin, so the bar is t >= ~3.65 / DSR 0.95 for promotion).
Rule = EOS (monthly options expiry: third Friday, Thursday when the Friday is closed; short NQ at the 08:30 open, stop 0.3 x ATR15,
CME early-close days skipped) with the exit moved from the 10:00 close to the 14:55 close. Costs $7.25 + 1 tick per market / stop fill.
Checks: $ a trade by period / year, the 10:00 -> 14:55 part on its own; placebo = other Fridays with the same 08:30 -> 14:55 short (same
count per year, 500 runs); checker checks/candidates/eos_late/; REPLACEMENT of the plan's EOS in every book, both versions from the same
Python rebuild: 150K evaluation (EOS risk $1,250), funded 150K x 1.5 + Twin 2 (EOS risk $1,050), personal (EOS 1 MNQ column).
  tools/run_stamped.sh analysis/eos_late_exit_test.py > analysis/outputs/eos_late_exit_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close
from portfolio import paths
from funded_lab import with_slippage
from ingredient_ablation4 import third_fridays
from ingredient_ablation3 import line
import bench150 as BB

PV, TICK, COMM = 20.0, 0.25, 7.25


def eos_trades(g, days, t1, stop=0.3):
    atr = g.daily_atr(15); pos = pd.Series(np.arange(len(g.ts)), index=pd.DatetimeIndex(g.ts)); rows = []
    for d in days:
        if d not in pos.index or is_early_close(d): continue
        r = int(pos[d])
        if np.isnan(atr[r]): continue
        j0, jx = jof(831), jof(t1); e = g.o[r, j0]
        if np.isnan(e) or np.isnan(g.c[r, jx]): continue
        sp = e + stop * atr[r]; px, kind, j1 = None, 2, jx
        for j in range(j0, jx + 1):
            if not np.isnan(g.h[r, j]) and g.h[r, j] >= sp: px, kind, j1 = max(g.o[r, j], sp), 0, j; break
        if px is None: px = g.c[r, jx]
        rows.append(dict(day=r, j0=j0, j1=j1, side=-1, entry=e, exit=px, kind=kind, date=d,
                         net=(e - px) * PV - COMM - 2 * TICK * PV, j10=jof(1000)))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); ts = pd.DatetimeIndex(g.ts); pos = pd.Series(np.arange(len(ts)), index=ts); tr = set(g.trading.tolist())
    exp = [d for d in third_fridays("2018-01-01", "2026-11-01") if d in pos.index and int(pos[d]) in tr]
    T0 = eos_trades(g, exp, 1000); T1 = eos_trades(g, exp, 1455)
    print(line(T0.net, T0.date, "EOS as is (out 10:00)")); print(line(T1.net, T1.date, "EOS held to 14:55"))
    print(f"      by year (14:55) $: {T1.groupby(T1.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    m = T0.set_index("date").net.reindex(T1.date).values; part = T1.net.values - m
    print(line(part, T1.date, "the 10:00 -> 14:55 part alone (difference)"))
    oth = [d for d in ts[ts >= "2018-01-01"] if d.dayofweek == 4 and d not in set(exp) and int(pos[d]) in tr]
    To = eos_trades(g, oth, 1455).set_index("date").net; cnt = T1.groupby(T1.date.dt.year).size(); rng = np.random.default_rng(43); pl = []
    for run in range(500):
        for y, n in cnt.items():
            pool = To[To.index.year == y]; pl += [(run, x) for x in pool.loc[rng.choice(pool.index, min(n, len(pool)), replace=False)].values]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
    print(f"   placebo other Fridays (same exit, 500 runs): ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T1.net.mean():.0f}; p {np.mean(pm >= T1.net.mean()):.3f}", flush=True)
    cd = "checks/candidates/eos_late"; os.makedirs(cd, exist_ok=True)
    T1.assign(date=T1.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": False, "variants": 2}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# EOS held to 14:55 (2026-11-08, post hoc)\nShort NQ at the 08:30 open on monthly options expiry (third Friday; Thursday if closed), stop 0.3 x ATR15, out at the 14:55 close; early closes skipped. $7.25 + 1 tick per fill. Placebo = other Fridays.\n")
    # books: replacement, both from the rebuild
    ctx = BB.setup(); trr = ctx["trr"]; atr = g.daily_atr(15)
    P = {k: (lambda w_r: (w_r[0][trr] / 10, w_r[1][trr] / 10))(paths(g, with_slippage(t[["day", "j0", "j1", "side", "entry", "exit", "kind"]]))) for k, t in (("R", T0), ("V", T1))}
    q = np.floor(1250 / (np.nan_to_num(0.3 * atr[trr], nan=1e12) * 2))[:, None]
    print(); BB.eval_bench(ctx, {"EOS rebuild -> held to 14:55": (q * (P["V"][0] - P["R"][0]), q * (P["V"][1] - P["R"][1]))})
    lab = ctx["lab"]
    for k, t in (("EOS_R", T0), ("EOS_V", T1)): lab.add(k, with_slippage(t[["day", "j0", "j1", "side", "entry", "exit", "kind"]]), stop_pts=0.3 * atr, slippage=False)
    base = {k: v for k, v in BB.BASE_FUNDED.items() if k != "EOS"}; ev = BB.BASE_FUNDED["EOS"]
    BB.BASE_FUNDED = {**base, "EOS_R": ev}
    print(); BB.funded_bench(ctx, {"EOS held to 14:55": {**base, "EOS_V": ev}}, label="Funded 150K x 1.5 + Twin 2 (EOS rebuild as the base)")
    dmn = lambda t: (t.net / 10 - 0.55).groupby(t.date).sum()
    print("\n   Personal book 1-year MC return / DD p95 (EOS column replaced, 1 MNQ):")
    BB.personal({"EOS rebuild": dmn(T0), "held to 14:55": dmn(T1)}, drop=("ExpirationOpenShort",))
