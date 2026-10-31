"""H05 immediate current-personal19 bench; imports read no financial rows.

The command requires committed source/adjudication and an exact successful
protected-design marker. CSV date metadata is inspected BEFORE numeric fields;
only2018--22 numbers may be converted. No account/payout engine or prices run.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import csv
import fcntl
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
import numpy as np
import pandas as pd
import metrics as M
import resampling as R
from codex_anson_personal import histories, simulate_daily, paired_mean_interval, historical_annual_effect_interval
from codex_hunt_v2_ldf_delta import runtime_versions, utcnow

SCRIPT = "analysis/codex_hunt_v2_highwin_bench.py"
PLAN = "agents/codex/plans/hunt_v2_highwin_confirmation.md"
ADJUDICATION = "agents/codex/research/hunt_v2_highwin_bench_adjudication.md"
SOURCE_MAP = "agents/codex/research/hunt_v2_bench_source_map.md"
OUT = ROOT / "analysis/outputs/codex_hunt_v2_highwin_confirmation"
BENCH = OUT / "personal19_design"
DESIGN = OUT / "design_verified_execution.json"
SOURCE_PIN = "d14dc9a153df128aafd3f48d4fea2aa78b88bb28"
SEED, N, HORIZON, BLOCK = 2026102605, 5000, 252, 20
LEG_COLUMNS = ("VaultBreak", "OvernightBiasML", "MondayLong", "ExpirationOpenShort", "LateDayFlow", "NFPFade",
    "BridgeMondayLong", "CLSundayFade_perMCL", "ESMOCFollow_perMES", "RelativeStrength", "FC2B", "TwinContinuation",
    "OvernightTick", "DualThrust", "Kusho", "S47", "S30", "SwingTarget", "PaperTrend")
BASELINES = {
    "1.24": ("analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.24/baseline_daily19.csv",
        "d724c7d02b6db71e63ba705079dbea7fefaa42c6b4f436308a28993ca1908803"),
    "1.04": ("analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.04/baseline_daily19.csv",
        "a52649b1e7301ebafe474a781a0cb25c5a1d24204ccb9716a382d0405056b24f")}
LIMITS = [
    "Daily published-book booking only; no joint intraday margin/liquidation, funded, evaluation, pass or payout claim.",
    "Core native-fee correction uses nonzero daily activity and undercounts some reentries; exact per-leg trade-count bounds are unsupported here.",
    "Twin is marked v1 checker history, not an exact v2.1 ledger. EMPTY/REPLACE remove BOTH BO and MO, not an isolated MO slot.",
    "Kusho is exit-booked; S30/MOC retain inherited fee/mark approximations. An exact current alternate daily-mark envelope is unsupported here.",
    "Baseline input endsOT evidence2026-07-07; only2018--22 is inspected now. Later book zeros are never assumed known no-trade.",
    "Fee1.04 is the fixed published-research diagnostic, not a verified broker quote or complete fee/mark/coverage uncertainty bound.",
    "Nominal statistical book improvement can be reported; unsupported implementation bounds prevent a certified book PASS."]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe(value):
    if isinstance(value, dict): return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)): return [safe(v) for v in value]
    if isinstance(value, np.generic): return safe(value.item())
    if isinstance(value, float) and not np.isfinite(value): return None
    return value


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(safe(value), handle, indent=2, allow_nan=False)
        handle.write("\n")


def csv_once(path, frame, *, index=False):
    with path.open("x") as handle: frame.to_csv(handle, index=index, float_format="%.12g")


def date_first_rows(handle, fields):
    """Strings outside design period never reach float(), pandas inference or numpy."""
    reader = csv.DictReader(handle)
    if not reader.fieldnames or "date" not in reader.fieldnames or any(f not in reader.fieldnames for f in fields):
        raise ValueError("Missing required CSV header.")
    kept, metadata, excluded = [], [], 0
    for source_line, raw in enumerate(reader, 2):
        date = pd.Timestamp(raw["date"])
        if pd.isna(date) or date.tzinfo is not None or date != date.normalize(): raise ValueError("Invalid daily date metadata.")
        if not pd.Timestamp("2018-01-01") <= date < pd.Timestamp("2023-01-01"):
            excluded += 1
            continue
        values = {name: float(raw[name]) for name in fields}
        if not all(np.isfinite(list(values.values()))): raise ValueError("Invalid design-period financial value.")
        kept.append(dict(date=date, **values))
        metadata.append(dict(source_line=source_line, date=date.date().isoformat(), event_id=raw.get("event_id")))
    return pd.DataFrame(kept, columns=["date", *fields]), metadata, excluded


def read_baseline(path):
    with Path(path).open(newline="") as handle:
        header = next(csv.reader(handle))
        if header != ["date", *LEG_COLUMNS]: raise ValueError("Exact current19 roster/order required.")
    with Path(path).open(newline="") as handle: frame, metadata, excluded = date_first_rows(handle, LEG_COLUMNS)
    frame = frame.set_index("date")
    if frame.empty or frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
        raise ValueError("Baseline design dates must be complete/unique/ordered.")
    if set(frame.index.year) != set(range(2018, 2023)): raise ValueError("Five design years required.")
    return frame, dict(design_rows=len(frame), excluded_date_metadata_rows=excluded,
        future_financial_values_converted=0, exact19_columns=True, first=str(frame.index[0].date()), last=str(frame.index[-1].date()))


def read_candidate(path, days, fee):
    fields = ("gross_mnq", "commission_mnq", "entry_slippage_mnq", "exit_slippage_mnq", "net_mnq")
    with Path(path).open(newline="") as handle: trades, metadata, excluded = date_first_rows(handle, fields)
    if excluded or len(trades) != 216: raise ValueError("Exact216design-only frozen events required.")
    event_ids = [row["event_id"] for row in metadata]
    if None in event_ids or len(set(event_ids)) != 216: raise ValueError("Distinct saved event IDs required.")
    if trades.date.duplicated().any() or not trades.date.isin(days).all(): raise ValueError("Candidate dates must map exactly into baseline; no later-date rescue.")
    if not np.allclose(trades.commission_mnq, 1.24, rtol=0, atol=1e-12): raise ValueError("Frozen native design fee changed.")
    expected = trades.gross_mnq - trades.commission_mnq - trades.entry_slippage_mnq - trades.exit_slippage_mnq
    np.testing.assert_allclose(expected, trades.net_mnq, rtol=0, atol=1e-7)
    values = trades.net_mnq.to_numpy() + 1.24 - float(fee)
    daily = pd.Series(values, index=pd.DatetimeIndex(trades.date)).groupby(level=0).sum().reindex(days, fill_value=0.)
    np.testing.assert_allclose(daily.sum(), values.sum(), rtol=0, atol=1e-7)
    return daily, dict(events=216, contracts_per_event=1, event_ids=event_ids,
        total_native_net=float(values.sum()), fee_RT=float(fee), mapping="same date, no lost/future-capped rows")


def configurations(frame, primary, control):
    base = frame.sum(axis=1)
    empty = base - frame.TwinContinuation
    return {"BASE": base, "ADD": base + primary, "EMPTY": empty, "REPLACE": empty + primary,
        "TIME_ADD": base + control, "TIME_REPLACE": empty + control}


def measurements(frame, primary, control, idx, fee):
    plans = configurations(frame, primary, control)
    raw, rows, effects, historical, joint = {}, [], [], [], []
    for name, values in plans.items():
        profit, dd = simulate_daily(values.to_numpy(), idx)
        raw[name + "__profit"], raw[name + "__dd"] = profit, dd
        rows.append(dict(fee=fee, plan=name, profit_p5=np.percentile(profit, 5), profit_p50=np.median(profit),
            profit_p95=np.percentile(profit, 95), profit_mean=profit.mean(), dd_p50=np.median(dd), dd_p95=np.percentile(dd, 95),
            p_losing_year=np.mean(profit <= 0), return_DD=np.median(profit) / max(np.median(dd), 1e-9),
            median_profit_over_DD95=np.median(profit) / max(np.percentile(dd, 95), 1e-9), histories=len(idx), whole_contract_size=1))
        for period in ("2018-22", *map(str, range(2018, 2023))):
            subset = values if period == "2018-22" else values[values.index.year == int(period)]
            metrics = M.perf(np.r_[0., subset.to_numpy()], subset[subset != 0].to_numpy())
            historical.append(dict(fee=fee, plan=name, period=period, days=len(subset), total=subset.sum(),
                historical_annual_profit=subset.mean() * 252, max_DD_from_zero=R.max_dd(subset), **metrics,
                metric_basis="daily portfolios; initialzero passed to sharedmetrics for DD, no trade t promotion claim"))
    summary = pd.DataFrame(rows).set_index("plan", drop=False)
    for name in ("ADD", "REPLACE", "TIME_ADD", "TIME_REPLACE"):
        for ref in ("BASE", "EMPTY"):
            dp = raw[name + "__profit"] - raw[ref + "__profit"]
            dd = raw[name + "__dd"] - raw[ref + "__dd"]
            lo, hi = paired_mean_interval(dp, seed=SEED, n=N)
            dlo, dhi = paired_mean_interval(dd, seed=SEED, n=N)
            hlo, hhi = historical_annual_effect_interval((plans[name] - plans[ref]).to_numpy(), seed=SEED, n=N, block=BLOCK)
            ratio_delta = summary.loc[name, "return_DD"] - summary.loc[ref, "return_DD"]
            dd95_delta = summary.loc[name, "dd_p95"] - summary.loc[ref, "dd_p95"]
            nominal = bool(ratio_delta > 0 and np.median(dp) > 0 and dd95_delta <= 0)
            effects.append(dict(fee=fee, plan=name, reference=ref, paired_profit_delta_p5=np.percentile(dp, 5),
                paired_profit_delta_p50=np.median(dp), paired_profit_delta_p95=np.percentile(dp, 95),
                mean_profit_delta=dp.mean(), mean_profit_MC_sampling_CI95_lo=lo, mean_profit_MC_sampling_CI95_hi=hi,
                p_profit_delta_positive=np.mean(dp > 0), mean_DD_delta=dd.mean(),
                paired_DD_delta_p5=np.percentile(dd, 5), paired_DD_delta_p50=np.median(dd), paired_DD_delta_p95=np.percentile(dd, 95),
                mean_DD_MC_sampling_CI95_lo=dlo, mean_DD_MC_sampling_CI95_hi=dhi,
                historical_annual_effect_CI95_lo=hlo, historical_annual_effect_CI95_hi=hhi,
                return_DD_delta=ratio_delta, DD95_delta=dd95_delta, nominal_paired_gate_pass=nominal,
                intervals_scope="MC precision conditional on history; separate historical block interval; not independent forward confidence"))
    for model, candidate in (("PROTECTED_HW", primary), ("TIME_CONTROL", control)):
        for name, other in {"BASE": plans["BASE"], "EMPTY": plans["EMPTY"], **{k: frame[k] for k in ("VaultBreak", "DualThrust", "RelativeStrength", "TwinContinuation")}}.items():
            loss = other < 0
            correlation = candidate.corr(other) if candidate.std() > 0 and other.std() > 0 else None
            joint.append(dict(fee=fee, model=model, reference=name, correlation=correlation,
                reference_loss_days=int(loss.sum()), joint_loss_days=int((loss & (candidate < 0)).sum()),
                candidate_profit_on_reference_loss_days=float(candidate[loss].sum()),
                candidate_profit_on_reference_nonloss_days=float(candidate[~loss].sum())))
    return pd.DataFrame(plans), pd.DataFrame(rows), pd.DataFrame(effects), pd.DataFrame(historical), pd.DataFrame(joint), raw


def require_design_ledgers(marker):
    """Pure marker-schema gate: every financial ledger read must be hash-bound."""
    artifacts = marker.get("artifacts_sha256")
    required = {"design_PROTECTED_HW_trades.csv", "design_TIME_CONTROL_trades.csv"}
    if not isinstance(artifacts, dict) or not required.issubset(artifacts):
        raise ValueError("Design PASS marker must hash-bind both exact financial ledgers.")
    for name in required:
        value = artifacts[name]
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError("Malformed required design-ledger SHA256:" + name)


def verify(prereg, design_sha):
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    if branch != "codex/work": raise ValueError("Research stays codex/work.")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", prereg, "HEAD"], cwd=ROOT)
    dependencies = (SCRIPT, PLAN, ADJUDICATION, SOURCE_MAP, "analysis/codex_anson_personal.py", "analysis/metrics.py",
        "analysis/resampling.py", "analysis/codex_hunt_v2_ldf_delta.py", "agents/codex/RESEARCH_CONTROLS.md")
    hashes = {}
    for name in dependencies:
        raw = (ROOT / name).read_bytes()
        for ref in (prereg, "HEAD"):
            if subprocess.check_output(["git", "show", f"{ref}:{name}"], cwd=ROOT) != raw:
                raise ValueError("Commit exact bench code/protocol/dependency before returns:" + name)
        hashes[name] = hashlib.sha256(raw).hexdigest()
    if sha(DESIGN) != design_sha: raise ValueError("Explicit exact design marker SHA required.")
    marker = json.loads(DESIGN.read_text())
    if marker.get("statistical_design_pass") is not True or marker.get("phase") != "frozen_two_model_native_cost_design":
        raise ValueError("Immediate bench only after exact H05 protected design PASS.")
    if marker.get("models") != ["PROTECTED_HW", "TIME_CONTROL"]: raise ValueError("Unexpected design models.")
    require_design_ledgers(marker)
    for name, expected in marker["artifacts_sha256"].items():
        if Path(name).name != name or sha(OUT / name) != expected: raise ValueError("Design artifact changed:" + name)
        hashes[str((OUT / name).relative_to(ROOT))] = expected
    hashes[str(DESIGN.relative_to(ROOT))] = design_sha
    for fee, (name, expected) in BASELINES.items():
        if sha(ROOT / name) != expected: raise ValueError("Fixed baseline changed:" + name)
        other = name.replace("/UNIFORM/", "/SUNDAY2/")
        if sha(ROOT / other) != expected: raise ValueError("Independent saved baseline copy differs:" + fee)
        hashes[name], hashes[other] = expected, expected
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_highwin_confirmation*"):
        if (directory / "personal19_design/bench_attempt.json").exists():
            raise ValueError("Retain prior bench attempt; no automatic retry/alternate directory.")
    return dict(prereg=prereg, implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        design_marker_sha256=design_sha, hashes=hashes, runtime=runtime_versions(), source_pin=SOURCE_PIN,
        bootstrap=dict(n=N, horizon=HORIZON, block=BLOCK, seed=SEED, paired=True, convention="shared noncircular starts0..T-block exclusive"))


def recheck(binding):
    for name, expected in binding["hashes"].items():
        if sha(ROOT / name) != expected: raise ValueError("Frozen bench input changed:" + name)


@contextmanager
def exclusive_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "bench.lock").open("a+") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try: yield
        finally: fcntl.flock(handle, fcntl.LOCK_UN)


def run(prereg, design_sha):
    with exclusive_lock():
        binding = verify(prereg, design_sha)
        BENCH.mkdir(parents=True, exist_ok=True)
        dump(BENCH / "bench_attempt.json", dict(started_utc=utcnow(), **binding))
        dump(BENCH / "bench_pre_rows_binding.json", binding)
        frames, candidates, audits = {}, {}, {}
        for fee, (name, _) in BASELINES.items():
            frame, audit = read_baseline(ROOT / name)
            frames[fee] = frame
            p, pa = read_candidate(OUT / "design_PROTECTED_HW_trades.csv", frame.index, fee)
            c, ca = read_candidate(OUT / "design_TIME_CONTROL_trades.csv", frame.index, fee)
            if pa["event_ids"] != ca["event_ids"]: raise ValueError("Both models require same ordered events.")
            candidates[fee] = p, c
            audits[fee] = dict(baseline=audit, primary=pa, control=ca)
        pd.testing.assert_index_equal(frames["1.24"].index, frames["1.04"].index)
        idx = histories(len(frames["1.24"]), n=N, horizon=HORIZON, block=BLOCK, seed=SEED)
        with (BENCH / "paired_histories.npy").open("xb") as handle: np.save(handle, idx, allow_pickle=False)
        gates, names = {}, ["paired_histories.npy", "bench_attempt.json", "bench_pre_rows_binding.json"]
        for fee in BASELINES:
            folder = BENCH / ("fee_" + fee)
            folder.mkdir()
            portfolios, summary, effects, historical, joint, raw = measurements(frames[fee], *candidates[fee], idx, fee)
            csv_once(folder / "baseline_design19.csv", frames[fee].rename_axis("date"), index=True)
            csv_once(folder / "candidate_daily.csv", pd.DataFrame(dict(PROTECTED_HW=candidates[fee][0], TIME_CONTROL=candidates[fee][1])).rename_axis("date"), index=True)
            csv_once(folder / "daily_portfolios.csv", portfolios.rename_axis("date"), index=True)
            for name, table in (("mc_summary.csv", summary), ("paired_effects.csv", effects), ("historical_metrics_by_year.csv", historical), ("joint_losses.csv", joint)):
                csv_once(folder / name, table)
            with (folder / "paired_paths.npz").open("xb") as handle: np.savez_compressed(handle, **raw)
            gates[fee] = {plan: bool(effects[effects.plan == plan].nominal_paired_gate_pass.all()) for plan in ("ADD", "REPLACE")}
            names.extend(str(path.relative_to(BENCH)) for path in folder.iterdir() if path.is_file())
        nominal = [name for name in ("ADD", "REPLACE") if gates["1.24"][name] and gates["1.04"][name]]
        gate = dict(nominal_design_book_improvement=bool(nominal), nominal_survivors=nominal, paired_tests_by_fee=gates,
            certified_book_pass=False, status="LIMITED_UNSUPPORTED_BASELINE_IMPLEMENTATION_ENVELOPE" if nominal else "FAIL_NO_FROZEN_BOOK_IMPROVEMENT",
            uncertainty_bound_supported=False, next_action="No promotion/validation from nominal gain until declared baseline limitations are resolved; no retuning." if nominal else "CloseH05before further robustness/2023+.",
            full_Twin_slot_removed_in_EMPTY_REPLACE=True, economic_strategy_evaluations_added=0, limitations=LIMITS)
        dump(BENCH / "bench_gate.json", gate)
        dump(BENCH / "bench_source_calendar_audit.json", audits)
        names += ["bench_gate.json", "bench_source_calendar_audit.json"]
        recheck(binding)
        marker = dict(completed_utc=utcnow(), phase="immediate_personal19_design_bench", **binding, **gate,
            artifacts_sha256={name: sha(BENCH / name) for name in names}, future_candidate_or_book_financial_values_converted=0,
            random_histories_shared_across_all_models_and_fees=True, native_candidate_fee_exact=True,
            book_rows=4, unselectable_time_context_rows=2, funded_or_evaluation_or_live_action=False)
        dump(BENCH / "bench_verified_execution.json", marker)
        return gate


def fixtures():
    # Future numeric sentinels would fail float(); only date metadata may pass.
    raw = io.StringIO("date,x\n2018-01-02,3\n2023-01-02,FORBIDDEN_FUTURE_NUMBER\n2017-12-29,FORBIDDEN_WARMUP_NUMBER\n")
    frame, metadata, excluded = date_first_rows(raw, ["x"])
    assert frame.x.tolist() == [3.] and excluded == 2 and metadata[0]["source_line"] == 2
    days = pd.bdate_range("2018-01-01", periods=60)
    frame = pd.DataFrame(0., index=days, columns=LEG_COLUMNS)
    frame["TwinContinuation"] = np.tile([10., -7., 3.], 20)
    frame["VaultBreak"] = np.tile([4., -8., 9.], 20)
    primary = pd.Series(np.tile([3., -1., 2.], 20), index=days)
    plans = configurations(frame, primary, primary * 2)
    np.testing.assert_allclose(plans["REPLACE"], plans["EMPTY"] + primary)
    np.testing.assert_allclose(plans["ADD"], plans["BASE"] + primary)
    idx = histories(60, n=5, horizon=252, block=20, seed=SEED)
    assert idx.shape == (5, 252) and idx.min() >= 0 and idx.max() < 60
    p, dd = simulate_daily(np.full(60, -2.), idx)
    np.testing.assert_array_equal(p, np.full(5, -504.))
    np.testing.assert_array_equal(dd, np.full(5, 504.))
    # All five years, invented values only: exercise metrics/interval/joint paths
    # and independently reconcile saved endpoint and drawdown arrays.
    days = pd.bdate_range("2018-01-01", "2022-12-31")
    frame = pd.DataFrame(0., index=days, columns=LEG_COLUMNS)
    frame["TwinContinuation"] = np.resize([10., -7., 3.], len(days))
    frame["VaultBreak"] = np.resize([4., -8., 9.], len(days))
    primary = pd.Series(np.resize([3., -1., 2.], len(days)), index=days)
    idx = histories(len(days), n=5, horizon=252, block=20, seed=SEED)
    daily, summary, effects, yearly, joint, raw_paths = measurements(frame, primary, 2 * primary, idx, "ARTIFICIAL")
    assert len(summary) == 6 and len(effects) == 8 and len(yearly) == 36 and len(joint) == 12
    for name in daily:
        values = daily[name].to_numpy()[idx]
        cumulative = values.cumsum(1)
        peak = np.maximum.accumulate(np.c_[np.zeros(len(idx)), cumulative], axis=1)[:, 1:]
        np.testing.assert_allclose(raw_paths[name + "__profit"], values.sum(1), rtol=0, atol=1e-9)
        np.testing.assert_allclose(raw_paths[name + "__dd"], (peak - cumulative).max(1), rtol=0, atol=1e-9)
    assert effects[effects.plan == "ADD"].paired_profit_delta_p50.gt(0).all()
    bound = {"design_PROTECTED_HW_trades.csv": "a" * 64, "design_TIME_CONTROL_trades.csv": "b" * 64}
    require_design_ledgers(dict(artifacts_sha256=bound))
    for incomplete in ({}, {"design_PROTECTED_HW_trades.csv": "a" * 64},
            {"design_TIME_CONTROL_trades.csv": "b" * 64}, {**bound, "design_TIME_CONTROL_trades.csv": "bad"}):
        try: require_design_ledgers(dict(artifacts_sha256=incomplete))
        except ValueError: pass
        else: raise AssertionError("Missing/malformed financial-ledger binding must reject before rows.")
    assert safe(dict(a=np.float64(1), b=np.nan)) == dict(a=1., b=None)
    return dict(passed=True, checks=["date-before-float future/warmup sentinel", "exactwholeTwin EMPTY/REPLACE", "fixedpaired252x20draw shape", "DD includes initialzero", "fullsixrow/fiveyearpairedbench arithmetic", "bothfinancialledgerhashesrequired_before_rows", "nonfiniteJSONexplicit"],
        actual_baseline_or_candidate_financial_rows_read=False, script_sha256=sha(ROOT / SCRIPT))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("fixtures", "bench"))
    parser.add_argument("--prereg")
    parser.add_argument("--design-sha")
    args = parser.parse_args()
    if args.phase == "fixtures": print(json.dumps(fixtures()))
    else:
        if not args.prereg or not args.design_sha: parser.error("bench requires explicit --prereg and --design-sha")
        print(json.dumps(safe(run(args.prereg, args.design_sha))))
