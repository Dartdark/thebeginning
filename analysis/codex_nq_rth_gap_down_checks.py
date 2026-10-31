"""Post-run invariants and plot from retained ledgers; no new strategy trial."""
from pathlib import Path
import json
import os
import numpy as np
import pandas as pd
import codex_nq_rth_gap_down as E


def run():
    checked, unresolved = 0, 0
    for phase in ("design", "validation"):
        p = E.OUT / ("reconstruction_" + phase)
        marker = json.loads((p / "completed.json").read_text())
        cache = E.ROOT / marker["cache_path"]
        assert E.sha(cache) == marker["cache_sha256"]
        with np.load(cache) as archive:
            g = {name: archive[name] for name in archive.files}
        t = pd.read_csv(p / "all_long_trades.csv")
        for row in t.itertuples():
            if not row.resolved:
                assert pd.isna(row.net_mnq) and pd.isna(row.pnl)
                unresolved += 1; continue
            r, j0, j1, end = int(row.day), int(row.j0), int(row.j1), int(row.exit_j)
            assert j0 == E.ENTRY_J and row.qty == 1 and row.side == 1
            assert g["valid"][r, j0:j1 + 1].all()
            entry = g["o"][r, j0]; stop = entry - 100
            hits = np.flatnonzero(g["l"][r, j0:end + 1] <= stop)
            if row.kind == 0:
                assert len(hits) and j0 + hits[0] == j1
                assert np.isclose(row.exit, min(stop, g["o"][r, j1]))
            else:
                assert row.kind == 2 and j1 == end and not len(hits)
                assert np.isclose(row.exit, g["c"][r, end])
            assert np.isclose(row.net_mnq, (row.exit - entry) * 2 - 2.24)
            assert row.j1 <= 900 and end in (720, 900)
            checked += 1
        first = json.loads((E.OUT / "design/pre_value_binding.json").read_text())
        if phase == "design":
            second = json.loads((p / "pre_value_binding.json").read_text())
            assert first["files"] == second["files"]
    full = pd.read_csv(E.OUT / "diagnostics/full_daily.csv")
    metrics = pd.read_csv(E.OUT / "diagnostics/full_metrics.csv")
    m = metrics[(metrics.period == "full") & (metrics.model == "GAP_NATIVE")].iloc[0]
    assert np.isclose(full.GAP_NATIVE.sum(), m.total)
    assert checked == len(full)
    original = json.loads((E.OUT / "design/completed.json").read_text())
    assert original["status"] == "REJECT_GROSS"
    progress = json.loads((E.ROOT / "agents/codex/research/strategy_hunt_v2_progress.json").read_text())
    assert progress["budget"]["hypotheses_started"] == 10 and not progress["continuation_pause"]["is_enabled"]
    result = dict(passed=True, all_long_resolved_paths_checked=checked,
                  unresolved_paths_retained_as_unknown=unresolved,
                  invariant_scope="Every resolved ledger: first stop touch, worse gap, exact scheduled time exit, native fee arithmetic, clock and quantity",
                  fresh_independent_raw_spec_checker=False, no_promotion=True,
                  design_input_identity_unchanged=True, original_gross_rejection_preserved=True,
                  hunt_budget_and_pause_unchanged=True)
    E.dump(E.OUT / "execution_invariants.json", result)

    os.environ["MPLCONFIGDIR"] = str(E.OUT / "cache/matplotlib")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    full["date"] = pd.to_datetime(full.date)
    fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True, gridspec_kw={"height_ratios": [2, 1]}, constrained_layout=True)
    for name, color, label in (("GAP_NATIVE", "#1677b8", "Down-gap long"), ("ALL_LONG_NATIVE", "#777777", "Always-long control")):
        curve = full[name].cumsum()
        axes[0].plot(full.date, curve, label=label, color=color, lw=1.4)
        axes[1].plot(full.date, curve - np.maximum.accumulate(np.maximum(curve, 0)), color=color, lw=1)
    for ax in axes:
        ax.axvline(pd.Timestamp("2023-01-01"), color="#9c713b", ls="--", lw=1)
        ax.grid(alpha=.2)
    axes[0].legend(loc="upper left"); axes[0].set_ylabel("Cumulative P&L ($ / MNQ)")
    axes[1].set_ylabel("Drawdown ($)")
    axes[0].set_title("NQ gap-down reconstruction: 100-point stop, delayed entry, native MNQ costs\nResolved history only; 16 cash dates excluded for unknown signal/outcome; no book approval", fontsize=11)
    axes[1].set_xlabel("2018–22 design | 2023+ previously seen historical reconstruction")
    fig.savefig(E.OUT / "reconstruction_equity.png", dpi=160)
    print(json.dumps(result))


if __name__ == "__main__": run()
