"""Frozen OB v2 diagnostics; consumes replay ledgers, never changes strategy rules.

Prepared before returns. The CLI requires --allow-return-analysis; recent data also
requires --design-gate-passed. Replay, including random controls, belongs to
codex_ob_v2_replay.py. Statistical definitions come from the repository helpers.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd

import metrics as M
import montecarlo as MC
import resampling as R
from trials import parse_tier_list


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "analysis/outputs/codex_ob_v2_plan_test/diagnostics"
SEED = 231023
PERIODS = ("full", "design", "recent")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump_json(path, obj):
    def clean(x):
        if isinstance(x, dict):
            return {str(k): clean(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [clean(v) for v in x]
        if isinstance(x, (np.integer,)):
            return int(x)
        if isinstance(x, (np.floating, float)):
            return float(x) if np.isfinite(x) else None
        if isinstance(x, np.bool_):
            return bool(x)
        if isinstance(x, Path):
            return str(x)
        return x
    value = json.dumps(clean(obj), indent=2) + "\n"
    if str(path).endswith(".gz"):
        with gzip.open(path, "wt") as stream:
            stream.write(value)
    else:
        Path(path).write_text(value)


def normalize_trades(trades):
    t = trades.copy()
    needed = {"date", "side", "j0", "j1", "entry", "exit", "net"}
    missing = needed - set(t)
    if missing:
        raise ValueError(f"Replay ledger lacks {sorted(missing)}")
    t["date"] = pd.to_datetime(t["date"]).dt.normalize()
    t = t.sort_values(["date", "j0", "j1", "side"]).reset_index(drop=True)
    if not t["side"].isin([-1, 1]).all():
        raise ValueError("Sides must be -1/+1")
    if not np.isfinite(t[["entry", "exit", "net"]].to_numpy(float)).all():
        raise ValueError("Nonfinite replay fill/P&L")
    return t


def period_mask(dates, period):
    dates = pd.DatetimeIndex(dates)
    if period == "full":
        return np.ones(len(dates), dtype=bool)
    if period == "design":
        return dates.year <= 2022
    if period == "recent":
        return dates.year >= 2023
    return dates.year == int(period)


def daily(trades, days):
    days = pd.DatetimeIndex(days).normalize()
    return trades.groupby("date")["net"].sum().reindex(days, fill_value=0.0)


def t_stat(x):
    x = np.asarray(x, dtype=float)
    sd = x.std(ddof=1) if len(x) > 1 else np.nan
    return float(x.mean() / sd * np.sqrt(len(x))) if sd > 0 else np.nan


def ranked_counts():
    """Read-only use of trials.py's parser: never rebuild TRIALS.csv here."""
    ranked = parse_tier_list(ROOT / "TIER_LIST.md")
    logged = pd.read_csv(ROOT / "TRIALS.csv")
    return dict(
        ranked_items=len(ranked), ranked_variants=int(ranked.variants.sum()),
        trial_csv_items=len(logged), trial_csv_variants=int(logged.variants.sum()),
        source="current TIER_LIST.md parsed by analysis/trials.py; TRIALS.csv disclosed separately",
        tier_sha256=sha(ROOT / "TIER_LIST.md"), trials_sha256=sha(ROOT / "TRIALS.csv"),
        promotion_t_threshold=M.t_threshold(len(ranked)),
        current_trial_two_fixed_ledgers=2,
        ranked_count_includes_this_unranked_experiment=False,
    )


def one_metrics(trades, days, ranked_n):
    d = daily(trades, days)
    if not len(d):
        return {}
    x = trades.net.to_numpy(float)
    row = M.perf(d, x)
    row.update(total=float(x.sum()), t=t_stat(x),
               dsr_items=M.deflated_sharpe(x, ranked_n) if len(x) >= 10 else np.nan,
               ranked_items=ranked_n,
               max_dd_initial_zero=R.max_dd(d), days=len(d),
               event_days=int(trades.date.nunique()))
    return row


def standard_metrics(ledgers, days, ranked_n, include_recent=True):
    rows = []
    periods = list(PERIODS if include_recent else ("design",))
    periods += [str(y) for y in sorted(set(pd.DatetimeIndex(days).year))]
    for label, trades in ledgers.items():
        for period in periods:
            p_days = pd.DatetimeIndex(days)[period_mask(days, period)]
            if not len(p_days):
                continue
            p = trades.loc[period_mask(trades.date, period)]
            for side, select in (("all", np.ones(len(p), bool)), ("long", p.side > 0),
                                 ("short", p.side < 0)):
                row = one_metrics(p.loc[select], p_days, ranked_n)
                rows.append(dict(ledger=label, period=period, side=side, **row))
    return pd.DataFrame(rows)


def nested_filter(kept, control):
    """Assert exact nesting after shared 100-session warm-up before judging filter."""
    keys = ["date", "j0", "side"]
    if kept.duplicated(keys).any() or control.duplicated(keys).any():
        raise ValueError("Nonunique date/entry-minute/side key")
    c = control.set_index(keys)
    k = kept.set_index(keys)
    if not k.index.isin(c.index).all():
        raise ValueError("OBV2 is not a subset of BRIDGE100 trades")
    paired = c.reindex(k.index)
    for col in ("j1", "entry", "exit", "net"):
        if not np.allclose(paired[col], k[col], rtol=0, atol=1e-7):
            raise ValueError(f"Filter nesting changed kept-trade {col}")
    mask = control.set_index(keys).index.isin(k.index)
    return control.loc[mask].copy(), control.loc[~mask].copy(), mask


def filter_metrics(kept, control, days, ranked_n, include_recent=True):
    selected, removed, mask = nested_filter(kept, control)
    selected["filter_status"] = "kept"
    removed["filter_status"] = "removed"
    frame = standard_metrics({"kept": selected, "removed": removed,
                              "unfiltered": control}, days, ranked_n, include_recent)
    return frame, selected, removed, mask


def _null_summary(samples, actual, period, kind):
    return dict(
        period=period, kind=kind, runs=len(samples), actual_trades=actual["trades"],
        actual_event_days=actual["event_days"], actual_total=actual["total"],
        actual_max_dd=actual["max_dd"],
        random_total_p5=samples.total.quantile(.05),
        random_total_p50=samples.total.quantile(.50),
        random_total_p95=samples.total.quantile(.95),
        random_max_dd_p5=samples.max_dd.quantile(.05),
        random_max_dd_p50=samples.max_dd.quantile(.50),
        random_max_dd_p95=samples.max_dd.quantile(.95),
        p_random_total_ge_actual=float((samples.total >= actual["total"]).mean()),
        p_random_dd_le_actual=float((samples.max_dd <= actual["max_dd"]).mean()),
        p_random_dominates_both=float(((samples.total >= actual["total"]) &
                                       (samples.max_dd <= actual["max_dd"])).mean()),
        actual_profit_percentile=float((samples.total < actual["total"]).mean()),
        actual_lower_dd_percentile=float((samples.max_dd > actual["max_dd"]).mean()),
    )


def random_removal_nulls(kept, control, days, runs=1000, seed=SEED,
                         include_recent=True):
    """Keep exact year/side counts; separately keep exact yearly event-day counts."""
    rows, summaries = [], []
    periods = PERIODS if include_recent else ("design",)
    rng = np.random.default_rng(seed)
    for period in periods:
        calendar = pd.DatetimeIndex(days)[period_mask(days, period)]
        if not len(calendar):
            continue
        k = kept.loc[period_mask(kept.date, period)].reset_index(drop=True)
        c = control.loc[period_mask(control.date, period)].reset_index(drop=True)
        day_idx = calendar.get_indexer(c.date)
        if (day_idx < 0).any():
            raise ValueError("Trade day outside common trading calendar")
        net = c.net.to_numpy(float)
        years = c.date.dt.year.to_numpy()
        side = c.side.to_numpy()
        actual_daily = daily(k, calendar)
        actual = dict(trades=len(k), event_days=k.date.nunique(), total=k.net.sum(),
                      max_dd=R.max_dd(actual_daily))
        groups = []
        for year in np.unique(years):
            for s in (-1, 1):
                pool = np.flatnonzero((years == year) & (side == s))
                count = int(((k.date.dt.year == year) & (k.side == s)).sum())
                if count > len(pool):
                    raise ValueError("Retained stratum larger than control")
                groups.append((pool, count))
        day_groups = []
        control_event_days = np.unique(day_idx)
        for year in np.unique(years):
            pool = control_event_days[calendar[control_event_days].year == year]
            count = int(k.loc[k.date.dt.year == year, "date"].nunique())
            day_groups.append((pool, count))
        for kind in ("year_side_exact_trade_count", "year_exact_event_day_count"):
            current = []
            for run in range(runs):
                if kind == "year_side_exact_trade_count":
                    chunks = [rng.choice(pool, count, replace=False) for pool, count in groups
                              if count]
                    idx = np.concatenate(chunks) if chunks else np.empty(0, dtype=int)
                else:
                    chunks = [rng.choice(pool, count, replace=False) for pool, count in day_groups
                              if count]
                    chosen_days = np.concatenate(chunks) if chunks else np.empty(0, dtype=int)
                    idx = np.flatnonzero(np.isin(day_idx, chosen_days))
                d = np.bincount(day_idx[idx], weights=net[idx], minlength=len(calendar))
                row = dict(period=period, kind=kind, run=run, trades=len(idx),
                           event_days=len(np.unique(day_idx[idx])), total=float(net[idx].sum()),
                           mean=float(net[idx].mean()) if len(idx) else np.nan,
                           max_dd=R.max_dd(d))
                rows.append(row)
                current.append(row)
            summaries.append(_null_summary(pd.DataFrame(current), actual, period, kind))
    return pd.DataFrame(rows), pd.DataFrame(summaries)


def bootstrap_and_mc(ledgers, days, out, include_recent=True):
    """Existing block bootstrap; standalone MC is scaled NQ, EOD only."""
    bootstrap_rows, permutations, mc_rows = [], [], []
    for label, trades in ledgers.items():
        if include_recent:
            p = trades.loc[period_mask(trades.date, "recent")]
            p_days = pd.DatetimeIndex(days)[period_mask(days, "recent")]
            for side, q in (("all", p), ("long", p[p.side > 0]), ("short", p[p.side < 0])):
                d = daily(q, p_days)
                if len(d) >= 10 and (d != 0).any():
                    bt = R.bootstrap(d, n=5000, block=10, seed=SEED, chunk=250)
                    for metric, values in bt.iterrows():
                        bootstrap_rows.append(dict(ledger=label, period="recent", side=side,
                                                   metric=metric, **values.to_dict()))
                    bootstrap_rows.append(dict(ledger=label, period="recent", side=side,
                        metric="P(Sharpe<=0)", actual=np.nan, p5=np.nan,
                        p50=bt.attrs["p_sharpe_le_0"], p95=np.nan))
                    permutations.append(dict(ledger=label, period="recent", side=side,
                        **R.permutation(d, n=5000, seed=SEED, chunk=250)))
        for period in (PERIODS if include_recent else ("design",)):
            p = trades.loc[period_mask(trades.date, period)]
            p_days = pd.DatetimeIndex(days)[period_mask(days, period)]
            if len(p_days) <= 10 or len(p) == 0:
                continue
            for cost in ("scaled_NQ", "candidate_extra_1.275_MNQ_RT"):
                micro = p.copy()
                micro["net"] = p.net.to_numpy(float) * .1 - (0 if cost == "scaled_NQ" else 1.275)
                d = daily(micro, p_days)
                mc_rows.append(dict(ledger=label, period=period, cost=cost, kind="daily_block",
                    **MC.daily_mc(d, horizon=252, n=5000, block=10, seed=SEED,
                                  trail=2000, lock=100)))
                if period == "full" or not include_recent:
                    mc_rows.append(dict(ledger=label, period=period, cost=cost, kind="trade_bootstrap",
                        **MC.trade_mc(micro.net, n=10000, replace=True, seed=SEED)))
    pd.DataFrame(bootstrap_rows).to_csv(out / "recent_bootstrap.csv", index=False)
    pd.DataFrame(permutations).to_csv(out / "recent_permutation.csv", index=False)
    pd.DataFrame(mc_rows).to_csv(out / "standalone_1mnq_montecarlo.csv", index=False)
    return dict(bootstrap_series=len(permutations), bootstrap_resamples_per_series=5000,
                mc_evaluations=len(mc_rows), mc_daily_resamples=5000,
                mc_trade_resamples=10000)


def random_control_metrics(controls, actual, days, ranked_n, requested_runs=100,
                           include_recent=True):
    """Consume the replay engine's frozen side/time controls, without selecting one."""
    controls = controls.copy()
    if not {"control", "run"}.issubset(controls):
        raise ValueError("Random control ledger needs control and run columns")
    controls["date"] = pd.to_datetime(controls.date).dt.normalize()
    rows, summaries = [], []
    for control in ("random_side", "random_entry_time"):
        for run in range(requested_runs):
            t = normalize_trades(controls[(controls.control == control) & (controls.run == run)])
            for period in (PERIODS if include_recent else ("design",)):
                p_days = pd.DatetimeIndex(days)[period_mask(days, period)]
                if not len(p_days):
                    continue
                p = t.loc[period_mask(t.date, period)]
                a = actual.loc[period_mask(actual.date, period)]
                rows.append(dict(control=control, run=run, period=period,
                    requested_trades=len(a), effective_trade_ratio=len(p) / len(a) if len(a) else np.nan,
                    **one_metrics(p, p_days, ranked_n)))
        frame = pd.DataFrame([r for r in rows if r["control"] == control])
        for period in frame.period.unique():
            sub = frame[frame.period == period]
            a = actual.loc[period_mask(actual.date, period)]
            p_days = pd.DatetimeIndex(days)[period_mask(days, period)]
            am = one_metrics(a, p_days, ranked_n)
            summaries.append(dict(control=control, period=period, runs=len(sub),
                actual_trades=am["trades"], actual_mean=am["avg"], actual_total=am["total"],
                actual_max_dd_initial_zero=am["max_dd_initial_zero"],
                effective_trades_min=int(sub.trades.min()),
                effective_trades_median=float(sub.trades.median()),
                effective_trades_max=int(sub.trades.max()),
                mean_p5=sub.avg.quantile(.05), mean_p50=sub.avg.quantile(.5), mean_p95=sub.avg.quantile(.95),
                total_p5=sub.total.quantile(.05), total_p50=sub.total.quantile(.5), total_p95=sub.total.quantile(.95),
                dd_p50=sub.max_dd_initial_zero.quantile(.5), dd_p95=sub.max_dd_initial_zero.quantile(.95),
                p_random_total_ge_actual=float((sub.total >= am["total"]).mean()),
                p_random_mean_ge_actual=float((sub.avg >= am["avg"]).mean())))
    return pd.DataFrame(rows), pd.DataFrame(summaries)


def generate_controls(base, out, *, g=None, ctx=None):
    """Use the replay owner's engine; 200 descriptive paths, zero selection."""
    import codex_ob_v2_replay as replay

    if g is None or ctx is None:
        g, ctx = replay.build_context()
    frames, metadata = [], []
    for control, first_seed in (("random_side", SEED), ("random_entry_time", SEED + 1000)):
        for run in range(100):
            kwargs = {"rand_side_seed" if control == "random_side" else "random_time_seed": first_seed + run}
            t = replay.replay_events(g, ctx, base, **kwargs)
            details = t.attrs.get("diagnostics", {}).copy()
            t = t.copy()
            t["control"] = control
            t["run"] = run
            t["seed"] = first_seed + run
            frames.append(t)
            metadata.append(dict(control=control, run=run, seed=first_seed + run,
                                 requested_events=len(base), effective_events=len(t),
                                 replay_diagnostics=details))
    controls = pd.concat(frames, ignore_index=True)
    controls.to_csv(Path(out) / "random_control_trades.csv.gz", index=False, compression="gzip")
    dump_json(Path(out) / "random_control_replay_counts.json.gz", metadata)
    return controls


def run_diagnostics(ledgers, days, out=DEFAULT_OUT, *, include_recent=True,
                    controls=None, input_paths=()):
    """Parent must explicitly authorize return analysis and the recent-data release."""
    started = time.monotonic()
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    days = pd.DatetimeIndex(pd.to_datetime(days)).normalize().unique().sort_values()
    days = days[days.year >= 2018]
    if not include_recent:
        days = days[days.year <= 2022]
    normalized = {label: normalize_trades(t) for label, t in ledgers.items()}
    if set(normalized) != {"OBV2", "BRIDGE100"}:
        raise ValueError("Exactly OBV2 and BRIDGE100 frozen ledgers are required")
    if not include_recent and any((t.date.dt.year >= 2023).any() for t in normalized.values()):
        raise ValueError("Design-only invocation received recent returns")
    counts = ranked_counts()
    metrics = standard_metrics(normalized, days, counts["ranked_items"], include_recent)
    metrics.to_csv(out / "metrics.csv", index=False)
    filtered, selected, removed, keep_mask = filter_metrics(
        normalized["OBV2"], normalized["BRIDGE100"], days, counts["ranked_items"], include_recent)
    filtered.to_csv(out / "filter_kept_removed_metrics.csv", index=False)
    removed.to_csv(out / "filter_removed_trades.csv", index=False)
    samples, null_summary = random_removal_nulls(selected, normalized["BRIDGE100"], days,
                                               include_recent=include_recent)
    samples.to_csv(out / "matched_random_removal_runs.csv", index=False)
    null_summary.to_csv(out / "matched_random_removal_summary.csv", index=False)
    statistical_counts = bootstrap_and_mc(normalized, days, out, include_recent)
    control_counts = {}
    if controls is not None:
        cr, cs = random_control_metrics(controls, normalized["OBV2"], days,
                                       counts["ranked_items"], include_recent=include_recent)
        cr.to_csv(out / "random_side_time_runs.csv", index=False)
        cs.to_csv(out / "random_side_time_summary.csv", index=False)
        control_counts = dict(random_side_runs=100, random_entry_time_runs=100,
                              random_control_period_evaluations=len(cr))
    dump_json(out / "diagnostics_metadata.json", dict(
        elapsed_seconds=time.monotonic() - started,
        date_min=str(days.min().date()), date_max=str(days.max().date()), trading_days=len(days),
        recent_released=include_recent, fixed_rule_ledgers=2, ledgers=list(normalized),
        trials=counts, standard_metrics_rows=len(metrics), filter_metrics_rows=len(filtered),
        matched_removal_samples=len(samples), matched_removal_samples_per_family_period=1000,
        random_removal_families=2, random_removal_periods=3 if include_recent else 1,
        filter_exact_nested=True, kept_trades=int(keep_mask.sum()), removed_trades=int((~keep_mask).sum()),
        statistical_evaluations=statistical_counts, **control_counts,
        controls_are_descriptive=True, no_best_control_selected=True,
        audit_packaging="Detailed replay per-day counts and control trade ledger gzip-compressed; no return calculation changed.",
        previous_selection_exposure="2023+ already seen by original author; historical replication, not clean holdout",
        dd_definition="metrics.perf standard max_dd plus resampling.max_dd with initial-zero peak; nulls use latter",
        micro_accounting_limitation="One MNQ is 0.1 times NQ replay net, primary commission $0.725 RT; extra-cost sensitivity subtracts $1.275/MNQ RT. Neither verifies native actual MNQ fees.",
        standalone_mc_limitation="Existing montecarlo.daily_mc checks end-of-day trailing only; not intraday mark-to-market/daily-loss enforcement or a substitute for the paired account bench.",
        trial_count_limitation="Two frozen strategy ledgers. Null samples/side-time controls and metric/MC/bootstrap evaluations are disclosed diagnostic evaluations, not independently selected candidates; original author's prior optimization count unknown.",
        input_sha256={str(Path(p).relative_to(ROOT) if Path(p).is_relative_to(ROOT) else p): sha(p)
                      for p in input_paths},
        script_sha256=sha(Path(__file__)), seed=SEED,
    ))
    return dict(metrics_rows=len(metrics), matched_null_rows=len(samples),
                random_controls_done=controls is not None,
                output=str(out), elapsed_seconds=time.monotonic() - started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obv2", nargs="+", type=Path, required=True)
    parser.add_argument("--bridge100", nargs="+", type=Path, required=True)
    parser.add_argument("--days", type=Path, required=True, help="CSV with date column; trading sessions only")
    parser.add_argument("--controls", type=Path, help="Replay-generated 100 side/time controls, CSV")
    parser.add_argument("--generate-controls", action="store_true", help="Use codex_ob_v2_replay.replay_events")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--allow-return-analysis", action="store_true")
    parser.add_argument("--design-gate-passed", action="store_true")
    args = parser.parse_args()
    if not args.allow_return_analysis:
        parser.error("Return analysis needs explicit parent authorization (--allow-return-analysis)")
    if args.controls and args.generate_controls:
        parser.error("Choose --controls or --generate-controls")
    # Read no candidate file before the authorization guard above.
    paths = args.obv2 + args.bridge100 + [args.days] + ([args.controls] if args.controls else [])
    ledgers = {label: pd.concat([pd.read_csv(p) for p in files], ignore_index=True)
               for label, files in (("OBV2", args.obv2), ("BRIDGE100", args.bridge100))}
    days = pd.read_csv(args.days).date
    controls = pd.read_csv(args.controls) if args.controls else None
    if args.generate_controls:
        args.out.mkdir(parents=True, exist_ok=True)
        if not args.design_gate_passed and (pd.to_datetime(ledgers["OBV2"].date).dt.year >= 2023).any():
            parser.error("Recent controls require the released design gate")
        controls = generate_controls(normalize_trades(ledgers["OBV2"]), args.out)
    result = run_diagnostics(ledgers, days, args.out, include_recent=args.design_gate_passed,
                             controls=controls, input_paths=paths)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
