"""Worst-case stacking of the funded plan's NQ lines (2026-10-22, after Kevin Davey's 'unknown future correlation':
Feb 2018, all his uncorrelated index strategies went long together). Uses Codex's per-entry table of the accepted
50K funded plan at FULL size (no cushion scaling): analysis/outputs/codex_overlap_risk_cap/nq_overlap_entries.csv on
branch codex/work (commit 3998a8e): VB 2/1, ONB ML $400, Monday 1, EOS $700, LDF 2, NFP $500, Bridge Monday 1,
RS longs 1 MNQ. ES MOC (2 MES) and the CL fade are not in it.
  git show origin/codex/work:analysis/outputs/codex_overlap_risk_cap/nq_overlap_entries.csv > /tmp/e.csv
  python3 analysis/stack_stress_test.py /tmp/e.csv
"""
import sys, pandas as pd

e = pd.read_csv(sys.argv[1], parse_dates=["date"]); e["pnl"] = e.net_mnq * e.q_orig
d = e.groupby("date").pnl.sum()
print(f"days with an NQ trade: {len(d)}")
for lim in (1000, 1500, 2000):
    print(f"days losing more than ${lim}: {(d < -lim).sum()}")
print("worst 10 days:")
for dt, v in d.nsmallest(10).items():
    print(f"  {dt.date()} {v:8.0f}  {e[e.date == dt].groupby('source').pnl.sum().round(0).to_dict()}")
for a, b, lab in (("2018-02-01", "2018-02-12", "Feb 2018"), ("2020-02-20", "2020-03-31", "Feb-Mar 2020"),
                  ("2022-01-01", "2022-12-31", "2022"), ("2025-04-01", "2025-04-15", "Apr 2025 tariffs")):
    x = d[(d.index >= a) & (d.index <= b)]
    print(f"{lab}: worst day {x.min():.0f}, total {x.sum():.0f}")
full = d.reindex(pd.bdate_range(d.index.min(), d.index.max()), fill_value=0)
for k in (2, 3, 5):
    r = full.rolling(k).sum(); print(f"worst {k}-day stretch: {r.min():.0f} ending {r.idxmin().date()}")
per = e.groupby(["source", "date"]).pnl.sum().reset_index(); per["wd"] = per.date.dt.dayofweek
worst = per.groupby("source").pnl.min()
print("worst single day per line:", worst.round(0).to_dict())
for wd, nm in enumerate("Mon Tue Wed Thu Fri".split()):
    lines = per[per.wd == wd].source.unique()
    print(f"{nm}: every line's worst day at once = {worst[lines].sum():.0f} ({', '.join(sorted(lines))})")
