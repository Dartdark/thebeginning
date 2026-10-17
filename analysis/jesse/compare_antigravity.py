"""Antigravity's blind rebuilds (branch antigravity/jesse, tasks/out_NN/trades.csv) vs the MultiCharts reports and Claude's
Jesse ports, trade by trade (2026-10-17). Matching by entry date and order within the day, over each MC report's range.
  python3 analysis/jesse/compare_antigravity.py [SCRATCH_DIR]
"""
import sys, io, subprocess, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis/jesse")
import numpy as np, pandas as pd
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
sys.argv = sys.argv[:1]
import compare as C

TASKS = {"02": "VaultBreak", "03": "ONBiasADX30", "04": "ONBiasML", "05": "MondayLong", "06": "ExpOpenShort", "07": "LateDayFlow", "08": "NFPFade"}


def ag(nn):
    raw = subprocess.check_output(["git", "show", f"origin/antigravity/jesse:tasks/out_{nn}/trades.csv"]).decode()
    t = pd.read_csv(io.StringIO(raw))
    t["entry_time"] = pd.to_datetime(t.date.astype(str) + " " + t.entry_time_ct.astype(str)); t["side"] = np.where(t.side.str.lower().str.startswith("l"), 1, -1)
    t = t.rename(columns={"entry_price": "entry", "exit_price": "exit"})
    return t[["entry_time", "side", "entry", "exit", "points", "exit_reason"]]


def match(a, b):
    a, b = a.copy(), b.copy()
    for d in (a, b): d["day"] = d.entry_time.dt.normalize(); d["k"] = d.sort_values("entry_time").groupby("day").cumcount()
    return a.merge(b, on=["day", "k"], how="outer", suffixes=("_a", "_b"), indicator="src")


if __name__ == "__main__":
    rows = []
    for nn, nm in TASKS.items():
        path, pv, tick, cost = C.REPORTS[nm]
        m = C.mc_trades(path); A = ag(nn)
        J = pd.read_csv(SP + f"jesse_{nm}.csv", parse_dates=["entry_time"])
        lo, hi = m.entry_time.min().normalize(), m.entry_time.max().normalize() + pd.Timedelta(days=1)
        A = A[(A.entry_time >= lo) & (A.entry_time < hi)]; J = J[(J.entry_time >= lo) & (J.entry_time < hi)]
        mm = match(A, m); both = mm[mm.src == "both"]
        same_side = (both.side_a == both.side_b).mean()
        dp = (both.points_a - both.points_b) * pv
        mj = match(A, J); bj = mj[mj.src == "both"]; dpj = (bj.points_a - bj.points_b) * pv
        r = dict(task=nn, strategy=nm, mc=len(m), antigravity=len(A), claude_jesse=len(J), same_days_mc=len(both),
                 only_mc=int((mm.src == "right_only").sum()), only_ag=int((mm.src == "left_only").sum()), same_side=same_side,
                 pnl50_mc=np.mean(dp.abs() <= 50), corr_mc=np.corrcoef(both.points_a, both.points_b)[0, 1],
                 pnl50_jesse=np.mean(dpj.abs() <= 50), gross_mc=m.points.sum() * pv / len(m), gross_ag=A.points.sum() * pv / len(A),
                 gross_j=J.points.sum() * pv / len(J))
        rows.append(r)
        print(f"\n=== Task {nn} {nm}: MC {len(m)} | Antigravity {len(A)} | Claude's Jesse {len(J)}; same day+order as MC {len(both)} "
              f"(only MC {r['only_mc']}, only AG {r['only_ag']}), same side {same_side:.1%}")
        print(f"   P&L within $50 of MC {r['pnl50_mc']:.1%} (corr {r['corr_mc']:.3f}); within $50 of Claude's Jesse {r['pnl50_jesse']:.1%}")
        print(f"   gross $ per trade: MC {r['gross_mc']:.0f} | AG {r['gross_ag']:.0f} | Claude's Jesse {r['gross_j']:.0f}")
        big = both.assign(dp=dp).reindex(dp.abs().sort_values(ascending=False).index).head(3)
        for x in big.itertuples():
            print(f"      {x.day.date()} #{x.k}: AG {x.entry_a:.2f}->{x.exit_a:.2f} ({x.exit_reason}) | MC {x.entry_b:.2f}->{x.exit_b:.2f}  diff ${x.dp:,.0f}")
        om = mm[mm.src == "right_only"].day.dt.date.tolist()[:8]; oa = mm[mm.src == "left_only"].day.dt.date.tolist()[:8]
        if om: print(f"      only MC: {om}")
        if oa: print(f"      only AG: {oa}")
    df = pd.DataFrame(rows)
    print("\nSummary:\n" + df.round(3).to_string(index=False))
