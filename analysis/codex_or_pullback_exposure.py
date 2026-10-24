"""Descriptive MNQ occupancy for the frozen ORPullback portfolio comparison.

This reads the already prepared current-plan cache and saved candidate/RS
ledgers. It does not replay a signal, compute a return, resize the account, or
change a candidate. Existing MC timestamps use the pinned report loader.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents/codex/runtime/or_pullback_python"))
sys.path.insert(0, str(ROOT / "analysis"))
import numpy as np
import pandas as pd
import codex_or_pullback_plan as P

PORTFOLIO = ROOT / "analysis/outputs/codex_or_pullback_portfolio"
OUT = PORTFOLIO / "exposure"
BASELINE = ROOT / "analysis/outputs/codex_or_pullback/baseline"
NQ_NAMES = ("VB_N", "VB_F", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC",
            "NFP_MC", "MON_BR_MC", "RS_L")
MODES = ("reported_rule", "literal_mc_delay")
COHORTS = {"2018_plus": ("2018-01-01", "2100-01-01"),
           "2018_22": ("2018-01-01", "2023-01-01"),
           "2023_plus": ("2023-01-01", "2100-01-01")}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")


def occupancy(trades, row_lookup, sizes, shape, *, candidate=False):
    """Separate long/short quantities so opposite trades never cancel gross.

    Candidate fills at a close begin at entry+1. An open exit has no exposure
    during its stamped minute's range. MC/RS entries and exits are inclusive:
    the reports do not resolve exact phase, and the frozen RS ledger is open
    entry. Inclusive MC endpoints may conservatively count a same-minute
    reversal in both directions.
    """
    long = np.zeros(shape, dtype=np.int16)
    short = np.zeros(shape, dtype=np.int16)
    retained = skipped = 0
    for x in trades.itertuples():
        row = row_lookup.get(int(x.day))
        if row is None:
            skipped += 1
            continue
        base_qty = float(getattr(x, "qty", 1.0))
        qty = float(sizes[row]) * base_qty
        if qty < 0 or not np.isclose(qty, round(qty), rtol=0, atol=1e-9):
            raise ValueError("Occupancy requires nonnegative integer MNQ quantities")
        q = int(round(qty))
        start = int(x.entry_j) + 1 if candidate else int(x.j0)
        end = int(x.exit_j) - int(x.exit_phase == "open") if candidate else int(x.j1)
        if not (0 <= start < shape[1] and start - 1 <= end < shape[1]):
            raise ValueError(f"Invalid held-minute interval {start}..{end}")
        side = int(x.side)
        if side not in (-1, 1):
            raise ValueError("Unknown trade side")
        if q and end >= start:
            a = long if side > 0 else short
            a[row, start:end+1] += q
        retained += 1
    return long, short, dict(trades_on_lab_calendar=retained, trades_outside_lab_calendar=skipped)


def fixtures():
    rows = {7: 0}
    t = pd.DataFrame([dict(day=7, side=1, entry_j=2, exit_j=5, exit_phase="open"),
                      dict(day=7, side=-1, entry_j=5, exit_j=7, exit_phase="close")])
    a, b, _ = occupancy(t, rows, np.array([1]), (1, 10), candidate=True)
    assert np.array_equal(np.flatnonzero(a[0]), [3, 4])
    assert np.array_equal(np.flatnonzero(b[0]), [6, 7])
    t = pd.DataFrame([dict(day=7, side=1, j0=2, j1=5),
                      dict(day=7, side=-1, j0=5, j1=7)])
    a, b, _ = occupancy(t, rows, np.array([2]), (1, 10))
    assert a[0, 5] == 2 and b[0, 5] == 2
    return dict(candidate_close_entry_excluded=True, candidate_open_exit_range_excluded=True,
                gross_does_not_cancel_opposite_positions=True)


def load_current(scratch, cache):
    """Load pinned classes and MC reports; never reconstruct the cached lab."""
    with P.pinned_imports(P.DEFAULT_RUNTIME, scratch) as sources:
        pf = importlib.import_module("portfolio")
        build = importlib.import_module("build_lab")
        bridge = importlib.import_module("bridge_monday_confirm")
        with cache.open("rb") as f:
            lab = pickle.load(f)
        dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
        flags = pd.read_pickle(scratch / "single_print_sessions.pkl").flag.reindex(dates).fillna(False).to_numpy(bool)
        raw, paths = {}, {}
        for name in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC"):
            paths[name] = ROOT / build.REPORTS[name][0]
            raw[name] = pf.load_mc(lab.g, str(paths[name]))
        paths["MON_BR_MC"] = ROOT / bridge.F
        raw["MON_BR_MC"] = bridge.load_bridge_mc(lab.g, str(paths["MON_BR_MC"]))
        paths["RS_L"] = BASELINE / "baseline_rs_replay.csv"
        rs = pd.read_csv(paths["RS_L"], parse_dates=["date"])
        raw["RS_L"] = rs[rs.side > 0].copy()
        flag_by_gridrow = dict(zip(lab.tr, flags))
        vb_flag = raw["VB"].day.map(flag_by_gridrow).fillna(False).to_numpy(bool)
        ledgers = {k: v for k, v in raw.items() if k != "VB"}
        ledgers.update(VB_F=raw["VB"].loc[vb_flag].copy(), VB_N=raw["VB"].loc[~vb_flag].copy())
        names, b = lab._base({k: P.CURRENT_PLAN[k] for k in NQ_NAMES})
        if names != list(NQ_NAMES) or not np.isfinite(b).all():
            raise ValueError("Unexpected current-plan quantity metadata")
        q = np.floor(b + 1e-9).astype(np.int16)
        return lab, dates, ledgers, q, paths, sources


def summarize(current, candidate, dates, trades, mode):
    total_long = sum(v[0] for v in current.values())
    total_short = sum(v[1] for v in current.values())
    gross = total_long + total_short
    long_legs = sum((v[0] > 0).astype(np.int16) for v in current.values())
    short_legs = sum((v[1] > 0).astype(np.int16) for v in current.values())
    vb_gross = sum(current[k][0] + current[k][1] for k in ("VB_N", "VB_F"))
    clong, cshort = candidate[:2]
    held = (clong + cshort) > 0
    if (clong + cshort).max() > 1:
        raise ValueError("Candidate occupancy has overlapping trades")
    same_qty = np.where(clong > 0, total_long, total_short)
    opposite_qty = np.where(clong > 0, total_short, total_long)
    same_legs = np.where(clong > 0, long_legs, short_legs)
    opposite_legs = np.where(clong > 0, short_legs, long_legs)
    summary, per_leg = [], []
    for cohort, (lo, hi) in COHORTS.items():
        daymask = np.asarray((dates >= lo) & (dates < hi))
        mask = held & daymask[:, None]
        n = int(mask.sum())
        if not n:
            raise ValueError("Empty candidate occupancy cohort")
        def fraction(a):
            return float(np.count_nonzero(mask & a) / n)
        def maximum(a):
            return int(a[mask].max(initial=0))
        common = dict(timing=mode, cohort=cohort,
                      candidate_trades=int(((trades.date >= lo) & (trades.date < hi)).sum()),
                      candidate_held_minutes=n, candidate_held_days=int(mask.any(axis=1).sum()),
                      any_current_nq_overlap_fraction=fraction(gross > 0),
                      vb_overlap_fraction=fraction(vb_gross > 0),
                      same_side_overlap_fraction=fraction(same_qty > 0),
                      opposite_side_overlap_fraction=fraction(opposite_qty > 0),
                      both_sides_overlap_fraction=fraction((same_qty > 0) & (opposite_qty > 0)),
                      max_current_gross_mnq_while_candidate_held=maximum(gross),
                      max_same_side_current_mnq=maximum(same_qty),
                      max_opposite_side_current_mnq=maximum(opposite_qty),
                      max_same_side_current_legs=maximum(same_legs),
                      max_opposite_side_current_legs=maximum(opposite_legs))
        for size in (1, 2):
            summary.append(dict(**common, candidate_mnq=size,
                                max_gross_add_mnq=maximum(gross) + size,
                                max_gross_replace_vb_mnq=maximum(gross-vb_gross) + size,
                                max_total_same_side_add_mnq=maximum(same_qty) + size))
        for leg, (long, short, _) in current.items():
            lgross = long + short
            lsame = np.where(clong > 0, long, short)
            lopp = np.where(clong > 0, short, long)
            per_leg.append(dict(timing=mode, cohort=cohort, leg=leg, candidate_held_minutes=n,
                                overlap_minutes=int((mask & (lgross > 0)).sum()),
                                overlap_fraction=fraction(lgross > 0),
                                same_side_fraction=fraction(lsame > 0),
                                opposite_side_fraction=fraction(lopp > 0),
                                max_leg_mnq_while_candidate_held=maximum(lgross)))
    return summary, per_leg


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scratch", default=str(ROOT / "scratch_data"))
    ap.add_argument("--cache", default=str(ROOT / "agents/codex/runtime/or_pullback_current_lab.pkl"))
    args = ap.parse_args()
    scratch, cache = Path(args.scratch).resolve(), Path(args.cache).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    lab, dates, ledgers, q, paths, sources = load_current(scratch, cache)
    shape = (lab.D, lab.g.o.shape[1])
    lookup = {int(d): i for i, d in enumerate(lab.tr)}
    current, metadata = {}, {}
    for i, name in enumerate(NQ_NAMES):
        current[name] = occupancy(ledgers[name], lookup, q[i], shape)
        metadata[name] = dict(**current[name][2], ledger_rows=len(ledgers[name]),
                              full_size_min=int(q[i].min()), full_size_max=int(q[i].max()))
        # Match daily trade counts to the fee-count metadata in the baseline.
        count = np.bincount(ledgers[name].day.to_numpy(int), minlength=lab.g.D)[lab.tr]
        if name in lab.N:
            np.testing.assert_allclose(count, lab.N[name], rtol=0, atol=0,
                                       err_msg=f"Current-plan ledger differs: {name}")
            metadata[name]["daily_trade_count_matches_cached_lab"] = True
    records, legs = [], []
    candidate_files = {}
    for mode in MODES:
        path = PORTFOLIO / "replay" / f"{mode}_trades.csv"
        trades = pd.read_csv(path, parse_dates=["date"])
        cand = occupancy(trades, lookup, np.ones(lab.D, dtype=int), shape, candidate=True)
        a, b = summarize(current, cand, dates, trades, mode)
        records += a
        legs += b
        candidate_files[str(path.relative_to(ROOT))] = sha(path)
    pd.DataFrame(records).to_csv(OUT / "occupancy_summary.csv", index=False)
    pd.DataFrame(legs).to_csv(OUT / "per_leg_overlap.csv", index=False)
    manifest = dict(current_plan_ref=P.PINNED_REF, preregistration_commit="1ad4306",
                    scope="Descriptive full-size NQ/MNQ occupancy only; not an account-performance result",
                    excluded_instruments={"CLS": "MCL is not MNQ", "MOC_MES": "MES is not MNQ"},
                    sizing="Plan fixed sizes or floor(risk dollars / (stop points * $2)); no cushion multiplier",
                    candidate_minutes="entry+1 through exit, excluding exit minute when filled at open",
                    current_minutes="Pinned MC inferred entry/exit minutes inclusive; RS frozen open entry inclusive",
                    timestamp_limits=["MC reports resolve chart bars, not exact ticks; load_mc infers the first matching minute",
                                      "Inclusive MC endpoints can count same-minute reversal directions together",
                                      "Bridge keeps pinned Monday booking; Sunday-night exits are booked at Monday minute zero",
                                      "Fractions use candidate held price-minutes, not all market minutes or trade counts",
                                      "Same and opposite side exposures can coexist; gross quantities never net them",
                                      "Each maximum may occur on a different minute; MNQ exposures exclude CL and ES legs"],
                    no_candidate_variants_changed=True, no_signals_or_returns_replayed=True,
                    fixtures=fixtures(), ledgers=metadata,
                    inputs={str(cache.relative_to(ROOT)): sha(cache),
                            str((scratch / "single_print_sessions.pkl").relative_to(ROOT)): sha(scratch / "single_print_sessions.pkl"),
                            **{str(p.relative_to(ROOT)): sha(p) for p in paths.values()}, **candidate_files},
                    pinned_module_manifest_sha256=sha(P.DEFAULT_RUNTIME / "manifest.json"),
                    script_sha256=sha(Path(__file__)))
    dump(OUT / "exposure_manifest.json", manifest)
    display = pd.DataFrame(records)
    print(display[(display.cohort == "2023_plus") & (display.candidate_mnq == 2)].to_string(index=False))


if __name__ == "__main__":
    main()
