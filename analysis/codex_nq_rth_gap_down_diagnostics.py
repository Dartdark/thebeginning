"""Fixed-ledger diagnostics and nulls; no parameter search or account proxy claims."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

# Must precede importing numba; setting it after that import is too late.
os.environ["NUMBA_CACHE_DIR"] = str(Path(__file__).resolve().parents[1] /
    "analysis/outputs/codex_nq_rth_gap_down_20261027/cache/numba")

import numpy as np
import pandas as pd
from numba import njit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codex_nq_rth_gap_down as E
import grid as G
import metrics as M
import resampling as R
import montecarlo as MC

OUT = E.OUT
WALK = G._walk


@njit(cache=True)
def null_values(o, h, l, c, prefix_bad, rows, entries, exits, sides):
    result = np.full(entries.shape, np.nan)
    for sim in range(entries.shape[0]):
        for event in range(entries.shape[1]):
            r, j, end, side = rows[event], entries[sim, event], exits[event], sides[sim, event]
            entry = o[r, j]
            if not np.isfinite(entry): continue
            stop = entry - side * 100.
            target = np.inf if side == 1 else -np.inf
            k, px, kind, worst = WALK(o[r], h[r], l[r], c[r], j, end, side, stop, target, 1.)
            if kind == 2 and k != end: continue
            if prefix_bad[r, k + 1] - prefix_bad[r, j] != 0: continue
            result[sim, event] = (px - entry) * side * 2. - 2.24
    return result


def snapshot(phase):
    folder = OUT / ("reconstruction_" + phase)
    marker = json.loads((folder / "completed.json").read_text())
    cache_path = E.ROOT / marker["cache_path"]
    if E.sha(cache_path) != marker["cache_sha256"]: raise ValueError("Cache identity changed")
    data = np.load(cache_path)
    g = SimpleNamespace(**{k: data[k] for k in data.files})
    all_long = pd.read_csv(folder / "all_long_trades.csv", parse_dates=["date"])
    daily = pd.read_csv(folder / "daily.csv", parse_dates=["date"]).set_index("date")
    all_long = all_long[all_long.date.isin(daily.index)].copy()
    if not all_long.resolved.all(): raise ValueError("Unknowns entered known daily ledger")
    gap = all_long[all_long.gap_down.astype(bool)].copy()
    np.testing.assert_allclose(gap.net_mnq.sum(), daily.GAP_NATIVE.sum(), atol=1e-7)
    np.testing.assert_allclose(all_long.net_mnq.sum(), daily.ALL_LONG_NATIVE.sum(), atol=1e-7)
    return g, all_long, gap, daily


def probability(result, observed):
    complete = np.isfinite(result).all(axis=1)
    totals = np.full(len(result), np.nan)
    totals[complete] = result[complete].sum(axis=1)
    exceed = int((totals[complete] >= observed).sum())
    unknown = int((~complete).sum())
    return dict(paths=len(result), complete_paths=int(complete.sum()), unknown_paths=unknown,
                p_total_lower=(1 + exceed) / (len(result) + 1),
                p_total_upper=(1 + exceed + unknown) / (len(result) + 1),
                p_mean_lower=(1 + exceed) / (len(result) + 1),
                p_mean_upper=(1 + exceed + unknown) / (len(result) + 1),
                fixed_event_count=result.shape[1], observed_net=observed,
                null_total_median=float(np.nanmedian(totals)) if complete.any() else None,
                unknown_paths_not_redrawn=True), totals


def run():
    rel = "analysis/codex_nq_rth_gap_down_diagnostics.py"
    if subprocess.check_output(["git", "show", "HEAD:" + rel], cwd=E.ROOT) != Path(__file__).read_bytes():
        raise ValueError("Commit diagnostics before resampling/null outputs")
    dest = OUT / "diagnostics"
    if dest.exists(): raise ValueError("Retained diagnostics exist")
    dest.mkdir()
    sources = {p: snapshot(p) for p in ("design", "validation")}
    full = pd.concat([x[1] for x in sources.values()]).sort_values("date")
    days = pd.DatetimeIndex(pd.concat([x[3] for x in sources.values()]).sort_index().index)
    if full.date.duplicated().any() or days.has_duplicates: raise ValueError("Duplicate split/date")
    rows, daily_values = [], {}
    for name, value in (("GAP_NATIVE", "net_mnq"), ("ALL_LONG_NATIVE", "net_mnq"),
                        ("GAP_SOURCE_COST", "net_nq_source_cost"), ("GAP_SEVERE_COST", "net_mnq_severe")):
        for period in ("full", "2018-22", "2023+", "author_window", "author_ex2025", *map(str, sorted(set(days.year)))):
            if period == "full": mask = np.ones(len(days), bool)
            elif period == "2018-22": mask = days.year <= 2022
            elif period == "2023+": mask = days.year >= 2023
            elif period.startswith("author"):
                mask = (days >= "2020-12-01") & (days <= "2025-11-30")
                if period == "author_ex2025": mask &= days.year < 2025
            else: mask = days.year == int(period)
            d = days[mask]
            t = full[full.date.isin(d)]
            m, daily = E.measurements(t, d, name, value)
            rows.append(dict(period=period, **m))
            if period == "full": daily_values[name] = daily
    E.csv(dest / "full_metrics.csv", pd.DataFrame(rows))
    frame = pd.DataFrame(daily_values)
    E.csv(dest / "full_daily.csv", frame.rename_axis("date").reset_index())

    opening = pd.concat([pd.read_csv(OUT / ("reconstruction_" + p) / "opening_print_diagnostic.csv",
                                   parse_dates=["date"]) for p in sources])
    opening_rows = []
    for period, mask in (("full", days == days), ("author_window", (days >= "2020-12-01") & (days <= "2025-11-30")),
                         ("2018-22", days.year <= 2022), ("2023+", days.year >= 2023)):
        d = days[mask]; t = opening[opening.date.isin(d)]
        for value in ("net_nq_source_cost", "net_nq_author_severe"):
            m, _ = E.measurements(t, d, "GAP_OPENING_PRINT_NONEXECUTABLE", value)
            opening_rows.append(dict(period=period, **m))
    E.csv(dest / "opening_print_metrics.csv", pd.DataFrame(opening_rows))

    # Frozen same-day nulls; independent random numbers across both chronological splits.
    gaps = pd.concat([x[2] for x in sources.values()]).sort_values("date").reset_index(drop=True)
    n, count = 1000, len(gaps)
    rng_side, rng_time = np.random.default_rng(2026102702), np.random.default_rng(2026102703)
    sides = np.where(rng_side.integers(0, 2, size=(n, count)) == 0, -1, 1).astype(np.int16)
    times = np.empty((n, count), np.int16)
    same_time = np.full((n, count), E.ENTRY_J, np.int16)
    null_side, null_time = np.full((n, count), np.nan), np.full((n, count), np.nan)
    for phase, (g, all_long, gap, daily) in sources.items():
        take = np.flatnonzero(gaps.date.dt.year.le(2022) if phase == "design" else gaps.date.dt.year.ge(2023))
        sub = gaps.iloc[take]
        prefix = np.concatenate([np.zeros((len(g.valid), 1), np.int64), (~g.valid).cumsum(axis=1)], axis=1)
        for col in take:
            event = gaps.iloc[col]; r = int(event.day)
            latest = 841 if event.calendar_kind == "normal" else 661
            options = np.flatnonzero(g.valid[r, E.ENTRY_J:latest + 1]) + E.ENTRY_J
            if not len(options): raise ValueError("No admissible observed random-time opening")
            times[:, col] = options[rng_time.integers(0, len(options), size=n)]
        rr = sub.day.to_numpy(np.int64); ends = sub.exit_j.to_numpy(np.int64)
        null_side[:, take] = null_values(g.o, g.h, g.l, g.c, prefix, rr, same_time[:, take], ends, sides[:, take])
        null_time[:, take] = null_values(g.o, g.h, g.l, g.c, prefix, rr, times[:, take], ends, np.ones((n, len(take)), np.int16))
    np.savez_compressed(dest / "placebo_selected_paths.npz", event_ids=gaps.event_id.to_numpy(str),
                        dates=gaps.date.to_numpy(dtype="datetime64[D]"), random_sides=sides, random_entry_close_labels=times,
                        random_side_net_MNQ=null_side, random_time_net_MNQ=null_time)
    placebo_rows, placebo_runs = [], []
    for period, mask in (("full", np.ones(count, bool)), ("2018-22", gaps.date.dt.year.le(2022).to_numpy()),
                         ("2023+", gaps.date.dt.year.ge(2023).to_numpy())):
        observed = float(gaps.loc[mask, "net_mnq"].sum())
        for name, result in (("random_side", null_side), ("random_time", null_time)):
            p, totals = probability(result[:, mask], observed)
            placebo_rows.append(dict(period=period, null=name, **p))
            placebo_runs.extend(dict(period=period, null=name, path=i, total=t) for i, t in enumerate(totals))
    E.csv(dest / "placebo_summary.csv", pd.DataFrame(placebo_rows))
    E.csv(dest / "placebo_runs.csv", pd.DataFrame(placebo_runs))

    # Matched-year kept subsets, preserving every sampled ID/path, no outcome-based redraw.
    base = full.sort_values("date").reset_index(drop=True)
    kept = base.gap_down.astype(bool).to_numpy(); values = base.net_mnq.to_numpy()
    masks = np.zeros((n, len(base)), bool); rng = np.random.default_rng(2026102704)
    for year in sorted(base.year.unique()):
        choices = np.flatnonzero(base.year.to_numpy() == year); k = int(kept[choices].sum())
        for i in range(n): masks[i, rng.choice(choices, k, replace=False)] = True
    paths = masks * values
    np.savez_compressed(dest / "filter_selected_paths.npz", event_ids=base.event_id.to_numpy(str),
                        selected=masks, net_paths_MNQ=paths)
    observed = values * kept; profit = paths.sum(axis=1)
    curve = paths.cumsum(axis=1); peaks = np.maximum.accumulate(np.maximum(curve, 0), axis=1)
    dd = (peaks - curve).max(axis=1); actual_dd = R.max_dd(observed)
    subset = dict(all_long_base_profit=float(values.sum()), kept_profit=float(observed.sum()),
                  removed_profit=float(values[~kept].sum()), kept_events=int(kept.sum()), base_events=len(base),
                  removed_events=int((~kept).sum()), removed_mean=float(values[~kept].mean()),
                  removed_trade_t=E.tstat(values[~kept]), observed_kept_DD=actual_dd,
                  matched_paths=n, fraction_profit_at_least_observed=float(np.mean(profit >= observed.sum())),
                  fraction_observed_beats_both_profit_DD=float(np.mean((profit <= observed.sum()) & (dd >= actual_dd))),
                  zero_unknowns_fabricated=True, statistical_paths_not_executable_combined_portfolios=True)
    E.dump(dest / "filter_summary.json", subset)
    E.csv(dest / "filter_runs.csv", pd.DataFrame(dict(path=np.arange(n), total=profit, drawdown=dd)))

    daily = frame.GAP_NATIVE
    chosen = full[full.gap_down.astype(bool)].net_mnq
    E.dump(dest / "standalone_montecarlo.json", dict(
        trade_bootstrap=MC.trade_mc(chosen, n=5000, seed=2026102701),
        daily_one_year=MC.daily_mc(daily, horizon=252, n=5000, block=20, seed=2026102701),
        scope="OneMNQ standalone EOD diagnostic only; NOT a funded/evaluation or joint-book account result"))
    E.csv(dest / "bootstrap_full.csv", R.bootstrap(daily, n=5000, block=20, seed=2026102701).rename_axis("metric").reset_index())
    E.dump(dest / "permutation_full.json", R.permutation(daily, n=5000, seed=2026102701))
    E.csv(dest / "bootstrap_validation.csv", R.bootstrap(daily[daily.index.year >= 2023], n=5000, block=20,
                                                      seed=2026102701).rename_axis("metric").reset_index())
    E.dump(dest / "completed.json", dict(status="REJECT_NO_PROMOTION", economic_paths=3,
        frozen_cost_definitions=5, selected_null_paths=2000, matched_subset_paths=1000,
        gross_design_failed=True, stopped_design_failed=True, source_unknowns_retained=True,
        script_sha256=E.sha(Path(__file__)), files_sha256={str(p.name): E.sha(p) for p in dest.iterdir() if p.is_file()}))
    print(pd.DataFrame(rows).query("model=='GAP_NATIVE' and period in ['full','2018-22','2023+','author_window']")
          [["period", "trades", "total", "trade_t", "daily_NW5_t", "sharpe", "max_dd"]].to_string(index=False))
    print(pd.DataFrame(placebo_rows).query("period=='full'").to_string(index=False))


if __name__ == "__main__":
    run()
