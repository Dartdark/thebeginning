"""Reconcile and summarize saved design outputs; never reruns strategy returns or tests."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("analysis/outputs/codex_ldf_flow_sizing")
t = pd.read_csv(OUT / "design_trades.csv", parse_dates=["date"])
d = pd.read_csv(OUT / "design_daily_pnl.csv", index_col=0, parse_dates=True)
decision = json.loads((OUT / "design_decision.json").read_text())
checkpoint = json.loads((OUT / "input_checkpoint.json").read_text())
assert t.date.min() >= pd.Timestamp(checkpoint["evaluation_start"])
assert t.date.max() <= pd.Timestamp("2022-12-31") and d.index.max() <= pd.Timestamp("2022-12-31")
assert len(t) == checkpoint["evaluated_entries"]
assert np.allclose(t.gross_nq - 17.25, t.net_nq)
assert np.allclose(t.net_R-t.net_B, t.increment_R)
assert np.allclose(t.net_S-t.net_B, t.increment_S)
for key in ("B", "R", "S", "increment_R", "increment_S"):
    assert np.isclose(d[key].sum(), t[key if key.startswith("increment") else f"net_{key}"].sum())
fallback = ~t.joint_ready
assert t.loc[fallback, "q_R"].eq(2).all() and t.loc[fallback, "q_S"].eq(2).all()
q_total = float(t.q_R.sum())
base_total = 2*len(t)
cells = pd.read_csv(OUT / "design_placebo_cells.csv")
roll = pd.read_csv(OUT / "input_roll_volume_diagnostics.csv")
active_roll = roll[roll.last_hour_notional.notna()]
summary = dict(
    arithmetic_and_date_reconciliation="PASS",
    evaluated_entries=len(t),
    baseline_contract_round_trips=base_total,
    candidate_contract_round_trips=q_total,
    increase_in_contract_round_trips=q_total/base_total-1,
    fallback_entries=int(fallback.sum()),
    matched_placebo_cells=len(cells),
    matched_cells_with_movable_sizes=int(cells.movable.sum()),
    entries_in_cells_with_movable_sizes=int(cells.loc[cells.movable, "entries"].sum()),
    roll_window_rows=len(roll),
    usable_roll_window_rows=len(active_roll),
    min_usable_roll_window_contracts=float(active_roll.last_hour_contracts.min()),
    min_roll_notional_relative_to_lagged_expected=float(active_roll.relative_to_lagged_expected_notional.min()),
    max_candidate_date=str(t.date.max().date()),
    no_replication_or_funded_simulation=not decision["replication_opened"] and decision["funded_simulations"]==0,
)
rows = []
for key in ("R", "S"):
    for group, z in t[t.joint_ready].groupby(f"group_{key}"):
        rows.append(dict(configuration=key, group=group, entries=len(z), mean_net_nq=z.net_nq.mean(), sd_net_nq=z.net_nq.std()))
pd.DataFrame(rows).to_csv(OUT / "design_covered_flow_groups.csv", index=False)
(OUT / "report_reconciliation.json").write_text(json.dumps(summary, indent=2)+"\n")
print(json.dumps(summary, indent=2))
print(pd.DataFrame(rows).to_string(index=False))
