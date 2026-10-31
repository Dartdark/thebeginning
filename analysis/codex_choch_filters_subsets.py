"""Frozen fixed-trade subset diagnostics for the hourly CHoCH filters.

This module reads no market data and runs nothing at import.  The executable
filtered strategies may admit additional signals; these diagnostics retain the
common BASE's original exits and costs and are not executable portfolios.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import warnings

import numpy as np
import pandas as pd

import metrics as M
import resampling as R
from codex_hunt_v2_ldf_delta import tstat  # The same helper used by codex_choch4h.

ROOT = Path(__file__).resolve().parents[1]
FILTER_ORDER = ("F1", "F1_5", "A4", "F1_A4")
N_SUBSETS, SEED = 1000, 20261028


def _safe(value):
    if isinstance(value, dict):
        return {str(k): _safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(v) for v in value]
    if isinstance(value, np.generic):
        return _safe(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _write_csv(path, frame):
    with path.open("x", newline="") as handle:
        frame.to_csv(handle, index=False, float_format="%.17g")


def _daily(values, selected, day_positions, day_count):
    return np.bincount(day_positions[selected], weights=values[selected], minlength=day_count)


def _stats(values, daily):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        metrics = M.perf(daily, values)
    return _safe(dict(count=len(values), net_total=float(values.sum()),
        net_mean=float(values.mean()) if len(values) else None,
        trade_t=tstat(values), max_dd=R.max_dd(daily), metrics=metrics,
        metrics_basis="Shared metrics.perf on supplied daily calendar; max_dd is shared resampling.max_dd from zero."))


def _inputs(base_trades, membership_masks, daily_index):
    frame = base_trades.copy()
    required = ("trade_id", "side", "signal", "entry_time", "net_mnq")
    if any(name not in frame for name in required):
        raise ValueError("BASE needs stable trade_id, side, signal, entry_time and net_mnq.")
    if frame.empty or frame.trade_id.isna().any() or frame.trade_id.astype(str).duplicated().any():
        raise ValueError("BASE must be nonempty with distinct nonmissing stable IDs.")
    if not frame.index.is_unique:
        raise ValueError("BASE row index must be unique for mask alignment.")
    if "state" in frame and not frame.state.eq("resolved").all():
        raise ValueError("Numeric diagnostics require resolved BASE trades only; disclose unknowns separately.")
    if tuple(membership_masks) != FILTER_ORDER:
        raise ValueError("Masks must be supplied in frozen F1,F1_5,A4,F1_A4 order.")
    entries = pd.DatetimeIndex(pd.to_datetime(frame.entry_time))
    if entries.hasnans or entries.tz is not None:
        raise ValueError("entry_time must be valid timezone-naive CT timestamps.")
    if not np.all((entries >= "2018-01-01") & (entries < "2023-01-01")):
        raise ValueError("This helper is restricted to 2018--22 design trades.")
    if "exit_time" in frame:
        exits = pd.DatetimeIndex(pd.to_datetime(frame.exit_time))
        if exits.hasnans or exits.tz is not None or not exits.normalize().equals(entries.normalize()):
            raise ValueError("Only same-calendar-day intraday ledgers can use entry-date attribution.")
    sides = np.asarray(frame.side, float)
    signal = np.asarray(frame.signal, float)
    values = np.asarray(frame.net_mnq, float)
    if not np.isin(sides, [-1, 1]).all() or not np.isfinite(values).all():
        raise ValueError("Resolved BASE sides and net values must be valid and finite.")
    if not np.isfinite(signal).all() or (signal < 0).any() or not np.equal(signal, np.floor(signal)).all():
        raise ValueError("signal must contain nonnegative flattened minute indices.")
    calendar = daily_index.index if isinstance(daily_index, pd.Series) else daily_index
    days = pd.DatetimeIndex(calendar)
    if (not len(days) or days.hasnans or days.tz is not None or days.has_duplicates
            or not days.is_monotonic_increasing or not days.equals(days.normalize())):
        raise ValueError("Daily calendar must be nonempty, unique, ordered, normalized and timezone-naive.")
    if not np.all((days >= "2018-01-01") & (days < "2023-01-01")):
        raise ValueError("Only 2018--22 daily design calendar is permitted.")
    positions = days.get_indexer(entries.normalize())
    if (positions < 0).any():
        raise ValueError("BASE entry date missing from daily calendar; do not delete or rebook it.")
    masks = {}
    for name, raw in membership_masks.items():
        if isinstance(raw, pd.Series):
            if not raw.index.equals(frame.index):
                raise ValueError(name + " mask Series index must exactly match BASE row index.")
            if raw.isna().any():
                raise ValueError(name + " mask has missing values.")
        arr = np.asarray(raw)
        if arr.shape != (len(frame),) or arr.dtype != np.dtype(bool):
            raise ValueError(name + " must be one boolean membership per resolved BASE row.")
        masks[name] = arr.copy()
    frame["year"] = entries.year
    frame["signal_hour"] = ((signal.astype(np.int64) % 1440) // 60)
    frame["side"] = sides.astype(np.int64)
    # Entry is signal+2, so an intraday signal cannot change its calendar year.
    # entry_time supplies the calendar year; signal supplies only the hour.
    base_daily = _daily(values, np.arange(len(frame)), positions, len(days))
    if not np.isclose(base_daily.sum(), values.sum(), rtol=1e-12, atol=1e-8):
        raise AssertionError("BASE daily attribution lost trade P&L.")
    verified = isinstance(daily_index, pd.Series)
    if verified:
        expected = np.asarray(daily_index, float)
        if not np.isfinite(expected).all():
            raise ValueError("Supplied BASE daily series contains unknown/nonfinite P&L.")
        np.testing.assert_allclose(base_daily, expected, rtol=1e-12, atol=1e-8,
            err_msg="Intraday entry-date attribution differs from supplied BASE daily marks.")
    return frame, masks, days, positions, values, base_daily, verified


def evaluate(base_trades, membership_masks, daily_index, outdir):
    """Save 1,000 year/side/signal-hour matched paths for each fixed filter.

    ``daily_index`` can be a DatetimeIndex, or the BASE daily P&L Series to
    additionally verify date-by-date parity with the caller's daily marks.
    Masks are positional bool arrays or Series with the exact BASE row index.
    A single seeded RNG advances across all filters in the preregistered order.
    All files are exclusive-create; a rerun cannot overwrite prior diagnostics.
    """
    frame, masks, days, day_positions, values, base_daily, verified = _inputs(
        base_trades, membership_masks, daily_index)
    out = Path(outdir).resolve()
    permitted = (out.is_relative_to(ROOT / "agents/codex") or
        (out.is_relative_to(ROOT / "analysis/outputs") and
         out.relative_to(ROOT / "analysis/outputs").parts[0].startswith("codex_")))
    if not permitted:
        raise ValueError("Diagnostic outputs must stay in an allowed Codex directory.")
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise FileExistsError("Subset output directory must be empty; preserve every prior run.")
    _write_csv(out / "base_daily.csv", pd.DataFrame(dict(date=days.strftime("%Y-%m-%d"), net_mnq=base_daily)))
    group_items = list(frame.reset_index(drop=True).groupby(["year", "side", "signal_hour"], sort=True).indices.items())
    rng = np.random.default_rng(SEED)
    summary = dict(scope="Fixed common-BASE trade IDs; original exits/costs; diagnostics, not executable returns.",
        seed=SEED, random_subsets_per_filter=N_SUBSETS, filter_order=list(FILTER_ORDER),
        baseline_daily_verified=verified, base=_stats(values, base_daily),
        first_date=str(days[0].date()), last_date=str(days[-1].date()), daily_rows=len(days), filters={})
    for name in FILTER_ORDER:
        directory = out / name
        directory.mkdir()
        mask = masks[name]
        kept, removed = np.flatnonzero(mask), np.flatnonzero(~mask)
        observed_daily = _daily(values, kept, day_positions, len(days))
        removed_daily = _daily(values, removed, day_positions, len(days))
        np.testing.assert_allclose(observed_daily + removed_daily, base_daily, rtol=1e-12, atol=1e-8)
        strata = [dict(year=int(key[0]), side=int(key[1]), signal_hour=int(key[2]), base_count=len(pool),
            kept_count=int(mask[pool].sum()), removed_count=int((~mask[pool]).sum())) for key, pool in group_items]
        _write_csv(directory / "strata.csv", pd.DataFrame(strata))
        membership = frame[["trade_id", "year", "side", "signal_hour"]].copy()
        membership["kept"] = mask
        _write_csv(directory / "observed_membership.csv", membership)
        _write_csv(directory / "observed_daily.csv", pd.DataFrame(dict(date=days.strftime("%Y-%m-%d"),
            kept_net_mnq=observed_daily, removed_net_mnq=removed_daily)))
        paths = np.zeros((N_SUBSETS, len(days)), dtype=np.float64)
        profits, drawdowns = np.empty(N_SUBSETS), np.empty(N_SUBSETS)
        membership_bits = np.empty((N_SUBSETS, (len(frame) + 7) // 8), dtype=np.uint8)
        selected_rows, unique_memberships = [], set()
        for trial in range(N_SUBSETS):
            chosen = np.zeros(len(frame), dtype=bool)
            for (_, pool), stratum in zip(group_items, strata):
                count = stratum["kept_count"]
                if count == len(pool):
                    chosen[pool] = True
                elif count:
                    chosen[rng.choice(pool, size=count, replace=False)] = True
                if int(chosen[pool].sum()) != count:
                    raise AssertionError("Matched subset changed a stratum count.")
            indices = np.flatnonzero(chosen)
            if len(indices) != len(kept):
                raise AssertionError("Matched subset changed total kept count.")
            paths[trial] = _daily(values, indices, day_positions, len(days))
            profits[trial], drawdowns[trial] = values[indices].sum(), R.max_dd(paths[trial])
            if not np.isclose(paths[trial].sum(), profits[trial], rtol=1e-12, atol=1e-8):
                raise AssertionError("Random subset daily sum differs from its retained trades.")
            membership_bits[trial] = np.packbits(chosen)
            unique_memberships.add(hashlib.sha256(membership_bits[trial].tobytes()).hexdigest())
            selected_rows.extend((trial + 1, trade_id) for trade_id in frame.trade_id.iloc[indices])
        _write_csv(directory / "random_selected_ids.csv", pd.DataFrame(selected_rows, columns=["trial", "trade_id"]))
        _write_csv(directory / "random_summary.csv", pd.DataFrame(dict(trial=np.arange(1, N_SUBSETS + 1),
            kept_count=len(kept), net_total=profits, max_dd=drawdowns)))
        with (directory / "random_daily_paths.npz").open("xb") as handle:
            np.savez_compressed(handle, daily_paths=paths, dates=days.strftime("%Y-%m-%d").to_numpy(dtype="U10"),
                trials=np.arange(1, N_SUBSETS + 1), seed=np.array(SEED), filter_name=np.array(name),
                membership_bits=membership_bits, membership_bitorder=np.array("big"),
                trade_ids=frame.trade_id.astype(str).to_numpy(dtype=str), trade_count=np.array(len(frame)),
                base_net_mnq=values, day_positions=day_positions,
                strata=frame[["year", "side", "signal_hour"]].to_numpy(dtype=np.int64),
                observed_membership=mask, observed_daily_path=observed_daily)
        observed_profit, observed_dd = float(values[kept].sum()), R.max_dd(observed_daily)
        profit_better, dd_better = profits >= observed_profit, drawdowns <= observed_dd
        summary["filters"][name] = _safe(dict(kept=_stats(values[kept], observed_daily),
            removed=_stats(values[removed], removed_daily), strata=strata,
            kept_net=observed_profit, base_net=float(values.sum()), removed_net=float(values[removed].sum()),
            p_profit=(1 + int(profit_better.sum())) / (N_SUBSETS + 1),
            p_dd=(1 + int(dd_better.sum())) / (N_SUBSETS + 1),
            p_joint=(1 + int((profit_better & dd_better).sum())) / (N_SUBSETS + 1),
            profit_p_plus_one=(1 + int(profit_better.sum())) / (N_SUBSETS + 1),
            dd_p_plus_one=(1 + int(dd_better.sum())) / (N_SUBSETS + 1),
            joint_p_plus_one=(1 + int((profit_better & dd_better).sum())) / (N_SUBSETS + 1),
            ties_profit=int(np.equal(profits, observed_profit).sum()),
            ties_dd=int(np.equal(drawdowns, observed_dd).sum()),
            ties_joint=int((np.equal(profits, observed_profit) & np.equal(drawdowns, observed_dd)).sum()),
            unique_memberships=len(unique_memberships), unique_daily_paths=len(np.unique(paths, axis=0)),
            unique_profit_dd_pairs=len(np.unique(np.column_stack([profits, drawdowns]), axis=0)),
            strata_with_random_choice=sum(0 < s["kept_count"] < s["base_count"] for s in strata),
            artifacts={key: str(directory / key) for key in ("strata.csv", "observed_membership.csv",
                "observed_daily.csv", "random_selected_ids.csv", "random_summary.csv", "random_daily_paths.npz")}))
    summary = _safe(summary)
    with (out / "summary.json").open("x") as handle:
        json.dump(summary, handle, indent=2, allow_nan=False)
        handle.write("\n")
    return summary


def synthetic_checks():
    """Partition/count/strata/daily-sum checks only; no market data or returns."""
    dates = pd.DatetimeIndex([pd.Timestamp(f"{year}-01-{day:02d}") for year in (2018, 2019)
        for day in range(8, 16)])
    n = len(dates)
    sides = np.tile([1, 1, 1, 1, -1, -1, -1, -1], 2)
    hours = np.where(sides > 0, 9, 10)
    entries = dates + pd.to_timedelta(hours, unit="h") + pd.Timedelta(minutes=2)
    frame = pd.DataFrame(dict(trade_id=[f"synthetic_{i}" for i in range(n)], side=sides,
        signal=np.arange(n) * 1440 + hours * 60, entry_time=entries,
        exit_time=entries + pd.Timedelta(minutes=5), net_mnq=np.tile([-3., 4., -1., 2.], 4), state="resolved"))
    days = pd.date_range(dates.min(), dates.max())
    daily = frame.groupby(frame.entry_time.dt.normalize()).net_mnq.sum().reindex(days, fill_value=0.)
    strict = np.arange(n) % 2 == 0
    masks = dict(F1=strict, F1_5=np.arange(n) % 4 != 3, A4=sides > 0, F1_A4=strict & (sides > 0))
    runtime = ROOT / "agents/codex/runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="codex_choch_subset_check_", dir=runtime) as temporary:
        out = Path(temporary) / "subsets"
        result = evaluate(frame, masks, daily, out)
        assert result["baseline_daily_verified"]
        assert result["base"]["count"] == n
        for name in FILTER_ORDER:
            observed = result["filters"][name]
            assert observed["kept"]["count"] + observed["removed"]["count"] == n
            assert np.isclose(observed["kept"]["net_total"] + observed["removed"]["net_total"], daily.sum())
            selected = pd.read_csv(out / name / "random_selected_ids.csv")
            sums = pd.read_csv(out / name / "random_summary.csv")
            with np.load(out / name / "random_daily_paths.npz", allow_pickle=False) as saved:
                saved_paths, saved_values = saved["daily_paths"], saved["base_net_mnq"]
                saved_positions = saved["day_positions"]
                assert saved_paths.shape == (N_SUBSETS, len(days))
                np.testing.assert_allclose(saved_paths.sum(axis=1), sums.net_total, atol=1e-10)
                unpacked = np.unpackbits(saved["membership_bits"], axis=1, count=int(saved["trade_count"])).astype(bool)
                assert unpacked.shape == (N_SUBSETS, n)
                assert (unpacked.sum(axis=1) == observed["kept"]["count"]).all()
                for trial, mask in enumerate(unpacked):
                    np.testing.assert_allclose(_daily(saved_values, np.flatnonzero(mask),
                        saved_positions, len(days)), saved_paths[trial], atol=1e-10)
            chosen = selected.merge(frame[["trade_id", "side", "signal", "entry_time"]], on="trade_id", validate="many_to_one")
            chosen["year"] = pd.DatetimeIndex(chosen.entry_time).year
            chosen["signal_hour"] = (chosen.signal % 1440) // 60
            for stratum in observed["strata"]:
                match = ((chosen.year == stratum["year"]) & (chosen.side == stratum["side"])
                    & (chosen.signal_hour == stratum["signal_hour"]))
                counts = chosen.loc[match].groupby("trial").size().reindex(range(1, N_SUBSETS + 1), fill_value=0)
                assert (counts == stratum["kept_count"]).all()
            assert not selected.duplicated(["trial", "trade_id"]).any()
    return dict(partition=True, exact_counts=True, year_side_signal_hour_matching=True,
        saved_membership_unique=True, daily_sums=True, baseline_daily_parity=True, market_data_read=False)


def checks():
    """Runner-compatible name for the synthetic-only invariants."""
    return synthetic_checks()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic-check", action="store_true")
    arguments = parser.parse_args()
    if not arguments.synthetic_check:
        parser.error("Only --synthetic-check is exposed; economic execution belongs to the authorized runner.")
    print(json.dumps(synthetic_checks(), indent=2))
