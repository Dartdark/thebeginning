"""Evidence sheets' descriptive inventory only; plan 574f81b.

Reads the saved design occupancy map, filenames and CSV headers. Never reads candidate
price observations, builds signals/returns, reconstructs strategies or calls account tools.
Run: /workspace/venvs/thebeginning/bin/python -B analysis/codex_flow_evidence_inventory.py
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

SOURCE = Path("analysis/outputs/codex_sge_delivery_screen/roster_minute_occupancy.csv")
OUT = Path("analysis/outputs/codex_flow_evidence_sheets")
WINDOWS = [
    ("A_spy_open", "ES", 8 * 60 + 15, 8 * 60 + 16, 8 * 60 + 25),
    ("B_spy_post_close", "ES", 15 * 60 + 1, 15 * 60 + 2, 15 * 60 + 10),
    ("C_letf_reset", "NQ", 14 * 60 + 31, 14 * 60 + 32, 14 * 60 + 49),
    ("D_spx_charm", "ES", 14 * 60 + 31, 14 * 60 + 32, 14 * 60 + 49),
]


def clock(j):
    return f"{j // 60:02}:{j % 60:02}"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    p = pd.read_csv(SOURCE)
    assert len(p) == 5 * 1440 and not p.duplicated(["weekday", "minute"]).any()
    assert p.any_open_fraction.between(0, 1).all()
    rows = []
    for candidate, symbol, decision, first, last in WINDOWS:
        for weekday, g in p.groupby("weekday", sort=True):
            assert g.dates.nunique() == 1
            n = int(g.dates.iloc[0])
            at_decision = float(g.loc[g.minute == decision, "any_open_fraction"].iloc[0])
            count = n * (1 - at_decision)
            assert abs(count - round(count)) < 1e-6
            use = g[g.minute.between(first, last)]
            assert len(use) == last - first + 1
            opened = use.any_open_fraction.to_numpy()
            rows.append(dict(candidate=candidate, instrument=symbol, weekday=int(weekday), day=g.day.iloc[0],
                             design_dates=n, decision_ct=clock(decision), first_bar_ct=clock(first), last_bar_ct=clock(last),
                             flat_decision_dates=int(round(count)),
                             fraction_minutes_flat=float(1 - opened.mean()),
                             whole_window_flat_lower_bound=float(max(0, 1 - opened.sum())),
                             whole_window_flat_upper_bound=float(1 - opened.max())))
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / "window_occupancy_by_weekday.csv", index=False)
    totals = []
    for candidate, g in detail.groupby("candidate", sort=False):
        n = int(g.design_dates.sum())
        totals.append(dict(candidate=candidate, instrument=g.instrument.iloc[0], design_dates=n,
                           flat_decision_dates=int(g.flat_decision_dates.sum()),
                           flat_decision_fraction=float(g.flat_decision_dates.sum() / n),
                           fraction_minutes_flat=float(np.average(g.fraction_minutes_flat, weights=g.design_dates)),
                           decision_ct=g.decision_ct.iloc[0], first_bar_ct=g.first_bar_ct.iloc[0], last_bar_ct=g.last_bar_ct.iloc[0]))
    totals = pd.DataFrame(totals)
    totals.to_csv(OUT / "window_occupancy_summary.csv", index=False)
    costs = []
    for symbol, pv, commission in (("NQ", 20., 7.25), ("ES", 50., 5.)):
        rt = commission + 2 * .25 * pv
        costs.append(dict(instrument=symbol, point_value=pv, tick=.25, commission=commission,
                          baseline_round_trip=rt, break_even_points=rt / pv,
                          proposed_screen_gross_hurdle=1.5 * rt, hurdle_points=1.5 * rt / pv))
    costs = pd.DataFrame(costs)
    costs.to_csv(OUT / "cost_hurdles.csv", index=False)
    schemas = {}
    for pattern in ("SPY_daily.csv", "GEXOI_*.csv", "GEX_1min_*.csv", "OF_1min_*.csv", "ES_1min_*.csv", "NQ_1min_20*.csv"):
        files = sorted(Path("data").glob(pattern))
        column_sets = {tuple(pd.read_csv(f, nrows=0).columns.tolist()) for f in files}
        schemas[pattern] = dict(file_count=len(files), first_file=str(files[0]) if files else None,
                               distinct_schemas=[list(x) for x in sorted(column_sets)])
    (OUT / "repo_schema_inventory.json").write_text(json.dumps(schemas, indent=2) + "\n")
    manifest = dict(plan_commit="574f81b", prior_catalog_source_commit="2d1f279", period="2018-22 saved map only",
                    occupancy_source=str(SOURCE), occupancy_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                    return_trials=0, candidate_signals_calculated=False, candidate_returns_calculated=False,
                    holdout_opened=False, account_simulations_run=False,
                    interpretation="Flat-decision counts precede all external-signal filters. Minute averages are unconditional; joint candidate/window overlap is not measured.")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(totals.to_string(index=False))
    matrix = detail.pivot(index="day", columns="candidate", values="fraction_minutes_flat").reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    print("\n".join(line.rstrip() for line in matrix.to_string().splitlines()))
    print(costs.to_string(index=False))
    print("No strategy signal, return or account test executed.")


if __name__ == "__main__":
    main()
