"""Second-agent implementation/accounting audit of existing frozen design ledgers.

No alternative strategy, parameter search, economic replication or account simulation.
Reads raw design minutes and existing ledgers; writes only task-output audit.json.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_drift_video_20261030"
SCRIPT = ROOT / "analysis/codex_drift_video_20261030.py"
PLAN = ROOT / "agents/codex/plans/drift_video_20261030.md"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    checks, errors = {}, []

    def check(name, value, detail=None):
        checks[name] = dict(passed=bool(value), detail=detail)
        if not value:
            errors.append(name)

    def close(a, b):
        return bool(np.allclose(np.asarray(a, float), np.asarray(b, float), atol=1e-7, rtol=1e-10, equal_nan=True))

    inv = json.loads((OUT / "design_inventory.json").read_text())
    cov = pd.read_csv(OUT / "design_coverage.csv", parse_dates=["date"])
    sig = pd.read_csv(OUT / "design_signals.csv")
    daily = pd.read_csv(OUT / "design_daily.csv", index_col=0, parse_dates=[0])
    metrics = pd.read_csv(OUT / "design_metrics.csv", dtype={"year": str})
    files = [Path(z["path"]) for z in inv["inputs"]]
    check("design_input_names_only_2018_2022", {p.name for p in files} == {f"NQ_1min_{y}.csv" for y in range(2018, 2023)})
    check("raw_input_hashes_match_inventory", all(sha(z["path"]) == z["sha256"] for z in inv["inputs"]))
    raw = pd.concat([pd.read_csv(p) for p in files], ignore_index=True)
    raw["j"] = raw.time // 100 * 60 + raw.time % 100
    raw = raw.drop_duplicates(["date", "j"]).sort_values(["date", "j"])
    bydate = {int(d): x.set_index("j") for d, x in raw.groupby("date", sort=False)}
    first = pd.Timestamp(str(int(raw.date.min())))
    day_dates = {int((r.date - first).days): r.date for r in cov.itertuples()}
    coverage_by_date = cov.set_index("date")
    eligible = pd.DatetimeIndex(cov.loc[cov.eligible, "date"])
    exclusions = []
    for r in cov.itertuples():
        x = bydate.get(int(r.date.strftime("%Y%m%d")))
        present = set() if x is None else set(x.index)
        missing = sorted(set(range(510, r.exit_j + 1)) - present)
        check(f"coverage_{r.date.date()}", bool(r.eligible) == (not missing) and int(r.required) == r.exit_j - 509 and int(r.minutes) == int(r.required) - len(missing))
        if missing:
            exclusions.append(dict(date=r.date.date().isoformat(), missing_close_stamps_ct=[f"{j//60:02d}:{j%60:02d}" for j in missing], missing_minutes=len(missing)))
    check("twelve_missing_paths_retained", len(exclusions) == 12 and len(eligible) == 1247 and len(cov) == 1259)
    check("daily_eligible_dates_exact", daily.index.equals(eligible))

    # Independent, trailing-only pandas aggregation on deterministic sampled dates.
    samples = set(cov.loc[cov.eligible & (cov.kind == "early"), "date"])
    rng = np.random.default_rng(301036)
    for year, x in cov[cov.eligible].groupby(cov[cov.eligible].date.dt.year):
        samples.update(rng.choice(x.date.to_numpy(), min(6, len(x)), replace=False))
    samples = sorted(pd.Timestamp(z) for z in samples)
    feature_checks = 0
    for date in samples:
        d = int((date - first).days)
        x = bydate[int(date.strftime("%Y%m%d"))]
        exit_j = int(coverage_by_date.loc[date, "exit_j"])
        expected = []
        for j in range(570, min(870, exit_j - 25) + 1, 5):
            # Cut input at decision time; a future minute cannot enter any feature.
            trailing = x.loc[x.index <= j]
            agg = trailing.assign(bucket=((trailing.index + 14) // 15) * 15).groupby("bucket").agg(high=("high", "max"), low=("low", "min"), close=("close", "last"), volume=("volume", "sum"))
            end = j // 15 * 15
            full = agg.loc[(agg.index >= 525) & (agg.index <= end)]
            pv = ((full.high + full.low + full.close) / 3 * full.volume).cumsum()
            vw = pv / full.volume.cumsum()
            c, prior = agg.loc[end, "close"], agg.loc[end - 60, "close"]
            bias = 1 if c > vw.iloc[-1] and vw.iloc[-1] > vw.iloc[-2] and c / prior - 1 >= .001 else -1 if c < vw.iloc[-1] and vw.iloc[-1] < vw.iloc[-2] and c / prior - 1 <= -.001 else 0
            color = np.sign(trailing.loc[j, "close"] - trailing.loc[j - 4, "open"])
            previous = np.sign(trailing.loc[j - 5, "close"] - trailing.loc[j - 9, "open"])
            if bias and color == -bias and previous != -bias:
                expected.append((d, j, bias, 80., 40. if bias > 0 else 50., exit_j))
            feature_checks += 1
        saved = sig.loc[sig.day == d, ["day", "dj", "side", "stop", "target", "exit_j"]].to_numpy()
        check(f"independent_trailing_signals_{date.date()}", saved.shape == (len(expected), 6) and close(saved, np.asarray(expected).reshape(-1, 6)))

    summaries = {}
    all_trades = []
    for label, name, loss_col, total in [("primary", "design_trades.csv", "net_mnq", False), ("total_losses", "design_total_losses_trades.csv", "net_mnq", True), ("stress", "design_stress_trades.csv", "stress_mnq", False)]:
        t = pd.read_csv(OUT / name, parse_dates=["date"])
        all_trades.append(t)
        market = 1 + (t.kind != 1).astype(int)
        check(f"{label}_gross_cost_bridge", close(t.pnl, (t.exit-t.entry)*t.side*20*t.qty) and close(t.gross_mnq, t.pnl/10) and close(t.fees_mnq, 1.04) and close(t.market_fills, market) and close(t.slippage_mnq, .5*market) and close(t.net_mnq, t.pnl/10-1.04-.5*market) and close(t.stress_mnq, t.pnl/10-1.24-market) and close(t.net_nq, t.pnl-7.25-5*market))
        timing_ok = caps_ok = membership_ok = True
        for day, z in t.groupby("day", sort=False):
            date = day_dates[int(day)]
            exit_j = int(coverage_by_date.loc[date, "exit_j"])
            timing_ok &= date in eligible and len(z) <= 4 and bool(((z.j0 - 1) % 5 == 0).all()) and bool((z.j0 >= 571).all()) and bool((z.j0 - 1 <= min(870, exit_j - 25)).all()) and bool((z.j1 <= exit_j).all()) and bool((z.j1 >= z.j0).all())
            membership_ok &= all(bool(((sig.day == day) & (sig.dj == r.j0-1) & (sig.side == r.side)).any()) for r in z.itertuples())
            losses, prev_exit = 0, -1
            for r in z.itertuples():
                caps_ok &= losses < 2 and r.j0-1 >= prev_exit
                losses = losses + 1 if getattr(r, loss_col) < 0 else losses if total else 0
                prev_exit = r.j1
        check(f"{label}_timing_and_halfday_cutoff", timing_ok)
        check(f"{label}_one_position_and_net_loss_caps", caps_ok)
        check(f"{label}_entries_are_saved_source_signals", membership_ok)
        summaries[label] = dict(trades=len(t), by_year={str(y): dict(trades=len(z), net=float(z[loss_col].sum())) for y, z in t.groupby(t.date.dt.year)}, by_side={str(s): dict(trades=len(z), net=float(z[loss_col].sum())) for s, z in t.groupby("side")})
        if label == "primary":
            cols = ["gross_mnq", "fees_mnq", "slippage_mnq", "net_mnq", "stress_mnq", "net_nq"]
            summed = t.groupby("date")[cols].sum().reindex(eligible, fill_value=0.)
            check("all_primary_daily_columns_reconcile", close(daily[cols], summed))
            for r in metrics.itertuples():
                z = t if r.side == "all" else t[t.side == (1 if r.side == "long" else -1)]
                ds = eligible
                if r.year != "all":
                    z = z[z.date.dt.year == int(r.year)]
                    ds = eligible[eligible.year == int(r.year)]
                dd = z.groupby("date").net_mnq.sum().reindex(ds, fill_value=0.)
                eq = np.r_[0., dd.cumsum().to_numpy()]
                mdd = float((np.maximum.accumulate(eq)-eq).max())
                check(f"metric_accounting_{r.side}_{r.year}", len(z) == r.trades and len(ds) == r.days and close(z.net_mnq.sum(), r.total) and close(z.gross_mnq.sum(), r.gross) and close(z.fees_mnq.sum(), r.fees) and close(z.slippage_mnq.sum(), r.slippage) and close(dd.mean()/dd.std()*np.sqrt(len(dd)), r.daily_t) and close(mdd, r.max_dd))

    # All unique saved trades: verify entry price, earlier unhit brackets, exit conditions.
    unique = pd.concat(all_trades).drop_duplicates(["date", "j0", "j1", "side", "entry", "exit"])
    path_ok = True
    counts = dict(unique_saved_trades=len(unique), entry_bar_exits=0, target_exits=0, stop_exits=0, time_exits=0, simultaneous_exit_bars=0)
    for r in unique.itertuples():
        x = bydate[int(r.date.strftime("%Y%m%d"))]
        target = r.entry + r.side * (40 if r.side > 0 else 50)
        stop = r.entry - r.side * 80
        before = x.loc[(x.index >= r.j0) & (x.index < r.j1)]
        at = x.loc[r.j1]
        path_ok &= close(x.loc[r.j0, "open"], r.entry)
        if r.side > 0:
            earlier = (before.low <= stop) | (before.high >= target+1)
            hit_s, hit_t = at.low <= stop, at.high >= target+1
            gap = r.j1 > r.j0 and at.open <= stop
            target_first = at.high-at.open <= at.open-at.low
        else:
            earlier = (before.high >= stop) | (before.low <= target-1)
            hit_s, hit_t = at.high >= stop, at.low <= target-1
            gap = r.j1 > r.j0 and at.open >= stop
            target_first = at.open-at.low <= at.high-at.open
        path_ok &= not bool(earlier.any())
        if r.kind == 0:
            counts["stop_exits"] += 1
            path_ok &= bool(hit_s) and close(r.exit, at.open if gap else stop) and (gap or not hit_t or not target_first)
        elif r.kind == 1:
            counts["target_exits"] += 1
            path_ok &= bool(hit_t) and close(r.exit, target) and not gap and (not hit_s or target_first)
        else:
            counts["time_exits"] += 1
            path_ok &= int(r.kind) == 2 and not hit_s and not hit_t and close(r.exit, at.close) and r.j1 == int(coverage_by_date.loc[r.date, "exit_j"])
        counts["entry_bar_exits"] += int(r.j0 == r.j1)
        counts["simultaneous_exit_bars"] += int(hit_s and hit_t)
    check("all_saved_minute_paths_and_bracket_prices", path_ok)

    # Small synthetic checks invoke the shared engine, not an alternative engine.
    from types import SimpleNamespace
    from grid import execute
    toy = np.full((1, 6), 100.)
    g = SimpleNamespace(o=toy.copy(), h=toy.copy(), l=toy.copy(), c=toy.copy(), last_j=np.array([5]), ts=np.array(["2020-01-02"], dtype="datetime64[ns]"))
    s = pd.DataFrame([dict(day=0, dj=0, side=1, stop=80., target=40., exit_j=5)])
    g.h[0, 1], g.h[0, 2] = 140., 141.
    z = execute(g, s)
    check("shared_engine_requires_one_point_target_through", len(z) == 1 and z.kind.iloc[0] == 1 and z.j1.iloc[0] == 2)
    g.l[0, 1] = 20.
    z = execute(g, s)
    check("shared_engine_entry_bar_stop_active", z.kind.iloc[0] == 0 and z.j1.iloc[0] == 1 and z.exit.iloc[0] == 20.)
    g.l[0, 1], g.o[0, 2], g.l[0, 2] = 100., 10., 10.
    z = execute(g, s)
    check("shared_engine_gap_stop_at_open", z.kind.iloc[0] == 0 and z.j1.iloc[0] == 2 and z.exit.iloc[0] == 10.)

    watched = [PLAN, SCRIPT]
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    check("frozen_plan_and_script_match_HEAD", all(subprocess.run(["git", "cat-file", "-e", "HEAD:"+p.relative_to(ROOT).as_posix()], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0 and subprocess.run(["git", "diff", "--quiet", "HEAD", "--", str(p)], cwd=ROOT).returncode == 0 for p in watched))
    ledger_names = ["design_trades.csv", "design_total_losses_trades.csv", "design_stress_trades.csv", "design_daily.csv", "design_signals.csv", "design_metrics.csv", "design_coverage.csv", "design_inventory.json"]
    result = dict(review="Independent implementation/accounting review by a second agent; not blind economic replication, native fill validation, or Monte Carlo verification", passed=not errors, failing_checks=errors, checked_head=head, plan_sha256=sha(PLAN), implementation_sha256=sha(SCRIPT), audit_code_sha256=sha(__file__), ledger_sha256={n: sha(OUT/n) for n in ledger_names}, raw_design_years=[2018, 2019, 2020, 2021, 2022], sampled_signal_days=[d.date().isoformat() for d in samples], trailing_feature_decisions_checked=feature_checks, minute_path_checks=counts, accounting=summaries, excluded_missing_paths=exclusions, checks=checks, limits=["No new candidate definition or parameter selection", "Signals independently reconstructed only on listed sampled days", "All saved trade paths/costs/caps/accounting checked; not a separate full-universe economic replication", "Shared one-minute tie-break and NQ-price-to-MNQ proxy remain assumptions", "No 2023+ or account/MC tests performed", "Random-time control conditions on the complete-day source signal count and side order: retrospective null, not an executable alternative strategy", "Stress column in primary daily.csv is a fixed-primary-ledger cost bridge; executable stress is separately saved stress_trades.csv"])
    (OUT / "audit.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps(dict(passed=result["passed"], failing_checks=errors, checks=len(checks), sampled_days=len(samples), trailing_decisions=feature_checks, unique_trades=len(unique), excluded_paths=len(exclusions))))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
