"""Frozen NQDB2 filter nulls and same-exit placebos.

No market data is loaded and no historical return is computed on import.
The caller supplies a Grid24 and the annotated features returned by replay.run.
Each potential decision/side is walked once with the shared grid._walk. A
compiled scheduler then preserves position occupancy, daily submission caps,
and changed reentries for thousands of random signal masks. The cache must
match the authoritative replay before its null distributions are used.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd

try:
    from numba import njit
except ImportError:
    def njit(*args, **kwargs):
        return lambda fun: fun

try:
    from grid import _walk
    from codex_nqdb2_replay import _period, _minute
except ImportError:
    from analysis.grid import _walk
    from analysis.codex_nqdb2_replay import _period, _minute


WHY = {0: "DB2.Stop", 1: "DB2.Target", 2: "DB2.VwapX", 3: "DB2.TimeX",
       4: "DB2.Carry", 5: "DB2.ExitOnClose", 6: "APEX.EarlyTimeX"}


@njit(cache=True)
def _outcomes(o, h, l, c, first, last, day, minute, below, early,
              decisions, target_points, stop_points, target_through,
              slip_ticks, commission, end_min, flat_min, vwap_bars,
              exit_on_close):
    # Each output row is decision candidate, side (-1,+1), then fields:
    # entry minute/price, exit minute/price, kind, exit feature row,
    # earliest new decision row, worst price, reason, net.
    n = len(first)
    result = np.full((len(decisions), 2, 10), np.nan)
    for q in range(len(decisions)):
        i = decisions[q]
        for side_ix in range(2):
            side = -1 if side_ix == 0 else 1
            result[q, side_ix, 6] = n + 1  # pending/censored stays occupied
            if i + 1 >= n:
                continue
            entry_minute = first[i + 1]
            entry = o[entry_minute]
            stop, target = entry - side * stop_points, entry + side * target_points
            worst, pending = entry, -1
            result[q, side_ix, 0] = entry_minute
            result[q, side_ix, 1] = entry
            for k in range(i + 1, n):
                a, z = first[k], last[k]
                kind, reason, px, ex, release = -1, -1, np.nan, -1, k
                if pending >= 0:
                    ex, px, kind, reason = a, o[a], 2, pending
                    worst = min(worst, o[a]) if side > 0 else max(worst, o[a])
                else:
                    gap = a > entry_minute and ((side > 0 and o[a] <= stop) or
                                                (side < 0 and o[a] >= stop))
                    if gap:
                        ex, px, kind, reason = a, o[a], 0, 0
                        worst = min(worst, px) if side > 0 else max(worst, px)
                    else:
                        ex0, px0, kind0, worst0 = _walk(o, h, l, c, a, z, side,
                                                        stop, target, target_through)
                        worst = min(worst, worst0) if side > 0 else max(worst, worst0)
                        if kind0 != 2:
                            ex, px, kind, reason = ex0, px0, kind0, kind0
                    if kind < 0 and end_min >= 0 and minute[k] == end_min:
                        ex, px, kind, reason = z, c[z], 2, 5
                if kind < 0:
                    if day[k] != day[k - 1]:
                        pending = 4
                    if vwap_bars > 0 and below[k] >= vwap_bars:
                        pending = 2
                    early_flat = early[k] and minute[k] >= 690
                    if early_flat or minute[k] >= flat_min:
                        if early_flat or exit_on_close:
                            ex, px, kind = z, c[z], 2
                            reason, release = (6 if early_flat else 3), k + 1
                        else:
                            pending = 3
                if kind >= 0:
                    result[q, side_ix, 2] = ex
                    result[q, side_ix, 3] = px
                    result[q, side_ix, 4] = kind
                    result[q, side_ix, 5] = k
                    result[q, side_ix, 6] = release
                    result[q, side_ix, 7] = worst
                    result[q, side_ix, 8] = reason
                    result[q, side_ix, 9] = (px - entry) * side * 20.0 - commission - (
                        1 + (kind != 1)) * 0.25 * slip_ticks * 20.0
                    break
    return result


@njit(cache=True)
def _schedule(rows, days, release, eligible, submission_sides, max_trades):
    chosen = np.empty(len(rows), dtype=np.int64)
    previous_day, attempts, free_at, count = -1, 0, -1, 0
    for q in range(len(rows)):
        if days[q] != previous_day:
            previous_day, attempts = days[q], 0
        if eligible[q] and rows[q] >= free_at and attempts < max_trades:
            side_ix = 1 if submission_sides[count] > 0 else 0
            chosen[count] = q * 2 + side_ix
            free_at = int(release[q, side_ix])
            attempts += 1
            count += 1
    return chosen[:count]


@njit(cache=True)
def _score(chosen, nets, exit_days, n_days):
    daily = np.zeros(n_days)
    total, count, squares = 0.0, 0, 0.0
    for encoded in chosen:
        value = nets[encoded]
        if np.isfinite(value):
            total += value
            squares += value * value
            count += 1
            daily[exit_days[encoded]] += value
    equity, peak, dd = 0.0, 0.0, 0.0
    for value in daily:
        equity += value
        peak = max(peak, equity)
        dd = max(dd, peak - equity)
    avg = total / count if count else np.nan
    variance = (squares - total * total / count) / (count - 1) if count > 1 else np.nan
    t = avg / np.sqrt(variance / count) if variance > 0 else np.nan
    return total, dd, count, avg, t


@dataclass
class OutcomeCache:
    features: pd.DataFrame
    decisions: np.ndarray
    values: np.ndarray
    dates: pd.DatetimeIndex
    max_trades: int
    years: tuple
    config: dict

    def eligible(self, veto_mode=1):
        if veto_mode not in (0, 1):
            raise ValueError("only frozen veto modes 0/1 are supported")
        rows = self.features.iloc[self.decisions]
        keep = rows.price_ok.to_numpy(bool)
        if veto_mode:
            keep &= rows.drift_pct.to_numpy(float) > -self.config["drift_threshold"]
        return keep

    def select(self, eligible=None, *, veto_mode=1, random_side_seed=None):
        if eligible is None:
            eligible = self.eligible(veto_mode)
        eligible = np.asarray(eligible, bool)
        if eligible.shape != self.decisions.shape:
            raise ValueError("eligible must have one flag per cached decision")
        sides = (np.ones(len(self.decisions), dtype=np.int64) if random_side_seed is None
                 else np.random.default_rng(random_side_seed).choice((-1, 1), len(self.decisions)))
        days = self.features.day.to_numpy(np.int64)[self.decisions]
        return _schedule(self.decisions, days, self.values[:, :, 6], eligible,
                         sides, self.max_trades)

    def score(self, selected):
        exits = self.values[:, :, 2].ravel()
        exit_days = np.where(np.isfinite(exits), exits // 1440, 0).astype(np.int64)
        result = _score(np.asarray(selected, np.int64), self.values[:, :, 9].ravel(),
                        exit_days, len(self.dates))
        return dict(zip(("total", "max_daily_dd", "trades", "avg", "t"), result))

    def ledger(self, selected):
        rows = []
        for encoded in selected:
            q, side_ix = divmod(int(encoded), 2)
            a = self.values[q, side_ix]
            if not np.isfinite(a[9]):
                continue  # authoritative replay omits censored/open orders too
            f = self.features.iloc[self.decisions[q]]
            entry_day, entry_j = divmod(int(a[0]), 1440)
            exit_day, exit_j = divmod(int(a[2]), 1440)
            rows.append(dict(decision_index=int(f.bar_index), global_decision=int(f.global_close),
                             decision_day=int(f.day), decision_j=int(f.j),
                             global_entry=int(a[0]), global_exit=int(a[2]),
                             day=entry_day, j0=entry_j, exit_day=exit_day, j1=exit_j,
                             date=self.dates[entry_day], exit_date=self.dates[exit_day],
                             raw_entry=a[1], raw_exit=a[3], side=(-1 if side_ix == 0 else 1),
                             kind=int(a[4]), exit_bar_index=int(self.features.iloc[int(a[5])].bar_index),
                             why=WHY[int(a[8])], net=a[9]))
        return pd.DataFrame(rows, columns=["decision_index", "global_decision", "decision_day", "decision_j",
            "global_entry", "global_exit", "day", "j0", "exit_day", "j1", "date", "exit_date",
            "raw_entry", "raw_exit", "side", "kind", "exit_bar_index", "why", "net"])


def build_outcome_cache(g, features, years=(2018, 2022), *, allow_post2022=False,
                        apex_safe=True, target_points=40.0, stop_points=75.0,
                        target_through=1.0, slip_ticks=1.0, commission=7.25,
                        session_end=2400, flatten_time=1530, max_trades=2,
                        vwap_exit_bars=7, exit_on_bar_close=False, boundary_len=15,
                        drift_threshold=0.10):
    """Walk every valid timing-window decision once per side, then cache it.

    ``features`` must be the annotated output from replay.run on the same
    frozen configuration and years. This does not infer holiday end times.
    """
    lo, end = _period(years, allow_post2022)
    f = features.loc[pd.DatetimeIndex(features.date) < end].reset_index(drop=True).copy()
    if f.empty:
        raise ValueError("cache needs nonempty annotated replay features")
    required = {"price_ok", "timing_ok", "early_date", "first_minute", "last_minute"}
    if not required.issubset(f.columns):
        raise ValueError("use annotated features returned by replay.run")
    if not apex_safe and f.early_date.any():
        raise ValueError("features and cache disagree on Apex early-close handling")
    universe = ((f.date >= lo) & f.timing_ok & (f.win_count >= boundary_len) & (f.boundary > 0))
    decisions = np.flatnonzero(universe.to_numpy()).astype(np.int64)
    arrays = [np.asarray(getattr(g, k).ravel(), float) for k in ("o", "h", "l", "c")]
    values = _outcomes(*arrays, f.first_minute.to_numpy(np.int64), f.last_minute.to_numpy(np.int64),
        f.day.to_numpy(np.int64), f.j.to_numpy(np.int64), f.bars_below_vwap.to_numpy(np.int64),
        f.early_date.to_numpy(bool) if apex_safe else np.zeros(len(f), bool), decisions,
        float(target_points), float(stop_points), float(target_through), float(slip_ticks),
        float(commission), -1 if session_end is None else _minute(session_end),
        _minute(flatten_time), int(vwap_exit_bars), bool(exit_on_bar_close))
    config = dict(apex_safe=apex_safe, target_points=target_points, stop_points=stop_points,
                  target_through=target_through, slip_ticks=slip_ticks, commission=commission,
                  session_end=session_end, flatten_time=flatten_time, vwap_exit_bars=vwap_exit_bars,
                  exit_on_bar_close=exit_on_bar_close, boundary_len=boundary_len,
                  drift_threshold=drift_threshold)
    return OutcomeCache(f, decisions, values, pd.DatetimeIndex(g.ts), max_trades, tuple(years), config)


def assert_replay_match(cache, trades, *, veto_mode=1, selected=None):
    """Require exact event/exit matching and cent-level net matching to replay."""
    actual = cache.ledger(cache.select(veto_mode=veto_mode) if selected is None else selected)
    keys = ["global_decision", "global_entry", "global_exit", "side", "kind", "why"]
    if len(actual) != len(trades):
        raise AssertionError(f"cache/replay trade counts differ: {len(actual)} / {len(trades)}")
    for key in keys:
        if not np.array_equal(actual[key].to_numpy(), trades[key].to_numpy()):
            raise AssertionError(f"cache/replay mismatch in {key}")
    for key in ("raw_entry", "raw_exit", "net"):
        np.testing.assert_allclose(actual[key].to_numpy(float), trades[key].to_numpy(float), atol=1e-8, rtol=0)
    return {"trades": len(actual), "exact_event_match": True, "net_tolerance": 1e-8}


def _ledger_stats(trades, dates):
    dates = pd.DatetimeIndex(dates)
    daily = trades.groupby("exit_date").net.sum().reindex(dates, fill_value=0).to_numpy(float)
    equity = np.r_[0.0, np.cumsum(daily)]
    x = trades.net.to_numpy(float)
    return dict(trades=len(x), total=float(x.sum()), avg=float(x.mean()) if len(x) else np.nan,
                t=float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 1 and x.std(ddof=1) > 0 else np.nan,
                max_daily_dd=float(np.max(np.maximum.accumulate(equity) - equity)))


def _null_summary(samples, observed):
    n = len(samples)
    return dict(replicates=n, observed=observed,
                fraction_observed_beats_profit=float((samples.total <= observed["total"]).mean()),
                fraction_observed_beats_dd=float((samples.max_daily_dd >= observed["max_daily_dd"]).mean()),
                fraction_observed_beats_both=float(((samples.total <= observed["total"]) &
                    (samples.max_daily_dd >= observed["max_daily_dd"])).mean()),
                p_profit_ge=float((1 + (samples.total >= observed["total"]).sum()) / (n + 1)),
                p_dd_le=float((1 + (samples.max_daily_dd <= observed["max_daily_dd"]).sum()) / (n + 1)),
                quantiles={key: {str(p): float(samples[key].quantile(p)) for p in (0.025, 0.5, 0.975)}
                           for key in ("total", "max_daily_dd", "trades")})


def filter_diagnostics(base, filtered, dates, *, replicates=1000, seed=20261024):
    """Match actual decisions; compare A1 with equal-count random A0 removals.

    Principal random drops match the NET trade-count reduction. If changed
    reentries make gross removals larger, return that sensitivity separately.
    """
    key = "global_decision" if "global_decision" in base else "decision_index"
    if base[key].duplicated().any() or filtered[key].duplicated().any():
        raise ValueError("decision matching requires one trade per source decision")
    removed = base.loc[~base[key].isin(filtered[key])].copy()
    added = filtered.loc[~filtered[key].isin(base[key])].copy()
    net_drop = len(base) - len(filtered)
    if net_drop < 0:
        raise ValueError("same-count random removal undefined when filtered has more trades")
    observed = _ledger_stats(filtered, dates)
    output = dict(base=_ledger_stats(base, dates), filtered=observed,
                  removed=_ledger_stats(removed, dates), new_reentries=_ledger_stats(added, dates),
                  removed_trades=removed, new_reentry_trades=added)
    for label, count in [("matched_net_count", net_drop), ("gross_removed_count", len(removed))]:
        if label == "gross_removed_count" and count == net_drop:
            continue
        rows = []
        for iteration in range(replicates):
            rng = np.random.default_rng(seed + iteration)
            keep = np.ones(len(base), bool)
            keep[rng.choice(len(base), count, replace=False)] = False
            rows.append(dict(seed=seed + iteration, **_ledger_stats(base.iloc[np.flatnonzero(keep)], dates)))
        samples = pd.DataFrame(rows)
        output[label] = dict(drop_count=count, summary=_null_summary(samples, observed), samples=samples)
    return output


def signal_drop_null(cache, *, replicates=1000, seed=20271024):
    """Drop as many eligible A0 signal decisions as actual veto, then rerun.

    Every price-eligible decision participates, including decisions that were
    blocked by an open position or the daily cap in A0. Random removals can
    therefore change subsequent entries, occupancy and total trade count.
    """
    base = cache.eligible(0)
    filtered = cache.eligible(1)
    eligible_indices = np.flatnonzero(base)
    n_drop = int((base & ~filtered).sum())
    observed = cache.score(cache.select(filtered))
    rows = []
    for iteration in range(replicates):
        rng = np.random.default_rng(seed + iteration)
        keep = base.copy()
        keep[rng.choice(eligible_indices, n_drop, replace=False)] = False
        rows.append(dict(seed=seed + iteration, **cache.score(cache.select(keep))))
    samples = pd.DataFrame(rows)
    return dict(drop_signal_decisions=n_drop, base_signal_decisions=int(base.sum()),
                summary=_null_summary(samples, observed), samples=samples)


def placebos(cache, *, side_replicates=100, time_replicates=100,
             side_seed=20281024, time_seed=20291024, veto_mode=1):
    """Randomize actual primary sides/times, retaining its submitted count/date.

    Random sides are assigned at the actual primary decision set. Changed
    exits can block a later scheduled decision but never add a new decision.
    Random times sample the primary submitted count for each Date, from all
    warmed-up decisions in the same eligible clock window without price/veto.
    """
    primary = cache.select(veto_mode=veto_mode)
    observed = cache.score(primary)
    primary_mask = np.zeros(len(cache.decisions), bool)
    primary_mask[primary // 2] = True
    side_rows, time_rows = [], []
    for iteration in range(side_replicates):
        seed = side_seed + iteration
        selected = cache.select(primary_mask, random_side_seed=seed)
        side_rows.append(dict(seed=seed, **cache.score(selected)))
    options = time_schedule_options(cache, primary_mask)
    for iteration in range(time_replicates):
        seed = time_seed + iteration
        eligible = random_time_mask(cache, seed, options=options)
        selected = cache.select(eligible)
        time_rows.append(dict(seed=seed, submitted=len(selected), target_submitted=len(primary),
                              **cache.score(selected)))
    output = {}
    for name, rows in (("random_side", side_rows), ("random_time", time_rows)):
        samples = pd.DataFrame(rows)
        output[name] = dict(summary=_null_summary(samples, observed), samples=samples)
        if name == "random_time":
            output[name]["count_check"] = dict(
                target_submissions=len(primary),
                min_actual_submissions=int(samples.submitted.min()),
                max_actual_submissions=int(samples.submitted.max()),
                all_dates_preserved=True)
            output[name]["conditioning"] = (
                "Primary active Dates and submitted counts are fixed; feasible decision sets "
                "also condition on the realized future path through position occupancy. "
                "This is a constrained timing diagnostic, not an unconditional entry-time null.")
    return output


def time_schedule_options(cache, primary_mask=None):
    """All feasible same-Date decision sets with the primary submitted count.

    Source cap is two. A two-decision option is feasible only when the first
    long position has exited before the second decision phase. This prevents
    proposed signals blocked by occupancy from silently shrinking the null.
    """
    if primary_mask is None:
        primary_mask = np.zeros(len(cache.decisions), bool)
        primary_mask[cache.select() // 2] = True
    days = cache.features.day.to_numpy(np.int64)[cache.decisions]
    options = []
    for day in np.unique(days):
        group = np.flatnonzero(days == day)
        count = int(primary_mask[group].sum())
        if count == 0:
            continue
        if count == 1:
            choices = group[:, None]
        elif count == 2:
            choices = np.array([(a, b) for i, a in enumerate(group) for b in group[i + 1:]
                                if cache.decisions[b] >= cache.values[a, 1, 6]], dtype=np.int64)
        else:
            raise ValueError("frozen time-null supports at most two submissions per Date")
        if not len(choices):
            raise AssertionError("no feasible schedule reproduces primary per-Date submission count")
        options.append(choices)
    return options


def random_time_mask(cache, seed, *, options=None):
    """Uniform feasible intradate choices; reject a cross-date blocked history."""
    if options is None:
        options = time_schedule_options(cache)
    rng = np.random.default_rng(seed)
    for _ in range(10000):
        keep = np.zeros(len(cache.decisions), bool)
        for choices in options:
            keep[choices[rng.integers(len(choices))]] = True
        # Each Date already has the exact source count. If an earlier Date's
        # carry blocks a chosen decision, reject the whole sampled history.
        if len(cache.select(keep)) == int(keep.sum()):
            return keep
    raise RuntimeError("could not sample a globally count-preserving time schedule")


def synthetic_checks():
    """Check occupancy/reentries, null counts and cache against synthetic replay."""
    try:
        from codex_nqdb2_replay import _fixture_grid, run
    except ImportError:
        from analysis.codex_nqdb2_replay import _fixture_grid, run
    bars = [("2020-01-01", 1200, 100, 110, 90, 100, 1)]
    bars += [("2020-01-02", 1000, 100, 120, 90, 120, 1),
             ("2020-01-02", 1001, 120, 161, 119, 160, 1),
             ("2020-01-02", 1030, 150, 160, 140, 160, 1),
             ("2020-01-02", 1031, 160, 201, 159, 200, 1),
             ("2020-01-02", 1100, 190, 200, 180, 200, 1),
             ("2020-01-02", 1130, 200, 201, 199, 200, 1),
             ("2020-01-02", 1530, 200, 201, 199, 200, 1),
             ("2020-01-02", 1531, 200, 201, 199, 200, 1)]
    g = _fixture_grid(["2020-01-01", "2020-01-02"], bars)
    kwargs = dict(years=(2020, 2020), boundary_len=1, apex_safe=False)
    trades, f = run(g, veto_mode=0, **kwargs)
    cache = build_outcome_cache(g, f, **kwargs)
    assert_replay_match(cache, trades, veto_mode=0)
    # Null sides must preserve exact draw consumption and reentries.
    for seed in (4, 17):
        trades, _ = run(g, veto_mode=0, random_side_seed=seed, **kwargs)
        assert_replay_match(cache, trades, selected=cache.select(veto_mode=0, random_side_seed=seed))
        trades, _ = run(g, veto_mode=0, random_time_seed=seed, **kwargs)
        rng = np.random.default_rng(seed)
        eligible = np.zeros(len(cache.decisions), bool)
        eligible[rng.choice(len(cache.decisions), min(2, len(cache.decisions)), replace=False)] = True
        assert_replay_match(cache, trades, selected=cache.select(eligible))
    keep = cache.eligible(0)
    keep[0] = False
    mask = np.ones(len(f), bool)
    mask[cache.decisions[0]] = False
    trades, _ = run(g, veto_mode=0, decision_mask=mask, **kwargs)
    assert_replay_match(cache, trades, selected=cache.select(keep))
    assert list(cache.ledger(cache.select(keep)).decision_j) == [630, 660]
    null = signal_drop_null(cache, replicates=5)
    assert len(null["samples"]) == 5
    for seed in (2, 11, 29):
        time_mask = random_time_mask(cache, seed)
        assert len(cache.select(time_mask)) == len(cache.select())
    # Built-in EOC is before decisions; the source Carry is next-native-open.
    carry_bars = [("2020-01-01", 1200, 100, 110, 90, 100, 1),
                  ("2020-01-02", 1000, 100, 120, 90, 120, 1),
                  ("2020-01-02", 1001, 120, 121, 119, 120, 1),
                  ("2020-01-02", 2345, 122, 123, 121, 122, 1),
                  ("2020-01-03", 1, 125, 126, 124, 125, 1)]
    g2 = _fixture_grid(["2020-01-01", "2020-01-03"], carry_bars)
    for session_end in (None, 2400):
        config = dict(**kwargs, flatten_time=2359, vwap_exit_bars=0,
                      session_end=session_end)
        trades, f = run(g2, veto_mode=0, **config)
        cache2 = build_outcome_cache(g2, f, **config)
        assert_replay_match(cache2, trades, veto_mode=0)
    # Early liquidation follows the entry decision phase, and costs two fills.
    early_bars = [("2020-07-02", 1200, 100, 110, 90, 100, 1),
                  ("2020-07-03", 1000, 100, 120, 90, 120, 1),
                  ("2020-07-03", 1001, 120, 121, 119, 120, 1),
                  ("2020-07-03", 1030, 120, 121, 119, 120, 1),
                  ("2020-07-03", 1130, 130, 131, 129, 130, 1),
                  ("2020-07-03", 1131, 200, 201, 199, 200, 1)]
    g3 = _fixture_grid(["2020-07-02", "2020-07-03"], early_bars)
    config = dict(years=(2020, 2020), boundary_len=1, apex_safe=True)
    trades, f = run(g3, veto_mode=0, **config)
    cache3 = build_outcome_cache(g3, f, **config)
    assert_replay_match(cache3, trades, veto_mode=0)
    assert trades.iloc[0].why == "APEX.EarlyTimeX"
    # Censored positions are omitted without unlocking subsequent decisions.
    g4 = _fixture_grid(["2020-01-01", "2020-01-02"], bars[:4])
    trades, f = run(g4, veto_mode=0, target_points=1000, **kwargs)
    cache4 = build_outcome_cache(g4, f, target_points=1000, **kwargs)
    assert_replay_match(cache4, trades, veto_mode=0)
    assert len(trades) == 0 and len(trades.attrs["censored"]) == 1
    return ["cached_shared_walk_exact_synthetic_replay", "random_side_draw_consumption",
            "random_time_same_window", "dropped_decision_new_reentry", "signal_null_counts",
            "carry_vs_EOC_phase", "early_close_phase", "endpoint_censoring",
            "time_null_actual_submissions_preserved"]


def run_saved_period(*, stage="design", prereg_sha, gate_file=None,
                     output_root="analysis/outputs/codex_nqdb2_test"):
    """Reproduce diagnostics from the five frozen, already-saved profiles.

    Recent diagnostics require the same explicit saved passing gate as the
    profile runner. A failed design strategy gate never opens a later period.
    """
    import json
    import pickle
    import time
    from pathlib import Path
    try:
        from codex_nqdb2_replay import run
        from codex_nqdb2_run_profiles import PREREG_SHA, PROFILES, sha256
    except ImportError:
        from analysis.codex_nqdb2_replay import run
        from analysis.codex_nqdb2_run_profiles import PREREG_SHA, PROFILES, sha256
    if prereg_sha != PREREG_SHA or stage not in ("design", "recent"):
        raise ValueError("explicit frozen preregistration SHA and valid stage required")
    if stage == "recent":
        if gate_file is None:
            raise ValueError("recent diagnostics require a saved passing design gate")
        gate = json.loads(Path(gate_file).read_text())
        if gate.get("passed") is not True or gate.get("prereg_sha") != PREREG_SHA:
            raise ValueError("design gate must pass and match preregistration")
    root = Path(output_root)
    manifest = json.loads((root / f"{stage}_manifest.json").read_text())
    if manifest["prereg_sha"] != prereg_sha:
        raise ValueError("saved profiles do not match frozen preregistration")
    years = tuple(manifest["years"])
    started = time.perf_counter()
    with open(manifest["cache_path"], "rb") as stream:
        g = pickle.load(stream)
    features = pd.read_pickle(root / f"{stage}_features.pkl")
    ledgers, caches, checks = {}, {}, {}
    for profile, parameters in PROFILES.items():
        ledger = pd.read_csv(root / f"{stage}_{profile}.csv", parse_dates=["date", "exit_date"])
        trades, f = run(g, years, features=features, allow_post2022=stage == "recent", **parameters)
        cache_parameters = {key: value for key, value in parameters.items() if key != "veto_mode"}
        cache = build_outcome_cache(g, f, years, allow_post2022=stage == "recent", **cache_parameters)
        checks[profile] = assert_replay_match(cache, ledger, veto_mode=parameters["veto_mode"])
        assert_replay_match(cache, trades, veto_mode=parameters["veto_mode"])
        ledgers[profile], caches[profile] = ledger, cache
    print(f"{stage}: five fixed profiles match cached outcomes exactly", flush=True)

    # Verify selected null seeds in the authoritative stateful Python replay.
    null_checks = []
    for family in ("A", "S"):
        cache = caches[family + "1"]
        base_mask = cache.eligible(0)
        indices = np.flatnonzero(base_mask)
        drop_count = int((base_mask & ~cache.eligible(1)).sum())
        for seed in (20271024, 20271025, 20272023):
            keep = base_mask.copy()
            keep[np.random.default_rng(seed).choice(indices, drop_count, replace=False)] = False
            full_mask = np.ones(len(cache.features), bool)
            full_mask[cache.decisions[~keep]] = False
            trades, _ = run(g, years, features=features, veto_mode=0, apex_safe=family == "A",
                            decision_mask=full_mask, allow_post2022=stage == "recent", record_orders=False)
            assert_replay_match(cache, trades, selected=cache.select(keep))
            null_checks.append(dict(type="signal_drop", family=family, seed=seed, trades=len(trades)))
    cache = caches["A1"]
    primary = cache.select()
    primary_mask = np.zeros(len(cache.decisions), bool)
    primary_mask[primary // 2] = True
    primary_ids = cache.features.bar_index.to_numpy(np.int64)[cache.decisions[primary_mask]]
    days = cache.features.day.to_numpy(np.int64)[cache.decisions]
    for seed in (20281024, 20281025, 20281123):
        trades, _ = run(g, years, features=features, apex_safe=True, entry_schedule=primary_ids,
                        random_side_seed=seed, allow_post2022=stage == "recent", record_orders=False)
        assert_replay_match(cache, trades, selected=cache.select(primary_mask, random_side_seed=seed))
        null_checks.append(dict(type="random_side", seed=seed, trades=len(trades)))
    for seed in (20291024, 20291025, 20291123):
        keep = random_time_mask(cache, seed)
        schedule = cache.features.bar_index.to_numpy(np.int64)[cache.decisions[keep]]
        trades, _ = run(g, years, features=features, apex_safe=True, entry_schedule=schedule,
                        allow_post2022=stage == "recent", record_orders=False)
        assert_replay_match(cache, trades, selected=cache.select(keep))
        null_checks.append(dict(type="random_time", seed=seed, trades=len(trades)))
    print(f"{stage}: 12 selected null reruns match cached outcomes exactly", flush=True)
    output = root / f"diagnostics_{stage}"
    output.mkdir(parents=True, exist_ok=True)

    def save_nested(value, path):
        if isinstance(value, pd.DataFrame):
            filename = "_".join(path) + ".csv"
            value.to_csv(output / filename, index=False)
            return dict(csv=filename, rows=len(value), sha256=sha256(output / filename))
        if isinstance(value, dict):
            return {str(key): save_nested(item, path + [str(key)]) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [save_nested(item, path) for item in value]
        if isinstance(value, (np.integer, np.bool_)):
            return value.item()
        if isinstance(value, (float, np.floating)):
            return float(value) if np.isfinite(value) else None
        return value

    results = dict(stage=stage, prereg_sha=prereg_sha, years=list(years),
                   seed_offsets=dict(trade_drop=0, signal_drop=10000, random_side=20000,
                                     random_time=30000), base_seed=20261024,
                   profile_parity=checks, selected_null_parity=null_checks,
                   synthetic_checks=synthetic_checks(),
                   daily_dd_definition="realized exit-date net, zero initial equity included; not account MTM",
                   time_null_definition="exact actual primary submitted count per Date; uniform feasible same-Date decision sets from warmed-up clock bars; cross-Date blocking histories rejected",
                   side_null_definition="actual primary decision set, randomized submitted sides; no added decisions")
    invalid_time = output / "placebos_random_time_samples_before_count_fix.csv"
    results["time_null_implementation_correction"] = dict(
        issue="first design implementation preserved proposed count, but occupancy blocked later decisions",
        resolution="uniform sampling among feasible same-Date decision sets preserving actual submissions",
        strategy_rules_changed=False, prior_design_time_null_valid=False,
        prior_invalid_design_count_range=[691, 720], prior_invalid_design_count_median=704,
        primary_design_count=813, prior_invalid_draws=100,
        retained_invalid_samples=str(invalid_time) if invalid_time.exists() else "diagnostics_design/placebos_random_time_samples_before_count_fix.csv")
    for family in ("A", "S"):
        results[family + "_filter"] = filter_diagnostics(ledgers[family + "0"], ledgers[family + "1"], g.ts)
        results[family + "_signal_null"] = signal_drop_null(caches[family + "1"])
        print(f"{stage}: {family} 1000 matched trade drops and 1000 signal reruns complete", flush=True)
    results["placebos"] = placebos(caches["A1"])
    results["elapsed_seconds"] = time.perf_counter() - started
    saved = save_nested(results, [])
    (output / "summary.json").write_text(json.dumps(saved, indent=2, allow_nan=False) + "\n")
    print(f"{stage}: diagnostics saved to {output} in {results['elapsed_seconds']:.2f}s", flush=True)
    return saved


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    stage = parser.add_mutually_exclusive_group()
    stage.add_argument("--design", action="store_true")
    stage.add_argument("--recent", action="store_true")
    parser.add_argument("--prereg-sha")
    parser.add_argument("--gate-file")
    parser.add_argument("--output", default="analysis/outputs/codex_nqdb2_test")
    args = parser.parse_args()
    if args.design or args.recent:
        run_saved_period(stage="design" if args.design else "recent", prereg_sha=args.prereg_sha,
                         gate_file=args.gate_file, output_root=args.output)
    else:
        print("Synthetic checks:", ", ".join(synthetic_checks()))
