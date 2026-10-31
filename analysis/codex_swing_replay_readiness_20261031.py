"""Audit replay inputs; no signals, account simulation or live access.

Run from repo root with a scratch directory containing build_lab's g24/ge pickles.
The explicit open-sentinel adapter is a research proposal, not a shared-file fix.
"""
import argparse
import hashlib
import json
import pickle
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))


def closed_pairs(raw):
    entries = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True)
    exits = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    if len(entries) != len(exits):
        raise ValueError("Unpaired report entries/exits")
    opened = exits.Signal.astype(str).str.strip().str.casefold().eq("open")
    return entries, exits, opened


def load_closed_mc(g, path):
    """Remove explicit report 'open' marks; reject other unsupported time paths.

    Never infer closure from a price or from j1 < j0. Genuine cross-date closed
    trades need a separate supported path adapter and cannot be dropped here.
    """
    from portfolio import load_mc
    ent, ex, opened = closed_pairs(pd.read_excel(path, sheet_name="List of Trades", header=2))
    ed, xd = pd.to_datetime(ent.Date), pd.to_datetime(ex.Date)
    cross = (~opened) & (ed.dt.normalize() != xd.dt.normalize())
    if cross.any():
        raise ValueError(f"{int(cross.sum())} closed cross-date trades need explicit handling")
    dates = ed.dt.strftime("%Y%m%d").astype(int).to_numpy()
    row = np.searchsorted(g.dates, dates)
    keep = (row < g.D) & (g.dates[np.minimum(row, g.D - 1)] == dates)
    trades = load_mc(g, path)
    assert len(trades) == int(keep.sum())
    trades = trades.loc[(~opened).to_numpy()[keep]].reset_index(drop=True)
    if ((trades.j0 < 0) | (trades.j1 < trades.j0) | (trades.j1 >= 1440)).any():
        raise ValueError("Invalid closed-trade minute bounds")
    return trades


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scratch", type=Path)
    args = parser.parse_args()
    scratch = args.scratch.resolve()
    # Existing modules read argv[1] at import. Give them the existing scratch path.
    sys.argv = [sys.argv[0], str(scratch)]
    from build_lab import REPORTS
    from portfolio import load_mc, paths
    import swing_target_bench as st
    out = ROOT / "analysis/outputs/codex_swing_replay_readiness_20261031"
    out.mkdir(parents=True, exist_ok=True)
    with (scratch / "g24.pkl").open("rb") as handle:
        g = pickle.load(handle)
    report_rows, defects = [], []
    sources = [ROOT / "analysis/build_lab.py", ROOT / "analysis/portfolio.py",
               ROOT / "analysis/swing_target_bench.py", ROOT / "analysis/funded_lab.py"]
    for name, (report, _) in REPORTS.items():
        path = ROOT / report
        sources.append(path)
        ent, ex, opened = closed_pairs(pd.read_excel(path, sheet_name="List of Trades", header=2))
        t = load_mc(g, path)
        invalid = t[(t.j1 < t.j0) | (t.j0 < 0) | (t.j1 >= 1440)]
        for r in invalid.itertuples():
            defects.append(dict(strategy=name, date=str(r.date.date()), entry_minute=int(r.j0),
                                exit_minute=int(r.j1), kind=int(r.kind)))
        row = dict(strategy=name, report=report, loaded_rows=len(t), open_sentinels=int(opened.sum()),
                   invalid_minute_rows=len(invalid))
        try:
            closed = load_closed_mc(g, path)
            row.update(proposed_adapter="valid", closed_rows=len(closed))
            if name == "ONB_ML2_MC":
                w, r = paths(g, closed)
                assert np.isfinite(w).all() and np.isfinite(r).all()
                row["canonical_paths_complete_after_explicit_open_exclusion"] = True
                del w, r
        except ValueError as error:
            row.update(proposed_adapter="blocked", reason=str(error))
        report_rows.append(row)
    # The offending export is an open-position mark, not a real midnight exit.
    onb = next(r for r in report_rows if r["strategy"] == "ONB_ML2_MC")
    assert onb["open_sentinels"] == 1 and onb["closed_rows"] == 343
    assert onb["canonical_paths_complete_after_explicit_open_exclusion"]
    ledger = ROOT / "checks/candidates/swing_target/codex_be_trades.csv"
    sources.append(ledger)
    frozen = pd.read_csv(ledger)
    # Canonical loader input is staged outside tracked sources.
    with tempfile.TemporaryDirectory(prefix="st_readiness_") as td:
        Path(td, "swing_be.csv").write_bytes(ledger.read_bytes())
        st.SP = td + "/"
        trades = st.pt_trades(g)
    assert set(trades.kind).issubset({0, 1, 2})
    assert len(trades) == len(frozen) == 602
    mapped = frozen.reason.map(st.ST_KIND)
    assert mapped.notna().all()
    np.testing.assert_array_equal(mapped.to_numpy(), frozen.kind.to_numpy())
    # Merely increasing an isolated strategy's cashflow does not certify a
    # path-dependent sizing/payout outcome; no account outcome is computed here.
    target_count = int((trades.kind == 1).sum())
    required = ["lab.pkl", "g24.pkl", "ge.pkl", "cl.pkl", "s_rank_gap2.pkl",
                "single_print_sessions.pkl", "rs_trades.csv", "swing_be.csv"]
    result = dict(status="BLOCKED_BEFORE_ACCOUNT_REPLAY", new_strategy_trials=0,
        account_simulations=0, reports=report_rows, invalid_paths=defects,
        swing_target=dict(rows=len(trades), numeric_kind_counts=trades.kind.value_counts().to_dict(),
            holiday_repairs=int(frozen.apex_flat_violation.sum()),
            enum_matches_frozen_ledger=True, targets=target_count,
            corrected_target_cash_delta_per_one_MNQ=target_count * .5),
        missing_scratch_files=[name for name in required if not (scratch / name).exists()],
        remaining=["Rebuild complete baseline with explicit open-sentinel policy and documented holiday handling",
            "Rebuild CL gap frames, VB flags and RS trades; reconcile cache calendars",
            "Run paired historical and current-roster BASE/ADD/REPLACE/EMPTY account comparisons"],
        limitations=["Canonical ONB path completion checks finiteness, not native-fill parity",
            "ST historical loader flattens three holiday holds; deployed v3 skips those dates",
            "No fresh payout, risk, timing, standalone performance or adoption result"],
        source_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        files={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sources + [Path(__file__)]},
        versions=dict(python=sys.version, numpy=np.__version__, pandas=pd.__version__))
    (out / "checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "swing_target", "missing_scratch_files")}, indent=2))


if __name__ == "__main__":
    main()
